# 01 · 覆盖场：栅格、检测模型、贝叶斯信念与 cellRisk

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs` #region CoverageField（24–315 行）
> 提炼代码：[code/coverage_field.cs](../code/coverage_field.cs)

覆盖场（CoverageField）是规划的感知基础。它在内存中维护三个等长数组：

| 数组 | 含义 | 取值范围 |
|---|---|---|
| `Pmiss[i]` | 格 i 内存在目标但**未被发现**的概率（漏检概率） | [0, 1]，初始 1 |
| `Belief[i]` | 目标位于格 i 的后验信念（归一化） | [0, 1]，Σ = 1 |
| `ObstacleMask[i]` | 格 i 是否障碍（不可搜索） | bool |

核心密度：**cellRisk[i] = Pmiss[i] × Belief[i]**，同时驱动聚类权重、目标选择与覆盖指标。

---

## 1. 栅格化

- 栅格原点 = 场景区域包围盒左下角 `(originX, originY)`（XZ 平面）。
- `cellSize` = `probabilityModel.gridCellSize`（默认 50 m，下限 20 m）。
- 列/行数：`cols = ⌈width/cellSize⌉`，`rows = ⌈height/cellSize⌉`。
- 世界坐标 ↔ 栅格坐标（格中心）：

```text
col(x) = clamp(⌊(x − originX)/cellSize⌋, 0, cols−1)
row(z) = clamp(⌊(z − originY)/cellSize⌋, 0, rows−1)
cellCenterX(col) = originX + (col + 0.5)·cellSize
cellCenterZ(row) = originY + (row + 0.5)·cellSize
flatIndex = row·cols + col
```

## 2. 障碍物建模

输入障碍为轴对齐矩形 `ObcRect{x, y, width, height}`，统一转换为**圆形**（与路径后处理的碰撞语义一致）：

```text
circleCenter = (x + w/2, y + h/2)
circleRadius = max(w, h) / 2
finalRadius  = circleRadius + inflationRadius     // inflationRadius = probabilityModel.obstacleInflationRadius, 默认 80 m
```

格 i 被标记为障碍 ⇔ 格中心到圆心的距离 ≤ finalRadius。障碍格：`Pmiss` 不参与更新（保持 1 但从不被扫描/选择），`Belief = 0`，不可达、不可聚类、不可作为目标。

## 3. 检测概率模型（传感更新）

每帧（或每 `UpdateSearchProbabilities` 调用）对每艘船扫描其视野内的格子：

```text
对格 i（非障碍，距船 dist ≤ maxVisionRange）:
    pmc = Π_m (1 − Pdetect_m(dist))          // 多探测手段独立假设
    Pmiss[i] ← Pmiss[i] · clamp01(pmc)       // 乘法更新：多船多帧累积
```

### Pdetect 距离曲线

- 无自定义公式时（默认 power 曲线）：

```text
Pdetect(m, dist) = m.searchProb × (0.18 + 0.82·(1 − t^1.35)),   t = clamp01(dist / visionRange)
```

- 有 `detectorFormulas[scanType]` 时：

```text
Pdetect(m, dist) = clamp01(m.searchProb × gain × (edgeProbFactor + (1 − edgeProbFactor)·f(t)))
```

其中 `f(t)` 按 `distanceCurve` 选择：

| distanceCurve | f(t) |
|---|---|
| `flat` | 1 |
| `linear` | 1 − t |
| `power`（默认） | 1 − t^exponent（默认 exponent=1.35） |
| `exponential` | (e^(−λt) − e^(−λ)) / (1 − e^(−λ))（默认 λ=2.5） |

> 论文写作注意：该公式属于"检测/漏检似然模型"的工程实现（AGENTS.md Bayesian belief rule 要求概率化似然）。参数（gain、edgeProbFactor、exponent、λ）的物理/传感器依据需要在论文中说明来源（传感器标定、仿真设置等）。

## 4. 信念更新与时间衰减

### 时间衰减恢复（timeDecay）

若 `timeDecayPerHour > 0` 且 `pmissRecoveryBoostForDemo > 0`，模拟目标可能重新出现/环境变化导致的漏检概率回升：

```text
h = dt/3600
gamma = 1 − e^(−λ·h)        (mode=exponential | recovery_exponential)
      = min(1, λ·h)         (mode=linear | recovery_linear)
Pmiss[i] ← Pmiss[i] + (1 − Pmiss[i])·(boost·gamma)
```

默认 `timeDecayMode = "none"`，即关闭。

### 贝叶斯信念归一化

每次 Pmiss 更新后重算：

```text
Belief[i] = ObstacleMask[i] ? 0 : Pmiss[i] / Σ_{j∉obstacle} Pmiss[j]
```

初始状态：所有自由格 `Pmiss = 1`，故 `Belief[i] = 1/freeCellCount`（均匀先验）。

## 5. cellRisk 与覆盖指标

```text
cellRisk[i] = Pmiss[i] × Belief[i]
```

| 指标 | 定义 | 代码 |
|---|---|---|
| meanPmiss | (Σ Pmiss) / freeCellCount | `GetMeanPmiss()` |
| meanCoverage | 1 − meanPmiss | `GetMeanCoverage()` |
| **C80** | 覆盖率：满足 (1 − Pmiss) > 0.8 的自由格占比 | `GetC80()` |
| **TotalRisk** | Σ cellRisk = Σ Pmiss·Belief（规划目标函数的下界量） | `GetCoverageTotalRisk()` |

> C80 的阈值 0.8 是硬编码常量（`RefreshStats` 中 `1f - p > 0.8f`）。论文中需说明该阈值的选取依据或标注为工程设定。

## 6. 与规划器的接口约定

- 覆盖场**只做感知状态维护**，不做文件 I/O；记录由 `ExperimentRecorder` 旁路完成（不在本包范围）。
- 规划器（ExecuteReplan）从覆盖场读取：`Pmiss`、`Belief`、`ObstacleMask`（聚类的 cellRisk 权重、目标评分、A* 可行域）。
- 覆盖场从规划器外部接收：船舶列表（位置 + 探测手段）、时间步长、障碍物变更（`ApplyObstacles`）。
