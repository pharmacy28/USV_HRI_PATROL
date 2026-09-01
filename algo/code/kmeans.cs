// ============================================================================
#nullable disable
// kmeans.cs — risk 加权 K-means (普通模式 + fixed human anchor 模式) (无 Unity 依赖提炼版)
//
// 源文件: Assets/Scripts/Planning/PlannerPathPlanningService.cs
//   WeightedKMeansWithFixedAnchor (657–767 行) / WeightedKMeansBasic (770–832 行)
// 文档:   ../docs/03_clustering_kmeans.md
//
// 提炼差异: Mathf → MathF; 随机源注入 System.Random。算法逐段一致。
// ============================================================================

using System;
using System.Collections.Generic;

namespace UsvPatrolPlanning
{
    public static class CoverageKMeans
    {
        // ═══ fixed-anchor 模式 (源 657–767 行) ═══
        // center[0] = human anchor (固定不更新), center[1..K] = 自主中心 (迭代)
        // RF 预测点作为固定中心参与聚类, human 区域由聚类自然形成。

        public static List<CoverageCluster> WeightedKMeansWithFixedAnchor(
            int k,                                   // 总中心数 = K + 1 (K 艘自主船 + 1 human anchor)
            List<ShipDes> autoShips,                 // 自主船 (K 艘)
            CoverageCluster humanAnchor,             // RF 预测投影格 (可为 null → 用地图中心)
            List<(float cx, float cz)> lastAutoCentroids,  // 热启动质心缓存 (仅自主中心, 不含 human)
            bool coldStart,                          // = (replanReason == "target_reached")
            PlannerRuntimeConfig cfg,
            CoverageField field,
            Random rng,
            out int iterations)
        {
            var clusters = new List<CoverageCluster>();
            int maxIter = cfg.MaxKMeansIterations;
            float tol = cfg.KMeansTolerance;
            iterations = 0;
            int cols = field.Columns, rows = field.Rows;

            // ── 初始化: center[0] = human anchor (fixed), center[1..K] = auto ──
            var centers = new List<(float cx, float cz)>();
            centers.Add(humanAnchor != null
                ? (humanAnchor.CentroidX, humanAnchor.CentroidZ)
                : (field.OriginX + field.CellSize * cols / 2,
                   field.OriginY + field.CellSize * rows / 2));

            for (int i = 0; i < autoShips.Count; i++)
            {
                if (!coldStart && i < lastAutoCentroids.Count)
                    centers.Add(lastAutoCentroids[i]);
                else if (i < autoShips.Count)
                {
                    float px = (float)(rng.NextDouble() - 0.5) * field.CellSize * 4;
                    float pz = (float)(rng.NextDouble() - 0.5) * field.CellSize * 4;
                    centers.Add((autoShips[i].X + px, autoShips[i].Y + pz));
                }
                else
                    centers.Add((field.OriginX + rng.Next(cols) * field.CellSize,
                                 field.OriginY + rng.Next(rows) * field.CellSize));
            }

            // ── 所有非障碍自由格参与聚类 (不预先排除任何格子) ──
            var freeCells = CollectFreeCells(field);

            int[] assignments = new int[freeCells.Count];

            for (int iter = 0; iter < maxIter; iter++)
            {
                bool changed = false;
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    var fc = freeCells[fi];
                    float bestD = float.MaxValue; int bestK = 0;
                    for (int kk = 0; kk < k; kk++)
                    {
                        float dx = fc.wx - centers[kk].cx, dz = fc.wz - centers[kk].cz;
                        float d = dx * dx + dz * dz;
                        if (d < bestD) { bestD = d; bestK = kk; }
                    }
                    if (assignments[fi] != bestK) { assignments[fi] = bestK; changed = true; }
                }
                if (!changed && iter > 0) break;

                // ── 更新步: center[0] 固定不更新, center[1..K] 加权重心 ──
                var newCenters = new List<(float, float)> { centers[0] };
                var sums = new float[k]; var sumX = new float[k]; var sumZ = new float[k];
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    int kk = assignments[fi];
                    float w = freeCells[fi].risk;
                    if (w < 1e-6f) w = 1e-6f;
                    sumX[kk] += freeCells[fi].wx * w; sumZ[kk] += freeCells[fi].wz * w; sums[kk] += w;
                }
                float maxShift = 0f;
                for (int kk = 1; kk < k; kk++)     // skip fixed center[0]
                {
                    float nx = sums[kk] > 0f ? sumX[kk] / sums[kk] : centers[kk].cx;
                    float nz = sums[kk] > 0f ? sumZ[kk] / sums[kk] : centers[kk].cz;
                    float shift = MathF.Abs(nx - centers[kk].cx) + MathF.Abs(nz - centers[kk].cz);
                    if (shift > maxShift) maxShift = shift;
                    newCenters.Add((nx, nz));
                }
                centers = newCenters;
                if (maxShift < tol) { iterations = iter + 1; break; }
            }
            if (iterations == 0) iterations = maxIter;

