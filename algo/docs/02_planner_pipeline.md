# 02 · 规划管道：ExecuteReplan 全流程

> 源实现：`Assets/Scripts/Planning/PlannerPathPlanningService.cs` `ExecuteReplan`（363–649 行）
> 提炼代码：[code/planner_orchestrator.cs](../code/planner_orchestrator.cs)

## 1. 定位

`ExecuteReplan` 是覆盖规划的单次执行入口，被 `GeneratePlan` 调用。每次重规划完成一次
"感知状态 → 聚类 → 指派 → 目标 → 路径"的完整决策，输出每艘自主船的航路点列表。

**两个实验条件的唯一差异**：`enableHumanAnchor`（F2 面板 / `experiment_ui_config.json` 控制）。
- `AUTO_COVERAGE`（无 HRCDMS）：enableHumanAnchor=false → 普通 K-means，无 human cluster。
- `RF_ASSIST`（HRCDMS）：enableHumanAnchor=true → 条件满足时 fixed-anchor K-means。

底层规划完全相同，不存在第二套业务逻辑。

## 2. 输入输出

| 输入 | 说明 |
|---|---|
| `allShips` | 全部船舶（含人控船），`ShipDes{m_id, m_x, m_y, m_scan_methods, IsHandControl}` |
| `obstacles` | `List<ObcRect>`（经 `ApplyObstacles` 已同步到障碍 mask） |
| `contextManualShip` | 当前人控船（`ShipDes?`），**必须 `IsHandControl=true` 才生效**（防御脏数据） |
| 覆盖场 | `Pmiss / Belief / ObstacleMask`（上一轮感知结果） |
| RF 预测 | `IHumanIntentSource`（RFNextPointRuntime 的抽象，见 [06](06_human_anchor.md)） |

| 输出 | 说明 |
|---|---|
| `PathPlan.m_paths` | usvId → `List<Vector2>` 航路点（A* 结果，含真实船位起点） |
| `m_Assignments` | 每船指派详情（clusterId、目标格、reachable、cachedPath） |
| `m_NavigationRecords` | 本轮全部 NavigationWaypoint（含不可达船的记录） |
| `PlannerPerfSnapshot` | 性能诊断（decisionMs、kMeansMs、astarMs 等） |

## 3. 伪代码（与源码 9 步一一对应）

```text
ExecuteReplan(allShips, obstacles, contextManualShip):
  ri ← m_ReplanIndex                          // 本轮重规划编号
  // ── 步骤 1：分离船舶 ──
  humanShip ← contextManualShip 若 IsHandControl，否则从 allShips 找 IsHandControl 者
  autoShips ← allShips − humanShip
  voiceShip ← voiceAnchor 有效且指向的自动船（从 autoShips 移出）
  coverageShips ← autoShips − voiceShip
  K ← |coverageShips|
  if K = 0 且无 voiceShip: 清空 assignments，ri+1，返回

  // ── 步骤 2：RF human anchor（fail-closed，见 06 文档）──
  humanCluster ← null
  if enableHumanAnchor 且 humanShip 存在 且 rf.CurrentMode = "RF_ASSIST"
     且 rf.IsPredictionValid 且 rf.Confidence ≥ rfAnchorConfidenceThreshold(0.3):
      hx ← humanShip.x + PredictedDistance·cos(PredictedAngleDeg)
      hz ← humanShip.y + PredictedDistance·sin(PredictedAngleDeg)
      nearest ← FindNearestFreeCell(hx, hz)      // 投影到最近自由格
      if nearest 存在:
          rfValid ← true
          humanCluster ← {clusterId=−1, isHumanAnchor=true, centroid=nearest}

  // ── 步骤 3：聚类 ──
  if rfValid:
      clusters ← WeightedKMeansWithFixedAnchor(K+1, coverageShips, humanCluster)
      //   center[0]=human anchor 固定；center[1..K] 迭代
      humanClusterResult ← clusters[0]
      autoClusters ← clusters[1..K]
      m_HumanAnchorAvoidCells ← humanClusterResult.cellIndices   // A* 避让区域（聚类自然形成）
  else:
      autoClusters ← WeightedKMeansBasic(K, coverageShips)        // 无 fake humanCluster
      清空避让区域

  // ── 步骤 4：Hungarian 指派 ──
  autoClusters[i].clusterId ← i（0 起连续）
  assignments ← HungarianAssign(coverageShips, autoClusters)     // 见 04 文档

  // ── 步骤 5：语音命令定向（跳过聚类）──
  if voiceActive:
      ProjectVoiceAnchorOutsideAvoidance()                        // 目标落障碍/避让区→最近允许格
      assignments += voiceAssignment(clusterId=−2, 目标=voice target)

  // ── 步骤 6：分区内目标选择 ──
  for a in assignments (非 voice):
      failCount ← m_AStarFailCount[usvId]
      if failCount ≥ 3: SelectGlobalBestTarget(a)                 // 连败降级：全局最高 risk
      else: SelectTargetInCluster(a, cluster)                     // 默认 WeightedCentroidMedoid
      a.reachable ← 目标格非障碍

  // ── 步骤 7：逐船 A* + 导航点记录 ──
  for a in assignments:
      nw ← NavigationWaypoint{ri, usvId, clusterId, target, reachable, ...}
      if a.reachable:
          path ← BuildAStarPath(shipPos, a.targetWorld, usvId)    // 见 05 文档
          if path ≠ null: a.cachedPath ← path; 失败计数清零
          else: a.reachable ← false; 失败计数+1                   // ≥3 次 → 下次全局目标
      m_NavigationRecords += nw

  // ── 步骤 8：性能快照 ──
  m_LastPerfSnapshot ← {ri, reason, decisionMs, kMeansMs, assignmentMs, astarMs,
                        pathGenMaxMs, astarExpandedNodesMax, ...}

  // ── 步骤 9：状态维护 ──
  m_Clusters ← [humanClusterResult?] + autoClusters
  m_LastCompletedReplanIndex ← ri
  m_ReplanIndex ← ri + 1
  m_LastAutoCentroids ← autoClusters 质心列表      // 下次热启动用
  m_LastShipCluster ← usvId → clusterId            // 下次切换惩罚判断用
```

