# 05 · A* 避障寻路

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs` `BuildAStarPath`（1180–1298 行）
> 提炼代码：[code/astar.cs](../code/astar.cs)

## 1. 定位

为每艘自主船生成"当前位置 → 分区目标格"的栅格级避障路径。
路径输出为世界坐标点列（第 1 点始终是真实船位，随后是经过的格中心，最后是目标）。

## 2. 搜索图与代价

| 项 | 定义 |
|---|---|
| 节点 | 非障碍格 (col, row) |
| 邻域 | 8 方向（4 直角 + 4 对角） |
| 步进代价 g | 直角 10，对角 14（≈√2×10 的整数近似） |
| 启发式 h | `10 × Manhattan(col,row → target)`（一致启发式） |
| open set | `SortedSet<(f, g, col, row)>`（按 f 排序，取出 Min） |
| 迭代上限 | `maxIter = cols × rows × 2`（防御性上限，正常情况远不触达） |

## 3. 对角禁穿角

对角移动前检查两个相邻直角格：`(cc, nr)` 与 `(nc, cr)` 任一为障碍则禁止该对角移动。
防止路径斜穿两个障碍格之间的缝隙（源文件 1279–1283 行）。

## 4. Human anchor 避让（HRCDMS 特有）

```text
if usvId ≠ m_HumanAnchorManualId 且 避让格集合非空:
    将 humanCluster.cellIndices 全部临时置为障碍（记录原值 avoidBackup）
... A* 搜索 ...
恢复 avoidBackup 中原值（成功与失败路径都恢复）
```

- 避让区域 = human cluster **聚类自然形成的分区**（`cellIndices`），不是预设几何区域；
- 人控船自己（usvId = m_HumanAnchorManualId）**不避让**该区域（人控船由人驾驶，无路径约束）；
- 仅当 rfValid（RF_ASSIST 模式 + 预测有效）时避让区域非空；AUTO_COVERAGE 条件下为空集，A* 行为与无 HRCDMS 完全一致；
- 配置字段 `rfAnchorAvoidanceCells`（注释称 1 圈 dilation）**当前未在 A* 中消费**——实际避让区域就是 cluster 原始格集，无膨胀。见 [09_config_reference.md](09_config_reference.md) §3。

## 5. 起终点投影

若起点格或目标格被障碍覆盖（船已驶入 inflated 区 / 目标格刚被新障碍覆盖）：

```text
投影目标 = FindNearestFreeCell(worldPos)      // 以所在格为中心的环形搜索，找最近非障碍格
路径第 1 点 = 真实船位（始终保留）            // 逃逸段：船先驶出障碍区
路径追加     = 投影起点格中心（若发生投影）
路径末尾     = 原目标世界坐标（未投影时）
```

投影发生时会打日志（`[A*] projection: startProj=... targetProj=...`）。

## 6. 失败与降级链

```text
BuildAStarPath 返回 null（不可达）
  → ExecuteReplan: 该船 reachable=false, m_AStarFailCount[usvId]++
  → 下次重规划: failCount ≥ MaxAStarRetries(3)
      → SelectGlobalBestTarget（全局最高 risk·rw − 0.25·dw·normDist 自由格）
      → 仍失败则继续计数，循环直到可达到达
```

同时 `missingPathCount++`，性能快照记录 `astarFailCount`。船在无路可走期间由 ReplanScheduler
的 missing_path 触发尽快重规划（见 [07](07_replan_scheduler.md)）。

### 已知边缘行为（真实实现固有，非 bug）

当船本身位于 human cluster 避让区**凹口**时：起点投影（FindNearestFreeCell）选中的格
其 8 邻域可能全部落在避让区内 → A* 以 expanded=1 立即失败。此时即使连败降级到全局目标
仍失败（起点被困，与目标无关）。脱困机制依赖：

1. 每轮重规划 human cluster 重新聚类，分区形状改变，船可能脱离凹口；
2. missing_path 触发频繁重规划，加速上述过程。

该行为已用提炼代码冒烟测试复现（船挤在 human anchor 附近时 5 轮全失败；船分散部署时
rfValid 分支 4 轮全部正常）。论文若讨论 HRCDMS 的鲁棒性，此边缘情况值得说明。

## 7. 路径几何后处理

A* 输出的格中心折线在 `PathPlan.ConvertPlannerPathToWaypoints` 中进一步过滤（见
[08_execution.md](08_execution.md) §2）：丢弃落入障碍安全圈的点、截断与障碍相交的线段。
因此最终 WaypointFollower 收到的路径是"栅格 A* + 连续空间安全过滤"的复合结果。

## 8. 复杂度

| 项 | 值 |
|---|---|
| 最坏复杂度 | O(cols·rows·log(cols·rows))（SortedSet 实现；实际远低于上界，实测单船毫秒级） |
| 实测指标 | `astarExpandedNodesTotal/Max`（性能快照）；`pathGenMaxMs`（单船最久） |
| 网格规模示例 | 4 km × 4 km 海域 + 50 m 格 = 80×80 = 6400 格 |

> 论文写作注意：A* 是标准组件，不是贡献点。值得论文描述的是其**集成语义**：
> human anchor 区域如何临时进入障碍语义（`ObstacleMask` 临时修改 + 恢复）、
> 起终点投影的逃逸段处理、连续失败的目标降级链。
