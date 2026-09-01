# algo/ — 多 USV 覆盖搜索路径规划算法包

本目录从 Unity 仿真工程（`usvpatrolsystem-1`）中提取完整的路径规划算法，作为**当前实现的规格说明与参考代码**，供三方面使用：

1. **论文写作**：算法流程、数学定义、参数含义的权威描述（与真实代码逐行对应）。
2. **Codex / AI 理解**：模块边界、数据流、伪代码、源文件行号映射，便于 AI 在迁移或改写时不偏离真实实现。
3. **平台迁移**：`code/` 中提供去除 Unity 依赖的提炼实现，作为向 ROS 2 / Gazebo（本仓库 `platform/`）迁移的参考。

> 一致性原则：本文档描述的是 **Unity 工程中当前真实运行的实现**（2026-05 冻结版）。
> 文档与代码如有出入，以真实代码为准；`source_map.md` 给出了每个文件对应的源文件与行号。

---

## 1. 算法定位

本算法解决：**在已知粗粒度障碍栅格的海域中，多艘无人艇（USV）协同搜索一个位置未知的静止目标，并支持人机协同（HRCDMS）**。

闭环数据流：

```text
Bayesian belief (Pmiss → 归一化信念)
  → belief-aware clustering (risk 加权 K-means)
  → human-constrained re-clustering (RF 预测人控船目的地 → 固定中心)
  → USV–center assignment (Hungarian)
  → A* obstacle-aware path generation
  → waypoint execution (WaypointFollower)
  → sensing (检测概率模型更新 Pmiss)
  → Bayesian posterior update
  → event-driven replanning (target_reached / missing_path / rolling / voice)
```

**核心研究假设**（来自 `idea/研究决策状态.md`，CONFIRMED 待检验）：

> 预测人类干预的未来空间后果，并在信念驱动重聚类期间固定该预测目的地，可使其余自主 USV 舰队主动重新分配搜索责任。

**科学纪律**（来自仓库根 `AGENTS.md`，论文写作时必须遵守）：

- K-means、Hungarian、A*、随机森林都是**标准组件**，不得仅因"使用了它们"而将其表述为科学贡献。
- 科学贡献在于**闭环架构与人机协同机制**（human anchor 的固定中心语义、belief-aware 聚类、事件驱动重规划），而非基础算法本身。
- 核心假设必须通过实验检验，不得在论文中当作已证明结论。

---

## 2. 模块地图

| 模块 | 职责 | 周期 | 文档 | 代码 | Unity 源文件 |
|---|---|---|---|---|---|
| CoverageField | 栅格化、障碍物 mask、检测概率模型、贝叶斯信念、cellRisk、指标 | 5–10 Hz | [01_belief_and_coverage_field.md](docs/01_belief_and_coverage_field.md) | [coverage_field.cs](code/coverage_field.cs) | `Assets/Scripts/Planning/PlannerPathPlanningService.cs` #region CoverageField |
| CoveragePlanner | K-means 聚类 + Hungarian 指派 + 目标选择 + A* 寻路（ExecuteReplan 编排） | ~12 s 重规划 | [02_planner_pipeline.md](docs/02_planner_pipeline.md) | [planner_orchestrator.cs](code/planner_orchestrator.cs) | 同上 #region CoveragePlanner |
| Human Anchor | RF 预测人控船目的地 → 固定聚类中心 → A* 避让 | 每次重规划 | [06_human_anchor.md](docs/06_human_anchor.md) | [kmeans.cs](code/kmeans.cs)（fixed-anchor 部分） | 同上 `ExecuteReplan` 第 2 步 |
| ReplanScheduler | 重规划触发调度（事件驱动 + rolling 兜底） | 每帧检查 | [07_replan_scheduler.md](docs/07_replan_scheduler.md) | [planner_orchestrator.cs](code/planner_orchestrator.cs)（scheduler 部分） | `Assets/Scripts/PathPlan.cs` |
| Path Execution | 航路点过滤、跟随、卡点检测、到达通知 | 每物理帧 | [08_execution.md](docs/08_execution.md) | [waypoint_filter.cs](code/waypoint_filter.cs) | `Assets/Scripts/PathPlan.cs` + `Assets/Scripts/WaypointFollower.cs` |
| Voice Anchor | 语音命令指定 USV 直达目标（跳过聚类） | 命令驱动 | [02_planner_pipeline.md](docs/02_planner_pipeline.md) §7 | [planner_orchestrator.cs](code/planner_orchestrator.cs) | `Assets/Scripts/PathPlan.cs` `SubmitVoiceCommand` |

## 3. 文件导航

