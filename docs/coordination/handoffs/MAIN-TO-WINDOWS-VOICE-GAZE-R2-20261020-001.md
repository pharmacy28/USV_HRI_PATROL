> **2026-10-26 续接：本轮收件对象为用户明确指定、聊天名为 `windows` 的现有 Windows 本机 agent。**
> 以下 2026-10-20 正文作为历史保留；其中“用户正在运行 R1”等时态不作为当前机器/会话状态。不要因本次重新配置而覆盖用户现有资产。

## 2026-10-26 当前协作消息（main → windows）

用户本轮原话：“现在我在这个windows电脑上配置眼动仪相关环境，请与本机agent（聊天名为windows）进行交流”。main 已收到并沿现有通信分支续接；本消息不是第二份工程 READY，也不改变 instructor 的平台集成与验收分工。

请 windows 在当前配置工作中读取并本人回执：

1. **先对齐当前环境与进度。** 回报眼动仪实际型号、Windows/驱动与 SDK 版本、识别状态、校准是否完成、正在使用的 Unity 工程或发行程序、已完成项/当前错误/下一步。历史 `C:\\bridge` 和 `C:\\EyeTrackerBridge` 仅供核对，不能假定本次路径、设备和版本未变。
2. **先验证本机真实样本，再核跨机。** 分开给出设备新样本、Unity Update、UDP 发包三个计数及统计窗口；核 `tracker_us` 唯一/重复/倒退/缺失和 valid/null 传播。固定发包率不等于设备采样率；离线 fixture 不代替实际设备证据。
3. **确认现场拓扑与实际生效目标。** 明确 Linux 接收端当前是否同时在线、是否为另一台机器；若是同机双系统互斥运行，先完成 Windows 本机采集验证，不能宣称已完成同时跨系统链路。核 UDP 15555 的实际生效配置，不能仅读默认值或把 127.0.0.1 当跨机地址；真实地址留本地，报告只写匹配状态。
4. **保留已确定的数据语义。** `tracker_us` 为 SDK 原始微秒域；`t/unity_t` 不冒充统一时钟。归一化坐标、Y 翻转、窗口内容区/DPI/黑边须核当前实现；无效点不得沿用上次值伪装有效。跨机时钟未对齐继续写 UNALIGNED；眼动不直接修改目标后验。
5. **有证据再改延迟链。** 若本次观察到重复或积压，定位采集/回调→队列→socket 的本机耗时，在隔离候选中给必要 patch、兼容性检查与前后数据；保留原始采样、原时间和无效状态。不要无故扩展音频15556任务，不静默替换正在使用的 UUV.exe，也不改 Linux 生产或启动仿真。
6. **将回执留在现有链路。** 优先在本人既有报告追加本轮日期段，或按原约定使用 `docs/coordination/reports/WINDOWS-BRIDGE-20261020-002.md`。回报 read_commit、实际执行项、必要 hash/命令/聚合结果、当前阻塞和需要 constructor 配合的接口问题。原始眼动、身份、凭据和具体网络地址不上传。
7. **补全可达入口。** 请提供当前聊天/线程的准确标识及本人实际可用的 read/send 接口或现有接收机制；若能够直接联系 main，请本人回传。只有真实接收后才写 ACK；文件发布不等于唤醒，不启动冒名云端 agent。

main 本轮核验：已读原 Windows 报告（blob `b92be47d67a0685e01fa8fdf09e7fc56f7832b65`）与本交接历史段；约定的 002 报告当前未找到。当前 main 工具未暴露跨 Work read/send，agent 列表只有 /root，所能访问的云端浏览器未登录 ChatGPT；此限制仅指本轮 main 能力，不否定其他 Work 存在原消息入口。状态为 **RELAY_PUBLISHED / WINDOWS_ACK_PENDING**，尚无本轮本机执行或配置完成证明。

---

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
