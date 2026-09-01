// ============================================================================
#nullable disable
// astar.cs — 栅格级 8 方向 A* (含 human anchor 避让与起终点投影) (无 Unity 依赖提炼版)
//
// 源文件: Assets/Scripts/Planning/PlannerPathPlanningService.cs
//   BuildAStarPath (1180–1298 行) / IsSamePoint / Heuristic / CalcPathLength (1300–1317 行)
// 文档:   ../docs/05_astar.md
//
// 提炼差异: SortedSet<(f,g,col,row)> 与源实现一致; 避让格的临时障碍修改在 CoverageField
// 上完成并恢复 (源实现直接改 m_ObstacleMask + avoidBackup 恢复, 语义相同)。
// ============================================================================

using System;
using System.Collections.Generic;
using NumericsVector2 = System.Numerics.Vector2;

namespace UsvPatrolPlanning
{
    public static class GridAStar
    {
        /// <summary>
        /// 返回世界坐标点列: [0]=真实船位, 随后格中心折线, 末尾=目标 (或投影目标)。
        /// 不可达返回 null (由调用方执行失败计数与降级链)。
        /// humanAnchorAvoidCells: 非人控船临时避让格集 (rfValid 时 = human cluster 格集, 否则空)。
        /// humanAnchorManualId: 人控船 id, 其自身不避让。
        /// </summary>
        public static List<NumericsVector2> BuildAStarPath(
            CoverageField field,
            float sx, float sz, float tx, float tz,
            ICollection<int> humanAnchorAvoidCells,
            string humanAnchorManualId,
            string usvId,
            out int expandedNodes)
        {
            expandedNodes = 0;
            int cols = field.Columns, rows = field.Rows;
            var mask = field.ObstacleMask;
            int sc = field.WorldToCol(sx), sr = field.WorldToRow(sz);
            int tc = field.WorldToCol(tx), tr = field.WorldToRow(tz);
            bool startProjected = false, targetProjected = false;
            float projectedStartX = field.ColToWorldX(sc), projectedStartZ = field.RowToWorldZ(sr);
            float projectedTargetX = field.ColToWorldX(tc), projectedTargetZ = field.RowToWorldZ(tr);

            // ── Human anchor 避让: 非人控船避开预测区域 (临时置障碍, 用后恢复) ──
            bool isManualShip = !string.IsNullOrEmpty(usvId) && usvId == humanAnchorManualId;
            var avoidBackup = new List<(int idx, bool orig)>();
            if (!isManualShip && humanAnchorAvoidCells != null && humanAnchorAvoidCells.Count > 0)
            {
                foreach (int idx in humanAnchorAvoidCells)
                    if (idx >= 0 && idx < mask.Length) { avoidBackup.Add((idx, mask[idx])); mask[idx] = true; }
            }

            // ── 起终点投影: 被障碍物挡住时找最近自由格 ──
            int sidx = sr * cols + sc;
            if (sidx >= 0 && sidx < cols * rows && mask[sidx])
            {
                var nearest = field.FindNearestFreeCell(sx, sz);
                if (nearest.idx >= 0) { sc = nearest.col; sr = nearest.row; projectedStartX = nearest.wx; projectedStartZ = nearest.wz; startProjected = true; }
            }
            int tidx = tr * cols + tc;
            if (tidx >= 0 && tidx < cols * rows && mask[tidx])
            {
                var nearest = field.FindNearestFreeCell(tx, tz);
                if (nearest.idx >= 0) { tc = nearest.col; tr = nearest.row; projectedTargetX = nearest.wx; projectedTargetZ = nearest.wz; targetProjected = true; }
            }

            // 保留真实船位作为路径第一个点
            var path = new List<NumericsVector2> { new NumericsVector2(sx, sz) };
            if (startProjected)
                path.Add(new NumericsVector2(projectedStartX, projectedStartZ));
            if (sc == tc && sr == tr)
            {
                if (targetProjected && !IsSamePoint(path[path.Count - 1], projectedTargetX, projectedTargetZ))
                    path.Add(new NumericsVector2(projectedTargetX, projectedTargetZ));
                if (!targetProjected && !IsSamePoint(path[path.Count - 1], tx, tz))
                    path.Add(new NumericsVector2(tx, tz));
                RestoreAvoidCells(mask, avoidBackup);
                return path;
            }

            int[][] dirs = { new[]{0,1}, new[]{0,-1}, new[]{-1,0}, new[]{1,0},
                             new[]{1,1}, new[]{1,-1}, new[]{-1,1}, new[]{-1,-1} };

            var openSet = new SortedSet<(float f, int g, int col, int row)>();
            var gScore = new Dictionary<(int, int), int>();
            var cameFrom = new Dictionary<(int, int), (int, int)>();
            var closed = new HashSet<(int, int)>();

            gScore[(sc, sr)] = 0;
            openSet.Add((Heuristic(sc, sr, tc, tr), 0, sc, sr));
            int maxIter = cols * rows * 2, iter = 0;

            while (openSet.Count > 0 && iter++ < maxIter)
            {
                var cur = openSet.Min; openSet.Remove(cur);
                int cc = cur.col, cr = cur.row;
                expandedNodes++;
                if (cc == tc && cr == tr)
                {
                    // 重构路径
                    var rev = new List<(int, int)> { (tc, tr) };
                    var key = (tc, tr);
                    while (cameFrom.TryGetValue(key, out var prev))
                    { rev.Add(prev); key = prev; if (key == (sc, sr)) break; }
                    rev.Reverse();
                    for (int i = 1; i < rev.Count; i++)
                    {
                        float wx = field.ColToWorldX(rev[i].Item1);
                        float wz = field.RowToWorldZ(rev[i].Item2);
                        if (!IsSamePoint(path[path.Count - 1], wx, wz))
                            path.Add(new NumericsVector2(wx, wz));
                    }
                    if (!targetProjected && !IsSamePoint(path[path.Count - 1], tx, tz))
                        path.Add(new NumericsVector2(tx, tz));
                    RestoreAvoidCells(mask, avoidBackup);
                    return path;
                }
                if (closed.Contains((cc, cr))) continue;
                closed.Add((cc, cr));

                for (int d = 0; d < dirs.Length; d++)
                {
                    int nc = cc + dirs[d][0], nr = cr + dirs[d][1];
                    if (nc < 0 || nc >= cols || nr < 0 || nr >= rows) continue;
                    int idx = nr * cols + nc;
                    if (mask[idx]) continue;
                    // 对角禁穿角: 检查相邻两格 (cc,nr) 和 (nc,cr)
                    if (d >= 4)
                    {
                        int idx1 = nr * cols + cc, idx2 = cr * cols + nc;
                        if (mask[idx1] || mask[idx2]) continue;
                    }
                    if (closed.Contains((nc, nr))) continue;
                    int ng = gScore[(cc, cr)] + (d < 4 ? 10 : 14);   // 4方向10, 对角14
                    if (!gScore.TryGetValue((nc, nr), out var oldG) || ng < oldG)
                    {
                        gScore[(nc, nr)] = ng;
                        cameFrom[(nc, nr)] = (cc, cr);
                        openSet.Add((ng + Heuristic(nc, nr, tc, tr), ng, nc, nr));
                    }
                }
            }
            // 不可达 — 返回 null, 由调用方执行失败计数与降级
            RestoreAvoidCells(mask, avoidBackup);
            return null;
        }

        private static void RestoreAvoidCells(bool[] mask, List<(int idx, bool orig)> avoidBackup)
        {
            foreach (var (i, orig) in avoidBackup) mask[i] = orig;
        }

        private static bool IsSamePoint(NumericsVector2 p, float x, float z)
        {
            float dx = p.X - x;
            float dz = p.Y - z;
            return dx * dx + dz * dz < 0.01f;
        }

        private static int Heuristic(int c1, int r1, int c2, int r2)
            => 10 * (Math.Abs(c1 - c2) + Math.Abs(r1 - r2));

        public static float CalcPathLength(List<NumericsVector2> path)
        {
            float len = 0f;
            for (int i = 1; i < path.Count; i++)
                len += MathF.Sqrt((path[i].X - path[i - 1].X) * (path[i].X - path[i - 1].X) +
                                  (path[i].Y - path[i - 1].Y) * (path[i].Y - path[i - 1].Y));
            return len;
        }
    }
}
