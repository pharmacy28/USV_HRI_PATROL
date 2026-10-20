# constructor 角色与记忆接收回执 — 2026-10-20

- role: `constructor`
- read_commit: `ea4e9bf8e946de6c653627b1d7b297e6318023fd`（写入前通信分支 HEAD）
- contract_version: `RC-20261020-v1`；通信协议 `v1` + `ROLE_PROTOCOL_v1_1`
- active_task: `USV-20261020-003R / 003` 均已由 instructor 正式 `ACCEPTED`；本轮仅文档接收/状态收口，无新 READY 工程任务、无新增运行额度。
- 更新：2026-10-20 15:10，Asia/Shanghai。

## 已读取与实际基线

已读取最新 `MAIN_MEMORY.md`（blob `d4eba881e1a0c1c03af689affcb74b24aa2108f4`）、`PROTOCOL.md`、`ROLE_PROTOCOL_v1_1.md`、instructor 交接与回执、003R/003 正式 review、003R 通信报告及 STATUS。通信分支由 `acb5760` 前进到本次 read_commit 的改动只涉及 main memory、instructor 回执和两份 review；未将远端旧 `platform/` 当生产源码，也未执行远端脚本。

- 实际运行树：`/home/cyz/vrx_ws`；根 Git 尚无提交，运行源码分支/HEAD=`UNKNOWN`，实现提交 SHA=`NONE`，不能以通信 SHA 代替。既有 003/004D 修改保留，不能从根 Git 给出可靠生产 diff/dirty 基线。
- 版本化研究树：`/home/cyz/USV_HRI_PATROL`，`main@5f263c694f3d601bf1596bb92b0849d98f7e677b`；既有 `idea/研究决策状态.md` 未提交修改保留。
- 独立 VRX 树：`humble@dc30ed8d17aa1083fd872edad9c77c69896d2b07`；5 个既有 tracked 修改及未跟踪 world/model 保留。
- 当前 source/install `research_pipeline.launch.py` SHA256 均为 `b835b65920141d68966cf3d664c08e3d0ecf98553c659ec8be546b2fc5f85f21`；Planner 源 `01f672b16cd8c04a59dc5728df9da100ad8794c8e54f6a7f0cbb918c0e5328ea`、责任合同 `2c68363eebe6acc18b55424a1601d9839fa6243cd4585956730610338e579417`、Recorder `19120b8e83085b3df9c74d505519aa9add8e348321259786df258d8a75c42992`。这是文件身份核对，不是完整环境可复现证明。

## 记忆校正与时钟精度

- 002/SLIM-004D 已 `ACCEPTED`（工程预算终止），并非未验收；003R 最终时钟配置与 003 ROS API 级显式 SEARCH/B2 均已 `ACCEPTED`，不是仍待执行/待审。003R 唯一有界 Gazebo smoke 已用尽；本轮未重跑。
- TAKEOVER 只转移执行控制权；显式 SEARCH 才激活 B2 当前位责任；NAVIGATE、CANCEL、RELEASE 撤销。远端旧平台与离线测试均不能替代最终生产运行证据。
- generation 3 人工中心与 28.324 s 的 fleet pose 相距约 0.0287 m。原报告的 **0.024 s** 是 `28.348 s` Recorder assignment 外层时刻与该 fleet pose 的差；与 Planner 原始 plan/source stamp `28.152 s` 比较，差为 **0.172 s**。这支持邻近时段当前位中心，不证明源事件时刻精确同步；保留处理/接收延迟。本回执澄清历史报告的含糊“时间差”，不改写原始记录。
- 真实 UI 点击=`NOT_OBSERVED`；B3 fallback、有效遭遇、正式 FOUND、科学比较、RMST=`NOT VALIDATED`。R、τ、正式预算、encounter↔FOUND/同 tick、B3 时域/阈值仍由 main 裁决。旧 Gamma/FOUND 或概率正检出不能擅自等同 RC 的有效遭遇。

## 本次核查与边界

只读执行 `git status --short --branch` / `git rev-parse HEAD`（研究树、VRX、运行树）、`sha256sum`（上述 source/install）、读取本地 003R 详报，并经 GitHub fetch/compare 核对 HEAD、review 与任务目录（001/002/003/003R，无新 READY）。没有运行 Gazebo、构建、测试、训练或修改生产源码；本回执不是新的 runtime 证据。后续生产 B3 任务须由 instructor 单独发布；本轮仅确认真实接收，不代替 main/overleaf 的 ACK。

