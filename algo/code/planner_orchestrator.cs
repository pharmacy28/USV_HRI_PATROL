// ============================================================================
#nullable disable
// planner_orchestrator.cs — ExecuteReplan 编排 + 目标选择 + voice anchor + 重规划调度
// (无 Unity 依赖提炼版)
//
// 源文件:
//   Assets/Scripts/Planning/PlannerPathPlanningService.cs
//     GeneratePlan (321–351) / UpdatePlan (353–361) / ExecuteReplan (363–649)
//     目标选择 (978–1146) / GetShipX/Y (1148–1174) / voice anchor (1353–1476)
//   Assets/Scripts/PathPlan.cs  ReplanScheduler (351–436)
// 文档:   ../docs/02_planner_pipeline.md, ../docs/07_replan_scheduler.md
//
// 提炼差异: Time.time → NowSeconds (调用方维护); RFNextPointRuntime.Instance →
// IHumanIntentSource 注入; Debug.Log → 移除; FleetMovementDiagnostics → 移除。
// ============================================================================

using System;
using System.Collections.Generic;
using System.Diagnostics;
using NumericsVector2 = System.Numerics.Vector2;

namespace UsvPatrolPlanning
{
    public class CoveragePlannerEngine
    {
        // ── 依赖注入 ──
        public CoverageField Field;
        public IHumanIntentSource IntentSource;      // RF 预测抽象 (Unity 侧: RFNextPointRuntime.Instance)
        public double NowSeconds;                    // 时钟 (Unity 侧: Time.time)
        public PlannerRuntimeConfig Config = new PlannerRuntimeConfig();
        public bool ConfigOverriddenByUi;            // F2 面板配置优先 (Unity 侧持久化语义)

        private readonly Random _rng = new Random();

        // ── 规划结果缓存 ──
        private List<CoverageCluster> _clusters = new List<CoverageCluster>();
        private List<CoverageAssignment> _assignments = new List<CoverageAssignment>();
        private List<NavigationWaypoint> _navigationRecords = new List<NavigationWaypoint>();
        private List<(float cx, float cz)> _lastAutoCentroids = new List<(float cx, float cz)>();
        private HumanIntentPrediction _lastHumanIntent = new HumanIntentPrediction();
        private Dictionary<string, int> _lastShipCluster = new Dictionary<string, int>();
        private Dictionary<string, int> _astarFailCount = new Dictionary<string, int>();
        private const int MaxAStarRetries = 3;
        private HashSet<int> _humanAnchorAvoidCells = new HashSet<int>();
        private string _humanAnchorManualId = "";
        private VoiceCommandAnchor _voiceAnchor = new VoiceCommandAnchor();

        private int _replanIndex;
        private int _lastCompletedReplanIndex = -1;
        private string _replanReason = "initial";
        private double _lastDecisionTimeMs;
        private PlannerPerfSnapshot _lastPerfSnapshot;
        private int _fallbackAStarCount;

        // ── 公开查询 (对应源 1424–1443 行) ──
        public List<CoverageAssignment> GetLatestCoverageAssignments() => _assignments;
        public List<NavigationWaypoint> GetLatestNavigationWaypoints() => _navigationRecords;
        public HumanIntentPrediction GetLatestHumanIntentPrediction() => _lastHumanIntent;
        public List<CoverageCluster> GetCoverageClusters() => _clusters;
        public PlannerPerfSnapshot GetLastPlannerPerfSnapshot() => _lastPerfSnapshot;
        public int LastCompletedReplanIndex => _lastCompletedReplanIndex;
        public bool IsHumanAnchorEnabled => Config.EnableHumanAnchor;
        public string LastReplanReason => _replanReason;
        public PlannerRuntimeConfig GetPlannerRuntimeConfigSnapshot() => Config;

        public void SetHumanAnchorEnabled(bool enabled)
        {
            if (Config.EnableHumanAnchor != enabled) Config.ConfigVersion++;
            Config.EnableHumanAnchor = enabled;
            ConfigOverriddenByUi = true;
            if (!enabled) _lastHumanIntent = new HumanIntentPrediction { Valid = false };
        }

        public void ApplyPlannerRuntimeConfig(PlannerRuntimeConfig cfg)
        {
            if (cfg == null) return;
            int nextVersion = Math.Max(Config?.ConfigVersion ?? 1, cfg.ConfigVersion) + 1;
            Config = cfg.Clone();
            Config.NormalizeDefaults();
            Config.ConfigVersion = nextVersion;
            ConfigOverriddenByUi = true;
        }