```
algo/
├── README.md                        # 本文件：总览
├── source_map.md                    # algo 文件 ↔ Unity 源文件行号对照表
├── docs/
│   ├── 01_belief_and_coverage_field.md   # 栅格 / 检测模型 / 信念 / cellRisk / 指标（含公式）
│   ├── 02_planner_pipeline.md            # ExecuteReplan 全流程伪代码（9 步）
│   ├── 03_clustering_kmeans.md           # risk 加权 K-means（普通 / fixed-anchor 两种模式）
│   ├── 04_assignment.md                  # Hungarian 指派（代价模型 + 与 CONFIRMED 架构差异）
│   ├── 05_astar.md                       # 8 方向 A*、对角禁穿、human anchor 避让、投影
│   ├── 06_human_anchor.md                # RF human anchor（HRCDMS 机制）
│   ├── 07_replan_scheduler.md            # 重规划调度（3 触发源 + debounce/cooldown）
│   ├── 08_execution.md                   # 路径后处理 + WaypointFollower 执行模型
│   └── 09_config_reference.md            # PlannerRuntimeConfig / ProbabilityModelConfig 参数全表
└── code/
    ├── core_types.cs                     # 纯数据结构（无 Unity 依赖）
    ├── coverage_field.cs                 # 覆盖场
    ├── kmeans.cs                         # K-means
    ├── hungarian.cs                      # Hungarian
    ├── astar.cs                          # A*
    ├── planner_orchestrator.cs           # ExecuteReplan 编排 + 调度
    └── waypoint_filter.cs                # 航路点过滤（PathPlan 后处理）
```

## 4. 已知差异与开放问题（如实标注，不静默解决）

以下差异在对应文档中均有详细标注，供研究决策参考：

| # | 事项 | 当前 Unity 实现 | 仓库 CONFIRMED 要求 | 状态 |
|---|---|---|---|---|
| 1 | 指派顺序 | `clustering → Euclidean-Hungarian → A*` | `clustering → pairwise A* → path-dependent assignment → Hungarian` | **差异**。见 [04_assignment.md](docs/04_assignment.md) §4。迁移到 ROS 平台时需决策是否改为路径依赖指派 |
| 2 | 配置字段消费 | `rfAnchorShiftCells` / `anchorTtlSeconds` / `anchorEmaAlpha` / `rfAnchorAvoidanceCells` / `missingPathCooldownSeconds` / `unreachablePenalty` / `densityMode` 已定义但**未被规划代码消费** | — | 见 [09_config_reference.md](docs/09_config_reference.md) §3，标注"声明未消费" |
| 3 | A* 避让实现 | 人控船避让区域 = human cluster 自然形成的 `cellIndices`（无额外 dilation） | — | 与 `rfAnchorAvoidanceCells` 注释描述（1 圈 dilate）不一致；实际行为以代码为准 |
| 4 | 检测模型 | Pdetect 距离曲线（power/linear/exponential/flat）+ 时间衰减恢复 | `idea/` 中检测似然模型的最终确认形式 | 以本包 [01 文档](docs/01_belief_and_coverage_field.md) 描述的实现为准 |

## 5. 论文写作快速索引

| 论文需要 | 看这里 |
|---|---|
| 问题定义、系统架构图素材 | 本文档 §1 + [02_planner_pipeline.md](docs/02_planner_pipeline.md) §1 |
| 信念更新公式 | [01_belief_and_coverage_field.md](docs/01_belief_and_coverage_field.md) §3–§4 |
| 检测概率模型公式 | [01_belief_and_coverage_field.md](docs/01_belief_and_coverage_field.md) §2 |
| cellRisk 与覆盖指标定义（C80 / TotalRisk） | [01_belief_and_coverage_field.md](docs/01_belief_and_coverage_field.md) §5 |
| 聚类目标函数与固定中心语义 | [03_clustering_kmeans.md](docs/03_clustering_kmeans.md) §2–§3 |
| 指派代价函数 | [04_assignment.md](docs/04_assignment.md) §2 |
| A* 代价与避让机制 | [05_astar.md](docs/05_astar.md) §2 |
| human anchor 生成条件与 fail-closed | [06_human_anchor.md](docs/06_human_anchor.md) §2 |
| 重规划触发条件 | [07_replan_scheduler.md](docs/07_replan_scheduler.md) §2 |
| 性能指标（decisionMs / pathGenMax / km iterations） | [02_planner_pipeline.md](docs/02_planner_pipeline.md) §6 + [09_config_reference.md](docs/09_config_reference.md) §4 |
| 实验条件差异（AUTO_COVERAGE vs RF_ASSIST） | [06_human_anchor.md](docs/06_human_anchor.md) §5 |