## USV-20261020-004 新任务接收（2026-10-20，Asia/Shanghai）

- role=constructor；read_commit=`a13585080c5e50d38d5ad76d13bc66e378d3453d`；contract_version=`RC-20261020-v1 + RC-20261020-v1.1`；active_task=`USV-20261020-004`，状态=`RECEIVED/RUNNING`，不是 DONE/ACCEPTED。
- 已读取唯一 READY 004、MAIN_MEMORY、RC-v1.1 D5、MAIN-20261020-002、协议/角色协议与 instructor 新回执；002/003/003R 前置均已 ACCEPTED。通信分支比 instructor 提交仅多 overleaf 回执更新，无竞争工程 READY。
- 当前生产基线复核：`/home/cyz/vrx_ws` 根无有效 Git HEAD，源码 SHA=UNKNOWN、实现提交 NONE；Planner SHA256 `01f672b16cd8c04a59dc5728df9da100ad8794c8e54f6a7f0cbb918c0e5328ea`，experiment_modes `076a355f5eb1dd616794664854fd99fb8889409af6f4081a556239754a05cede`，source/install launch 均 `b835b65920141d68966cf3d664c08e3d0ecf98553c659ec8be546b2fc5f85f21`。研究 main@5f263c6 有既有决策 dirty；独立 VRX humble@dc30ed8d 有既有修改与 world/model，均保留。
- 已确认旧说法需纠正：远端 platform 不是运行源码；RF 缺失目前会使 B3 fixed-center 返回错误，尚非已完成回退；H/年龄/位移阈值仍 OPEN。有效 prediction fixture 只能证明工程接线，不能宣称 RF 或正式 B3 已验证。
- 未决冲突：正式 H/预测年龄及重规划阈值、R/τ/B 与 encounter 终态仍交 main；本任务只做 D5 工程门控与失效回退，不推断这些数值。
- 本人 ACK 仅表示已经接收任务；后续离线、构建、至多一次 Gazebo smoke 按任务合同执行，另以 004 报告提交实际结果。

## USV-20261020-004 Constructor 完成回执（2026-10-20，Asia/Shanghai）

- 原上节 `RECEIVED/RUNNING` 是领取时快照；当前本人状态 `DONE / instructor REVIEW_PENDING`，不是本人 ACCEPTED。通信报告 `docs/coordination/reports/USV-20261020-004.md`，本地详报 `src/workspace/reports/USV_20261020_004_B3_FALLBACK_REPORT.md`。
- 已实施最小生产 B3 门控与无模型回退，162 项相关回归及受影响 package 构建通过；最终 Planner source/build SHA256 `8d955332b750a118805b4f56d1808fbe72cc5a80e414b62a7614e8636234ff5d`，实现提交 `NONE`（运行树无可用 Git HEAD）。
- 唯一新 Gazebo run_id `f87fc7b8a1934a52ada1fbc1fd7d4828`：TAKEOVER 无中心、显式 SEARCH 后当前位 fallback、CANCEL 移除、STOPPED/Recorder finalize 有证据。20 路实际 thruster 本 run 未直接记录，第二次 ACTIVE/NAVIGATE/RELEASE/UI 未闭合，不虚称 PASS；正式 RF/B3 科学效能仍未验证。
- 研究树/VRX 的既有修改、历史 world/model 与原始录制保留。H/预测有效年龄/位移阈值及 R/τ/B 仍 OPEN；未实施 D2/D3/D4，也未开始下一项工程任务。

## 004 正式审查后的 Constructor 离线返工回执（2026-10-20 16:10，Asia/Shanghai）

- 上节 `REVIEW_PENDING` 是历史快照；现 instructor `USV-20261020-004.review.md` 判 `CHANGES_REQUESTED`。本人已读取并按范围完成两类生产因果缺陷的失败测试、最小修复、166 项回归及 colcon 构建；详见通信报告增量和本地 `src/workspace/reports/USV_20261020_004_OFFLINE_R1.md`。
- 最终 Planner source/build SHA256 `ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`，实现提交 NONE。无源时间/段的 manual/gaze 仅作控制/诊断，不能被接收时刻认作新段 RF 证据；fleet pose t₂→t₁/同戳冲突被拒且不污染合法当前位。
- 当前状态 `OFFLINE_FIXED / RUNTIME_PENDING`，不是 004 ACCEPTED。004 原一次 Gazebo 额度已用尽；本轮没有新仿真，20 路实际 thruster 与修复后 runtime 仍待 instructor 单独发布 004R READY。保留原 004 报告与原始 run，不伪造历史版本验收。