        public void SetReplanReason(string reason) { _replanReason = reason ?? "unknown"; }

        // ═══ 入口 (源 321–361 行) ═══

        public PathPlan GeneratePlan(PlannerParam param)
        {
            var result = new PathPlan { Paths = new Dictionary<string, List<NumericsVector2>>() };
            if (!Field.Initialized || param.ShipDes == null) return result;

            var sw = Stopwatch.StartNew();
            ExecuteReplan(param.ShipDes, param.ObcRects ?? new List<ObcRect>(), param.ContextManualShip);
            sw.Stop();
            _lastDecisionTimeMs = sw.Elapsed.TotalMilliseconds;

            // 输出航路点 — 复用 ExecuteReplan 内缓存的 CachedPath (消除双重 A*)
            foreach (var a in _assignments)
            {
                if (!a.Reachable) continue;
                if (a.CachedPath != null && a.CachedPath.Count > 0)
                    result.Paths[a.UsvId] = a.CachedPath;
                else
                {
                    var path = GridAStar.BuildAStarPath(
                        Field, GetShipX(a.UsvId, param.ShipDes), GetShipY(a.UsvId, param.ShipDes),
                        a.TargetWorldX, a.TargetWorldZ, _humanAnchorAvoidCells, _humanAnchorManualId,
                        a.UsvId, out _);
                    result.Paths[a.UsvId] = path;
                    _fallbackAStarCount++;
                }
            }
            return result;
        }

        public PathPlan UpdatePlan(List<ShipDes> ships)
        {
            return GeneratePlan(new PlannerParam
            {
                X = (int)MathF.Round(Field.OriginX), Y = (int)MathF.Round(Field.OriginY),
                Width = Field.Columns * Field.CellSize, Height = Field.Rows * Field.CellSize,
                ShipDes = ships ?? new List<ShipDes>(), ObcRects = new List<ObcRect>()
            });
        }

        // ═══ ExecuteReplan (源 363–649 行, 9 步) ═══

