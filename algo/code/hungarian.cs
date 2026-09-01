// ============================================================================
#nullable disable
// hungarian.cs — USV–分区指派 (Hungarian) (无 Unity 依赖提炼版)
//
// 源文件: Assets/Scripts/Planning/PlannerPathPlanningService.cs
//   HungarianAssign (840–928 行) / SolveHungarian (931–971 行)
// 文档:   ../docs/04_assignment.md
//
// 注意: 当前实现为 clustering → Euclidean-Hungarian → A* 顺序;
//       仓库 idea/研究决策状态.md CONFIRMED 架构要求 path-dependent assignment
//       (先 pairwise A* 再指派), 差异详见 ../docs/04_assignment.md §4, 未静默解决。
// ============================================================================

using System;
using System.Collections.Generic;

namespace UsvPatrolPlanning
{
    public static class CoverageAssignmentSolver
    {
        // ═══ 代价矩阵 + 指派 (源 840–928 行) ═══

        /// <summary>
        /// TravelCostOnly (默认): cost = normDist + switchPenalty.
        /// LegacyMixedCost: 所有项均为惩罚; 风险密度/信念越高, 惩罚越低。
        /// lastShipCluster: usvId → 上次 clusterId (切换惩罚判断用, 可为空)。
        /// </summary>
        public static List<CoverageAssignment> HungarianAssign(
            List<ShipDes> autoShips,
            List<CoverageCluster> clusters,
            PlannerRuntimeConfig cfg,
            Dictionary<string, int> lastShipCluster,
            bool rfInfluenced,
            float humanPredictedTargetX,
            float humanPredictedTargetZ)
        {
            int n = autoShips.Count;
            var result = new List<CoverageAssignment>();

            // ── 归一化: 全局最大船–中心欧氏距离 ──
            float maxDist = 1f;
            for (int i = 0; i < n; i++)
            {
                float sx = autoShips[i].X, sz = autoShips[i].Y;
                for (int j = 0; j < n; j++)
                {
                    float d = MathF.Sqrt((sx - clusters[j].CentroidX) * (sx - clusters[j].CentroidX) +
                                         (sz - clusters[j].CentroidZ) * (sz - clusters[j].CentroidZ));
                    if (d > maxDist) maxDist = d;
                }
            }
            float invMaxDist = maxDist > 1f ? 1f / maxDist : 1f;
            float sw = cfg.SwitchPenalty;

            bool travelOnly = cfg.AssignmentMode == "TravelCostOnly";

            // LegacyMixedCost 归一化 (仅非 TravelCostOnly 使用):
            // 用风险密度而非分区总风险, 防止大分区仅凭面积取胜。
            float maxRisk = 1f, maxBelief = 1f;
            float invMaxRisk = 1f, invMaxBelief = 1f;
            float[] clusterRiskMean = null;
            float[] clusterBelief = null;
            if (!travelOnly)
            {
                clusterRiskMean = new float[n];
                clusterBelief = new float[n];
                for (int j = 0; j < n; j++)
                {
                    int cellCount = clusters[j].CellIndices != null ? clusters[j].CellIndices.Count : 0;
                    clusterRiskMean[j] = cellCount > 0 ? clusters[j].RiskSum / cellCount : 0f;
                    clusterBelief[j] = clusters[j].BeliefSum;
                    if (clusterRiskMean[j] > maxRisk) maxRisk = clusterRiskMean[j];
                    if (clusterBelief[j] > maxBelief) maxBelief = clusterBelief[j];
                }
                invMaxRisk = maxRisk > 0.0001f ? 1f / maxRisk : 1f;
                invMaxBelief = maxBelief > 0.0001f ? 1f / maxBelief : 1f;
            }

            float dw = cfg.DistanceWeight;
            float rw = cfg.RiskWeight;
            float bw = cfg.BeliefWeight;

            // ── 代价矩阵 ──
            var cost = new float[n, n];
            for (int i = 0; i < n; i++)
            {
                float sx = autoShips[i].X, sz = autoShips[i].Y;
                int prevCluster = lastShipCluster != null && lastShipCluster.TryGetValue(autoShips[i].Id, out var pc) ? pc : -1;
                for (int j = 0; j < n; j++)
                {
                    float d = MathF.Sqrt((sx - clusters[j].CentroidX) * (sx - clusters[j].CentroidX) +
                                         (sz - clusters[j].CentroidZ) * (sz - clusters[j].CentroidZ));
                    float nd = d * invMaxDist;
                    bool changed = prevCluster >= 0 && prevCluster != j;
                    if (travelOnly)
                        cost[i, j] = nd + (changed ? sw : 0f);
                    else
                    {
                        float normRisk = Math.Clamp(clusterRiskMean[j] * invMaxRisk, 0f, 1f);
                        float normBelief = Math.Clamp(clusterBelief[j] * invMaxBelief, 0f, 1f);
                        cost[i, j] = dw * nd + rw * (1f - normRisk) + bw * (1f - normBelief) + (changed ? sw : 0f);
                    }
                }
            }

            var assignment = SolveHungarian(cost, n);

            for (int i = 0; i < n; i++)
            {
                int j = assignment[i];
                result.Add(new CoverageAssignment
                {
                    UsvId = autoShips[i].Id,
                    ClusterId = clusters[j].ClusterId,
                    AssignmentCost = cost[i, j],
                    RfInfluenced = rfInfluenced,
                    HumanPredictedTargetX = humanPredictedTargetX,
                    HumanPredictedTargetZ = humanPredictedTargetZ
                });
            }
            return result;
        }

        // ═══ Hungarian O(n³) — 标准潜势实现 (源 931–971 行, 1-indexed) ═══

        public static int[] SolveHungarian(float[,] cost, int n)
        {
            var u = new float[n + 1]; var v = new float[n + 1];
            var p = new int[n + 1]; var way = new int[n + 1];
            for (int i = 1; i <= n; i++)
            {
                p[0] = i; int j0 = 0;
                var minv = new float[n + 1];
                var used = new bool[n + 1];
                for (int j = 0; j <= n; j++) minv[j] = float.MaxValue;
                do
                {
                    used[j0] = true;
                    int i0 = p[j0], j1 = 0;
                    float delta = float.MaxValue;
                    for (int j = 1; j <= n; j++)
                    {
                        if (!used[j])
                        {
                            float cur = cost[i0 - 1, j - 1] - u[i0] - v[j];
                            if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
                            if (minv[j] < delta) { delta = minv[j]; j1 = j; }
                        }
                    }
                    for (int j = 0; j <= n; j++)
                    {
                        if (used[j]) { u[p[j]] += delta; v[j] -= delta; }
                        else minv[j] -= delta;
                    }
                    j0 = j1;
                } while (p[j0] != 0);
                do
                {
                    int j1 = way[j0]; p[j0] = p[j1]; j0 = j1;
                } while (j0 != 0);
            }
            var result = new int[n];
            for (int j = 1; j <= n; j++)
                if (p[j] > 0) result[p[j] - 1] = j - 1;
            return result;
        }
    }
}
