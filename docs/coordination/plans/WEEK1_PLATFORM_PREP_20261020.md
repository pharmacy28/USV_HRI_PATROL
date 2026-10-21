# 第一周计划更新：可操作、可记录、可接入训练的平台准备

2026-10-20，main依据用户明确方向更新。来源：用户上传《1015-1115.pdf》及INSTRUCTOR-TO-MAIN-PREP-20261020-001@8cb9879fad74b7861554cdc62c47429ffbeb6f98。原PDF保留为历史月度计划，本文件是第一周执行口径；不将计划项写成完成项。

## 当前执行快照（2026-10-21，优先于下方历史阶段）

1. **今天组会**按原10/15—11/15月计划汇报第一周实际进展，稿件与计划对照表见 `../briefings/GROUP_MEETING_20261021.md`。第一周未整体验收，不将第二周RF训练或后续正式实验写成完成。
2. **005S1六文件维护已完成并经独立生产核验。** constructor655b5d7a确认正常结束R4、备份USV_20261021_005S1_20261021T1540、三包生产build/11+28+23门禁及安装后28+23通过；instructor d090c61f实际source生产setup/import五模块和registry六hash全部匹配。正式SIX_FILES_DEPLOYED / USER_CHECK_READY / FOUR_SENSOR_INTEGRATION_CONTINUES，仅六文件可供复验。维护未自动start，用户仍唯一 ./run_vrx.sh start；用户新run不受本次离线工作干扰。
3. **005R4-FIELD本轮唯一现场探针已由instructor收口，不再追加图像采样**：detector节点/发布者为空且Search状态关闭；08—10在三个真实更新批次geometry均valid，记录几何离线重算每艇每批有337—341个非1 miss项。FPV仍未解决，源9.666/relay7.84 wallHz、RTF0.539960、唯一干净Qt十秒窗约6 wallFPS，未证明R4相对R1改善。
4. **四路代码已落地，physical启动图仍未接/默认off**：模型/bridge/source-monitor/小UI与LOS批内CPU优化已有实际代码。独立候选11项、64000格等价与六hash通过；LOS离线0.33079→0.10357s不冒称FPS改善。instructor已在原S1续派单艇opt-in连接及默认false/仅一艇/原入口离线预检，不动冻结六文件/生产/用户新run，不新Gazebo、部署、默认负载或后验；完成后再给单艇运行门槛。
5. **当前完成边界**：R4现场detector关闭及08—10所查三批恢复有局部工程证据；FPV、长期在线逐艇贡献、语音准确率、眼动跨机延迟和完整搜索闭环未整体验收。真实RF数据/模型及B2/B3效能仍未验证；路径平滑与大UI继续后置。
6. **协作接续**：constructor候选实际代码b685e083、review2288608b和维护完成655b5d7a均已核，不再写仅通知/代码待交/维护待授权。原Work消息入口存在，constructor独立读用户原话已获本人回执支持；无须重复授权。后续现场效果/四路physical与整体验收按实际证据，不新增竞争任务、不自动start或追加采样。

## 本周目标与当前重心

先把现有VRX框架搭到“操作员能用、设备状态看得见、操作过程能记录、数据能导出并接入后续训练”的程度。instructor重头是UI设计、统一按键和现有硬件联动。先获得志愿者数据、训练出RF模型、冻结所有科学数值，都不是这项平台准备的前置。

原计划第一周的观测简化/搜索流程整合仍保留；已验收的底层/API工作作为基础复用，不重做整个平台审计。API通过不能替代实际UI点击和设备验证。第一周完成度按操作与记录流程验收，不按“测试数越来越多”代替交付。

## 历史阶段记录：R1/R2反馈、隔离补丁与切换准备（以下细节不覆盖上方当前状态）

本轮instructor本人回报已读main FIELD2 blob f9120401471c876df9ed610f04b905f923f25fc0，并已沿原005续派constructor隔离补丁与测试，接受FPV+08/09/10优先、四路三层/radar-lidar待裁决及暂不平滑。main写前读入新提交7495731013d3d9dce0c4c0b13a0271b84be02d2d与005追加条款，续派已正式发布；constructor本批新领取/结果仍待本人证据。用户已要求下一版切换准备；隔离候选经instructor核查后，待当前R1复验结束统一安排，当前未部署/未称已修复。

