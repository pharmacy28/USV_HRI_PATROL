// ============================================================================
#nullable disable
// core_types.cs — 覆盖规划核心数据类型（无 Unity 依赖提炼版）
//
// 源文件:
//   Assets/Scripts/Planner.cs                    (ShipDes / ScanMethod / ObcRect / PlannerParam / PathPlan)
//   Assets/Scripts/Planning/CoverageTypes.cs     (CoverageCluster / CoverageAssignment / NavigationWaypoint /
//                                                 PlannerRuntimeConfig / VoiceCommandAnchor / HumanIntentPrediction /
//                                                 PlannerPerfSnapshot)
//   Assets/NewData/TaskConfigData.cs             (ProbabilityModelConfig / DetectorFormulaConfig, 仅保留被规划消费的字段)
//
// 提炼差异: 去除 UnityEngine 依赖 (Mathf → MathF, Vector3 不引入, NonSerialized 移除);
//           算法语义与原实现逐段一致。详见 ../source_map.md
// ============================================================================

using System;
using System.Collections.Generic;

namespace UsvPatrolPlanning
{
    // ─────────────────────────────────────────────
    // 船舶与场景输入类型 (源自 Planner.cs)
    // ─────────────────────────────────────────────

    /// <summary>探测手段描述</summary>
    public struct ScanMethod
    {
        public int ScanType;        // m_scan_type: 探测手段类型 (对应 detectorFormulas 键)
        public int VisionRange;     // m_vision_range: 视野距离 (米)
        public float SearchProb;    // m_search_prob: 发现目标概率
    }

    /// <summary>船舶描述 (XZ 平面: m_x/m_y 即世界 x/z)</summary>
    public struct ShipDes
    {
        public string Id;                       // m_id: 舰船编号
        public int Speed;                       // m_speed: 移动速度 m/s
        public int X;                           // m_x: 船当前坐标 x
        public int Y;                           // m_y: 船当前坐标 z (XZ 平面)
        public List<ScanMethod> ScanMethods;    // m_scan_methods: 多种探测手段
        public bool IsHandControl;              // 是否人控
    }

    /// <summary>轴对齐矩形障碍物</summary>
    public struct ObcRect
    {
        public int X, Y;            // 左下角坐标
        public int Width, Height;   // 宽高
    }

    /// <summary>单次规划输入参数</summary>
    public struct PlannerParam
    {
        public int X, Y;                        // 目标区域左下角 (m_x/m_y)
        public int Width, Height;               // 目标区域宽高
        public List<ShipDes> ShipDes;           // 无人艇信息
        public List<ObcRect> ObcRects;          // 障碍物信息
        public ShipDes? ContextManualShip;      // 人控船上下文: 不参与自动船分配, 仅用于 Human Anchor
    }

    /// <summary>规划输出: usvId → 航路点 (XZ 平面坐标)</summary>
    public struct PathPlan
    {
        public Dictionary<string, List<System.Numerics.Vector2>> Paths;
    }

    // ─────────────────────────────────────────────
    // 覆盖规划类型 (源自 CoverageTypes.cs @Runtime 部分)
    // ─────────────────────────────────────────────

    /// <summary>K-means 聚类结果</summary>
    public class CoverageCluster
    {
        public int ClusterId;
        public float CentroidX, CentroidZ;              // 加权质心 (世界坐标)
        public int CentroidCol, CentroidRow;            // 加权质心 (栅格坐标)
        public List<int> CellIndices = new List<int>(); // 分区内自由格 flat index
        public float RiskSum;                           // Σ(Pmiss × belief)
        public float BeliefSum;                         // Σ(belief)
        public int BestTargetCol, BestTargetRow;        // 分区内 cellRisk 最高格
        public float BestTargetScore;
        public bool IsHumanAnchor;                      // 人控锚点集群
    }

    /// <summary>Hungarian 指派结果 (CachedPath 避免双重 A*)</summary>
    public class CoverageAssignment
    {
        public string UsvId;
        public int ClusterId;
        public int TargetCol, TargetRow;
        public float TargetWorldX, TargetWorldZ;
        public float AssignmentCost;
        public float TargetScore;
        public float PathLength;
        public bool Reachable;
        public bool RfInfluenced;
        public float HumanPredictedTargetX, HumanPredictedTargetZ;
        public bool AssignedByVoice;
        public string VoiceCommandId = "";
        public string VoiceRegion = "";
        public int VoiceTargetCol, VoiceTargetRow;
        public float VoiceTargetWorldX, VoiceTargetWorldZ;
        public List<System.Numerics.Vector2> CachedPath;   // ExecuteReplan 内 A* 结果, GeneratePlan 复用
    }

