// ============================================================================
#nullable disable
// waypoint_filter.cs — 航路点后处理 (障碍安全过滤 + 切换决策) (无 Unity 依赖提炼版)
//
// 源文件: Assets/Scripts/PathPlan.cs
//   ConvertPlannerPathToWaypoints (619–658) / ApplyWaypointSafetyConfig (660–672)
//   AssignWaypointsToFollower (674–711) / IsWaypointInsideObstacle (723–734)
//   IsWaypointSegmentBlocked (736–746) / SegmentIntersectsCircleXZ (748–764)
// 文档:   ../docs/08_execution.md
//
// 提炼差异: Vector3 → (x, z) float 元组 (XZ 平面); WaypointFollower 引用 → 决策函数
// (输入 follower 当前状态, 输出 新路径 / 保留旧路径 / 清空)。
// ============================================================================

using System;
using System.Collections.Generic;

namespace UsvPatrolPlanning
{
    public struct Waypoint2D
    {
        public float X, Z;                       // XZ 平面 (Unity 侧转换为 Vector3(x, shipY, z))
        public Waypoint2D(float x, float z) { X = x; Z = z; }
    }

    public static class WaypointFilter
    {
        // ═══ 安全边际 (源 660–672 行) ═══

        /// <summary>从概率模型配置推导点/线段安全边际</summary>
        public static (float pointMargin, float segmentMargin) ResolveSafetyMargins(int gridCellSize, int obstacleInflationRadius)
        {
            float baseMargin = obstacleInflationRadius > 0
                ? obstacleInflationRadius
                : (float)MathF.Ceiling(gridCellSize * 1.0f);
            float segmentExtra = Math.Max(10f, gridCellSize * 0.25f);
            float pointMargin = Math.Max(25f, baseMargin);
            float segmentMargin = Math.Max(pointMargin, baseMargin + segmentExtra);
            return (pointMargin, segmentMargin);
        }

        // ═══ 航路点过滤 (源 619–658 行) ═══

        /// <summary>
        /// A* 格中心折线 → 可执行航路点。
        /// 规则: [0]=船位始终保留; 障碍安全圈内点丢弃; <0.1m 重复点丢弃;
        ///       线段与障碍相交 (从第 2 段起) → 截断停止。
        /// </summary>
        public static List<Waypoint2D> ConvertPlannerPathToWaypoints(
            IList<System.Numerics.Vector2> plannerPath,
            List<ObcRect> obstacleRects,
            float pointMargin,
            float segmentMargin)
        {
            var waypoints = new List<Waypoint2D>();
            if (plannerPath == null || plannerPath.Count == 0) return waypoints;

            Waypoint2D? lastAccepted = null;
            bool isFirstPoint = true;
            for (int i = 0; i < plannerPath.Count; i++)
            {
                var point = plannerPath[i];
                Waypoint2D wp = new Waypoint2D(point.X, point.Y);

                // 第 0 个点(船当前位置)始终保留, 即使船在 inflated 区域内
                if (isFirstPoint)
                {
                    isFirstPoint = false;
                    waypoints.Add(wp);
                    lastAccepted = wp;
                    continue;
                }

                if (IsWaypointInsideObstacle(wp, obstacleRects, pointMargin)) continue;

                if (lastAccepted.HasValue && Dist(lastAccepted.Value, wp) < 0.1f) continue;

                // 第一段(船→A*首点)是逃逸段, 不做 segment 阻塞检查; 后续段正常检查
                if (waypoints.Count > 1 && lastAccepted.HasValue &&
                    IsWaypointSegmentBlocked(lastAccepted.Value, wp, obstacleRects, segmentMargin))
                    break;

                waypoints.Add(wp);
                lastAccepted = wp;
            }
            return waypoints;
        }

        // ═══ 切换决策 (源 674–711 行 AssignWaypointsToFollower) ═══

        public enum WaypointSwitchDecision { AssignNew, KeepOld, Clear }

