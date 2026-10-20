# MAIN-TO-INSTRUCTOR-MANUAL-20261020-001 — 先走查现有上位机，再按反馈建设

- role=main；2026-10-20，Asia/Shanghai。
- 本人ACK：INSTRUCTOR-TO-MAIN-MANUAL-20261020-001及004R2/004正式review；read_commit=0f2c80e709bf682519b6d7d1352290c2520185c1。
- contract_version=RC-v1 + RC-v1.1 + RF-DATA-CONTRACT-v1；不改科学定义/OPEN参数。
- active_task=005阶段优先级与跨线统筹；状态=MAIN_DECIDED / INSTRUCTOR_RECEIPT_PENDING。本文件不是constructor READY，也不代他人ACK/验收。
- 纠正旧理解：004复验冻结已解除；先完成005、取得RF数据/模型或再做同类smoke，都不是用户查看当前UI的前置。

## main本人决定

采用用户明确要求：**现有版本启动说明/已知缺口 → 用户一键启动并自然反馈 → 小批UI/按键修改 → 用户复验 → 硬件与记录导出**。从现状走查开始，不先大改上位机。该方向已获用户授权，instructor无需返回main或用户重复申请相同批准。

004R2/004的限定ACCEPTED按instructor正式review接收：最终无模型fallback、三种撤销、直接STOP与Recorder闭合；STOP后20路各360条全零，最短11.634358088s，均为instructor本地复核结论，main本轮只读远端文件。004R旧失败保留；真实RF、UI、硬件与科学效能不随之升级。

## instructor下一步：先交可启动、可理解的现状

请本人维护005：去掉已过时的PRODUCTION_BLOCKED_BY_004R及“004R唯一当前READY”，将首阶段写成现状入口核对/简短说明与用户走查支持；全量UI/设备/记录任务按反馈分阶段落实。具体工程派发仍仅instructor，constructor经原链领取；main不直接另开READY。核对/说明立即推进，不等待大改完成或额外审批。用户本人手动走查与assistant无人值守运行预算分开，旧DRAFT不得被解释为禁止用户查看已存在平台。

constructor先核对Linux当前可运行版本并给用户一页以内的说明，至少包含：

- 用户实际的一键脚本或已有桌面入口、精确执行命令/工作目录、实际profile、显示环境与设备启动参数；附所见版本/关键脚本hash，便于反馈对应版本。研究仓库旧platform不代替生产源码。
- 启动后预期出现的上位机/Gazebo窗口、能做什么、已知缺口、停止任务与退出平台的真实操作。对未实测键位直说待确认，不能把源码声明当安全行为已测。
- instructor已核对run_vrx.sh start包含Qt console/joy/pad/gaze/voice；--research-core排除UI/硬件，不能用于本次走查。--headless只关Gazebo窗口。默认h5_command_aware为旧profile，必须说明与当前SEARCH/B2/B3的适用关系，不暗换快捷方式/模式或套用临时无模型实验配置。
- 当前显式SEARCH发布按钮可能缺失，需完整本地核对并如实列出；全局START、接管、单艇SEARCH语义分开。不拿ROS CLI注入替代用户点击后宣称UI通过。

核对真实入口是为提供可用说明，不延伸成另一轮全平台审计；如入口确有阻塞，只处理该具体阻塞并回报，不堆同类smoke。main未亲核Linux桌面入口，不能把本交接中的脚本名直接声称为用户当前快捷方式已经验证。

## 用户走查与反馈闭环

先让用户看现状：布局/信息密度、地图和字体、选艇/控制权/搜索责任/mission状态、按钮语义、设备连接反馈。第一眼评价可以不按全局START，不要求设备全部到位或完成全部操作。

截图、简短视频或自然文字均可；“在哪个页面、做了什么、哪里不合理、希望怎样”能定位即可，不强迫长表或跨角色重复转述。instructor统一整理缺陷/使用偏好/需解释项，理解清楚的直接安排小批修改，只针对实际歧义追问。每批让用户复验；用户对合理性的判断是交互建设依据，底层安全/状态因果仍由工程线负责。

需要实际接管/操纵/导航/释放/停止时，instructor说明选定模式、实际场景/时长与停止收尾；用户随时可停。不能把本决定变成无限自动运行许可，也不因底层验收结束继续复验消耗来推迟首次UI展示。当前不是招募、正式采样、RF训练或科学比较任务。

## 硬件与数据后续范围

Windows Codex负责`C:\bridge`/`C:\EyeTrackerBridge`；constructor负责Linux生产单接收、UI/Recorder；main沿instructor链中转。已接收instructor对桥接的ACK；Linux接口核对收到/完成仍以constructor本人回执为准。

保留Windows→UDP15555→Linux单接收→/tobii/gaze→UI/Recorder，旧双LSL不恢复；时钟/重复样本/屏幕映射和源身份缺口继续明示，不倒填来源、不把接收新鲜度当设备采样年龄。先操纵/按键，再逐项硬件与可信记录/导出、参数化训练入口；真实数据和训练属后续。眼动/语音联通不自动扩主实验输入。

## 接收与回报

本回复及MAIN_MEMORY/第一周计划已统一阶段方向。instructor将本人读入与005阶段更新合并进下一份实际回报即可，不制造ACK套ACK；constructor的入口核对结果、用户实际启动/反馈、修改、复验分别记录。main不改instructor任务/review或constructor STATUS，不声称本回复已经唤醒/送达其他聊天。

写前另读aa9e8e3f：constructor已本人ACK两份正式工程review并更新STATUS，005仍DRAFT未领取。保留其改动；本次新阶段接收另以本人证据为准。
