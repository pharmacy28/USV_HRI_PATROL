# instructor 接收与记忆审计回执 — 2026-10-20

- role=instructor；read_commit=`27c5303cd1bab4097b83582e13a96c88ce4f659c`；contract_version=RC-20261020-v1；active_task=003R review / 003 复审。
- 已真实读取 MAIN_MEMORY（blob dcdad6044fbf1b9f8c86a245bb77be9ffa78237a）、INSTRUCTOR-20261020-001（blob 47c056c665cdbee911ac096049e087d7419d9375）、PROTOCOL、ROLE_PROTOCOL、STATUS、003/003R task/report、003 review、002 review、LOCAL_RECEIPT。
- 本地只读：003R 详报、source/install hashes、原始 time_series/manifest；范围和直接核查结果见 003R review。本轮没有启动仿真、修改生产代码或清理任何资产。
- 纠正记忆：003R 已 DONE 而非未领取；最终时钟配置已有唯一新 run；003R/003 当前 API 级工程 ACCEPTED；002/004D 已 ACCEPTED；TAKEOVER/NAVIGATE 不等于 SEARCH；旧 platform 不能替代生产源码；离线测试不是运行证据；UI/B3/encounter/正式实验仍未验证。
- 当前 READY/运行/阻断：旧任务文本 READY 为历史授权，已消费，不可重跑；无新 READY、无本轮运行；工程时钟 blocker 已解除，科学 OPEN 保留。constructor 角色 ACK=PENDING，不能代签。
- MAIN_MEMORY 按本次用户授权追加 instructor 审计更新，保留 main 原快照与所有权说明；未覆盖 constructor owned STATUS/报告/LOCAL_RECEIPT，也未覆盖 main 交接。
- 下一步：constructor 仅补本人角色/记忆回执、状态与时间差文档说明；无新 smoke；main 接收本 review 的 PAPER–PLATFORM HANDOFF 后再按依赖决定独立后续任务。未发送其他聊天消息或启动后台调度。
- INSTRUCTOR-20261020-001 接收=ACKNOWLEDGED；工程 review 与 instructor 回执完成。交接整体联动闭环仍待 constructor 真实 ACK，不能声称所有完成标准均已满足。


写入前并发检查：重新读取 HEAD=`acb5760c0b7aba1b1fcfcaf92ebd5b1429714bd2`，相对首读基线仅新增 overleaf 角色回执，已读取并保留；本次所写四个路径无并发修改。overleaf 回执的接收/科学内容以其原文为准。


## MAIN-20261020-002 / RC-v1.1 本轮接收
- role=instructor；read_commit=`b6f0b81e3d66f2cd9081efe60a516c437317c43d`；contract_version=RC-v1 + RC-v1.1；交接接收 ACKNOWLEDGED（仅 instructor 本人）。
- 已读取新交接、RC-v1.1、main 最新记忆、STATUS 与 constructor 本人 receipt。此前 constructor PENDING 已解除；不代表其已读本次004任务。
- 003/003R维持API级ACCEPTED，不重复评审或运行。新唯一 READY=USV-20261020-004（B3门控/失效回退），只允许一次新有界smoke，不等待RF训练，不冻结H/阈值。
- 当前生产接线已定向只读核查，RF不可用仍返回错误；本轮未实施、构建或运行。004发布不是执行完成，constructor新ACK仍待本人提交。
- D2/D3/D4已记入004后继要求，本次不同时实施观测/endpoint。参数依据表限已有配置日志，不新开标定。
- 004B本地原报告已亲读并计算hash；公开精简入口为reports/SLIM-004B-evidence-index.md；不追签历史ACCEPTED、不重跑。
- main论文CHANGES_REQUESTED与四项小修由overleaf负责，本轮不编辑母稿、不代签overleaf新交接ACK。


## 004回传接收与审查
- read_commit=c9bfa8b484f8e2f2ba5bd565d411fe9a95baa6f5；role=instructor；active_task=004 review；review=CHANGES_REQUESTED，详见tasks/USV-20261020-004.review.md。
- 亲读本地详报、定向源码/测试和原始manifest/time_series；版本hash及log hash匹配，无新运行或测试。保留无模型fallback/CANCEL/STOP局部运行事实；发现接收时刻绑定当前段不能证明输入来源、同段pose时间倒退未拒绝。20路实际推力缺测，NAVIGATE/RELEASE本run未观察。
- constructor本人004接收/交付回执已读取，不再PENDING；本review的新接收仍待本人，不代签。
- 先离线最小修正/测试/构建与身份回传，004运行额度不增加；后续004R需独立READY，当前未发布。不进入endpoint或正式实验。

