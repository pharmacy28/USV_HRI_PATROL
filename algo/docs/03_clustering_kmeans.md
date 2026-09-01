# 03 · 信念加权 K-means 聚类

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs`
> `WeightedKMeansWithFixedAnchor`（657–767 行）、`WeightedKMeansBasic`（770–832 行）
> 提炼代码：[code/kmeans.cs](../code/kmeans.cs)

## 1. 目标

把海域所有自由格划分为若干搜索分区（cluster），每个分区对应一艘自主 USV 的搜索责任区。
聚类权重用 **cellRisk = Pmiss × Belief**，使高漏检概率 × 高信念的格子对质心位置有更大吸引力——
即"信念感知"（belief-aware）的来源。

与仓库 `idea/研究决策状态.md` CONFIRMED 的 **Fixed-center semantics** 完全一致：

- 所有非障碍自由格**重新参与**每次聚类（不保留旧分区、不手工删除残余区域）；
- 固定中心保持不动，只更新自主中心；
- 人控预测目的地作为固定中心，其分区由聚类**自然形成**（不是预设几何区域）。

## 2. 两种模式

| 模式 | 触发条件 | 中心数 | center[0] |
|---|---|---|---|
| `WeightedKMeansWithFixedAnchor` | rfValid（RF 预测有效，见 [06](06_human_anchor.md)） | K+1 | human anchor（**固定**） |
| `WeightedKMeansBasic` | 无有效 RF 预测 | K | 普通中心（全部迭代） |

K = 参与覆盖的自主船数（不含人控船、语音命令船）。

## 3. 算法步骤（以 fixed-anchor 为例）

### 3.1 中心初始化

```text
centers[0] = (humanAnchor.centroidX, humanAnchor.centroidZ)          // 固定，永不更新
for i in 1..K:                                                        // 自主中心
    if !coldStart 且 i < |m_LastAutoCentroids|:
        centers[i] = m_LastAutoCentroids[i]                           // 热启动：上次质心
    else if i < |autoShips|:
        centers[i] = ship[i].pos + (±2·cellSize 均匀抖动)             // 冷启动：船位扰动
    else:
        centers[i] = 栅格内均匀随机格中心
```

`coldStart = (m_ReplanReason == "target_reached")`。
即：**target_reached 触发时冷启动（船位+抖动）**；rolling / missing_path / initial 等触发时热启动（沿用上次质心），保证分区随覆盖演进的连续性。

> 注意 `m_LastAutoCentroids` 的索引语义：fixed-anchor 模式下它只存 auto 质心（不含 human center），
> 热启动时与 autoShips 顺序对应（代码 `centers.Add(m_LastAutoCentroids[i])` 按 i 对齐）。

### 3.2 迭代（Lloyd 算法，risk 加权）

```text
freeCells ← 所有非障碍格，携带 (idx, col, row, risk=Pmiss·Belief, wx, wz)
assignments ← 每个自由格到最近中心的索引（欧氏距离²）
for iter in 1..maxIter(10):
    changed ← false
    for fc in freeCells:
        k ← argmin_k ‖fc − centers[k]‖²
        if assignments[fc] ≠ k: assignments[fc] ← k; changed ← true
    if !changed 且 iter > 0: break
    // 更新步：只更新 k ≥ 1（center[0] 固定）
    for k in 1..K:
        sumX[k] = Σ w·x,  sumZ[k] = Σ w·z,  sums[k] = Σ w
        w = max(risk, 1e-6)                          // 权重下限防零
        newCenter[k] = (sumX[k]/sums[k], sumZ[k]/sums[k])
    maxShift ← max_k |Δcenter[k]|（曼哈顿）
    if maxShift < tolerance(0.001): break
```

### 3.3 聚类结果构建

每个 cluster 记录：

| 字段 | 含义 |
|---|---|
| `clusterId` | fixed-anchor 模式：k=0 → −1（human），k≥1 → k−1（auto）；普通模式：k |
| `centroidX/Z, centroidCol/Row` | 加权质心（世界/栅格坐标） |
| `cellIndices` | 分区内全部自由格 flat index（**A* 避让与目标选择的作用域**） |
| `riskSum` | Σ cellRisk（分区总风险） |
| `beliefSum` | Σ Belief |
| `bestTargetCol/Row, bestTargetScore` | 分区内 cellRisk 最高格 |

## 4. 分区内目标选择（WeightedCentroidMedoid，默认 targetMode）

在分区内选一个自由格作为该船的 A* 目标：

```text
medoid = argmin_{cell ∈ cluster.cellIndices} ‖cellCenter − cluster.centroid‖²     // 离加权质心最近
候选集 = { cell ∈ cluster.cellIndices : ‖cellCenter − shipPos‖² ≥ 150² }           // 最短目标距离
if 候选集非空: target = argmin_{候选集} ‖cellCenter − centroid‖²                    // 优先满足距离约束
else if 全局存在满足 ≥150m 且离 centroid 最近的自由格: target = 该格                // TryFindGlobalFarCellNear
else: target = medoid（无距离约束的最近点）                                        // 最终降级
```

`MinTargetDistanceMeters = 150` 是硬编码常量（源码 1035 行）。动机：防止目标过近导致
"instant target_reached" 震荡。

## 5. 复杂度与参数

| 项 | 值 | 来源 |
|---|---|---|
| 最大迭代 | `maxKMeansIterations = 10` | PlannerRuntimeConfig |
| 收敛容差 | `kMeansTolerance = 0.001`（曼哈顿位移） | PlannerRuntimeConfig |
| 权重 | cellRisk（下限 1e-6） | 硬编码 |
| 冷启动抖动 | ±2·cellSize（即 `m_GridCellSize * 4 / 2`，均匀 ±2 格） | 硬编码 `m_Rng.NextDouble() − 0.5) * cellSize * 4` |
| 复杂度 | O(maxIter × N × K)，N = 自由格数 | — |

> 论文写作注意（AGENTS.md 科学纪律）：K-means 是标准组件。本系统的科学要点是
> **risk 加权重心 + 固定中心语义 + 热启动连续性**，以及 human anchor 固定中心如何
> 通过聚类**自然挤出**人控船附近区域并让自主舰队绕开，而非 K-means 本身。
