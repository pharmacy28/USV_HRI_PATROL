# 通信状态

- 协议：`PROTOCOL v1` + `ROLE_PROTOCOL_v1_1`；更新时间：2026-10-20 15:55（Asia/Shanghai）。
- 通道：`CONNECTED`；当前工程任务：`USV-20261020-004`，Constructor **DONE / instructor REVIEW_PENDING**，不是 ACCEPTED。
- 最新通信报告：`docs/coordination/reports/USV-20261020-004.md`；本地详报：`src/workspace/reports/USV_20261020_004_B3_FALLBACK_REPORT.md`；Constructor 回执：`docs/coordination/receipts/constructor-20261020.md`。
- 002/SLIM-004D、003、003R 均已有 instructor 正式 ACCEPTED；其 review 位于 `docs/coordination/tasks/<task_id>.review.md`。004 尚无 review，不以本状态代签。

## USV-20261020-004 实际结果

- 生产 B3 fixed-center 门控已接线；无 SEARCH 无人工中心，有合法预测可用预测中心，缺失/非法预测回退当前合法艇位，当前位置也非法则不设人工中心。epoch/车辆/控制段/仿真时钟/空间校验及撤销清窗有生产路径离线测试；未改 belief、基础算法或科学 endpoint。
- 相关 162 项测试通过、必要 colcon build 与 source/install 身份核对通过。运行树无可用根 Git HEAD，实际源码以报告内 SHA256 追溯，实现提交 NONE；研究树/VRX 原有 dirty、world/model/log 原样保留。
- 唯一有界无 RF 模型 Gazebo run_id `f87fc7b8a1934a52ada1fbc1fd7d4828`：START→TAKEOVER（无中心）→SEARCH_ACTIVE→当前位 fallback（gen4，9 艘自主继续）→CANCEL（gen10 移除）→STOPPED/Recorder finalize。原始数据仅本地 `log/experiments/run_1792482001665000585/`。
- 本 run STOP 后 28 条 path-follower 状态在 27 秒墙钟内保持 stop barrier、10/10 control_modes idle；**20 路实际 thruster topic 未直接采集，NOT_OBSERVED**。第二次 ACTIVE 的 CLI 发出但未有 Recorder 接收记录；NAVIGATE/RELEASE 和 UI 点击本轮 NOT_OBSERVED。一次 smoke 配额已用尽，未补跑。
- 旧 003R run_id `5c84c3736225450eb5d0759cd1498f59` 的 20/20 推进器与 SEARCH/B2 时钟验收仍是它自己的历史证据，不当作 004 run 的直接测量。

## 研究与保护边界

H=5 s、已有 1-cell 重规划/到达参数和传感器 `engineering_assumed` 仅工程沿用；正式 H/年龄/阈值、R/τ/B、encounter 定义的数值、预测准确率、正式 B3 效果、RMST 未验证或仍 OPEN。D2/D3/D4 不在 004 实施范围。通信分支不含生产代码/原始大日志，不自动合并旧 platform/；instructor 决定 004 ACCEPTED/CHANGES_REQUESTED/BLOCKED。