## 4. GeneratePlan 与 cachedPath（双重 A* 消除）

`GeneratePlan(param)` 调用 `ExecuteReplan` 后**直接复用**每艘船的 `cachedPath`：

```text
for a in assignments:
    if a.reachable 且 a.cachedPath 非空:  path ← a.cachedPath
    else: path ← BuildAStarPath(...)  // fallback（正常情况下不发生）
          m_FallbackAStarCount++     // 性能快照可观测该计数
```

`cachedPath` 标记 `[NonSerialized]`，是 ExecuteReplan 内部 A* 的唯一结果；历史版本曾在
GeneratePlan 中重算一次（双重 A*），现已消除。

## 5. 两种目标选择模式

`targetMode` 决定步骤 6 的评分函数：

| targetMode | 评分 | 说明 |
|---|---|---|
| `WeightedCentroidMedoid`（**默认**） | 距 cluster 加权质心最近 | 且满足 ≥150 m 最短目标距离约束（不足时全局搜索，再不足降级最近点）。详见 [03](03_clustering_kmeans.md) §4 |
| `LegacyBestRisk` | `rw·risk + bw·belief − tw·normDist` | 旧三权重评分，tw = distanceWeight×0.5 |

A* 连续失败 ≥3 次时**无论何种模式**都走 `SelectGlobalBestTarget`：
`score = rw·risk − 0.25·dw·(dist/maxD)` 全局扫描最高分自由格。

## 6. 性能快照字段（论文指标来源）

`PlannerPerfSnapshot`（[core_types.cs](../code/core_types.cs)）：

| 字段 | 含义 | 论文用途 |
|---|---|---|
| `replanIndex / replanReason` | 重规划序号与触发原因 | 时间序列分析 |
| `decisionMs` | 单次重规划总耗时（GeneratePlan 计时） | 决策时延指标 `dm` |
| `kMeansIterations / kMeansMs` | K-means 迭代次数/耗时 | 算法开销 |
| `assignmentMs` | Hungarian 耗时 | 算法开销 |
| `astarMs / pathGenTotalMs` | 所有自动船 A* 总耗时 | 路径生成开销 `pgTotal` |
| `pathGenMaxMs` | 单船 A* 最久耗时 | `pgMax` |
| `astarExpandedNodesTotal / Max` | A* 扩展节点总数/最大值 | 搜索复杂度 |
| `astarPathCount / astarFailCount` | 成功/失败路径数 | 鲁棒性 |
| `fallbackAStarCount` | cachedPath 缺失的 fallback 次数 | 应恒为 0（诊断） |
| `missingPathCount` | 不可达目标数 | 鲁棒性 |

> CLAUDE.md 记录：HRCDMS 组实测 `dm` ≈ 20.8 ms（均值），No HRCDMS 组 ≈ 18.6 ms；决策周期默认 12 s，故决策开销远小于规划周期，实时性满足。

## 7. 语音命令（Voice Anchor）

语音命令（`SubmitVoiceCommand` → `SetVoiceAnchor`）给指定 USV 一个**固定任务目标**：

- 目标格 = 命令世界坐标的最近自由格；命令有效期间该船**跳过聚类与指派**直接定向（clusterId=−2）。
- 与其他船的 A* 避让关系：voice 目标若落在 human cluster 避让区或障碍内 → 投影到最近允许格。
- 生命周期：到达 100 m 内 → `arrived`；超时 120 s → `expired`。两者都清除 anchor 并触发重规划。
- 被语音指定的 USV 必须是自主船（人控船拒绝）；命令期间被锁定，不参与自主重分配。
- 与 RF human anchor 的区别：voice anchor 是**任务约束**（人直接命令目的地），human anchor 是**安全避让**（预测区域，非人控船避开），两者语义不同，代码中字段完全分离。

## 8. 关键防御逻辑（实现细节）

| 防御 | 位置 | 行为 |
|---|---|---|
| fail-closed | 步骤 2 | RF 模式 ≠ "RF_ASSIST" 或预测无效 → **绝不生成** human anchor |
| 人控上下文校验 | 步骤 1 | `contextManualShip` 必须 `IsHandControl=true`，否则从船列表重找或跳过 |
| voice 目标船校验 | 步骤 1 | voice 指向的船必须存在于自主船列表，否则忽略该 anchor |
| A* 连败升级 | 步骤 6–7 | 同一船连续 3 次 A* 失败 → 目标选择降级到全局最高 risk 格 |
| K=0 早退 | 步骤 1 | 无自主船且无 voice 船 → 直接返回，不产生空规划 |
| 避让区域临时性 | BuildAStarPath | human anchor 避让格在每次 A* 前临时置障碍、**结束后恢复**（avoidBackup） |
