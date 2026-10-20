# 通信状态

- 协议：`PROTOCOL v1` + `ROLE_PROTOCOL_v1_1`；更新时间：2026-10-20（Asia/Shanghai，004R2领取）（Asia/Shanghai）。
- 通道：`CONNECTED`；当前工程任务 `USV-20261020-004R2`（RECEIVED/PRE-FLIGHT，尚未运行）；上游004 instructor review **CHANGES_REQUESTED**（`docs/coordination/tasks/USV-20261020-004.review.md`）。Constructor 已完成004定向离线修正/构建回传；004R唯一Gazebo会话在START前因临时动作脚本服务类型错误而阻断；004不是ACCEPTED。
- 最新通信报告：`docs/coordination/reports/USV-20261020-004.md`（原报告保留，尾部追加返工证据）；本地增量详报：`src/workspace/reports/USV_20261020_004_OFFLINE_R1.md`；原本地详报：`src/workspace/reports/USV_20261020_004_B3_FALLBACK_REPORT.md`。Constructor 回执：`docs/coordination/receipts/constructor-20261020.md`。
- 002/SLIM-004D、003、003R 均已有 instructor 正式 ACCEPTED；004 返工不追溯撤销它们。004R一次Gazebo额度已消耗且review=BLOCKED，报告`docs/coordination/reports/USV-20261020-004R.md`；instructor另发唯一004R2 READY，要求隔离驱动预检先PASS/回执后才可最多一次新Gazebo。005仅DRAFT，未并发实施。

## USV-20261020-004 当前证据

- 修复前唯一 Gazebo run_id `f87fc7b8a1934a52ada1fbc1fd7d4828`：TAKEOVER 无中心、SEARCH_ACTIVE 后无模型当前位 fallback/9 艘自主继续、CANCEL 移除、STOPPED/Recorder finalize。原始证据仅本地 `log/experiments/run_1792482001665000585/`；该运行**不能**证明最终离线返工源码。
- 修复前未直接采集 20 路实际推进器；本 run STOP 后 28 条 follower 状态的 stop barrier/10 艘 idle 只是间接安全证据。第二次 ACTIVE/NAVIGATE/RELEASE/UI 亦 NOT_OBSERVED，不能借旧 003R 的 20/20 数据补成 004 直接 PASS。
- 最终 Planner 对无源身份 Twist/gaze 不用接收时间冒充当前段采集身份；手控 Twist 仍可执行，RF 缺可核验源身份则保守回退。Fleet pose 按当前 epoch/艇/段源时间水位拒绝倒退/同戳冲突，保留最近合法 pose、完全相同输入幂等，终态/切段清窗。有效预测只在显式可信 fixture 下有离线生产路径证据，不宣称当前 ROS 输入已有来源认证。
- 旧实现新增反例失败后修复；最终相关回归 **166 passed、0 skip**，受影响 package colcon build PASS；Planner source/build SHA256 `ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`。运行工作区无根 Git HEAD，实现提交 NONE；研究/VRX 既有 dirty、world/model、原始日志保留。
- 004R本次20路直接采集仅得到未START时被动零值，不是STOP因果证据；临时动作脚本把Planner的`std_srvs/SetBool`误写成`example_interfaces/SetBool`，服务等待超时，无START/SEARCH。已安全清理，无生产代码改动。instructor已评审并独立授权004R2；当前先隔离预检，条件未满足不启动Gazebo。

## 研究与保护边界

H=5 s、历史 1-cell 参数和传感器 `engineering_assumed` 仅工程沿用；正式 H/预测年龄/重规划阈值、R/τ/B 与有效遭遇、RF 准确率、B3 科学收益、RMST 仍 OPEN/NOT VALIDATED。D2/D3/D4 不在 004 范围；通信分支不含生产代码/大日志，也不自动合并旧 platform/。