        private void ExecuteReplan(List<ShipDes> allShips, List<ObcRect> obstacles, ShipDes? contextManualShip)
        {
            Field.GetCoverageTotalRisk();   // RefreshStats
            int currentRi = _replanIndex;

            // ── 步骤 1: 分离自主船/人控船/语音船 ──
            var autoShips = new List<ShipDes>();
            string humanId = null;
            ShipDes humanShip = default;
            if (contextManualShip.HasValue && !string.IsNullOrEmpty(contextManualShip.Value.Id)
                && contextManualShip.Value.IsHandControl)   // 防御: 必须是真实手控状态
            {
                humanShip = contextManualShip.Value;
                humanId = humanShip.Id;
            }
            for (int i = 0; i < allShips.Count; i++)
            {
                var s = allShips[i];
                if (s.IsHandControl)
                {
                    if (string.IsNullOrEmpty(humanId)) { humanId = s.Id; humanShip = s; }
                }
                else autoShips.Add(s);
            }
            bool voiceActive = IsActiveVoiceAnchor();
            ShipDes voiceShip = default;
            bool hasVoiceShip = false;
            var coverageShips = new List<ShipDes>(autoShips.Count);
            for (int i = 0; i < autoShips.Count; i++)
            {
                var s = autoShips[i];
                if (voiceActive && IsSameUsvId(s.Id, _voiceAnchor.UsvId))
                { voiceShip = s; hasVoiceShip = true; continue; }
                coverageShips.Add(s);
            }
            if (voiceActive && !hasVoiceShip)
                voiceActive = false;   // 语音目标船不存在于自主船列表 → 忽略该 anchor

            int k = coverageShips.Count;
            if (k == 0 && !voiceActive)
            {
                _assignments.Clear();
                _lastCompletedReplanIndex = currentRi;
                _replanIndex++;
                return;
            }

            // ── 步骤 2: RF human anchor (fail-closed, 见 docs/06) ──
            CoverageCluster humanCluster = null;
            bool rfValid = false;
            var rf = IntentSource;
            if (Config.EnableHumanAnchor && string.IsNullOrEmpty(humanId))
            {
                _lastHumanIntent = new HumanIntentPrediction { Valid = false };
            }
            else if (Config.EnableHumanAnchor && rf != null
                && rf.CurrentMode == "RF_ASSIST"      // fail-closed: AUTO 模式绝不生成 human anchor
                && rf.IsPredictionValid
                && rf.LastPrediction != null && rf.LastPrediction.Confidence >= Config.RfAnchorConfidenceThreshold)
            {
                var p = rf.LastPrediction;
                float hx = humanShip.X + p.PredictedDistance * MathF.Cos(p.PredictedAngleDeg * MathF.PI / 180f);
                float hz = humanShip.Y + p.PredictedDistance * MathF.Sin(p.PredictedAngleDeg * MathF.PI / 180f);
                var nearest = Field.FindNearestFreeCell(hx, hz);
                if (nearest.idx >= 0)
                {
                    rfValid = true;
                    humanCluster = new CoverageCluster
                    {
                        ClusterId = -1, IsHumanAnchor = true,
                        CentroidX = nearest.wx, CentroidZ = nearest.wz,
                        CentroidCol = nearest.col, CentroidRow = nearest.row
                    };
                    _lastHumanIntent = new HumanIntentPrediction
                    {
                        Valid = true, PredictedWorldX = hx, PredictedWorldZ = hz,
                        NearestFreeCol = nearest.col, NearestFreeRow = nearest.row,
                        Confidence = p.Confidence, Mode = rf.CurrentMode
                    };
                }
            }
            if (!rfValid) _lastHumanIntent = new HumanIntentPrediction { Valid = false };

            // ── 步骤 3: 聚类 (rfValid → fixed-anchor K+1 means; 否则普通 K-means) ──
            var kmSw = Stopwatch.StartNew();
            CoverageCluster humanClusterResult = null;
            List<CoverageCluster> autoClusters;
            int kmIterations = 0;
            bool coldStart = _replanReason == "target_reached";
            if (rfValid)
            {
                var allClusters = CoverageKMeans.WeightedKMeansWithFixedAnchor(
                    k + 1, coverageShips, humanCluster, _lastAutoCentroids, coldStart, Config, Field, _rng, out kmIterations);
                humanClusterResult = allClusters[0];
                autoClusters = allClusters.GetRange(1, k);
                // A* 避让来源: humanCluster.CellIndices (聚类自然形成)
                _humanAnchorAvoidCells.Clear();
                if (humanClusterResult.CellIndices != null)
                    foreach (int idx in humanClusterResult.CellIndices)
                        _humanAnchorAvoidCells.Add(idx);
                _humanAnchorManualId = humanId ?? "";
            }
            else
            {
                autoClusters = k > 0
                    ? CoverageKMeans.WeightedKMeansBasic(k, coverageShips, _lastAutoCentroids, coldStart, Config, Field, _rng, out kmIterations)
                    : new List<CoverageCluster>();
                if (k == 0) kmIterations = 0;
                _humanAnchorAvoidCells.Clear();
                _humanAnchorManualId = "";
                _lastHumanIntent = new HumanIntentPrediction { Valid = false };
            }
            kmSw.Stop();
            float kmMs = (float)kmSw.Elapsed.TotalMilliseconds;

            // ── 步骤 4: Hungarian 指派 ──
            for (int ci = 0; ci < autoClusters.Count; ci++)
                autoClusters[ci].ClusterId = ci;   // 确保 auto cluster id 从 0 连续

            var asgSw = Stopwatch.StartNew();
            _assignments = k > 0
                ? CoverageAssignmentSolver.HungarianAssign(coverageShips, autoClusters, Config, _lastShipCluster,
                    _lastHumanIntent.Valid, _lastHumanIntent.PredictedWorldX, _lastHumanIntent.PredictedWorldZ)
                : new List<CoverageAssignment>();
            asgSw.Stop();
            float asgMs = (float)asgSw.Elapsed.TotalMilliseconds;

            // ── 步骤 5: voice anchor 定向 (跳过聚类) ──
            var astarSw = Stopwatch.StartNew();
            int missingPathCount = 0;
            int astarPathCount = 0, astarFailCount = 0, astarExpandedTotal = 0, astarExpandedMax = 0;

            if (voiceActive)
            {
                ProjectVoiceAnchorOutsideAvoidance();
                _assignments.Add(new CoverageAssignment
                {
                    UsvId = voiceShip.Id,
                    ClusterId = -2,
                    TargetCol = _voiceAnchor.TargetCol,
                    TargetRow = _voiceAnchor.TargetRow,
                    TargetWorldX = _voiceAnchor.TargetWorldX,
                    TargetWorldZ = _voiceAnchor.TargetWorldZ,
                    Reachable = true,
                    AssignmentCost = 0f,
                    TargetScore = 0f,
                    RfInfluenced = false,
                    HumanPredictedTargetX = _lastHumanIntent.PredictedWorldX,
                    HumanPredictedTargetZ = _lastHumanIntent.PredictedWorldZ,
                    AssignedByVoice = true,
                    VoiceCommandId = _voiceAnchor.CommandId,
                    VoiceRegion = _voiceAnchor.RegionId,
                    VoiceTargetCol = _voiceAnchor.TargetCol,
                    VoiceTargetRow = _voiceAnchor.TargetRow,
                    VoiceTargetWorldX = _voiceAnchor.TargetWorldX,
                    VoiceTargetWorldZ = _voiceAnchor.TargetWorldZ
                });
            }

            // ── 步骤 6: 分区内目标选择 ──
            foreach (var a in _assignments)
            {
                if (a.AssignedByVoice) continue;
                var cluster = autoClusters.Find(cl => cl.ClusterId == a.ClusterId);
                if (cluster == null) { a.Reachable = false; missingPathCount++; continue; }

                int failCount = _astarFailCount.TryGetValue(a.UsvId, out var c) ? c : 0;
                if (failCount >= MaxAStarRetries)
                    SelectGlobalBestTarget(a, allShips);       // A* 连败 3 次 → 全局最高 cellRisk
                else
                    SelectTargetInCluster(a, cluster, allShips);

                a.Reachable = !Field.ObstacleMask[a.TargetRow * Field.Columns + a.TargetCol];
                if (!a.Reachable) missingPathCount++;
            }

            // ── 步骤 7: 逐船 A* + 导航点记录 ──
            float pathGenMaxMs = 0f;
            foreach (var a in _assignments)
            {
                var nw = new NavigationWaypoint
                {
                    UnityTime = NowSeconds, ReplanIndex = currentRi,
                    UsvId = a.UsvId, AssignedClusterId = a.ClusterId,
                    TargetCol = a.TargetCol, TargetRow = a.TargetRow,
                    TargetWorldX = a.TargetWorldX, TargetWorldZ = a.TargetWorldZ,
                    PathLength = a.PathLength, Reachable = a.Reachable,
                    AssignmentCost = a.AssignmentCost, TargetScore = a.TargetScore,
                    RfInfluenced = a.RfInfluenced,
                    HumanPredictedTargetX = a.HumanPredictedTargetX,
                    HumanPredictedTargetZ = a.HumanPredictedTargetZ,
                    AssignedByVoice = a.AssignedByVoice,
                    VoiceCommandId = a.VoiceCommandId,
                    VoiceRegion = a.VoiceRegion
                };
                if (a.Reachable)
                {
                    var singleAstarSw = Stopwatch.StartNew();
                    var path = GridAStar.BuildAStarPath(
                        Field, GetShipX(a.UsvId, allShips), GetShipY(a.UsvId, allShips),
                        a.TargetWorldX, a.TargetWorldZ, _humanAnchorAvoidCells, _humanAnchorManualId,
                        a.UsvId, out int expandedNodes);
                    singleAstarSw.Stop();
                    float singleAstarMs = (float)singleAstarSw.Elapsed.TotalMilliseconds;
                    if (singleAstarMs > pathGenMaxMs) pathGenMaxMs = singleAstarMs;
                    if (path != null)
                    {
                        astarPathCount++;
                        astarExpandedTotal += expandedNodes;
                        if (expandedNodes > astarExpandedMax) astarExpandedMax = expandedNodes;
                        nw.PathLength = GridAStar.CalcPathLength(path);
                        foreach (var p in path) { nw.WaypointXs.Add(p.X); nw.WaypointZs.Add(p.Y); }
                        a.CachedPath = path;
                        a.PathLength = nw.PathLength;
                        _astarFailCount[a.UsvId] = 0;
                    }
                    else
                    {
                        astarFailCount++;
                        a.Reachable = false; nw.Reachable = false; missingPathCount++;
                        int fc = _astarFailCount.TryGetValue(a.UsvId, out var f) ? f + 1 : 1;
                        _astarFailCount[a.UsvId] = fc;
                    }
                }
                _navigationRecords.Add(nw);
            }
            astarSw.Stop();
            float astarMs = (float)astarSw.Elapsed.TotalMilliseconds;

            // ── 步骤 8: 性能快照 ──
            _lastPerfSnapshot = new PlannerPerfSnapshot
            {
                ReplanIndex = currentRi, ReplanReason = _replanReason,
                ConfigVersion = Config.ConfigVersion,
                DecisionMs = _lastDecisionTimeMs, AutoShipCount = autoShips.Count,
                ClusterCount = autoClusters.Count, AssignmentCount = _assignments.Count,
                MissingPathCount = missingPathCount,
                KMeansIterations = kmIterations, KMeansMs = kmMs,
                AssignmentMs = asgMs, AstarMs = astarMs,
                PathGenMaxMs = pathGenMaxMs, PathGenTotalMs = astarMs,
                AstarPathCount = astarPathCount, AstarFailCount = astarFailCount,
                AstarExpandedNodesTotal = astarExpandedTotal, AstarExpandedNodesMax = astarExpandedMax,
                FallbackAStarCount = _fallbackAStarCount
            };

            // ── 步骤 9: 状态维护 ──
            _clusters = new List<CoverageCluster>();
            if (humanClusterResult != null) _clusters.Add(humanClusterResult);
            _clusters.AddRange(autoClusters);
            _lastCompletedReplanIndex = currentRi;
            _replanIndex++;
            _lastAutoCentroids.Clear();
            foreach (var cl in autoClusters) _lastAutoCentroids.Add((cl.CentroidX, cl.CentroidZ));
            _lastShipCluster.Clear();
            foreach (var a in _assignments)
                if (!a.AssignedByVoice) _lastShipCluster[a.UsvId] = a.ClusterId;
        }