    /// <summary>导航点记录 (对应 Unity 侧 viz_frames.jsonl 输出)</summary>
    public class NavigationWaypoint
    {
        public double UnityTime;                 // 提炼版由调用方传入
        public int ReplanIndex;
        public string UsvId;
        public int AssignedClusterId;
        public int TargetCol, TargetRow;
        public float TargetWorldX, TargetWorldZ;
        public List<float> WaypointXs = new List<float>();
        public List<float> WaypointZs = new List<float>();
        public float PathLength;
        public bool Reachable;
        public float AssignmentCost;
        public float TargetScore;
        public bool RfInfluenced;
        public float HumanPredictedTargetX, HumanPredictedTargetZ;
        public bool AssignedByVoice;
        public string VoiceCommandId = "";
        public string VoiceRegion = "";
    }

    /// <summary>统一规划配置 (与 CoverageTypes.PlannerRuntimeConfig 字段一一对应)</summary>
    public class PlannerRuntimeConfig
    {
        // ── 重规划触发 ──
        public float ReplanIntervalSeconds = 12f;
        public float MinReplanCooldownSeconds = 4f;
        public float MissingPathCooldownSeconds = 5f;    // 注意: 当前实现未消费 (见 docs/09 §1)

        // ── human anchor ──
        public bool EnableHumanAnchor = true;
        public float RfAnchorConfidenceThreshold = 0.3f;
        public float RfAnchorShiftCells = 3f;            // 注意: 当前实现未消费
        public float AnchorTtlSeconds = 8f;              // 注意: 当前实现未消费
        public float AnchorEmaAlpha = 0.35f;             // 注意: 当前实现未消费
        public int RfAnchorAvoidanceCells = 1;           // 注意: 当前实现未消费 (实际避让=cluster 原始格集)

        // ── 评分约束 ──
        public float SwitchPenalty = 0.5f;
        public float UnreachablePenalty = 999f;          // 注意: 当前实现未消费

        // ── K-means ──
        public int MaxKMeansIterations = 10;
        public float KMeansTolerance = 0.001f;

        // ── 模式 ──
        public string DensityMode = "PmissBelief";               // 注意: 当前实现未消费 (cellRisk 唯一实现)
        public string AssignmentMode = "TravelCostOnly";         // TravelCostOnly | LegacyMixedCost
        public string TargetMode = "WeightedCentroidMedoid";     // WeightedCentroidMedoid | LegacyBestRisk

        // ── 旧兼容权重 (LegacyMixedCost / LegacyBestRisk 使用) ──
        public float DistanceWeight = 1.0f;
        public float RiskWeight = 2.0f;
        public float BeliefWeight = 1.5f;
        public float TerminationRiskThreshold = 0.05f;
        public int ConfigVersion = 1;

        public PlannerRuntimeConfig Clone() => (PlannerRuntimeConfig)MemberwiseClone();

        public void NormalizeDefaults()
        {
            var d = new PlannerRuntimeConfig();
            if (ReplanIntervalSeconds <= 0f) ReplanIntervalSeconds = d.ReplanIntervalSeconds;
            if (MinReplanCooldownSeconds <= 0f) MinReplanCooldownSeconds = d.MinReplanCooldownSeconds;
            if (MissingPathCooldownSeconds <= 0f) MissingPathCooldownSeconds = d.MissingPathCooldownSeconds;
            if (RfAnchorConfidenceThreshold <= 0f) RfAnchorConfidenceThreshold = d.RfAnchorConfidenceThreshold;
            RfAnchorConfidenceThreshold = Clamp01(RfAnchorConfidenceThreshold);
            if (RfAnchorShiftCells <= 0f) RfAnchorShiftCells = d.RfAnchorShiftCells;
            if (AnchorTtlSeconds <= 0f) AnchorTtlSeconds = d.AnchorTtlSeconds;
            if (AnchorEmaAlpha <= 0f) AnchorEmaAlpha = d.AnchorEmaAlpha;
            AnchorEmaAlpha = Clamp01(AnchorEmaAlpha);
            if (RfAnchorAvoidanceCells < 0) RfAnchorAvoidanceCells = d.RfAnchorAvoidanceCells;
            if (SwitchPenalty < 0f) SwitchPenalty = d.SwitchPenalty;
            if (UnreachablePenalty <= 0f) UnreachablePenalty = d.UnreachablePenalty;
            if (MaxKMeansIterations <= 0) MaxKMeansIterations = d.MaxKMeansIterations;
            if (KMeansTolerance <= 0f) KMeansTolerance = d.KMeansTolerance;
            if (string.IsNullOrWhiteSpace(DensityMode)) DensityMode = d.DensityMode;
            if (string.IsNullOrWhiteSpace(AssignmentMode)) AssignmentMode = d.AssignmentMode;
            if (string.IsNullOrWhiteSpace(TargetMode)) TargetMode = d.TargetMode;
            if (DistanceWeight <= 0f) DistanceWeight = d.DistanceWeight;
            if (RiskWeight <= 0f) RiskWeight = d.RiskWeight;
            if (BeliefWeight <= 0f) BeliefWeight = d.BeliefWeight;
            if (TerminationRiskThreshold <= 0f) TerminationRiskThreshold = d.TerminationRiskThreshold;
            if (ConfigVersion <= 0) ConfigVersion = 1;
        }

