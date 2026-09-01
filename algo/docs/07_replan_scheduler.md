# 07 · 重规划调度（ReplanScheduler）

> 源实现：`Assets/Scripts/PathPlan.cs`（351–436 行）
> 提炼代码：[code/planner_orchestrator.cs](../code/planner_orchestrator.cs)（scheduler 部分）

## 1. 定位

决定"何时触发一次舰队级重规划"。每次重规划都执行完整的 ExecuteReplan 管道（[02](02_planner_pipeline.md)）。
调度器每帧检查，事件驱动 + rolling 兜底，**不使用全局 cooldown 吞事件**。

## 2. 三种触发源

### 2.1 target_reached（船到点，debounce 合并）

```text
WaypointFollower 到达终点 → PathPlan.NotifyTargetReached(ship)
  → ship 加入 m_ReachedShips
  → m_ScheduledReplanTime = min(当前计划时间, now + 1.5s)     // ReplanDebounce = 1.5
每帧检查: 若 now ≥ m_ScheduledReplanTime 且 m_ReachedShips 中确有 finished 船
  → TriggerFleetReplan("target_reached")
```

- 1.5 s 合并窗口：多船几乎同时到点时只触发一次舰队重规划；
- 触发前复核 follower 确实 `IsFinished`（防止船已领新路径的误触发）。

### 2.2 missing_path（有船无路可走）

```text
AnyAutoShipNeedsPathRefresh():
    存在自主船（非人控、非寻获目标状态）且满足任一:
      follower 未启用 / 无可用航路点 / 已 finished 且无下一航路点
→ 满足且 now − m_LastFleetReplanTime ≥ minReplanCooldownSeconds(4s)
  → TriggerFleetReplan("missing_path")
```

手动切换船（`ProduceNewPathAgain(isEnter)`）、目标寻获/丢失（`FindTarget` / `LostTarget`）、
手动退出（`m_ManualJustExited` 抑制重复 initial）也走 missing_path 触发。

### 2.3 rolling（周期兜底）

```text
m_RollingReplanTimer += Δt
若 timer ≥ replanIntervalSeconds(12s) 且距上次 ≥ minCooldown(4s)
  → TriggerFleetReplan("rolling")
```

滚动重规划保证覆盖场随传感更新持续演进（即使没有船到点、没有路径缺失）。

### 2.4 其他触发（命令驱动）

| reason | 场景 |
|---|---|
| `initial` | 仿真启动，所有船进入自动驾驶后的首次规划 |
| `voice_command` / `voice_arrived` / `voice_expired` | 语音命令接受 / 到达 / 超时（见 [02](02_planner_pipeline.md) §7） |

## 3. TriggerFleetReplan 执行序列

```text
TriggerFleetReplan(reason):
    planner.SetReplanReason(reason)             // 冷/热启动分支与日志归因
    m_ReachedShips.Clear(); m_ScheduledReplan = false
    m_RollingReplanTimer = 0
    m_LastFleetReplanTime = now
    CollectShipsForReplan(exclude=m_CurShouDong)  // 收集自主船（排除人控船、寻获目标船）
    ProduceNewPathAgain()
      → 构建 PlannerParam（含 m_contextManualShip）
      → GeneratePlan → ExecuteReplan（聚类/指派/A*）
      → 每船: ConvertPlannerPathToWaypoints（过滤）
      → AssignWaypointsToFollower（最短路径阈值/rolling 保留旧路径，见 08 文档 §3）
```

## 4. 参数

| 参数 | 默认 | 位置 | 消费状态 |
|---|---|---|---|
| `ReplanDebounce` | 1.5 s | 硬编码 const | ✓ 消费 |
| `replanIntervalSeconds` | 12 s | PlannerRuntimeConfig | ✓ 消费 |
| `minReplanCooldownSeconds` | 4 s | PlannerRuntimeConfig | ✓ 消费 |
| `missingPathCooldownSeconds` | 5 s | PlannerRuntimeConfig | ✗ **未消费**（代码用 minReplanCooldownSeconds 做所有 cooldown） |

## 5. 设计性质（论文可引用）

- 事件驱动（to-point / no-path）保证响应性，rolling 保证覆盖率持续演进；
- debounce 合并 + cooldown 下限防止重规划风暴（避免每次到点都全舰队重算）；
- 每次重规划 reason 显式传递（`SetReplanReason`），冷/热启动策略、日志、性能快照
  （`replanReason` 字段）与实验分析可完整归因；
- 重规划期间船沿旧路径继续行驶，新路径经 `AssignWaypointsToFollower` 的保留策略平滑切换
  （见 08 文档 §3），避免路径跳变。