用户已给R1第二轮反馈：FPV仍卡、眼动主观快不少、09/10持续红需取证，四路/路径待后继判断；R2未部署，不能归因给R2。生产source/build/install与Windows当前exe/会话冻结，不在复验中静默替换；R2可以隔离继续修真实采音和眼动链。首轮和闭环走查已发生，005 R1实际代码候选已完成。instructor在1ae7932f7d84cb3bc16c719e7fe83a7e8db6efb0发布CANDIDATE_READY / FIELD_FEEDBACK_PENDING，005整体仍RUNNING、未最终ACCEPTED。instructor亲核三个模块source-build导入同hash、独立53tests（0 skip）和bash-n通过；三包构建通过依据constructor报告。主agent已集成，原三只读及本批两代码子agent已回传关闭。现场整体流畅度、真实ASR质量与眼动端到端改善仍待用户，不重复诊断或等005全量完成才展示。

1. **现状入口与最短说明已先交**：constructor的005报告已核脚本入口`cd /home/cyz/vrx_ws && ./run_vrx.sh start`、默认h5_command_aware及脚本hash，专用desktop未核实。后续候选版只补实际变化/安装身份/已知缺口，不为启动说明重开全平台审计、不暗换模式。
2. **用户一键走查**：先看布局、地图/字号、选艇、控制权/SEARCH/mission状态、按钮语义和设备反馈，可先不START。截图或文字自然反馈即可，不要求长表、不要求向多个角色重复转述。
3. **小批修改与用户复验**：instructor把反馈整理为缺陷、使用偏好、需解释项，按理解清楚的优先问题指导constructor；只在真实歧义时追问。每批给改动与复验入口，避免第一次展示前整体大改。
4. **硬件与记录导出**：随后逐项联调实体按键、手柄、Windows眼动单接收链、语音、可信记录/导出和训练入口。可继续不冲突的只读核对；真实联调按instructor的具体范围与停止收尾进行。

不等待RF数据/模型、005全量完成或额外同类smoke；用户手动走查已有本轮授权，不要求重复批准。constructor已核run_vrx.sh start含Qt，桌面入口若使用则另按实际核对；--research-core会关闭UI/硬件，不能用来走查；--headless只关闭Gazebo窗口，默认h5_command_aware须如实说明，不冒称新的SEARCH/B2/B3模式。缺失SEARCH按钮列明，不用ROS CLI代替用户点击。

## 当前R1交付及复验边界

当前R1实际交付：显示图/视频缩放缓存、避免重复图像处理及每10秒聚合计时；语音errors漏显、按同命令关联的分层失败/执行反馈及E5/E，5/E、5安全等义解析；眼动独立tracker/UDP计数、Linux阶段计时与UNALIGNED诊断。合成离屏10000格重复绘制70.05→0.89ms仅支持该显示链改善，不是现场FPS；Whisper/PTT/VAD未改，眼动未证明端到端提速。原始采样、概率/Recorder及手柄映射保留。热图美化/布局/SEARCH大功能/轨迹优化仍后置；四传感器期望/binary与闭环事实核对保留，不改科学合同。

原三名只读子agent及R1两名代码子agent已由instructor review记录完成并关闭，constructor主agent已集成console；报告已有实际文件/hash、测试/构建和离屏前后证据。运行根Git HEAD UNKNOWN、实现提交NONE，通信提交不是完整源码快照；精确三模块SHA256见tasks/USV-20261020-005.R1.review.md。