            // ── 构建 cluster: kk=0 → humanAnchor, kk=1..K → auto ──
            for (int kk = 0; kk < k; kk++)
            {
                float riskSum = 0f; var cellList = new List<int>();
                float bestScore = -1f; int bestCol = 0, bestRow = 0;
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    if (assignments[fi] != kk) continue;
                    var fc = freeCells[fi];
                    cellList.Add(fc.idx);
                    riskSum += fc.risk;
                    if (fc.risk > bestScore) { bestScore = fc.risk; bestCol = fc.col; bestRow = fc.row; }
                }
                bool isHuman = (kk == 0);
                clusters.Add(new CoverageCluster
                {
                    ClusterId = isHuman ? -1 : (kk - 1),
                    IsHumanAnchor = isHuman,
                    CentroidX = centers[kk].cx, CentroidZ = centers[kk].cz,
                    CentroidCol = field.WorldToCol(centers[kk].cx), CentroidRow = field.WorldToRow(centers[kk].cz),
                    CellIndices = cellList, RiskSum = riskSum,
                    BestTargetCol = bestCol, BestTargetRow = bestRow, BestTargetScore = bestScore
                });
            }

            return clusters;
        }

        // ═══ 普通模式 (源 770–832 行): 无 fixed center, rfValid=false 时使用 ═══

        public static List<CoverageCluster> WeightedKMeansBasic(
            int k,                                   // 中心数 = K 艘自主船
            List<ShipDes> autoShips,
            List<(float cx, float cz)> lastAutoCentroids,
            bool coldStart,
            PlannerRuntimeConfig cfg,
            CoverageField field,
            Random rng,
            out int iterations)
        {
            var clusters = new List<CoverageCluster>();
            int maxIter = cfg.MaxKMeansIterations;
            float tol = cfg.KMeansTolerance;
            iterations = 0;
            int cols = field.Columns, rows = field.Rows;

            var centers = new List<(float cx, float cz)>();
            for (int i = 0; i < k; i++)
            {
                if (!coldStart && i < lastAutoCentroids.Count)
                    centers.Add(lastAutoCentroids[i]);
                else if (i < autoShips.Count)
                {
                    float px = (float)(rng.NextDouble() - 0.5) * field.CellSize * 4;
                    float pz = (float)(rng.NextDouble() - 0.5) * field.CellSize * 4;
                    centers.Add((autoShips[i].X + px, autoShips[i].Y + pz));
                }
                else centers.Add((field.OriginX + rng.Next(cols) * field.CellSize,
                                 field.OriginY + rng.Next(rows) * field.CellSize));
            }

            var freeCells = CollectFreeCells(field);
            int[] assignments = new int[freeCells.Count];

            for (int iter = 0; iter < maxIter; iter++)
            {
                bool changed = false;
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    var fc = freeCells[fi]; float bestD = float.MaxValue; int bestK = 0;
                    for (int kk = 0; kk < k; kk++)
                    {
                        float dx = fc.wx - centers[kk].cx, dz = fc.wz - centers[kk].cz;
                        float d = dx * dx + dz * dz;
                        if (d < bestD) { bestD = d; bestK = kk; }
                    }
                    if (assignments[fi] != bestK) { assignments[fi] = bestK; changed = true; }
                }
                if (!changed && iter > 0) break;
                var sums = new float[k]; var sumX = new float[k]; var sumZ = new float[k];
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    int kk = assignments[fi];
                    float w = Math.Max(1e-6f, freeCells[fi].risk);
                    sumX[kk] += freeCells[fi].wx * w; sumZ[kk] += freeCells[fi].wz * w; sums[kk] += w;
                }
                float maxShift = 0f;
                for (int kk = 0; kk < k; kk++)
                {
                    float nx = sums[kk] > 0f ? sumX[kk] / sums[kk] : centers[kk].cx;
                    float nz = sums[kk] > 0f ? sumZ[kk] / sums[kk] : centers[kk].cz;
                    maxShift = Math.Max(maxShift, MathF.Abs(nx - centers[kk].cx) + MathF.Abs(nz - centers[kk].cz));
                    centers[kk] = (nx, nz);
                }
                if (maxShift < tol) { iterations = iter + 1; break; }
            }
            if (iterations == 0) iterations = maxIter;

            for (int kk = 0; kk < k; kk++)
            {
                float riskSum = 0f; var cellList = new List<int>();
                float bestScore = -1f; int bestCol = 0, bestRow = 0;
                for (int fi = 0; fi < freeCells.Count; fi++)
                {
                    if (assignments[fi] != kk) continue;
                    var fc = freeCells[fi];
                    cellList.Add(fc.idx);
                    riskSum += fc.risk;
                    if (fc.risk > bestScore) { bestScore = fc.risk; bestCol = fc.col; bestRow = fc.row; }
                }
                clusters.Add(new CoverageCluster
                {
                    ClusterId = kk, IsHumanAnchor = false,
                    CentroidX = centers[kk].cx, CentroidZ = centers[kk].cz,
                    CentroidCol = field.WorldToCol(centers[kk].cx), CentroidRow = field.WorldToRow(centers[kk].cz),
                    CellIndices = cellList, RiskSum = riskSum,
                    BestTargetCol = bestCol, BestTargetRow = bestRow, BestTargetScore = bestScore
                });
            }
            return clusters;
        }

        // ── 共享: 自由格收集 (risk = Pmiss × belief) ──

        private static List<(int idx, int col, int row, float risk, float wx, float wz)> CollectFreeCells(CoverageField field)
        {
            var freeCells = new List<(int, int, int, float, float, float)>();
            int n = field.Columns * field.Rows;
            var pmiss = field.Pmiss; var belief = field.Belief; var mask = field.ObstacleMask;
            for (int i = 0; i < n; i++)
            {
                if (mask[i]) continue;
                int col = i % field.Columns, row = i / field.Columns;
                freeCells.Add((i, col, row, pmiss[i] * belief[i], field.ColToWorldX(col), field.RowToWorldZ(row)));
            }
            return freeCells;
        }
    }
}