## 004R 本人领取回执（2026-10-20，Asia/Shanghai）

- role=constructor；read_commit=`629062c8a0f98c676ce364d9c8ad151e68de280b`；contract_version=`RC-20261020-v1 + RC-v1.1 D5`；active_task=`USV-20261020-004R`；状态=`RECEIVED / PREPARING`，非运行通过或ACCEPTED。
- 已读004R READY、004.review复审、MAIN_MEMORY、PROTOCOL、ROLE_PROTOCOL及STATUS。上节“004R待发布”和STATUS“无004R”均是历史状态；004R现为唯一READY，005为DRAFT，不并发改生产代码。
- 运行树`/home/cyz/vrx_ws`根Git HEAD=UNKNOWN、实现提交NONE；Planner source/build SHA256均`ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`，research launch source/install均`0c9ea2a19e13c307034d67d3b33f53e5c15e18bb0ad26d6a726e5def3c90065f`。研究树main@5f263c6的既有决策修改、VRX humble@dc30ed8的既有修改及world/model保持原状。
- 本次仅领取与启动前准备；未启动Gazebo，004R一次额度未消耗。运行前仍须验证20路直接采集与ROS权限；004整体保持CHANGES_REQUESTED/RUNTIME_PENDING。若准备不满足，报告BLOCKED，不用旧run或fixture代替。

## 004R 本人运行回传（2026-10-20，Asia/Shanghai）

- 此节取代上一节`RECEIVED/PREPARING`当前状态：`BLOCKED / RUN_CONSUMED`，不是DONE/ACCEPTED；详细报告`docs/coordination/reports/USV-20261020-004R.md`，本地`src/workspace/reports/USV_20261020_004R_RUNTIME_REPORT.md`。
- 最终生产source/build/install身份一致、26项定向回归PASS；唯一Gazebo会话确实启动且20/20推进器采集有效，但临时动作脚本错误使用`example_interfaces/SetBool`，Planner实际服务为`std_srvs/SetBool`，故未发送START。后续SEARCH、B3 fallback、撤销、STOP因果及合法Recorder终止均未观察到，不能以空闲零推力/manifest的STOPPED字段冒充验收。
- 已执行launcher stop并核对无活跃owner；未修改生产算法/配置/world、未训练、未跑第二次Gazebo。004仍CHANGES_REQUESTED，005仍DRAFT。是否追加独立有界验收由instructor决定。

## 004R2 本人领取（2026-10-20，Asia/Shanghai）

- role=constructor；read_commit=`3229e4b8eb575db4da8ad2850f5b4c0566770af5`；contract=`RC-20261020-v1/v1.1`；active_task=`USV-20261020-004R2`，状态=`RECEIVED / PRE-FLIGHT`，非运行/验收通过。
- 已读004R2唯一READY、004R.review及旧004R报告、最新STATUS/MAIN_MEMORY/协议；004R旧额度BLOCKED/RUN_CONSUMED，004仍CHANGES_REQUESTED，005仅DRAFT。当前未见竞争Gazebo runner，不并发改生产基线。
- 生产Planner source/build仍为`ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84`、launch source/install为`0c9ea2a19e13c307034d67d3b33f53e5c15e18bb0ad26d6a726e5def3c90065f`，根Git HEAD UNKNOWN、实现提交NONE；研究树与VRX旧dirty保留。
- 本人先做无Gazebo隔离ROS驱动预检、脚本失败码/安全清理核查和20路只读采集合同。全部PASS并提交准备回执之前，不消耗004R2的新Gazebo额度。004R原manifest hash转录差异已按原文件追加更正，未改原始记录。

## 004R2 隔离预检完成、运行前准备回执（2026-10-20，Asia/Shanghai）

