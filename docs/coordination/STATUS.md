# 通信状态

- 协议：`PROTOCOL v1` + `ROLE_PROTOCOL_v1_1`；更新时间：2026-10-20（Asia/Shanghai，005 READY 领取后）。
- 通道：`CONNECTED`；当前 `USV-20261020-005` 已由 instructor 发布 **READY / PHASE_1_STARTUP_AND_TARGETED_DIAGNOSIS**，constructor 已领取并进入只读定位；第一交付启动说明已回本聊天。004R2/004 正式 ACCEPTED 仅限无模型 B3 工程范围；旧 004R 保持 BLOCKED/RUN_CONSUMED。005 本阶段不自动启动 Gazebo/START/操纵/STOP，也不先大改 UI。
- 当前005阶段性通信报告：`docs/coordination/reports/USV-20261020-005.md`（RUNNING，只读诊断，未作生产修复）；上一份完成的通信报告：`docs/coordination/reports/USV-20261020-004R2.md`；历史004报告：`docs/coordination/reports/USV-20261020-004.md`（原报告保留，尾部追加返工证据）；本地增量详报：`src/workspace/reports/USV_20261020_004_OFFLINE_R1.md`；原本地详报：`src/workspace/reports/USV_20261020_004_B3_FALLBACK_REPORT.md`。Constructor 回执：`docs/coordination/receipts/constructor-20261020.md`。
- 002/SLIM-004D、003、003R 既有 instructor ACCEPTED 保留。004R 一次额度已消耗且 review=BLOCKED，报告 `docs/coordination/reports/USV-20261020-004R.md`；004R2 唯一新 Gazebo 会话已完成并正式 ACCEPTED，不再复验。005 已 READY，本阶段仅启动说明与定向诊断，未改生产代码或运行会话。

## USV-20261020-004 当前证据

- 修复前唯一 Gazebo run_id `f87fc7b8a1934a52ada1fbc1fd7d4828`：TAKEOVER 无中心、SEARCH_ACTIVE 后无模型当前位 fallback/9 艘自主继续、CANCEL 移除、STOPPED/Recorder finalize。原始证据仅本地 `log/experiments/run_1792482001665000585/`；该运行**不能**证明最终离线返工源码。
- 修复前未直接采集 20 路实际推进器；本 run STOP 后 28 条 follower 状态的 stop barrier/10 艘 idle 只是间接安全证据。第二次 ACTIVE/NAVIGATE/RELEASE/UI 亦 NOT_OBSERVED，不能借旧 003R 的 20/20 数据补成 004 直接 PASS。
- 最终 Planner 对无源身份 Twist/gaze 不用接收时间冒充当前段采集身份；手控 Twist 仍可执行，RF 缺可核验源身份则保守回退。Fleet pose 按当前 epoch/艇/段源时间水位拒绝倒退/同戳冲突，保留最近合法 pose、完全相同输入幂等，终态/切段清窗。有效预测只在显式可信 fixture 下有离线生产路径证据，不宣称当前 ROS 输入已有来源认证。
- 旧实现新增反例失败后修复；最终相关回归 **166 passed、0 skip**，受影响 package colcon build PASS；Planner source/build SHA256 `ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`。运行工作区无根 Git HEAD，实现提交 NONE；研究/VRX 既有 dirty、world/model、原始日志保留。
- 004R本次20路直接采集仅得到未START时被动零值，不是STOP因果证据；临时动作脚本把Planner的`std_srvs/SetBool`误写成`example_interfaces/SetBool`，服务等待超时，无START/SEARCH。已安全清理，无生产代码改动。instructor已评审并独立授权004R2；004R2最终配置实测三次SEARCH/三条撤销、9艇短时自主继续，STOP后20路各360条直接零值跨至少11.634s，Recorder STOPPED/finalize；真实RF/UI/encounter/科学效能仍未验证。直接证据见004R2报告；instructor已在004R2/004两份正式review中裁决为限定工程范围 ACCEPTED。旧004R失败仍保留为历史。

## 研究与保护边界

H=5 s、历史 1-cell 参数和传感器 `engineering_assumed` 仅工程沿用；正式 H/预测年龄/重规划阈值、R/τ/B 与有效遭遇、RF 准确率、B3 科学收益、RMST 仍 OPEN/NOT VALIDATED。D2/D3/D4 不在 004 范围；通信分支不含生产代码/大日志，也不自动合并旧 platform/。