用户保存/结束需保留的旧会话后，用原入口`cd /home/cyz/vrx_ws && ./run_vrx.sh start`重开；默认h5_command_aware含Qt/硬件，不加--research-core。start会清理旧进程，旧进程不自动加载改动，不对需保留会话重复执行。最少复验：①可先不START切FPV/全局页、切艇/鼠标，反馈哪页哪动作卡；②用户可控场景一次语音，看ASR原文/解析/策略/执行是否清楚；③Windows端在场时看眼动跟随、新tracker/重复/包Hz/Linux分段。短文字或截图即可，卡顿时一条ui_timing_10s辅助定位。若ASR原文错则查声学链；眼动按源样本或Linux耗时分段推进，UNALIGNED时总延迟仍未知。全套结束用`./run_vrx.sh stop`；本轮助手未运行。根据现场反馈沿原005小批修改，不重做全平台审计或重复smoke。


## R2当前协作：实际修复与生产切换分开

依据instructor@9e8bc6c7的005末节及跨线交接，constructor@3796d83f已报R2隔离候选（/tmp/usv_005_r2_hvSJ6a/、26离线tests），未部署、待instructor复核/统一切换。连续PTT采音候选针对逐块开关采音的机制；UI同源tracker重复/倒退过滤基于fixture，原depth1/latest_pending不是新优化。真实识别率/眼动端到端延迟仍未知，采音完整性与队列计数不能替代现场效果。

main已向既有Windows本地agent具名中转新tracker/Unity重复发送、本机单调时间/队列/阻塞、当前UUV构建和15555目标核对，详见handoffs/MAIN-TO-WINDOWS-VOICE-GAZE-R2-20261020-001.md。有证据再交隔离源新样本发送/显示最新优先patch；保留原始采样、时间、有效性及兼容协议；Windows音频仅实际15556路径才核。当前未有可调用Windows接收入口，本人ACK/执行待回执，发布不冒称已唤醒。

用户当前R1体验不等待R2全做完；R2也不因等待现场反馈而停止已授权隔离修复。候选hash/测试/前后证据准备后，等用户本轮复验结束，由instructor统一安排Linux/Windows切换与回退。不覆盖运行中的UUV.exe/配置或生产symlink源码，不新增麦克风录音、志愿者采样、RF训练、无人值守仿真；跨机未对齐仍UNALIGNED，不编总延迟。

## FIELD2后继：四路与路径

main判断见handoffs/MAIN-TO-INSTRUCTOR-FIELD2-20261020-001.md。constructor@4579f89a已回同run证据：当前command_aware / LEGACY_ASSUMED_BATCH，08/09/10在123次legacy更新均CAMERA_INFO_STALE、01—07有效，新离散事件0；先定位CameraInfo/freshness/时间域与实际profile根因，不能用视觉帧或旧sampler验收覆盖。FPV约5.4—6.5回调/s，同窗源Hz/源年龄/RTF未记录，Qt非已证唯一瓶颈；使用原只读总额度取证，不降低源采样或刷色。

四路建设期望保留；当前注册表camera/sonar/infrared/radar仅camera启用，用户lidar建议作为候选并列比较，不能暗换radar。逐项列展示占位、仿真传感器/物理近似、合法binary观测接线的实际/候选/缺失。camera占位不自动构成声学/红外物理模型，四画面不自动成四条独立后验证据。先清单和逐路资源预算，当前不增渲染/迁移模型或改科学profile；不以旧binary合同取消用户四路期望。

路径先区分同generation网格折线、generation替换和实际跟踪摆动；当前run163次generation有报告证据，但没有同generation轨迹/障碍对照，不能据此断言真实艇摆动。复杂轨迹优化当前无必要证据；障碍净空检查的最小简化是待评估候选，需用户理解必要性后再决定实施。真正改执行路径必须处理安全/成本/assignment一致性，本轮不改规划器或成本。

## 本批补丁与切换证据