        // ═══ 目标选择 (源 978–1146 行) ═══

        private const float MinTargetDistanceMeters = 150f;
        private const float MinTargetDistanceSq = MinTargetDistanceMeters * MinTargetDistanceMeters;

        private void SelectTargetInCluster(CoverageAssignment a, CoverageCluster cluster, List<ShipDes> allShips)
        {
            if (Config.TargetMode == "WeightedCentroidMedoid")
            {
                SelectCentroidMedoid(a, cluster, allShips);
                return;
            }

            // LegacyBestRisk: score = rw·risk + bw·belief − tw·normDist
            float rw = Config.RiskWeight;
            float bw = Config.BeliefWeight;
            float tw = Config.DistanceWeight * 0.5f;
            float sx = GetShipX(a.UsvId, allShips), sz = GetShipY(a.UsvId, allShips);
            float bestScore = float.MinValue;
            int bestCol = cluster.CentroidCol, bestRow = cluster.CentroidRow;
            float maxD = Field.Columns * Field.CellSize;

            var cells = cluster.CellIndices;
            if (cells == null || cells.Count == 0)
            {
                int n = Field.Columns * Field.Rows;
                for (int i = 0; i < n; i++)
                {
                    if (Field.ObstacleMask[i]) continue;
                    int c = i % Field.Columns, r = i / Field.Columns;
                    float risk = Field.Pmiss[i] * Field.Belief[i];
                    float dist = MathF.Sqrt((Field.ColToWorldX(c) - sx) * (Field.ColToWorldX(c) - sx) +
                                            (Field.RowToWorldZ(r) - sz) * (Field.RowToWorldZ(r) - sz));
                    float score = rw * risk + bw * Field.Belief[i] - tw * (dist / maxD);
                    if (score > bestScore) { bestScore = score; bestCol = c; bestRow = r; }
                }
            }
            else
            {
                for (int fi = 0; fi < cells.Count; fi++)
                {
                    int idx = cells[fi];
                    if (Field.ObstacleMask[idx]) continue;
                    int c = idx % Field.Columns, r = idx / Field.Columns;
                    float risk = Field.Pmiss[idx] * Field.Belief[idx];
                    float dist = MathF.Sqrt((Field.ColToWorldX(c) - sx) * (Field.ColToWorldX(c) - sx) +
                                            (Field.RowToWorldZ(r) - sz) * (Field.RowToWorldZ(r) - sz));
                    float score = rw * risk + bw * Field.Belief[idx] - tw * (dist / maxD);
                    if (score > bestScore) { bestScore = score; bestCol = c; bestRow = r; }
                }
            }

            a.TargetCol = bestCol; a.TargetRow = bestRow;
            a.TargetWorldX = Field.ColToWorldX(bestCol); a.TargetWorldZ = Field.RowToWorldZ(bestRow);
            a.TargetScore = bestScore;
            a.PathLength = MathF.Sqrt((a.TargetWorldX - sx) * (a.TargetWorldX - sx) +
                                      (a.TargetWorldZ - sz) * (a.TargetWorldZ - sz));
        }

