# 09 · 配置参数全表

> 源类型：`Assets/Scripts/Planning/CoverageTypes.cs`（PlannerRuntimeConfig）、
> `Assets/NewData/TaskConfigData.cs`（ProbabilityModelConfig / DetectorFormulaConfig）
> 消费状态以对 `Assets/Scripts/Planning/PlannerPathPlanningService.cs` 与 `Assets/Scripts/PathPlan.cs` 的
> grep 结果为准（2026-05 冻结版）。

## 1. PlannerRuntimeConfig

来源：`experiment_ui_config.json` 的 `planner_config` 块（F2 面板）优先；
否则 `default_task.json` 的 `plannerConfig`；再否则类型默认值。

| 字段 | 默认 | 消费位置 | 消费状态 | 说明 |
|---|---|---|---|---|
| `replanIntervalSeconds` | 12 | PathPlan.ReplanSchedulerUpdate | ✓ | rolling 兜底周期 |
| `minReplanCooldownSeconds` | 4 | PathPlan.ReplanSchedulerUpdate | ✓ | 重规划最小间隔（missing_path 与 rolling 共用） |
| `missingPathCooldownSeconds` | 5 | — | ✗ **声明未消费** | 代码实际用 minReplanCooldownSeconds 承担全部 cooldown |
| `enableHumanAnchor` | true | ExecuteReplan 步骤 2 | ✓ | 实验条件开关（F2 面板 `SetHumanAnchorEnabled`） |
| `rfAnchorConfidenceThreshold` | 0.3 | ExecuteReplan 步骤 2 | ✓ | RF 预测置信度下限 |
| `rfAnchorShiftCells` | 3 | — | ✗ **声明未消费** | 无代码读取 |
| `anchorTtlSeconds` | 8 | — | ✗ **声明未消费** | human anchor 无 TTL 逻辑（每轮重规划重新生成） |
| `anchorEmaAlpha` | 0.35 | — | ✗ **声明未消费** | 无 EMA 平滑逻辑 |
| `rfAnchorAvoidanceCells` | 1 | — | ✗ **声明未消费** | 注释称 A* 避让 dilation；实际避让 = cluster 原始 cellIndices，无膨胀 |
| `switchPenalty` | 0.5 | HungarianAssign | ✓ | 换区惩罚（TravelCostOnly 与 LegacyMixedCost 共用） |
| `unreachablePenalty` | 999 | — | ✗ **声明未消费** | 不可达处理走 A* 失败计数链，不用惩罚值 |
| `maxKMeansIterations` | 10 | 两种 K-means | ✓ | 迭代上限 |
| `kMeansTolerance` | 0.001 | 两种 K-means | ✓ | 质心曼哈顿位移收敛阈值 |
| `densityMode` | "PmissBelief" | — | ✗ **声明未消费** | cellRisk = Pmiss×Belief 为唯一实现，无模式分支 |
| `assignmentMode` | "TravelCostOnly" | HungarianAssign | ✓ | TravelCostOnly / LegacyMixedCost |
| `targetMode` | "WeightedCentroidMedoid" | SelectTargetInCluster | ✓ | WeightedCentroidMedoid / LegacyBestRisk |
| `distanceWeight` | 1.0 | LegacyMixedCost / LegacyBestRisk / SelectGlobalBestTarget | ✓（仅旧模式与降级路径） | TravelCostOnly 不用 |
| `riskWeight` | 2.0 | 同上 | ✓（同上） | |
| `beliefWeight` | 1.5 | LegacyMixedCost / LegacyBestRisk | ✓（仅旧模式） | |
| `terminationRiskThreshold` | 0.05 | `IsCoverageRiskBelowThreshold`（LegacyCompat 桩） | ✓（仅兼容桩，无运行时调用方触发终止） | |
| `configVersion` | 1 | ApplyPlannerRuntimeConfig / SetHumanAnchorEnabled | ✓ | 每次运行时配置修改 +1（`[NonSerialized]`） |

> 论文写作注意：上表"声明未消费"字段是**当前 Unity 实现**的真实状态。若论文描述
> EMA 平滑、TTL、避让膨胀等机制，必须以代码实际行为为准（当前不存在这些机制），
> 或先实现再描述。

## 2. ProbabilityModelConfig（覆盖场配置）

来源：`default_task.json` 的 `probabilityModel`（`ApplyScenarioConfig` 读取）。

| 字段 | 默认 | 消费位置 | 说明 |
|---|---|---|---|
| `gridCellSize` | 50 | InitializeCoverageRiskModel | 栅格尺寸（下限 20 m） |
| `obstacleInflationRadius` | 80 | MarkObstacles + ApplyWaypointSafetyConfig | 圆形障碍膨胀半径 |
| `timeDecayMode` | "none" | ApplyTimeDecay | none / linear / recovery_linear / exponential / recovery_exponential |
| `timeDecayPerHour` | 0 | ApplyTimeDecay | >0 才启用衰减 |
| `pmissRecoveryBoostForDemo` | 1 | ApplyTimeDecay | 衰减强度系数 |
| `detectorFormulas[]` | — | ComputePDetect | 按 scanType 的检测曲线公式（见 01 文档 §3） |
| `recheckIntervalSeconds` | 60 | — | ✗ 未被规划代码消费 |
| `coverageGapThreshold` / `speedRecoveryGain` / `speedRecoveryReference` | — | — | ✗ Phase 1 遗留字段，未被消费 |
| `alertConditionedBeta/Sigma` / `nMarkConditionedAlpha` / `useConditionedTargetField` | — | — | ✗ Phase 2 遗留字段，未被消费 |
| `inspectTimeSeconds` / `autoClassifyAccuracy` / `humanConfirmAccuracy` | — | — | 目标查验模块使用，不在本规划包范围 |

## 3. DetectorFormulaConfig

| 字段 | 默认 | 说明 |
|---|---|---|
| `scanType` | 1 | 探测手段类型键 |
| `detectorName` | "camera" | 名称（仅标识） |
| `distanceCurve` | "power" | flat / linear / power / exponential |
| `gain` | 1 | 增益 |
| `edgeProbabilityFactor` | 0.18 | 视野边缘探测概率系数 |
| `exponent` | 1.35 | power 曲线指数 |
| `exponentialLambda` | 2.5 | exponential 曲线 λ |

## 4. 硬编码常量（不在配置文件中）

| 常量 | 值 | 位置 |
|---|---|---|
| `MaxAStarRetries` | 3 | A* 连续失败后目标降级阈值 |
| `MinTargetDistanceMeters` | 150 | WeightedCentroidMedoid 最短目标距离 |
| `MinAssignedPathLength` | 100 m | 路径过短则保留旧路径 |
| `ReplanDebounce` | 1.5 s | target_reached 合并窗口 |
| `VoiceCommandTimeoutSeconds` | 120 s | 语音命令有效期 |
| `VoiceArrivalDistanceThreshold` | 100 m | 语音命令到达判定 |
| K-means 权重下限 | 1e-6 | 防零权 |
| K-means 冷启动抖动 | ±2×cellSize | 船位扰动 |
| A* 步进代价 | 10 / 14 | 直角 / 对角 |
| A* 启发式 | 10×Manhattan | — |
| A* 迭代上限 | 2×cols×rows | 防御性 |
| C80 阈值 | (1−Pmiss) > 0.8 | 覆盖率定义 |
| WaypointFollower 到达半径 | 8 m | — |
| WaypointFollower 卡点超时 | 3 s / 95% | — |

> 这些常量如需实验对比或消融，应在代码中参数化后再写入配置，论文中不要描述为"可配置"。
