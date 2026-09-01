# source_map.md — algo 文件 ↔ Unity 源文件对照表

本文档给出 `algo/` 中每个文件与 Unity 工程真实源代码的精确对应关系。
提炼代码（`code/*.cs`）在算法上与原实现**逐段等价**，仅移除了 Unity 依赖
（`Mathf` → `MathF`、`Debug.Log` → 移除、`Time.time` → 显式参数、`RFNextPointRuntime.Instance` → 接口注入）。

## 源文件总览

| Unity 源文件 | 行数 | 在算法链路中的角色 |
|---|---|---|
| `Assets/Scripts/Planning/PlannerPathPlanningService.cs` | 1597 | **核心**：CoverageField（栅格/传感器/信念/指标）+ CoveragePlanner（K-means + Hungarian + A* + humanAnchor + voiceAnchor）+ LegacyCompat 兼容桩 |
| `Assets/Scripts/Planning/CoverageTypes.cs` | 276 | 运行时类型定义（CoverageCluster / CoverageAssignment / PlannerRuntimeConfig / PlannerPerfSnapshot / HumanIntentPrediction / VoiceCommandAnchor） |
| `Assets/Scripts/Planning/IPathPlanningService.cs` | 78 | 旧接口兼容面（冻结） |
| `Assets/Scripts/PathPlan.cs` | 1594 | 场景入口 + ReplanScheduler 调度 + 路径后处理 + 语音命令 + 障碍物可视化 |
| `Assets/Scripts/WaypointFollower.cs` | 290 | 航路点执行（推力限速模型、卡点检测、到达通知） |
| `Assets/Scripts/Planner.cs` | 108 | `suanfaCshape` 命名空间类型定义（ShipDes / ObcRect / PlannerParam / PathPlan）+ 已清空的旧 Planner 壳 |
| `Assets/NewData/TaskConfigData.cs` | — | TaskScenarioConfig / ProbabilityModelConfig / DetectorFormulaConfig 配置类型 |
| `Assets/Scripts/Intent/RFNextPointAssist/RFNextPointRuntime.cs` | — | RF 预测运行时（human anchor 的预测来源） |

## 逐段映射：PlannerPathPlanningService.cs

| 源文件行号 | 内容 | algo 对应 |
|---|---|---|
| 24–315 | #region CoverageField：栅格状态、障碍物 mask、传感器扫描、时间衰减、信念归一化、指标 | [docs/01_belief_and_coverage_field.md](docs/01_belief_and_coverage_field.md)、[code/coverage_field.cs](code/coverage_field.cs) |
| 76–105 | `ApplyScenarioConfig`（读取 probabilityModel 配置） | coverage_field.cs `ApplyProbabilityModelConfig` |
| 107–140 | `InitializeCoverageRiskModel`（建栅格、初始 Pmiss=1、均匀信念） | coverage_field.cs `Initialize` |
| 142–195 | `ObcRectToCircle` / `MarkObstacles` / `ApplyObstacles`（圆形障碍 + inflation） | coverage_field.cs `MarkObstacles` |
| 201–240 | `UpdateSearchProbabilities`（传感器扫描更新 Pmiss） | coverage_field.cs `UpdateSearchProbabilities` |
| 242–262 | `ComputePDetect` / `EvalCurve`（检测概率距离曲线） | coverage_field.cs `ComputePDetect` |
| 263–276 | `ApplyTimeDecay`（时间衰减恢复） | coverage_field.cs `ApplyTimeDecay` |
| 277–283 | `RecomputeBelief`（信念归一化） | coverage_field.cs `RecomputeBelief` |
| 289–307 | `RefreshStats`（meanPmiss / C80 / TotalRisk） | coverage_field.cs `RefreshStats` |
| 321–351 | `GeneratePlan`（执行 ExecuteReplan + 输出 cachedPath，fallback A* 计数） | planner_orchestrator.cs `GeneratePlan` |
| 353–361 | `UpdatePlan`（包装 GeneratePlan） | planner_orchestrator.cs `UpdatePlan` |
| 363–649 | `ExecuteReplan`（9 步编排：分离船舶 → RF anchor → 聚类 → Hungarian → 目标选择 → A* → 导航点 → 状态维护） | planner_orchestrator.cs `ExecuteReplan`、[docs/02_planner_pipeline.md](docs/02_planner_pipeline.md) |
| 363–421 | 步骤 1：自主船/人控船/语音船分离 | 02 文档 §3.1 |
| 422–457 | 步骤 2：RF human anchor 生成（fail-closed 条件链） | 02 文档 §3.2、[docs/06_human_anchor.md](docs/06_human_anchor.md) |
| 459–488 | 步骤 3：聚类分支（fixed-anchor 10-means vs 普通 K-means） | 02 文档 §3.3、[docs/03_clustering_kmeans.md](docs/03_clustering_kmeans.md) |
| 490–498 | 步骤 4：Hungarian 指派 | 02 文档 §3.4、[docs/04_assignment.md](docs/04_assignment.md) |
| 500–553 | 步骤 5–6：voice anchor 定向 + 分区内目标选择 + A* 连败升级 | 02 文档 §3.5–3.6 |
| 555–605 | 步骤 7：逐船 A* 路径 + 失败计数 + NavigationWaypoint 记录 | 02 文档 §3.7、[docs/05_astar.md](docs/05_astar.md) |
| 609–633 | 性能快照 + 诊断日志 | 02 文档 §6 |
| 638–649 | 步骤 8–9：状态维护（clusters / replanIndex / 热启动质心缓存） | 02 文档 §3.8 |
| 657–767 | `WeightedKMeansWithFixedAnchor`（center[0] 固定） | [code/kmeans.cs](code/kmeans.cs) `WeightedKMeansWithFixedAnchor` |
| 770–832 | `WeightedKMeansBasic`（普通模式） | kmeans.cs `WeightedKMeansBasic` |
| 840–928 | `HungarianAssign`（代价矩阵构建） | [code/hungarian.cs](code/hungarian.cs) |
| 931–971 | `SolveHungarian`（O(n³) 标准实现） | hungarian.cs `SolveHungarian` |
| 978–1033 | `SelectTargetInCluster`（LegacyBestRisk 评分） | planner_orchestrator.cs `SelectTargetInCluster` |
| 1035–1097 | `SelectCentroidMedoid`（WeightedCentroidMedoid + 150m 约束 + 全局降级） | planner_orchestrator.cs `SelectCentroidMedoid` |
| 1099–1123 | `TryFindGlobalFarCellNear` | planner_orchestrator.cs |
| 1125–1146 | `SelectGlobalBestTarget`（A* 连败降级） | planner_orchestrator.cs |
| 1180–1298 | `BuildAStarPath`（8 方向 A* + human anchor 避让 + 起终点投影 + 对角禁穿） | [code/astar.cs](code/astar.cs)、[docs/05_astar.md](docs/05_astar.md) |
| 1300–1317 | `IsSamePoint` / `Heuristic` / `CalcPathLength` | astar.cs |
| 1323–1347 | 坐标转换 + `FindNearestFreeCell` | coverage_field.cs / astar.cs |
| 1353–1387 | `FindNearestAllowedCell` / `IsAllowedCell`（voice anchor 避让投影） | planner_orchestrator.cs |
| 1389–1411 | voice anchor 生命周期判断与投影 | planner_orchestrator.cs |
| 1446–1476 | `SetVoiceAnchor` / `ClearVoiceAnchor`（语音目标） | planner_orchestrator.cs |
| 1501–1596 | #region LegacyCompat（旧接口兼容桩，不参与主逻辑，**未提取**） | — |