        /// <summary>
        /// 决定 follower 路径如何切换。
        /// followerEnabled / hasTraversableWaypoints / isFinished / remainingCount
        /// 为 follower 当前状态 (Unity 侧由 WaypointFollower 提供)。
        /// </summary>
        public static WaypointSwitchDecision DecideSwitch(
            List<Waypoint2D> newPath,
            bool isRollingReplan,
            bool followerEnabled,
            bool hasTraversableWaypoints,
            bool isFinished,
            int remainingCount)
        {
            const float MinAssignedPathLength = 100f;   // 低于此长度不分配, 避免 instant target_reached

            bool hasTraversablePath = newPath != null && newPath.Count > 1;
            if (!hasTraversablePath)
            {
                if (followerEnabled && hasTraversableWaypoints) return WaypointSwitchDecision.KeepOld;
                return WaypointSwitchDecision.Clear;
            }

            // 路径太短 → 保留旧路径, 不制造 target_reached 循环
            float totalLen = 0f;
            for (int i = 1; i < newPath.Count; i++)
                totalLen += Dist(newPath[i - 1], newPath[i]);
            if (newPath.Count <= 2 && totalLen < MinAssignedPathLength)
                return WaypointSwitchDecision.KeepOld;

            // 仅在 rolling replan 且路径充足时保留旧路径, 避免频繁抖动;
            // target_reached / missing_path / manual_switch 必须接新路径
            // (旧路径可能穿越新 humanCluster)
            if (isRollingReplan && followerEnabled && hasTraversableWaypoints && !isFinished)
            {
                if (remainingCount > 2) return WaypointSwitchDecision.KeepOld;
            }

            return WaypointSwitchDecision.AssignNew;
        }

        // ═══ 障碍几何检查 (源 723–764 行) ═══

        private static bool IsWaypointInsideObstacle(Waypoint2D wp, List<ObcRect> obs, float safetyMargin)
        {
            if (obs == null || obs.Count == 0) return false;
            for (int i = 0; i < obs.Count; i++)
            {
                var (cx, cz, r) = CoverageField.ObcRectToCircle(obs[i]);
                float radius = r + Math.Max(0f, safetyMargin);
                float dx = wp.X - cx, dz = wp.Z - cz;
                if (dx * dx + dz * dz <= radius * radius) return true;
            }
            return false;
        }

        private static bool IsWaypointSegmentBlocked(Waypoint2D start, Waypoint2D end, List<ObcRect> obs, float safetyMargin)
        {
            if (obs == null || obs.Count == 0) return false;
            for (int i = 0; i < obs.Count; i++)
            {
                var (cx, cz, r) = CoverageField.ObcRectToCircle(obs[i]);
                float radius = r + Math.Max(0f, safetyMargin);
                if (SegmentIntersectsCircleXZ(start, end, cx, cz, radius)) return true;
            }
            return false;
        }

        /// <summary>线段与圆相交判定: 圆心到线段最近点 ≤ 半径 (投影参数 clamp [0,1])</summary>
        public static bool SegmentIntersectsCircleXZ(Waypoint2D start, Waypoint2D end, float centerX, float centerZ, float radius)
        {
            float sx = start.X, sz = start.Z;
            float ex = end.X, ez = end.Z;
            float segX = ex - sx, segZ = ez - sz;
            float segLenSq = segX * segX + segZ * segZ;
            if (segLenSq <= 0.0001f)
                return ((sx - centerX) * (sx - centerX) + (sz - centerZ) * (sz - centerZ)) <= radius * radius;

            float t = ((centerX - sx) * segX + (centerZ - sz) * segZ) / segLenSq;
            t = Math.Clamp(t, 0f, 1f);
            float cx = sx + segX * t, cz = sz + segZ * t;
            return (cx - centerX) * (cx - centerX) + (cz - centerZ) * (cz - centerZ) <= radius * radius;
        }

        private static float Dist(Waypoint2D a, Waypoint2D b)
        {
            float dx = a.X - b.X, dz = a.Z - b.Z;
            return MathF.Sqrt(dx * dx + dz * dz);
        }
    }
}