        /// <summary>WeightedCentroidMedoid: 离加权质心最近且满足 ≥150m 约束的自由格</summary>
        private void SelectCentroidMedoid(CoverageAssignment a, CoverageCluster cluster, List<ShipDes> allShips)
        {
            float cx = cluster.CentroidX, cz = cluster.CentroidZ;
            float sx = GetShipX(a.UsvId, allShips), sz = GetShipY(a.UsvId, allShips);
            int bestCol = cluster.CentroidCol, bestRow = cluster.CentroidRow;
            float bestDist = float.MaxValue;
            int bestColFar = -1, bestRowFar = -1; float bestDistFar = float.MaxValue;

            if (cluster.CellIndices != null && cluster.CellIndices.Count > 0)
            {
                for (int fi = 0; fi < cluster.CellIndices.Count; fi++)
                {
                    int idx = cluster.CellIndices[fi];
                    if (Field.ObstacleMask[idx]) continue;
                    int c = idx % Field.Columns, r = idx / Field.Columns;
                    float wx = Field.ColToWorldX(c), wz = Field.RowToWorldZ(r);
                    float d = (wx - cx) * (wx - cx) + (wz - cz) * (wz - cz);
                    if (d < bestDist) { bestDist = d; bestCol = c; bestRow = r; }
                    float shipDistSq = (wx - sx) * (wx - sx) + (wz - sz) * (wz - sz);
                    if (shipDistSq >= MinTargetDistanceSq && d < bestDistFar)
                    { bestDistFar = d; bestColFar = c; bestRowFar = r; }
                }
            }
            else
            {
                int n = Field.Columns * Field.Rows;
                for (int i = 0; i < n; i++)
                {
                    if (Field.ObstacleMask[i]) continue;
                    int c = i % Field.Columns, r = i / Field.Columns;
                    float wx = Field.ColToWorldX(c), wz = Field.RowToWorldZ(r);
                    float d = (wx - cx) * (wx - cx) + (wz - cz) * (wz - cz);
                    if (d < bestDist) { bestDist = d; bestCol = c; bestRow = r; }
                    float shipDistSq = (wx - sx) * (wx - sx) + (wz - sz) * (wz - sz);
                    if (shipDistSq >= MinTargetDistanceSq && d < bestDistFar)
                    { bestDistFar = d; bestColFar = c; bestRowFar = r; }
                }
            }

            if (bestColFar >= 0)                        // 优先: 满足 ≥150m 的最近格
            { bestCol = bestColFar; bestRow = bestRowFar; bestDist = bestDistFar; }
            else if (TryFindGlobalFarCellNear(cx, cz, sx, sz, out int globalCol, out int globalRow, out float globalDist))
            { bestCol = globalCol; bestRow = globalRow; bestDist = globalDist; }   // 降级 1: 全局满足约束
            // 降级 2: 使用无距离约束的最近 medoid

            a.TargetCol = bestCol; a.TargetRow = bestRow;
            a.TargetWorldX = Field.ColToWorldX(bestCol); a.TargetWorldZ = Field.RowToWorldZ(bestRow);
            a.TargetScore = bestDist;
        }

