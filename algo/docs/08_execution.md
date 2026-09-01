# 08 · 路径执行：航路点过滤与 WaypointFollower

> 源实现：`Assets/Scripts/PathPlan.cs`（619–764 行、674–711 行）、`Assets/Scripts/WaypointFollower.cs`
> 提炼代码：[code/waypoint_filter.cs](../code/waypoint_filter.cs)

## 1. 定位

A* 输出的是栅格格中心折线。从"栅格路径"到"实际执行"之间还有两个环节：

1. **航路点过滤**（`ConvertPlannerPathToWaypoints`）：连续空间安全校验，剔除靠近障碍的点；
2. **跟随执行**（`WaypointFollower`）：推力限速动力学模型驱动船体逐点行进。

## 2. 航路点过滤

### 安全边际配置

```text
baseMargin = probabilityModel.obstacleInflationRadius（>0 时），否则 cellSize×1.0
m_WaypointObstacleSafetyMargin = max(25, baseMargin)                       // 点障碍检查（默认 80）
m_WaypointSegmentSafetyMargin = max(点边际, baseMargin + max(10, cellSize×0.25))  // 线段检查（默认 92.5）
```

### 过滤规则（顺序执行）

```text
for 路径点 i:
    if i == 0: 保留（真实船位，即使船在 inflated 区内）         // 逃逸段起点
    if 点落入任一圆形障碍安全圈（半径 = r + 点边际）: 丢弃
    if 与上一保留点距离 < 0.1 m: 丢弃                          // 去重
    if i > 1 且 线段(上一保留点 → 本点)与圆形障碍相交（半径 = r + 线段边际）: 截断，停止追加
    保留
```

线段相交用 `SegmentIntersectsCircleXZ`（点到线段最近点 ≤ 半径，投影参数 clamp 到 [0,1]）。

### 最短路径阈值与滚动保留

`AssignWaypointsToFollower`（源 674–711 行）的两条切换规则：

```text
if 过滤后点数 ≤ 2 且总长 < MinAssignedPathLength(100 m):
    保留旧路径（防止 instant target_reached 循环）
if reason == "rolling" 且 follower 正在执行 且 旧路径剩余 > 2 点:
    保留旧路径（防止滚动重规划频繁打断航行）
否则: follower.SetWaypoints(新路径)
```

> rolling 保留规则的动机：滚动重规划周期（12 s）内船往往未走完旧路径；若每次都强切新路径，
> 会不断打断长距离航行。而 target_reached / missing_path / manual_switch 必须接新路径
> （旧路径可能穿越新 human cluster 区域）。

## 3. WaypointFollower 运动模型

### 起点选择（SetWaypoints）

```text
新路径下发给 follower 后，从"最靠近船且在船头前方"的点开始:
score(i) = dist(i) − dot(方向i, 船头)×5
bestIdx = argmin_i score(i)（要求 dist > 0.5×reachRadius）
若起点已在到达半径内 → 直接跳到下一索引
```

### 每物理帧控制（FixedUpdate）

```text
target ← waypoints[currentIndex]（水平面投影）
toTarget ← target − pos; dist ← ‖toTarget‖

卡点检测: 若 dist ≥ reachRadius 且 dist ≥ 0.95×上次dist 持续 3 s
    → 跳过当前航路点（currentIndex++），重置计时

到达判定: dist ≤ waypointReachRadius(8 m)
    → currentIndex++
    → 到达末尾且 loop=false: finished=true，水平速度清零，
      若船非人控 → PathPlan.NotifyTargetReached(船)     // 触发调度器

速度控制（未到达时）:
    speedFraction = clamp01(dist / waypointSlowdownDist(15 m))       // 减速接近
    desiredSpeed  = max(0.3×maxSpeed, maxSpeed×speedFraction)        // 最低 30% 巡航
    velocity ← MoveTowards(当前水平速度, direction×desiredSpeed, moveForce×Δt)   // 加速度限幅
```

| 参数 | 默认 | 说明 |
|---|---|---|
| maxSpeed | 8 m/s | 巡航速度 |
| moveForce | 50 | 加速度限幅（Δv = 50×Δt） |
| waypointReachRadius | 8 m | 到达半径（从 0.5 调大防 overshoot） |
| waypointSlowdownDist | 15 m | 减速距离 |
| lookAheadDistance | 20 m | 前瞻（字段保留，当前实现为最近点+减速模型） |
| 卡点超时 | 3 s | 距离不下降 95% 阈值 |

## 4. 闭环终点

```text
WaypointFollower 到达 → NotifyTargetReached
  → ReplanScheduler debounce 1.5 s
  → TriggerFleetReplan("target_reached")
  → ExecuteReplan（聚类热/冷启动取决于 reason）
```

覆盖循环由此闭合（感知 → 规划 → 执行 → 到达 → 再规划）。

## 5. 论文写作注意

- 运动模型是简化动力学（加速度限幅 + 限速 + 减速接近），**不是**真实 USV 水动力模型；
  论文若讨论仿真保真度需说明该简化（ROS 平台侧另有 Gazebo 物理仿真）。
- 卡点检测（3 s / 95%）与到达半径（8 m）等常量为工程调参结果，引用时标注为工程设定。