- 上节`RECEIVED/PRE-FLIGHT`更新为`PRE-FLIGHT PASS / GAZEBO NOT STARTED`。详细预检与脚本hash：`docs/coordination/reports/USV-20261020-004R2.md`及本地`src/workspace/reports/USV_20261020_004R2_RUNTIME_REPORT.md`。
- 同一实际动作脚本`std_srvs/SetBool`真/假请求、拒绝/超时在隔离ROS domain通过；监督器成功0、拒绝1、无服务超时1且均清理；20路只读Float64合成fixture各3条、真实收到全路才标READY；cleanup/watchdog同型。均OFFLINE/ISOLATED，未连生产任务。
- Planner source/build及launch source/install身份仍匹配004R2；无模型配置和最终临时脚本hash已登记。无竞争runner、未启动Gazebo/训练/005生产改动。按唯一READY后续至多一次有界运行，运行证据到达前不宣称004/004R2验收通过。

## 004R2 本人完成回执（2026-10-20，Asia/Shanghai）

- 上节`PRE-FLIGHT PASS / GAZEBO NOT STARTED`现更新为`DONE / instructor REVIEW_PENDING`，不是本人ACCEPTED。唯一新Gazebo run_id=`448cd4ea97f64161bcaf9d850386bba5`；报告`docs/coordination/reports/USV-20261020-004R2.md`和本地`src/workspace/reports/USV_20261020_004R2_RUNTIME_REPORT.md`已追加真实运行部分。
- 最终文件与临时脚本hash保持预检回传版本。START、3次显式SEARCH、当前位无模型fallback、CANCEL/NAVIGATE/RELEASE、9艇短时自主继续均有真实owner/Recorder和推力/位移证据；STOP后20路各360条直接零值跨至少11.634s，Recorder合法STOPPED/finalize，无活跃owner。单次额度已消耗，不补跑。生产源码、配置、world未改；实现提交NONE。
- 真实RF有效预测、实际UI/硬件、encounter、正式B2/B3科学效能与RMST仍NOT VALIDATED。旧004R失败与原始数据保持不变，004整体仍CHANGES_REQUESTED，待instructor独立裁决。005保持DRAFT、不并发改生产基线。

## 004R2/004 正式评审接收（2026-10-20，Asia/Shanghai）

- 本人已读取 instructor 正式 `tasks/USV-20261020-004R2.review.md` 与 `tasks/USV-20261020-004.review.md`：004R2 和 004 均为 **ACCEPTED（限无模型 B3 门控/失效回退工程范围）**。本节更新上节历史快照中的 `REVIEW_PENDING` / `CHANGES_REQUESTED`，不改写原报告或原始证据；004R 失败仍为 `BLOCKED/RUN_CONSUMED`。
- instructor 核查依据为最终 source/install 身份、原始 action/thruster/manifest/time_series 与回传交叉对照；004R2 run_id=`448cd4ea97f64161bcaf9d850386bba5`，STOP 后 20 路各 360 条直接零值，最短首末跨度 11.634358088 s。该结论仅为短时工程验收，不构成 RF 有效预测、真实 UI/硬件、有效遭遇、正式 B2/B3 比较或 RMST 验收。
- constructor 本次仅接收评审并更新本人通信状态；未修改生产源码、未启动仿真/构建/测试。运行树根 Git HEAD 仍 `UNKNOWN`，实现提交 `NONE`；通信提交不能代替生产代码身份。005 仍 `DRAFT`，未领取或实施；后续仅按新 READY 合同执行。

## 005 第一阶段本人领取（2026-10-20，Asia/Shanghai）

- role=constructor；read_commit=`cac0e02e10539768c6a12da25df48fe972543e34`；已回读 `tasks/USV-20261020-005.md`，状态 `READY / PHASE_1_STARTUP_AND_TARGETED_DIAGNOSIS`；本人状态 `RECEIVED/RUNNING`，不是 DONE/ACCEPTED。
- 已先向本聊天交付 `/home/cyz/vrx_ws` 的默认 `./run_vrx.sh start` 与最简操作说明；默认 `h5_command_aware`，Qt/joy/pad/voice/gaze启用，`--research-core` 不适用于 UI 走查。当前进程快照未见本工作环境的 Gazebo/Qt owner，不以此断言用户其他会话不存在。
- 按任务授权实际启动三名只读 sub agents，分别负责 UI/按键、性能/热图、语音/眼动数据流；主agent负责现有安装身份、回执、跨线集成与报告。初步证据为单艇显式 SEARCH UI 缺口、主线程回调图像处理的性能假设、语音分层拒绝与眼动 tracker 样本身份区别；尚无实测延迟/真实设备复验。
- 本阶段未启动 Gazebo、START/操纵/STOP、训练或清理用户会话；未修改生产代码。研究仓库 `main@5f263c694f3d601bf1596bb92b0849d98f7e677b` 既有 dirty，独立 VRX `humble@dc30ed8d17aa1083fd872edad9c77c69896d2b07` 既有 dirty/world/model 均保留；运行根 Git HEAD UNKNOWN，实现提交 NONE。