        private bool TryFindGlobalFarCellNear(float cx, float cz, float sx, float sz, out int bestCol, out int bestRow, out float bestDist)
        {
            bestCol = -1; bestRow = -1; bestDist = float.MaxValue;
            int n = Field.Columns * Field.Rows;
            for (int i = 0; i < n; i++)
            {
                if (Field.ObstacleMask[i]) continue;
                int c = i % Field.Columns, r = i / Field.Columns;
                float wx = Field.ColToWorldX(c), wz = Field.RowToWorldZ(r);
                float shipDistSq = (wx - sx) * (wx - sx) + (wz - sz) * (wz - sz);
                if (shipDistSq < MinTargetDistanceSq) continue;
                float d = (wx - cx) * (wx - cx) + (wz - cz) * (wz - cz);
                if (d < bestDist) { bestDist = d; bestCol = c; bestRow = r; }
            }
            return bestCol >= 0;
        }

        /// <summary>A* 连续失败降级: 全局最高 cellRisk 自由格 (源 1125–1146 行)</summary>
        private void SelectGlobalBestTarget(CoverageAssignment a, List<ShipDes> allShips)
        {
            float rw = Config.RiskWeight;
            float sx = GetShipX(a.UsvId, allShips), sz = GetShipY(a.UsvId, allShips);
            float bestScore = float.MinValue;
            int bestCol = 0, bestRow = 0;
            int n = Field.Columns * Field.Rows;
            float maxD = Field.Columns * Field.CellSize;
            for (int i = 0; i < n; i++)
            {
                if (Field.ObstacleMask[i]) continue;
                int c = i % Field.Columns, r = i / Field.Columns;
                float risk = Field.Pmiss[i] * Field.Belief[i];
                float dist = MathF.Sqrt((Field.ColToWorldX(c) - sx) * (Field.ColToWorldX(c) - sx) +
                                        (Field.RowToWorldZ(r) - sz) * (Field.RowToWorldZ(r) - sz));
                float score = rw * risk - 0.25f * Config.DistanceWeight * (dist / maxD);
                if (score > bestScore) { bestScore = score; bestCol = c; bestRow = r; }
            }
            a.TargetCol = bestCol; a.TargetRow = bestRow;
            a.TargetWorldX = Field.ColToWorldX(bestCol); a.TargetWorldZ = Field.RowToWorldZ(bestRow);
            a.TargetScore = bestScore;
        }

