# 通信状态

- 协议：`PROTOCOL v1` + `ROLE_PROTOCOL_v1_1`；更新时间：2026-10-20（Asia/Shanghai，005 R1 离线回传后）。
- 通道：`CONNECTED`；当前 `USV-20261020-005` 为 **RUNNING / R1 离线候选版已回传**：启动说明、整体地图显示缓存/聚合计时、语音错误分层与安全等义标点、眼动tracker样本诊断已在本地实施；53项相关离线测试与3包构建PASS，真实用户会话体验待复验。004R2/004仅限无模型B3工程ACCEPTED，旧004R保持BLOCKED。005未自行验收，未自动启动/操作Gazebo。
- 当前005阶段性通信报告：`docs/coordination/reports/USV-20261020-005.md`（RUNNING，R1离线候选版/未现场验收）；上一份完成的通信报告：`docs/coordination/reports/USV-20261020-004R2.md`；历史004报告：`docs/coordination/reports/USV-20261020-004.md`（原报告保留，尾部追加返工证据）；本地增量详报：`src/workspace/reports/USV_20261020_004_OFFLINE_R1.md`；原本地详报：`src/workspace/reports/USV_20261020_004_B3_FALLBACK_REPORT.md`。Constructor 回执：`docs/coordination/receipts/constructor-20261020.md`。
- 002/SLIM-004D、003、003R 既有 instructor ACCEPTED 保留。004R 一次额度已消耗且 review=BLOCKED，报告 `docs/coordination/reports/USV-20261020-004R.md`；004R2 唯一新 Gazebo 会话已完成并正式 ACCEPTED，不再复验。005 R1已局部修改本地console/voice parser/gaze bridge并完成离线测试与限定构建；未操作用户运行会话，原004R2证据与全部历史资产保留。

## USV-20261020-004 当前证据

- 修复前唯一 Gazebo run_id `f87fc7b8a1934a52ada1fbc1fd7d4828`：TAKEOVER 无中心、SEARCH_ACTIVE 后无模型当前位 fallback/9 艘自主继续、CANCEL 移除、STOPPED/Recorder finalize。原始证据仅本地 `log/experiments/run_1792482001665000585/`；该运行**不能**证明最终离线返工源码。
- 修复前未直接采集 20 路实际推进器；本 run STOP 后 28 条 follower 状态的 stop barrier/10 艘 idle 只是间接安全证据。第二次 ACTIVE/NAVIGATE/RELEASE/UI 亦 NOT_OBSERVED，不能借旧 003R 的 20/20 数据补成 004 直接 PASS。
- 最终 Planner 对无源身份 Twist/gaze 不用接收时间冒充当前段采集身份；手控 Twist 仍可执行，RF 缺可核验源身份则保守回退。Fleet pose 按当前 epoch/艇/段源时间水位拒绝倒退/同戳冲突，保留最近合法 pose、完全相同输入幂等，终态/切段清窗。有效预测只在显式可信 fixture 下有离线生产路径证据，不宣称当前 ROS 输入已有来源认证。
- 旧实现新增反例失败后修复；最终相关回归 **166 passed、0 skip**，受影响 package colcon build PASS；Planner source/build SHA256 `ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`。运行工作区无根 Git HEAD，实现提交 NONE；研究/VRX 既有 dirty、world/model、原始日志保留。
- 004R本次20路直接采集仅得到未START时被动零值，不是STOP因果证据；临时动作脚本把Planner的`std_srvs/SetBool`误写成`example_interfaces/SetBool`，服务等待超时，无START/SEARCH。已安全清理，无生产代码改动。instructor已评审并独立授权004R2；004R2最终配置实测三次SEARCH/三条撤销、9艇短时自主继续，STOP后20路各360条直接零值跨至少11.634s，Recorder STOPPED/finalize；真实RF/UI/encounter/科学效能仍未验证。直接证据见004R2报告；instructor已在004R2/004两份正式review中裁决为限定工程范围 ACCEPTED。旧004R失败仍保留为历史。

## 研究与保护边界

H=5 s、历史 1-cell 参数和传感器 `engineering_assumed` 仅工程沿用；正式 H/预测年龄/重规划阈值、R/τ/B 与有效遭遇、RF 准确率、B3 科学收益、RMST 仍 OPEN/NOT VALIDATED。D2/D3/D4 不在 004 范围；通信分支不含生产代码/大日志，也不自动合并旧 platform/。

## 2026-10-20 005 constructor R2 隔离候选

- USV-20261020-005仍`RUNNING / CONDITIONAL_CUTOVER`，非DONE/ACCEPTED。最新报告`docs/coordination/reports/USV-20261020-005.md`；本地候选`src/workspace/candidates/USV_20261020_005_R2/`、详报`src/workspace/reports/USV_20261020_005_UI_DIAGNOSIS_REPORT.md`。
- legacy十艇CameraInfo批内顺序偏置有旧版FAIL/候选PASS的正逆序反例，53项相关离线回归与隔离sensor包构建通过；R2语音/Qt/眼动26项离线通过。生产源码/build/install未切换，当前Gazebo仍活，安全检查退出3拒绝。
- FPV真实首次掉速与修复仍BLOCKED：Qt已退出，未进行新30秒同窗probe；下次正常Qt会话可按候选README单次运行只读探针。四传感器/平滑/科学合同未扩张。无生产实现提交SHA；通信提交不代表代码部署。

## 2026-10-20 005 R3 隔离候选（constructor）

- 当前`USV-20261020-005 = RUNNING / R3_CANDIDATE_NOT_DEPLOYED`；最新`docs/coordination/reports/USV-20261020-005.md`。本地九文件候选与一键受控切换说明：`src/workspace/candidates/USV_20261020_005_R3/README.md`。当前用户run仍R1，九文件production/build/install未切换。
- 09艇FPV两探针约17秒重叠，源约11.5Hz、relay10.2Hz、Qt显示7.6Hz、RTF0.67；源低于生成相机30仿真Hz，Gazebo/bridge边界仍OPEN。R3修relay/Qt已复现的burst/latest与相位掉帧，离线17 tests+隔离2包build PASS，未现场验FPS。08–10当前R1仍STALE、R3资格恢复未运行验收。
- 用户四传感器与默认禁真实detector的新要求另行独立小批，不改R3冻结候选、不擅定科学参数。R3切换仅用户正常结束会话后按README执行；不得代停或后台覆盖。


## 005R4 isolated detector-off candidate（2026-10-20 Asia/Shanghai）

- 当前唯一READY后继 `USV-20261020-005R4` 已由constructor实施为 `ISOLATED_READY / RUNTIME_NOT_VALIDATED`，非DONE/ACCEPTED。报告 `docs/coordination/reports/USV-20261020-005.md`，本地11文件候选及安全切换 `src/workspace/candidates/USV_20261020_005_R4/README.md`。生产仍R1，未apply/start/改原始资产。
- 默认真实detector节点、Search/Qt检测消费与黄色候选可视化已在隔离候选中门控；显式opt-in保留。旧反例FAIL→R4 PASS，相关82+GT7 PASS，隔离5包build PASS，假根切换及失败回滚PASS。真实Gazebo/UI未复验；源相机吞吐、08–10几何资格、四真实传感器仍OPEN。旧0.25仿真Hz假设与4秒belief不变，正式科学结果未验收。