        private static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);
    }

    /// <summary>语音命令 anchor — 固定任务目标 (区别于 RF human anchor 的安全避让)</summary>
    public class VoiceCommandAnchor
    {
        public bool Valid;
        public string CommandId = "";
        public string RawText = "";
        public string UsvId = "";
        public string RegionId = "";
        public int TargetCol;
        public int TargetRow;
        public float TargetWorldX;
        public float TargetWorldZ;
        public double CreatedTime;       // 提炼版: 调用方传入的 now
        public double ExpiresAt;
        public bool Projected;
        public string Status = "";
        public string RejectReason = "";
        public float ArrivalDistance = -1f;
    }

    /// <summary>性能诊断快照 — 每次 ExecuteReplan 产出</summary>
    public class PlannerPerfSnapshot
    {
        public int ReplanIndex;
        public string ReplanReason;
        public int ConfigVersion;
        public double DecisionMs;
        public int AutoShipCount;
        public int ClusterCount;
        public int AssignmentCount;
        public int MissingPathCount;
        public int KMeansIterations;
        public float KMeansMs;
        public float AssignmentMs;
        public float AstarMs;              // 所有自动船 A* 总耗时
        public float PathGenMaxMs;         // 单船 A* 最久耗时 (论文 pathGenMax)
        public float PathGenTotalMs;       // 所有自动船 A* 总耗时 (论文 pathGenTotal, = AstarMs)
        public int AstarPathCount;
        public int AstarFailCount;
        public int AstarExpandedNodesTotal;
        public int AstarExpandedNodesMax;
        public int FallbackAStarCount;
    }

    /// <summary>人控意图预测快照 (RF → human anchor)</summary>
    public class HumanIntentPrediction
    {
        public bool Valid;
        public float PredictedWorldX, PredictedWorldZ;
        public int NearestFreeCol, NearestFreeRow;
        public float Confidence;
        public string Mode;
    }

    // ─────────────────────────────────────────────
    // RF 预测抽象 (提炼版接口, 替代 Unity 侧 RFNextPointRuntime.Instance 单例)
    // ─────────────────────────────────────────────

    public class HumanIntentPredictionData
    {
        public float PredictedDistance;   // 极坐标 r (米)
        public float PredictedAngleDeg;   // 极坐标 θ (度, 世界系)
        public float Confidence;
    }

    public interface IHumanIntentSource
    {
        string CurrentMode { get; }                  // "RF_ASSIST" | "AUTO" | ...
        bool IsPredictionValid { get; }
        HumanIntentPredictionData LastPrediction { get; }
    }

    // ─────────────────────────────────────────────
    // 覆盖场配置 (源自 TaskConfigData.cs, 仅保留被规划消费的字段)
    // ─────────────────────────────────────────────

    public class ProbabilityModelConfig
    {
        public string TimeDecayMode = "none";
        public float TimeDecayPerHour = 0f;
        public int GridCellSize = 50;
        public int ObstacleInflationRadius = 80;
        public float PmissRecoveryBoostForDemo = 1f;
        public DetectorFormulaConfig[] DetectorFormulas = Array.Empty<DetectorFormulaConfig>();
    }

    public class DetectorFormulaConfig
    {
        public int ScanType = 1;
        public string DetectorName = "camera";
        public string DistanceCurve = "power";   // flat | linear | power | exponential
        public float Gain = 1f;
        public float EdgeProbabilityFactor = 0.18f;
        public float Exponent = 1.35f;
        public float ExponentialLambda = 2.5f;
    }
}