## 逐段映射：PathPlan.cs

| 源文件行号 | 内容 | algo 对应 |
|---|---|---|
| 351–436 | ReplanScheduler（`NotifyTargetReached` / `ReplanSchedulerUpdate` / `TriggerFleetReplan`） | [docs/07_replan_scheduler.md](docs/07_replan_scheduler.md)、planner_orchestrator.cs（scheduler 部分） |
| 60–94 | `Start`（初始化规划服务与栅格） | planner_orchestrator.cs（初始化说明） |
| 207–276 | `OnFirstProduceNewPath`（舰队初始覆盖规划） | 07 文档 §4 |
| 521–561 | `ProduceNewPathAgain`（重规划执行） | 07 文档 §3 |
| 619–658 | `ConvertPlannerPathToWaypoints`（航路点过滤：障碍内点丢弃 + segment 截断） | [code/waypoint_filter.cs](code/waypoint_filter.cs)、[docs/08_execution.md](docs/08_execution.md) §2 |
| 660–672 | `ApplyWaypointSafetyConfig`（安全边际推导） | waypoint_filter.cs |
| 674–711 | `AssignWaypointsToFollower`（最短路径阈值 100m / rolling 保留旧路径） | 08 文档 §3 |
| 723–764 | `IsWaypointInsideObstacle` / `IsWaypointSegmentBlocked` / `SegmentIntersectsCircleXZ` | waypoint_filter.cs |
| 1213–1403 | 语音命令入口 / 生命周期 / 记录 | planner_orchestrator.cs（voice 部分）、02 文档 §7 |
| 1483–1498 | `AnyAutoShipNeedsPathRefresh`（missing_path 检测） | 07 文档 §2.2 |

## 逐段映射：WaypointFollower.cs

| 源文件行号 | 内容 | algo 对应 |
|---|---|---|
| 60–88 | `SetWaypoints`（起点选择：最靠近且在前方的点） | [docs/08_execution.md](docs/08_execution.md) §4 |
| 99–199 | `FixedUpdate`（推力限速模型、减速接近、卡点检测 3s、到达判定 8m、到达通知） | 08 文档 §4 |

## 提炼代码与原实现的差异清单

`code/*.cs` 与 Unity 源码的**有意差异**（全部为依赖替换，非算法差异）：

| 差异 | 原因 |
|---|---|
| `Mathf.*` → `MathF.*` / 内联实现 | 去除 UnityEngine 依赖 |
| `Debug.Log*` → 移除（保留为注释） | 诊断日志属 Unity 侧 |
| `Time.time` → 调用方传入 `nowSeconds` | 时间来源显式化 |
| `RFNextPointRuntime.Instance` → `IHumanIntentSource` 接口 | RF 预测模块不在本包范围内，抽象为接口（见 planner_orchestrator.cs 顶部） |
| `GetShipX/Y` 的 `PlayerSwitcher` fallback → 移除 | 场景查找属 Unity 侧；ship 列表始终由调用方传入 |
| `FleetMovementDiagnostics` 赋值 → 移除 | 诊断辅助属 Unity 侧 |
| `PlannerPerfSnapshot` 保留但去掉 Unity 字段 | 性能指标对论文有用 |
| `TaskScenarioConfig` / `DetectorFormulaConfig` → 精简为 `ProbabilityModelConfig`（仅保留被规划消费的字段） | 完整配置类型在 `Assets/NewData/TaskConfigData.cs` |
| 未提取 #region LegacyCompat（1501–1596 行兼容桩） | 冻结的旧接口壳，不参与算法主逻辑 |