        private float GetShipX(string id, List<ShipDes> ships)
        {
            if (ships != null)
                for (int i = 0; i < ships.Count; i++)
                    if (ships[i].Id == id) return ships[i].X;
            return 0f;
        }

        private float GetShipY(string id, List<ShipDes> ships)
        {
            if (ships != null)
                for (int i = 0; i < ships.Count; i++)
                    if (ships[i].Id == id) return ships[i].Y;
            return 0f;
        }

        // ═══ voice anchor (源 1353–1476 行) ═══

        private bool IsActiveVoiceAnchor()
        {
            return _voiceAnchor != null
                && _voiceAnchor.Valid
                && !string.IsNullOrEmpty(_voiceAnchor.UsvId)
                && (_voiceAnchor.ExpiresAt <= 0f || NowSeconds <= _voiceAnchor.ExpiresAt);
        }

        private void ProjectVoiceAnchorOutsideAvoidance()
        {
            if (_voiceAnchor == null || !_voiceAnchor.Valid) return;
            int idx = _voiceAnchor.TargetRow * Field.Columns + _voiceAnchor.TargetCol;
            bool blocked = idx < 0 || idx >= Field.ObstacleMask.Length
                || Field.ObstacleMask[idx] || _humanAnchorAvoidCells.Contains(idx);
            if (!blocked) return;

            var nearest = FindNearestAllowedCell(_voiceAnchor.TargetWorldX, _voiceAnchor.TargetWorldZ, _humanAnchorAvoidCells);
            if (nearest.idx < 0) return;
            _voiceAnchor.TargetCol = nearest.col;
            _voiceAnchor.TargetRow = nearest.row;
            _voiceAnchor.TargetWorldX = nearest.wx;
            _voiceAnchor.TargetWorldZ = nearest.wz;
            _voiceAnchor.Projected = true;
        }

        private (int idx, int col, int row, float wx, float wz) FindNearestAllowedCell(float wx, float wz, HashSet<int> avoidCells)
        {
            int bc = Field.WorldToCol(wx), br = Field.WorldToRow(wz);
            int maxD = Math.Max(Field.Columns, Field.Rows);
            for (int d = 0; d <= maxD; d++)
                for (int dc = -d; dc <= d; dc++)
                {
                    int c = bc + dc;
                    int rowA = br + (d - Math.Abs(dc));
                    if (IsAllowedCell(c, rowA, avoidCells))
                    {
                        int idx = rowA * Field.Columns + c;
                        return (idx, c, rowA, Field.ColToWorldX(c), Field.RowToWorldZ(rowA));
                    }
                    int rowB = br - (d - Math.Abs(dc));
                    if (rowB != rowA && IsAllowedCell(c, rowB, avoidCells))
                    {
                        int idx = rowB * Field.Columns + c;
                        return (idx, c, rowB, Field.ColToWorldX(c), Field.RowToWorldZ(rowB));
                    }
                }
            return (-1, bc, br, Field.ColToWorldX(bc), Field.RowToWorldZ(br));
        }

        private bool IsAllowedCell(int col, int row, HashSet<int> avoidCells)
        {
            if (col < 0 || col >= Field.Columns || row < 0 || row >= Field.Rows) return false;
            int idx = row * Field.Columns + col;
            if (idx < 0 || idx >= Field.ObstacleMask.Length) return false;
            if (Field.ObstacleMask[idx]) return false;
            return avoidCells == null || !avoidCells.Contains(idx);
        }