- **观测链**：instructor亲读legacy逐艇resolve后昂贵LOS、CameraPoseSource动态monotonic/2s freshness，提出同批后排运算超时假设。先用假时钟/调换艇序使旧版直接反例失败，再做同批几何与判定时间快照；不放宽TTL、不改源戳，批开始已经陈旧/缺失的输入仍须拒绝，快照不跨批洗新。main尚未亲跑源码反例，不能把假设写成已定位/已修复。
- **FPV**：同窗源、relay、Qt定位最早瓶颈；30Hz配置上限不当实测源率。如需被动采样仅一次最多30秒且在原15分钟总额度剩余内，耗尽则用既有记录/离线链；不续时、不新开Gazebo/主动控制；缺同窗数据如实保留，离线前后证据不替代现场FPS。
- **交付/切换**：constructor主agent集成已有R2语音/眼动与本批修复，交隔离补丁、完整基线/候选hash、旧版失败与修后通过证据、必要回归/隔离构建及source/install一致性、待现场项、持久可取候选/备份与切换/回退说明；instructor核查后统一安排下一版，部署程序遇到存活的用户会话必须拒绝、不杀进程，用户保存退出后才切换。当前R1 source/build/install、用户会话及Windows exe不动，005保持RUNNING；用户现场复验与离线通过分别记录。不为本批另发竞争工程READY或扩科学合同。

## 本周最小交付

| 工作 | 必须交付 | 验收证据/当前限制 |
|---|---|---|
| 操作流程与UI | 启动/检查、选艇、接管、显式SEARCH/取消、导航/释放、STOP、记录结束/导出；显示当前艇、控制权、搜索责任、mission与记录状态 | 实际UI/按钮动作及对应状态变化；接管与导航不得被误显示为SEARCH。用户已给出真实使用反馈，完整UI流程仍未验收 |
| 统一按钮映射 | 实际设备的键/按钮—动作—适用状态—反馈—冲突处理表；保留合理兼容，查清语音取消、SEARCH取消、导航取消等语义 | 真实按键操作证据；main不凭记忆给键位定值，具体映射由instructor按实际资产设计 |
| 现有硬件联动 | 手柄、眼动仪、麦克风/语音及现有Windows↔Linux桥接的启动、连接、断连/恢复和状态反馈；清楚提示未连接设备 | 分设备标记实测/未连接/待现场；优先保证核心操纵链，未连接可选模态不冒称通过，也不自动阻断核心流程 |
| 会话与源身份记录 | participant/session/run/epoch/艇/段、按钮/控制事件、源/接收时间、合法位姿、硬件有效性和缺测/断连/停止原因 | 源身份真实来自采集端并绑定owner确认；不能由Recorder倒填新身份；对照实际操作核对记录 |
| 导出及训练入口 | 会话结束后输出可读数据和manifest；按会话/参与者分组、因果特征、可配置t+H离线标签、训练/验证入口及模型版本输出接口 | 用明确标记的工程样例验证格式/拆分/标签和入口；RF模型文件可缺失，不能因此阻断UI。不是正式训练完成 |
| 操作说明与联调结果 | 一份可执行的启动→设备检查→任务操作→停止→导出说明，配一份能力/缺口清单 | 开发者工程联调可用来验证可操作和记录完整性；注明非志愿者数据、非正式预测/协同效果 |

各项可放进一项小而完整的准备任务，也可按真实依赖拆分，由instructor唯一派发。不要为每一行单独增加审批。涉及实际运行的验证由instructor规定有界范围；没有设备/执行权限的项目保留待现场，不用CLI或fixture伪装真实UI/硬件实测。

硬件接入/可记录不改变RF主线输入：当前最小候选是运动状态与当前操纵，眼动/语音不自动升级为主实验必需特征。可选设备失效要如实显示和记录，不能让模型或UI暗中补值。

## 与004R2收口后的衔接

004R2与004已由instructor正式ACCEPTED（限定无模型B3门控/回退工程），review在0f2c80e7；其直接核最终hash与原始事件、重算20路STOP后各360条零值，最短11.634358088s。main读取review，不冒称独立本地复验。004复验冻结解除；004R历史失败/额度耗用保留，004R2额度已消费且完成，不再将同类smoke设为用户看UI的前置。

005已从原PHASE_1_STARTUP_AND_TARGETED_DIAGNOSIS推进到R1 CANDIDATE_READY / FIELD_FEEDBACK_PENDING，整体保持RUNNING；旧DRAFT/PRODUCTION_BLOCKED_BY_004R及“尚无生产修复”都不是当前状态。继续唯一005链，不新增自动Gazebo/START/操纵/STOP；用户亲自运行候选版，不把离线测试或底层通过当现场UI/硬件/RF/效能验收。

