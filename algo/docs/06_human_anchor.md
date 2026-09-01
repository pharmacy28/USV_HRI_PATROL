# 06 · RF Human Anchor（HRCDMS 人机协同机制）

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs` `ExecuteReplan` 步骤 2（422–457 行）
> RF 预测来源：`Assets/Scripts/Intent/RFNextPointAssist/RFNextPointRuntime.cs`（本包抽象为 `IHumanIntentSource`）

## 1. 机制总览

Human Anchor 是 HRCDMS（Human-Robot Collaborative Decision-Making System，实验条件名
`RF_ASSIST`）的**唯一**规划侧改动：

```text
RF 模型预测人控船的下一目的地（极坐标 r, θ + 置信度）
  → 预测点投影到最近自由格
  → 该格作为固定聚类中心（clusterId=−1，isHumanAnchor=true）
  → 其余 K 个自主中心在其周围重新聚类（fixed-anchor K-means）
  → human cluster 的格集成为非人控船 A* 的临时避让区
```

**语义**（与 `idea/研究决策状态.md` 一致）：预测的是**人类干预的未来空间后果**
（人控船即将前往的区域），不是"目标存在证据"——预测**不修改** Pmiss/Belief，
只通过聚类固定中心与 A* 避让影响自主舰队的责任区划分。

## 2. 生成条件（fail-closed 条件链）

以下条件**全部满足**才生成 human anchor，任一不满足则静默回退普通 K-means：

```text
1. PlannerRuntimeConfig.enableHumanAnchor = true       // 实验条件 RF_ASSIST
2. 存在人控船（contextManualShip 或船列表中 IsHandControl=true）
3. rf.CurrentMode = "RF_ASSIST"                        // fail-closed: AUTO 模式绝不生成
4. rf.IsPredictionValid                                // 最近一次推理有有效组件
5. rf.Confidence ≥ rfAnchorConfidenceThreshold         // 默认 0.3
6. 预测点投影 FindNearestFreeCell 成功
```

预测点世界坐标：

```text
hx = humanShip.x + PredictedDistance · cos(PredictedAngleDeg · π/180)
hz = humanShip.y + PredictedDistance · sin(PredictedAngleDeg · π/180)
```

`m_LastHumanIntent` 同时记录（valid、预测点、投影格、置信度、模式），供记录层
（`ExperimentRecorder` / `planned_paths.jsonl` 的 rf/hac/har 字段）与验证脚本
（`validate_rf_assist.py`）核对。

## 3. 对下游的影响

| 下游环节 | human anchor 有效时 | 无效时 |
|---|---|---|
| 聚类 | K+1 中心 fixed-anchor K-means（center[0] 固定） | K 中心普通 K-means |
| 指派 | 只匹配 K 个 auto cluster | 同左 |
| A* | 非人控船避开 human cluster 格集（临时障碍） | 无避让 |
| 目标选择 | 自主船目标仍在其 auto cluster 内（不受 human cluster 影响） | 同左 |
| 指标 | `rfInfluenced` / `rfx,rfz,hac,har` 记录字段激活 | 字段为 false/空 |

**关键性质**：human anchor 区域由聚类**自然形成**——fixed center 吸引附近自由格，
分区边界由 risk 加权距离竞争决定，不存在手工几何圈定。

## 4. RF 预测模块接口（本包抽象）

本包不包含 RF 训练/推理实现（属 `tools/intent_rf/` 与 `RFNextPoint*`），只依赖接口：

```csharp
public interface IHumanIntentSource
{
    string CurrentMode { get; }            // "RF_ASSIST" | "AUTO" | ...
    bool IsPredictionValid { get; }
    HumanIntentPredictionData LastPrediction { get; }   // {PredictedDistance, PredictedAngleDeg, Confidence}
}
```

Unity 侧实现：`RFNextPointRuntime`（特征 10 维 × 4 统计量 = 40 维，随机森林，
`Assets/StreamingAssets/RFModels/RF_N/model.json`）。

## 5. 实验条件对照

| 条件 | enableHumanAnchor | RF 模式 | 聚类 | A* 避让 |
|---|---|---|---|---|
| AUTO_COVERAGE（No HRCDMS） | false | — | K-means(K) | 无 |
| RF_ASSIST（HRCDMS） | true | RF_ASSIST | fixed-anchor K-means(K+1) | human cluster 格集 |

两条条件共用同一底层规划代码路径（同一个 ExecuteReplan），差异仅由配置开关产生——
这是"唯一差异为 human anchor 是否启用"实验设计的实现保证。

## 6. 论文写作注意

- 核心假设（CONFIRMED，待检验）：*"Predicting the future spatial consequence of human
  intervention and fixing that predicted destination during belief-driven re-clustering
  allows the remaining autonomous USV fleet to proactively redistribute search
  responsibility."*
- 假设的检验依据是实验数据（如 `validate_rf_assist.py` 的 humanCluster 避让、fleet
  health、ri linkage 检查与 `boxplot_nasa_tlx_duration.py` 的组间对比），算法文档本身
  不构成证据。
- RF 预测（随机森林）是标准组件；贡献点在于**预测结果如何进入规划闭环**（固定中心
  + 自然分区 + A* 避让 + fail-closed 条件链），而非模型结构。