        /// <summary>设置语音命令目标 (返回是否接受)。duration<=0 表示不过期。</summary>
        public bool SetVoiceAnchor(string commandId, string rawText, string usvId, string regionId,
                                   float wx, float wz, float duration)
        {
            var nearest = Field.FindNearestFreeCell(wx, wz);
            if (nearest.idx < 0)
            {
                _voiceAnchor = new VoiceCommandAnchor
                {
                    Valid = false,
                    CommandId = commandId ?? "",
                    RawText = rawText ?? "",
                    UsvId = NormalizeUsvId(usvId),
                    RegionId = regionId ?? "",
                    Status = "rejected",
                    RejectReason = "no_free_cell"
                };
                return false;
            }
            _voiceAnchor = new VoiceCommandAnchor
            {
                Valid = true, CommandId = commandId ?? "", RawText = rawText ?? "",
                UsvId = NormalizeUsvId(usvId), RegionId = regionId ?? "",
                TargetCol = nearest.col, TargetRow = nearest.row,
                TargetWorldX = nearest.wx, TargetWorldZ = nearest.wz,
                CreatedTime = NowSeconds, ExpiresAt = duration > 0 ? NowSeconds + duration : 0,
                Projected = (MathF.Abs(nearest.wx - wx) > 1f || MathF.Abs(nearest.wz - wz) > 1f),
                Status = "accepted"
            };
            return true;
        }

        public void ClearVoiceAnchor() { _voiceAnchor = new VoiceCommandAnchor(); }
        public VoiceCommandAnchor GetVoiceAnchor() => _voiceAnchor;

        private static string NormalizeUsvId(string id)
        {
            if (string.IsNullOrWhiteSpace(id)) return "";
            string s = id.Trim();
            if (s.StartsWith("T", StringComparison.OrdinalIgnoreCase) || s.StartsWith("U", StringComparison.OrdinalIgnoreCase))
                s = s.Substring(1);
            return int.TryParse(s, out int n) ? n.ToString() : s;
        }

        private static bool IsSameUsvId(string a, string b) => NormalizeUsvId(a) == NormalizeUsvId(b);
    }

    // ═══════════════════════════════════════════════════════════════════
    // ReplanScheduler — 对应 PathPlan.cs 351–436 行 (事件驱动 + rolling 兜底)
    // 文档: ../docs/07_replan_scheduler.md
    // ═══════════════════════════════════════════════════════════════════

    public class ReplanScheduler
    {
        public CoveragePlannerEngine Planner;
        public float DeltaSeconds;                    // 每帧传入 (Unity 侧: Time.deltaTime)

        private const float ReplanDebounce = 1.5f;    // 到点事件合并窗口
        private float _rollingReplanTimer;
        private float _lastFleetReplanTime = -999f;
        private readonly HashSet<string> _reachedShips = new HashSet<string>();  // 提炼版用 usvId 代替 Transform
        private float _scheduledReplanTime;
        private bool _scheduledReplan;

        /// <summary>船到达终点时调用 (Unity 侧: WaypointFollower → PathPlan.NotifyTargetReached)</summary>
        public void NotifyTargetReached(string usvId)
        {
            if (string.IsNullOrEmpty(usvId)) return;
            _reachedShips.Add(usvId);
            float nextTime = (float)Planner.NowSeconds + ReplanDebounce;
            if (!_scheduledReplan || nextTime < _scheduledReplanTime)
                _scheduledReplanTime = nextTime;
            _scheduledReplan = true;
        }

        /// <summary>返回本次应触发的 reason (null = 不触发)。由外部执行 TriggerFleetReplan。</summary>
        public string Tick(bool anyAutoShipNeedsPathRefresh)
        {
            var cfg = Planner.GetPlannerRuntimeConfigSnapshot();
            float replanInterval = cfg?.ReplanIntervalSeconds ?? 12f;
            float minCooldown = cfg?.MinReplanCooldownSeconds ?? 4f;

            // ── 1. Debounced target_reached ──
            if (_scheduledReplan && Planner.NowSeconds >= _scheduledReplanTime)
            {
                _scheduledReplan = false;
                if (_reachedShips.Count > 0)
                {
                    _reachedShips.Clear();
                    return "target_reached";
                }
            }

            // ── 2. Missing path (有船无路可走) ──
            if (anyAutoShipNeedsPathRefresh && Planner.NowSeconds - _lastFleetReplanTime >= minCooldown)
                return "missing_path";

            // ── 3. Rolling 兜底 ──
            _rollingReplanTimer += DeltaSeconds;
            if (_rollingReplanTimer >= replanInterval && Planner.NowSeconds - _lastFleetReplanTime >= minCooldown)
                return "rolling";

            return null;
        }

        /// <summary>触发 fleet replan (reason: initial/target_reached/missing_path/rolling/voice_*)</summary>
        public void TriggerFleetReplan(string reason)
        {
            Planner.SetReplanReason(reason);
            _reachedShips.Clear();
            _scheduledReplan = false;
            _rollingReplanTimer = 0f;
            _lastFleetReplanTime = (float)Planner.NowSeconds;
        }
    }
}