- 写入前复读HEAD=a9af355be7ed85303a2f99a704ee7eba94ae13f0及角色协议/main记忆新内容；并发变更保留，未触及本次两路径。


## 004 OFFLINE R1与004R路由
- role=instructor；read_commit=52f416e2c8391f14322e83351da06bd58f771321；已读constructor离线R1/最终004报告、STATUS、main最新记忆与自动化交接资料。当前消息只推进004审查/RF交互，不据仓库授权描述新建接收器或后台实验。
- 源码/build哈希直接匹配ad6b320e...；两项源码门控收口，亲跑26 tests通过；完整166 tests和构建依据constructor报告。004整体仍CHANGES_REQUESTED / RUNTIME_PENDING，不借旧run验收新版本。
- 已发布独立004R READY：唯一一次新有界smoke，最终回退/三种撤销/20路直接零推力闭环；本会话未启动仿真。
- 用户RF真实数据训练要求已提交INSTRUCTOR-TO-MAIN-RF-20261020-001；等待main本人决策/ACK，不代裁数值或启动训练。


## 第一周统一计划与RF合同接收
- role=instructor；read_commit=c821fbb92c3e3cd6d422f8c68a1a34e0952c74ac；本人ACK MAIN-20261020-003、MAIN-TO-INSTRUCTOR-PREP/RF、RF-DATA-CONTRACT-v1、WEEK1_PLATFORM_PREP_20261020。不再记“等待main合同”；main已作本人决定。
- 004R仍READY，最新目录/constructor receipt无其领取回执；STATUS“无004R”过时，应由constructor本人更新。instructor不代ACK、不覆盖STATUS。
- 已只读定向核对真实console/pad/launcher/bridge入口，准备005 DRAFT；不改004R生产source/install、不启动仿真或硬件。无竞争READY或新增运行额度。
- 第一周以UI/按钮/现有硬件/记录导出与训练入口准备为重心。005草案列现有资产、显式SEARCH UI缺口、完整操作流程、按键表、源身份和RF数据合同接入；待004R收口/工程依赖复核后转READY。
- RF首个候选运动状态/当前操纵，眼动语音非必需特征；分组/标签/源身份按已冻结合同，H等数值OPEN。不启动志愿者招募、正式数据采集/训练。真实硬件未验证如实待现场。


## 004R失败审查与后继
- role=instructor；read_commit=b758f6dd1906a2db8213f9b9f7f5f1d14e1f8ed0；亲读004R报告/本地详报/驱动脚本及关键原始hash。审查=BLOCKED/RUN_CONSUMED；错误为临时client/cleanup服务类型，不声称生产Planner失败。20路被动零不构成STOP验收，004仍CHANGES_REQUESTED。
- 新唯一READY=004R2，先隔离无Gazebo驱动预检（std_srvs/SetBool正反与退出码），通过/回传准备证据后才可消费一次新会话；继承原运行边界，不无限补跑。004R旧READY不可重领。
- UI005草案保持，instructor不依赖生产基线的UI设计/文档可继续，不把第一周准备无限挂在RF或smoke上。未修改生产代码/未启动Gazebo。


## 004R2审查与用户手动验收路由
- role=instructor；read_commit=6bfc5dcc88f5b2b3aad5e515f7a713acf72759a1；004R2及004限定工程ACCEPTED，亲核最终source/build/install与原始4份hash/事件，独立重算20topic各360零、最短11.634358088秒；本轮无仿真/构建/新测试。
- 004R原BLOCKED历史保留，复验冻结解除。005仍DRAFT，下一步用户现有上位机手动走查；用户要先亲看UI反馈，再指导constructor，已向main提交INSTRUCTOR-TO-MAIN-MANUAL-20261020-001并请求下一步判断。不要求先完成RF/005/更多smoke。
- 已ACK MAIN-TO-INSTRUCTOR-BRIDGE，跨机分工与Linux单接收/15555/UI坐标/新鲜度/身份边界纳入005后继。没有代签Windows端到端或硬件实测。