## 005 R1 本人回传（2026-10-20，Asia/Shanghai）

- 在005原READY下读取同路径R1增量；当前状态仍 `RUNNING / CANDIDATE_READY_FOR_USER_CHECK`，不是本人或instructor ACCEPTED。初版仅只读诊断的快照仍作为历史保留；新R1修改与证据见 `docs/coordination/reports/USV-20261020-005.md` 和本地 `src/workspace/reports/USV_20261020_005_UI_DIAGNOSIS_REPORT.md`。
- 主agent唯一修改/集成Qt console与直接测试；两名代码子agent分别拥有voice parser和eyetracker Linux receiver及其测试，不重叠修改共享文件。最终合并审核后相关离线测试53 passed、0 skip；仅三受影响包merged/symlink构建PASS且source/build SHA一致。运行树根Git HEAD UNKNOWN，实现提交NONE。
- 最终源码SHA256：console `7bd61147de984960c538c2a7eb59281411e78fda1bd2785d8d0b22d0c9964d2b`；voice parser `86065d7ed966a9f2ce444ba2f9a85c44f9d18dceea475f5db06c635105d40847`；gaze receiver `0a15877b6f03d9a061112d57ed6bb45e7f1304e0aee5f40bdee036c7756bb807`。地图离屏同条件10000格重复重绘70.05→0.89ms，属隔离Qt证据，不称真实平台整体流畅度改善。
- 本轮未新开Gazebo、START/操纵/STOP、杀用户会话、训练或改数学/感知/规划/Recorder。语音声学ASR、Windows跨机眼动时延、真实UI响应仍待用户现场；当前只交可复验候选版。004/004R2旧工程验收不因005修改追溯升级为新版本runtime通过。

## 005 R2 本人条件交付回执（2026-10-20，Asia/Shanghai）

- 本人状态`RUNNING / CONDITIONAL_CUTOVER`；最新报告`docs/coordination/reports/USV-20261020-005.md`，本地持久候选`src/workspace/candidates/USV_20261020_005_R2/`。运行树根Git SHA UNKNOWN、实现提交NONE；生产R1源码/build/install未变，Gazebo仍在运行，未部署R2、未替用户STOP或重启。
- 旧版逐艇resolve+逐格LOS造成后排CameraInfo跨2秒TTL的10艇正逆序反例已复现FAIL；隔离最小补丁先解析同批几何，10艇与真过期拒绝PASS。传感器相关53项离线测试、隔离包构建1 finished；R2语音/Qt/眼动26项离线测试。假根切换脚本的live/冲突拒绝与失败回滚PASS，真实主机check因活跃Gazebo退出3。
- FPV真实同窗测量未执行：Qt PID已退出，ROS沙箱socket权限拒绝；准备单次≤30秒被动探针且3项fixture通过，但首次掉速/性能修复继续BLOCKED。R2不是正式设备/运行验收，005不可自签DONE/ACCEPTED。下一步需用户正常结束当前会话后按README检查/受控切换，重启后单次探针和现场体验验收。

## 005 R3 本人交付回执（2026-10-20 Asia/Shanghai）

- `RUNNING / R3_CANDIDATE_NOT_DEPLOYED`；本地`src/workspace/candidates/USV_20261020_005_R3/`九文件/安全切换/README，报告`docs/coordination/reports/USV-20261020-005.md`。生产仍R1；本轮未停止/重启或改写用户进程，运行树根Git HEAD UNKNOWN，实现提交NONE。
- 授权同艇FPV窗口如报告：源、relay、Qt都有墙钟降速且源仿真Hz低于生成30Hz；另一个探针重叠约17秒。R3 relay/Qt burst/latest与33ms相位直接反例旧FAIL新PASS，17项离线测试、隔离两包构建PASS；九文件fake-root切换故障注入PASS。源Gazebo/bridge性能、R3真实FPS、08–10恢复仍OPEN/NOT_VALIDATED。
- 条件切换一条命令及持久日志见README；当前仍活跃会话不部署。后继独立核默认detector关闭与四传感器真实接口，不把黄色候选或占位图作为科学探测。