## 后续依赖

1. 平台准备：上述UI、硬件、源身份、记录/导出和训练入口就绪，形成可执行采样流程。
2. 志愿者实际采样：按原月计划核实所需报备/审批、受试者说明及数据使用安排；给出实际操作者范围、会话/时长预算、任务情境和分组方案后组织。当前未要求招募或正式采集，不声称报备/审批已完成。
3. RF开发训练/验证：使用可追溯实际操纵数据，按独立参与者/完整会话划分，选择H/特征/超参数并与当前位置/恒速方法比较；完成版本化模型。
4. 冻结与后续评价：冻结模型/数据处理/任务参数后，部署验证并开展另行安排的pilot及正式B2/B3评价；正式在线评价参与者与训练参与者隔离，不能把同一轨迹的窗口/replay当独立参与者。

原月计划第二周“不同目的地任务”仅作采集情境参考；标签资格和责任语义按当前显式SEARCH合同，不把NAVIGATE目的地当搜索中心。后续日期依据准备、数据与实际审查条件推进，不为追日历虚构就绪状态。

## 负责人及保持OPEN的事项

main维护本计划、RF数据语义和研究合同；instructor负责UI/键位/硬件/记录框架设计及唯一工程派发与验收；constructor实施；overleaf区分计划、已实现和已验证事实。

H、有效年龄/缺测/重规划阈值、R/tau/B、具体人数/会话数和正式统计设计继续OPEN。UI/记录/导出按参数化接口准备，不硬编码拍脑袋数值；可以在数值未冻时完成框架，正式数据处理或实验前再冻结对应配置。

## Windows Unity/Tobii桥接纳入（main本人ACK，2026-10-20）

依据：reports/WINDOWS-BRIDGE-20261020-001.md@c636b7fd11c6daabb5c1287ff823b2c0b1251fe7。main已读完整报告；接受其LOCAL_AUDIT_COMPLETE / LINUX_INTEGRATION_PENDING边界，不将本地文件存在或进程可见记为设备/端到端通过。工程接口交接见handoffs/MAIN-TO-INSTRUCTOR-BRIDGE-20261020-001.md，沿instructor→constructor原链；005阶段按上述用户走查优先落实，instructor已在0f2c80e7手动交接中本人ACK桥接；constructor接口核对仍待本人证据。不新增竞争READY或无人值守运行额度。

生产整合目标：Windows Unity/Tobii采集→UDP 15555→Linux现有单接收→/tobii/gaze→UI/Recorder。仓库旧双LSL链仅作历史参考，不恢复或复制覆盖生产环境。Linux实际接收器路径/source-install身份/消息字段及发布者数量由constructor按instructor安排核对。

| 本周整合项 | 记录与验收要求 |
|---|---|
| UI设备状态 | 区分发送进程可见、UDP收到、眼动有效、映射可用；显示无效/超时/恢复。接收新鲜度与设备采样新鲜度分开 |
| 时间与重复 | t是更新时Unity时间，不能证明真实采集年龄；tracker_us保留原单位/时钟域与重复事实，传输包数不当设备样本数；未测时钟偏差不报跨机延迟 |
| 显示映射 | 坐标属于Windows Unity窗口；实际观看屏幕/远程镜像内容区、DPI、黑边、翻转与角点/中心须现场核验，不能直接当Linux控制台像素 |
| 来源与记录 | 包缺可信session/epoch/vehicle/authority等源身份，不接收端倒填成RF证据；保留代码/DLL hash、配置、无效/缺测/重复/重启与身份缺失状态 |
| 分层联调证据 | 同次会话逐层核对Windows→UDP→ROS→UI→Recorder及失效/恢复和导出；当前有效采样、Linux实时接收、映射和完整导出均未验证 |

眼动接入不自动成为RF主实验必需特征；硬件/UI/记录框架准备继续，不等待志愿者数据、训练模型或最终H。004R2复验冻结已解除；只读核对可继续，生产改动按用户反馈分批进行，现场主动联调仍由instructor明确范围，不阻塞首次查看现状。