## 用户首轮UI使用反馈与005 READY
- role=instructor；read_commit=8d145cf5aaa59276f14e17d611f955665817e8a3；已ACK MAIN-TO-INSTRUCTOR-MANUAL。005由DRAFT改READY第一阶段：核实启动命令/最简说明、用户已反馈的卡顿/语音/眼动问题分层诊断和小修，不先大改布局。
- 用户明确要求constructor使用sub agents，任务已写主agent+3子agent分工/共享文件集成边界；无独立竞争运行者或自动Gazebo许可。用户截图用于静态布局/profile，运行性能需实测。
- 已向main/inspiration提交用户迷惘与解释要求，按RF合同讲清当前预测对象、数据/标签、待完成链路；眼动语音非主RF必需输入，不因此否认它们的使用问题。


## 005从只读诊断转R1候选版
- role=instructor；read_commit=0e3dfee02d8422f5827159c18a2ca7b0fc40a9b6；已本人读取MAIN-20261020-004和MAIN-TO-INSTRUCTOR-LOOP-FEEDBACK、005首报与三子agent最终输出，确认三者完成并close；尚无生产修复，不能称已优化。
- 用户当前明确优先整体卡顿/语音/眼动，已直接通知constructor继续005最小实施并同任务追加R1要求，不重复调查/不另开竞争任务。已证实voice parser错误UI漏显；Qt共享线程/图像处理是热点假设未实测；tracker样本与UDP包区别及跨机UNALIGNED是已知测量缺口。要求隔离基线+真实小修/测试/build/hash候选版，现场效能待用户。
- binary与传感器数独立，四路期望保留等待事实对应，不暗改合同；原始采样不为UI优化降频/洗时间。无新增自动Gazebo/控制会话权限，不大改布局，热图美化后置。


## 005 R1可启动候选核查
- role=instructor；read_commit=b1d5a4a5385fc893c7e8f9552c0ac240184fcdac；已收到constructor实际R1代码/53tests/三包build/最终回传，亲核三模块加载source-build同hash，独立53tests通过（2.37s）、bash-n通过；无Gazebo/实际设备运行。
- 结论CANDIDATE_READY / FIELD_FEEDBACK_PENDING，详见tasks/USV-20261020-005.R1.review.md；005仍RUNNING，不自称整体/设备ACCEPTED。卡顿显示缓存/图像路径有离屏改善，真实整体响应待体验；语音分层反馈和安全等义解析已改、ASR未训；眼动补诊断、未证实端到端提速。交用户用原一键入口复验，不新增无人值守运行。


## 005 R2实际修复与可切换候选
- role=instructor；read_commit=fe5cad6aebdfd14ac197df56cc4de595e4cbc132；本人ACK main FIELD2 blob f9120401471c876df9ed610f04b905f923f25fc0。005仍RUNNING，R2候选可受控切换，未部署/非ACCEPTED。
- 亲核legacy批内CameraInfo freshness偏置补丁，独立20tests通过；切换故障注入全通过，FPV探针3tests通过。详情tasks/USV-20261020-005.R2.review.md；FPV原因与修复仍OPEN，不能用地图缓存改善替代。
- 用户本轮排障新增独立<=30s只读窗口已告main，Qt已退出最终0采样，未新开Gazebo/操纵。生产R1冻结，用户正常结束会话后按脚本apply才部署，失败回滚；下次真实UI会话再用单次探针。
- 四传感器main决定已接收：先FPV/08–10，四路三层清单保留，radar/lidar第四路OPEN，不加入负载、不实施轨迹平滑、不改科学参数。


## 005 R3核查/R4用户纠正
- role=instructor；read_commit=8b6e0b7a0a4e0af54df3e5ef86be64492e7d8674。R3 CANDIDATE_READY/FIELD_PENDING；独立16tests及九文件切换故障注入通过，亲读relay/Qt与wrapper，生产未部署。FPV本人同窗数据及双探针重叠限制见R3 review，源端吞吐仍OPEN。
- 当前用户新run实际仍R1，08–10仍STALE，没有R2/R3运行恢复证据；不以热图颜色替代资格/贡献。用户不知切换输出位置，新wrapper持久日志并失败不启动。
- 用户再次明确四传感器未完成、禁真实检测、区分preview与低频观测。已追加R4实际隔离实施并向main发送SENSING-SPLIT交接；未以科学参数待定阻断默认关detector方向。维持ideal0.25simHz/belief4s、video30simHz名义配置，四路参数/相关性与第四路main裁决。当前会话不改不控。
