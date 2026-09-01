# 04 · USV–分区指派（Hungarian）

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs`
> `HungarianAssign`（840–928 行）、`SolveHungarian`（931–971 行）
> 提炼代码：[code/hungarian.cs](../code/hungarian.cs)

## 1. 问题形式

K 艘自主 USV（不含人控船、语音命令船）与 K 个搜索分区中心一一匹配，最小化总代价。
使用 O(n³) 标准 Hungarian（Jonker–Volgenant 风格增广路径实现，代码中为 1-indexed 潜势法）。

## 2. 代价矩阵（当前实现）

### 2.1 归一化

```text
maxDist = max_{i,j} ‖ship_i − centroid_j‖           // 全局最大船–中心欧氏距离
nd(i,j) = ‖ship_i − centroid_j‖ / maxDist           // 归一化距离
changed(i,j) = 1 若上次重规划 ship_i 的 cluster ≠ j，否则 0
```

### 2.2 TravelCostOnly（默认 assignmentMode）

```text
cost(i,j) = nd(i,j) + changed(i,j)·switchPenalty       // switchPenalty = 0.5
```

- `switchPenalty` 惩罚"换区"，抑制聚类热启动 + 指派联合导致的频繁责任区跳变。
- 上一轮 `ship_i → cluster` 记录于 `m_LastShipCluster`（每次 ExecuteReplan 末尾更新）。

### 2.3 LegacyMixedCost（旧模式，保留未删）

```text
clusterRiskMean[j] = riskSum[j] / |cellIndices[j]|              // 风险密度（防大面积分区靠面积取胜）
clusterBelief[j]   = beliefSum[j]
cost(i,j) = dw·nd(i,j) + rw·(1 − normRisk[j]) + bw·(1 − normBelief[j]) + changed(i,j)·switchPenalty
```

| 权重 | 默认 | 含义 |
|---|---|---|
| distanceWeight dw | 1.0 | 归一化距离 |
| riskWeight rw | 2.0 | 风险密度越高，代价越低（(1−normRisk)） |
| beliefWeight bw | 1.5 | 信念越高，代价越低 |

## 3. 求解

`SolveHungarian(cost, n)`：标准潜势（u, v）+ 交替路径实现，返回 `assignment[i] = j`。
源实现为 float 版（源文件 931–971 行逐行对应 [hungarian.cs](../code/hungarian.cs)）。

## 4. ⚠ 与仓库 CONFIRMED 架构的差异（重要）

仓库 `idea/研究决策状态.md` CONFIRMED 的 **Assignment architecture** 要求：

```text
belief-aware clustering
→ centers
→ pairwise obstacle-aware A* paths for eligible pairs     // 先为每个 (USV, center) 对算 A*
→ path-dependent assignment cost                          // 代价 = 路径长度等
→ Hungarian/equivalent optimal assignment
```

并明确将 `clustering → Hungarian → A*` 标记为**历史顺序，不得静默传播到实现或论文正文**。

**当前 Unity 实现仍是 `clustering → Euclidean-Hungarian → A*`**：

- 指派代价只依赖欧氏距离与切换惩罚（§2），**不依赖路径**；
- A* 在指派之后才计算，且只为最终配对的目标格计算（每个中心只算一次）；
- 障碍物对指派的影响仅通过聚类阶段（障碍格不参与聚类）间接体现。

差异的实践后果：

1. 两艘船欧氏距离相近但被障碍隔开时，指派可能"分配错误"（需绕远路的配对仍被选中）；
2. 计算量上当前实现更省（K 条 A* vs K² 条 A*），实测 decisionMs ≈ 20 ms 级别。

**处理状态：如实记录，未静默解决。** 是否在 Unity 侧重构为 path-dependent assignment、
或仅在 ROS 平台迁移时采用 CONFIRMED 架构，属于研究决策（paper 写作时若描述该顺序，
必须与最终实现的顺序一致）。

## 5. 语音/人控船的排除语义

- 人控船：不参与指派（步骤 1 已分离）；RF 预测时其目的地成为固定中心（clusterId=−1），
  该中心也**不参与**自主船指派（Hungarian 只匹配 autoClusters）。
- 语音命令船：跳过聚类与指派，直接定向 voice target（clusterId=−2），并在命令有效期内锁定。
- 上述"锁定人工配对、从自主重分配中排除"的语义与 `idea/研究决策状态.md` CONFIRMED
  的 Human collaboration 规则一致。
