# MAIN-TO-WINDOWS-VOICE-GAZE-R2-20261020-001

- 日期：2026-10-20，Asia/Shanghai；role=main。
- 接收者：既有Windows本地Codex（原WINDOWS-BRIDGE-20261020-001作者，负责C:\bridge / C:\EyeTrackerBridge）；抄送instructor，供constructor读取接口增量。
- active_task=USV-20261020-005 / R2；依据instructor交接9e8bc6c7d429cea00916c7a8322a08a7d3d96cb6；本轮另读constructor报告3796d83fef253b4da5add7369aa362e25b868b05。沿原005协作，不是第二份工程READY；工程review/版本切换仍归instructor。
- 状态：仓库中转已发布；WINDOWS_ACK_PENDING / EXECUTION_UNVERIFIED。main没有Windows本机执行证据，不代签接收。

## main本人接收与已完成的中转准备

main已读instructor的R2完整交接、原Windows桥接审计、005 R2条款及constructor新增隔离候选报告。用户报告已启动R1体验，生产版本保持稳定；R2实际修复可以在隔离副本继续，不需等所有现场反馈才开始。

原Windows报告仅证明源码/发行文件审计；当时UUV进程命令行读取被拒、Player.log为空，实际目标和有效采样未核实。原UUV.exe SHA256=059c313352892718258a120b87bdc6fc7c23ce67181084abe14f86f204f5dddb，Assembly-CSharp.dll=5070cc5bc922fa0dc7a0244f100362404c00bf20259fe9b70f8370a767e5378b，GazeUdpSender.cs=066e1c2bf06fb27bbc83af13250e26c1ff36fcb0f97cc2f91229a59407b5fc4c，仅作历史对照，须由Windows本人核当前身份，不能视为当前已加载证明。

Linux当前已确认UI gaze订阅depth=1且有latest_pending，不重复当新优化。constructor@3796d83f报告R2仅在/tmp/usv_005_r2_hvSJ6a/隔离候选：每PTT会话连续采音；同source/session的已知重复/倒退tracker不进入UI/attention，原始发布/Recorder保留；26项离线测试通过。该报告不代表Windows源已修、实际ASR/眼动延迟已改善，也不是R2已部署/已通过instructor复核。

## 请Windows现有agent立即接续的协作

仅在本机现有资产与原005允许范围内执行；先用现有实现和隔离fixture复现，证据充分则交实际最小patch及必要构建/兼容测试，不停留在重复诊断。真实设备观测沿用户本轮人工联调范围；不得新增录音/主动设备控制/无人值守运行。无设备证据时明确待现场，不把fixture统计叫真实采样。

| 协作项 | 本人应提供的事实与证据 |
|---|---|
| 设备新样本与Unity发包 | 分开统计设备回调/读取次数、唯一tracker_us、重复/倒退/缺失、Unity Update和UDP发包次数；给统计窗口及重复比率分母。t/unity_t不是设备采集年龄。缺采集回调观测时写UNKNOWN，不用Update次数代替。 |
| Windows本机分段耗时 | 在隔离候选中区分源读取/回调到达、入发送队列、出队、socket发送起止的单调时间；记录时钟来源/单位/频率、队列长度/高水位、等待/阻塞、Unity主线程停顿。主机回调到达不是SDK设备真实采集时刻。缺tracker↔Windows映射时保留UNALIGNED。 |
| 重复/积压最小修复 | 若证实重复旧tracker或FIFO阻塞，比较现有实现与“新设备样本发送”或“仅显示通道取最新”候选。用同条件burst/重复/倒退/停更/重连隔离输入给发送数量、唯一样本、队列年龄/阻塞前后，未测项保留UNKNOWN。原始采样/录制不删、不改有效性；不得以降采样掩盖延迟。 |
| 协议与重置 | 保持现有字段、单位、无效值与坐标含义；明确源实例/session、序号高水位、重连/时钟回退的重置范围。原报告缺源身份/序号等字段，不能假称已存在；新增诊断字段须可选、版本可辨，先与constructor验证兼容，不在生产发包中静默改协议，也不将诊断session冒充已认证研究身份。 |
| 正在运行的发行身份 | 核当前UUV.exe/DLL/配置/发送脚本hash及构建对应关系、进程与实际生效目标/15555，区分配置文件期望值和运行实值；目标地址保留本地，公开只给已核匹配/未核实。访问被拒如实记录，不能绕过权限。 |
| 条件音频项 | 先核当前语音输入来源。只有实际使用Windows UDP音频15556时才核采样率/格式/PTT/帧序号、发送连续性与积压；Linux本地麦克风则本项N/A，不扩大Windows音频任务。 |

## 候选与用户会话切换严格分开

用户正在跑R1；Windows既有UUV.exe、DLL、配置、目标与进程保持不动。候选使用独立路径/构建输出，给基线与候选完整SHA256、实际patch、必要直接反例/回归、同条件前后数据、已知缺口与回退文件。禁止在用户R1复验中覆盖发行目录、热加载、重启、改目的IP/端口或增加第二个生产发送器。

切换须等用户本轮R1复验结束，由instructor联合Linux/Windows安排明确版本、兼容性与回退步骤；本交接不提前批准切换。没有时钟映射不报告跨机总延迟，不把发包成功当Linux收到或Qt已显示。不改科学合同、RF特征、源采样/时间、手柄或大布局；无志愿者采样/训练/自动Gazebo。

## 本人回执与产出

Windows现有agent在本人首次执行时合并回传role、read_commit、本机路径、接收时间、实际执行/未执行项、当前阻塞。建议统一文件reports/WINDOWS-BRIDGE-20261020-002.md；可在既有本人报告中作明确R2追加，二选一，不另造长报告链。只上传不含坐标/身份/原始音频的聚合或去标识时间链摘要，详细原始证据与真实网络地址留本地。可复现最小patch不含私密路径配置/凭据。

同一回执附当前已有接收方式/本地触发器是否存在及可验证标识；没有则明确未配置，不要求用户再找聊天ID，不临时创建冒名Windows agent。本人ACK、开始执行、产出候选、切换和实测通过分开记录。main读实际回传后同步instructor；constructor只整合已核兼容的增量，不越权改Windows。

## 当前传输限制（给instructor的本人执行证据）

本轮main已查可用agent列表，仅/root，未见现有Windows会话；查仓库登记、既有Windows报告、历史通信线索与可见automations，未找到Windows可调用session/runner/接收器。现有工具没有Windows远程执行/跨Work直接发消息入口。GitHub是已验证可写可读的中转渠道，但发布文件不证明Windows已被唤醒。

因此本轮main完成“读取→具名跨线交接→仓库发布/回读”，Windows本人接收与设备执行仍PENDING。此为能力/路由缺口，不是用户未授权；不通过新建云端子agent冒充Windows，不制造ACK或现场数字，不把Linux候选当Windows修复。收到本人回执后沿同005闭环，不另发竞争工程任务。

FIELD2补充@8e03631b：用户眼动主观快不少，作为R1反馈保留，不能归因R2或Windows未实施候选；仍继续已授权的源链实际取证/隔离修复。FPV与09/10观测另由constructor沿005取证，Windows不扩大任务或增加渲染。
