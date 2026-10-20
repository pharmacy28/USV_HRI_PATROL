# main 共享工作记忆 — USV 研究统筹

更新日期：2026-10-20，Asia/Shanghai。维护者：main。研究语义：RC-20261020-v1 + decisions/RC-20261020-v1.1.md。
用途：六角色共同读取的研究和事实基线；不是平台完成证明，也不代表其他对话已经接收。
最新统筹补充：main本轮已核对六角色；通信读取基线f97997b3c55c49feb9cd69dd5cfd3091d0124711，论文f8de4da17dbc3cc70eeedca409376c530cf9547b。第一周平台准备优先已由用户明确并采用；004离线修复已核查、004R READY但未见constructor新ACK/报告；RF合同与PREP回复已发布；exploration本人交付已由main接收。main定时接口当前enabled=true，后台成功及其他接收器仍未验证。见第17节与handoffs/MAIN-20261020-003.md。
论文验收历史依据：5748cf31的R1修订、main当时精确源码独立编译/局部PDF复审，以及3ef5f2fa的004任务/回执/004B索引，详见第12节。当前事实见第1—9与17节；第10—16节保留历史快照。此次检查以当前仓库和用户指令为准，不声称读取所有历史对话或其他角色内部记忆。

## 1. 角色与工作目标

| 角色 | 负责 | 当前状态与下一步 |
|---|---|---|
| exploration | 文献整理、版本/原文证据、直接交付inspiration | 本人ACK及Xie2011证据包1b5067ea已读；main接收完成。后续按具体论断缺口增量核验，不扩大主实验 |
| inspiration | 向用户解释全貌、讨论反例与研究取舍 | 截至本轮三分支核对未见本人ACK或INSPIRATION_NOTES；先接收当前基线/Xie证据再讨论，不代用户作科研决定 |
| main | 科学合同、计划优先级、跨线状态与评审 | RF最小合同、PREP本人回复与第一周计划已发布；本轮同步共享记忆和全角色交接 |
| instructor | 平台设计、唯一工程派发与验收 | 004离线修复核查完成，独立004R已READY；接收PREP/RF回复，将后继重心转到UI/按键/硬件/记录导出 |
| constructor | 实际平台实现、测试、报告与本人STATUS | 最新为004 OFFLINE_FIXED / RUNTIME_PENDING；004R尚未见本人领取/执行回执，由instructor沿原任务安排 |
| overleaf | 唯一论文母稿、引用与论证 | PAPER-001 R1已main ACCEPTED；待本人ACK该review与最新统筹，按真实新证据增量维护，不重做已收口返修 |

exploration提供有来源的文献证据；inspiration据此与用户讨论；main统一有依据的新结论和用户明确决定，工程交instructor、母稿交overleaf。用户已明确的第一周方向无需再次批准，助手候选不能自升为合同。main不向constructor另发竞争工程READY。角色名、仓库发布、本人ACK、后台启用、执行和验收必须分别记录。

## 2. 当前研究主线

在操作员可接管、导航、切艇和中断任务的多 USV 概率搜索中，**以人控艇未来位置表征显式SEARCH责任，是否比只利用该艇当前位置改善协同？**

主对照 B2（当前位责任）与 B3（有效未来位预测，否则回退当前位）。收益是待检验假设。研究对象是未来位置信息进入责任分配后的决策价值；不主张首次预测人类行为，也不把 RF、Bayes、Lloyd/K-means、A*、Hungarian 的使用本身当创新。

用户明确要求假设简单、先冻结可推进的主线。当前不扩展为完整感知标定论文、主动询问/换艇建议系统或新路径规划/动力控制论文。眼动、语音和手柄是既有接口资产，眼动/语音不是 B2/B3 主比较的必需输入。

## 3. 已确认的研究语义

1. 平台是 VRX/Gazebo/ROS 2 Humble；十艇 WAM-V 是现有工程配置。Unity 算法/桥接资产为历史或参考材料，不能充当当前 VRX 运行证据。
2. 单静止目标、已知可搜索自由栅格、障碍概率为零、自由格目标信念归一化。
3. 命令、眼动、语音、手柄、目的地、SEARCH 声明和预测不能直接改变目标后验；合法传感器观测才是证据。NAVIGATE 期间也允许合法观测。
4. 接管只改变执行控制权。显式单艇 SEARCH 才激活人工搜索责任；离散操作、状态保持，不要求预先给目的地。全局 START/STOP 不等于单艇 SEARCH。
5. SEARCH 有效时 B2 使用当前位；B3 使用有效的未来位预测，失败时回退当前位。未声明 SEARCH 时两者都不插入人工搜索中心。RF 缺失不能阻断整个规划器。
6. NAVIGATE、取消、释放、控制段结束、切艇撤销旧责任；新艇重新声明。NAVIGATE 目的地不自动成为搜索中心。执行锁定与搜索责任分开。
7. 固定人工中心时，全体可搜索自由格仍进入责任域，只更新自主中心。零权格目标贡献为零，但几何责任仍定义；不能手动删掉所谓剩余区域。规划责任不是已经感知或覆盖的证据。
8. 先产生中心，再对合格艇—中心配对算 A*，由路径构造代价，再 Hungarian 分配和共享覆盖/跟踪。A* 不保证动力学可行。具体代价仍需冻结。
9. B2/B3 共享初始先验、观测机制和公共算法配置；轨迹不同后实际后验不必相同。相同随机种子也不保证相同观测序列。
10. B4 是离线真实未来人工轨迹的完美信息参考，不是目标真值 oracle，也不是保证成立的效果上界。RF 仍是候选；CV/当前位置是预测参照。
11. 目标选择权、执行权、搜索承诺/计划修改权限是本研究分析概念，不能未经原文核实归为 Dalmasso 的原始三分法。
12. belief 明确为给定几何/控制输入的 sensor-evidence 模型，不计人工动作选择的 likelihood，不声称利用全部人类信息的真实后验。UNKNOWN→p=0不保证真实后验保守；零归一化分母是模型/数值故障。

## 4. 简单成功判据与统计口径

理想连续判据 T_E^cont 为任意**同一艘**艇距离真实目标不超过 R（论文 rho_E），连续保持 tau（论文 tau_E）。实际主端点 T_E 为 sampled sustained proximity：连续有效合格样本的时间跨度达到tau，在当前样本时刻触发；不插值、不倒签。离开/无效/超限缺测重置，不跨访问或艇拼接时间。有限采样不证明样本之间物理连续停留。自主、人控、NAVIGATE同等评价，不加朝向、FOV或检测概率门槛。

这是 sustained-proximity / effective target encounter，不是视觉检测、人工确认或救援。隐藏真值仅在仿真观测生成器和独立encounter评价器内部使用；前者输出合法观测，后者输出事件/时间供记录与终止。规划/推断不接收隐藏目标位置或目标专属距离；公共地图上各假设格的几何距离仍是合法输入。

拟定主指标：共同预算 B 下遭遇时间的 RMST；主效应 RMST_B3(B) − RMST_B2(B)，负值支持更快遭遇。预算内未遭遇的有效试验必须保留。行政 STOP、崩溃和无效时钟需另行处理，不能随意混作普通预算删失。

R、tau、正式 B 仍 OPEN。main新补充已冻结：主实验正常成功仅encounter；POSITIVE/旧Gamma确认不能独自宣告成功或提前替代终点；合法T_E<=B计成功，T_E=B时成功优先于自然预算。位姿采样不插值、不回填，缺测超间隔/无效/离开重置；具体采样节拍与最大间隔仍待配置核对。正式统计截止不能因消息延迟扩大。上述是研究要求，现有预算验收不等于encounter实现或删失验收。

## 5. 工程事实快照

本轮main只读核对通信分支f97997b3、instructor review/任务、constructor报告状态与本人receipt；不声称访问实际/home/cyz/vrx_ws或独立重跑。最新review/独立任务优先于较早STATUS。constructor STATUS仍写“尚无004R”，是待其本人纠正的旧快照，main不覆盖其文件。

| 工作 | 当前状态 | 证据与限制 |
|---|---|---|
| 001静态审计 | DONE / ACCEPTED | 历史审计，不用旧“缺SEARCH”否定后续实现 |
| 002 / SLIM-004D | instructor ACCEPTED | 预算/STOP/Recorder工程验收，非正式实验 |
| 003 / 003R | instructor ACCEPTED，限ROS API SEARCH/B2 | 最终sim clock阻断解除；实际UI未观察，非B3/encounter验收 |
| 004 | CHANGES_REQUESTED / OFFLINE_FIXES_VERIFIED / RUNTIME_PENDING | f884a8ce中instructor核查两项源码修复并独立26 tests通过；完整166/build依constructor报告。最终Planner source/build SHA256=ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84 |
| 004R | 独立READY / CONSTRUCTOR_ACK_PENDING | f884a8ce已发布；未见004R本人ACK或运行报告，不称RUNNING/DONE。至多一次最终回退/撤销/STOP后20路实际推力持续零复验；不采集训练数据 |
| 第一周平台准备 | 用户方向已采用、计划和main回复已发布；instructor新ACK/工程任务待回传 | UI、统一按键、现有硬件连接与反馈、源身份记录/导出和训练入口。当前UI/硬件真实联调仍未验证 |
| RF真实来源与训练 | 最小数据合同已发布；真实来源链/数据/模型未验证 | 无模型不阻断准备；无法核验源身份时仍保守回退 |
| encounter、正式B2/B3与RMST | 未验证/未报告 | 不用工程验收或文本ACCEPTED升级科学结果 |

004旧run=f87fc7b8a1934a52ada1fbc1fd7d4828只支持修复前SEARCH→当前位fallback/CANCEL/STOP/Recorder局部事实；不支持最终返工版本，20路实际推力和NAVIGATE/RELEASE缺口由004R收口。有效预测仅离线可信fixture，不是真实RF验证。004R原任务的工程预算不是正式B；本轮不追加运行额度。

002 run=7904539e7ad44213b4baa971245e3bb9，deadline=82.540s、发布=83.000s；0.460s延迟不能延长分析预算。10/10 path STOPPED、20/20 thruster=0为该次证据，encounter_censoring_validated=false。003R最终run=5c84c3736225450eb5d0759cd1498f59，77条相关记录1—44s；邻近位姿差0.0287m，0.024s是Recorder外层差，源plan差0.172s，非精确同步。行政STOP不替代自然预算验收。

SLIM-004B历史索引reports/SLIM-004B-evidence-index.md：instructor亲读原报告并记录SHA256=755f89fbeb487ee3dae056731fb9496d26e95afa54ee4bc9c9b14569a8170083、183 tests/80唯一事件（48负更新/32ABSTAIN）。main只读公开索引，精确UNKNOWN目标runtime分支未重现，不追签历史独立验收。

## 6. 源码、论文与资产入口

- 实际运行工作区：/home/cyz/vrx_ws；根无有效 Git HEAD，实现提交 SHA=NONE。研究仓库和通信 SHA 不是运行平台 SHA。继续记录修改文件 SHA256、dirty 状态、构建和运行证据，后续由 instructor 安排可复现源码快照；不能把文件 hash 等同完整环境复现。
- 本地版本化研究仓库：/home/cyz/USV_HRI_PATROL；此前回执 main@5f263c694f3d601bf1596bb92b0849d98f7e677b 且有未提交决策，不清理或覆盖。
- 远端 main@749a4a06db0b24d0fdd3bcb47618a365dfa5bdfa 是旧仓库快照，不是当前生产源码。通信分支和论文分支中的旧 platform/ 不用于覆盖本地。
- VRX 上游 humble 固定 dc30ed8d17aa1083fd872edad9c77c69896d2b07；项目变更通过本项目 patch/setup 管理，不推上游。
- 通信：coordination/work-20261020 / docs/coordination/。
- 论文：paper/overleaf-20261020 / paper/manuscript/main.tex。R1审查快照=5748cf311cfa26e1db2ad9bc0d15f9c2f369abc3；正文提交27059ea8cb009c973ad4a6d0cf906afb8c801c64，SHA256=758058ae1c24dcfa70b7946cf444eaf61573bd6c00461e78c906c056b389c817。
- PAPER-20261020-001=**ACCEPTED（main R1局部复审）**。当前精确源码独立latexmk编译成功，**6页**，无undefined/Overfull，7条Underfull；已目视检查当前第2、4、5、6页，§VI首段字距改善、全部参考文献可读。没有把旧5页的全篇目视证据当作新稿全篇检查。当前仍为无正式结果的方法/协议稿，终稿版式/页限后续统一整理。原长稿在paper/archive/overleaf_20261020_main.tex。
- 用户回报本轮未同步线上Overleaf；线上具体文件版本仍未核验。仓库上传/独立PDF编译不等于线上已更新。后续修订TeX继续提交论文分支。
- 文献已有 literature/LITERATURE_LEDGER.md、novelty_boundary.md、PDF/metadata 与 paper/manuscript/references.bib。26 条旧台账、旧 FULLY_READ 标签是历史阅读记录，不代替本轮关键论断的原文定位。

## 7. 记忆审计：必须纠正的漂移

| 旧说法或风险 | 当前应记为 |
|---|---|
| 004D 一直未验收 | 002 已由 instructor ACCEPTED，限报告支持的预算/停止工程闭环 |
| 仍无SEARCH实现或003R尚未执行 | 003/003R已API级ACCEPTED；UI/B3/encounter仍未验证 |
| 接管/给导航目的地就获得 fixed center | 只有显式 SEARCH 激活；NAVIGATE 撤销搜索责任 |
| 论文正文路径未知/仅占位，或PAPER-001仍待四项返修 | 母稿已在论文分支；R1已main ACCEPTED，本轮线上Overleaf未同步、线上具体版本未核验 |
| “少量预测/多模态 + Bayes + 规划”就是创新 | 核验最相近工作的已实现机制，收紧责任层的问题与可检验区别 |
| 真实感知标定是当前第二贡献 | 旧 literature/novelty_boundary.md 的候选，当前精简主线未承诺，也没有验证证据 |
| 旧T_FD/T_conf、Gamma或R_miss就是当前成功判据 | 主实验成功仅encounter，旧确认不得单独触发主实验正常成功；字段映射和实现仍待instructor落实 |
| B2/B3 始终同 posterior，B4 必然上界 | 共享更新规则，后验可随轨迹分化；B4 只作完美未来信息参考 |
| verified_refs.bib 或 FULLY_READ 代表所有新论断已验证 | 必须记录真实原文版本、页/节/公式、支持范围和不能推出的结论 |
| 自动通信已经建立跨对话持续调度 | 用户新授权已使main每小时统筹启用；各Work接收器/本地runner仍待真实登记与端到端验证，见AUTOMATION.md |
| GT只能在评价器使用；b是包含全部人类行为信息的真实后验 | GT仅允许生成器/独立评价器两用途；b是给定几何且忽略动作选择likelihood的sensor-evidence模型 |
| B3尚未授权、004R尚未发布，或离线修复即代表完成 | 004已OFFLINE_FIXES_VERIFIED / RUNTIME_PENDING；004R已READY，尚未见本人ACK/运行证据，未ACCEPTED |

本轮只审计可见的记忆载体/产物，不能读取或改写其他对话内部记忆。各角色需提交自己读取的 commit、纠正条目和当前任务回执。旧 idea/研究决策状态.md 的“人工目的地可作固定中心”、旧传感器第二贡献等，与本轮已确认语义冲突时，按用户较新指令与 RC-20261020-v1 处理；不恢复旧语义。原文献结论则不能被研究偏好覆盖，必须回原文核查。

## 8. 当前优先级与开放事项

1. **平台准备优先**。用户已明确第一周重心为UI、统一按键、现有手柄/眼动/语音及桥接的连接反馈、会话源身份、记录导出和参数化训练入口。计划plans/WEEK1_PLATFORM_PREP_20261020.md、回复handoffs/MAIN-TO-INSTRUCTOR-PREP-20261020-001.md已发布；志愿者数据、RF训练和全部数值冻结不是准备工作的前置。
2. **004R沿原任务收口**。至多一次新有界运行，最终fallback、三种撤销和20路STOP直接证据；由instructor唯一安排/验收。未见constructor领取回执前不称在运行。其间可以继续UI设计、定向资产核对、隔离离线导出准备，不漂移待复验source/install。若阻塞，报告具体原因并继续不依赖项，不无限加smoke。
3. **依赖顺序**。可操作/可记录/可导出平台→后续志愿者实际采样→RF开发训练/按组验证→模型与参数冻结→另行安排pilot/正式B2/B3评价。当前不招募、不启动正式采集/训练；工程联调样例不称志愿者数据或效能证据。
4. **RF接口已有合同**。decisions/RF-DATA-CONTRACT-v1.md明确人控艇t+H二维位置、最少运动状态/当前操纵、因果可用性和源身份、先按会话/参与者分组再造窗口、开发与正式评估分离。instructor不需等main再次给同一数据语义；具体接口/键位按实际资产设计。硬件联动不把眼动/语音自动扩为主实验特征。
5. **文献与论文**。exploration的Xie证据已由main接收为讨论输入；inspiration本人ACK仍待。保留B2/B3信息价值主线，不因文献包新增机制对照。PAPER-001 R1已ACCEPTED，不重做返修/全文审计；overleaf据后续真实工程证据增量维护。
6. **仍OPEN**。H、源/预测年龄、缺测/标签插值、刷新/重规划阈值，R/tau/正式B，正式predictor、采样人数/会话数/预算及统计方案仍需依据。框架参数化准备可先做，不能把旧5s/1-cell/smoke预算当正式设置。

## 9. 当前交接与本人接收

- 本轮main统筹入口：handoffs/MAIN-20261020-003.md（含main本人接收及各角色下一步）；读入通信f97997b3、论文f8de4da1。新交接的各角色接收均等待本人ACK，不由main代签。
- instructor RF请求f884a8ce：main已本人ACK于receipts/main-rf-20261020-001.md，合同及MAIN-TO-INSTRUCTOR-RF回复已发布；PREP请求8cb9879f：main已本人ACK于MAIN-TO-INSTRUCTOR-PREP，计划已发布。两份回复的instructor新ACK尚未见；旧“等待main裁决”已由实际回复解决。
- constructor已接收并完成004离线返工；004R存在独立READY，尚未见其本人004R ACK/报告。instructor负责推进，main不改constructor STATUS。
- overleaf此前MAIN-002/R1本人ACK已核实；R1最终ACCEPTED的本人接收回执尚未见。论文分支最新f8de4da1，未新增返修要求，线上Overleaf同步仍未核实。
- exploration本人ACK及交付=1b5067ea，main本轮已实际读取并接收；不再标“exploration待本人ACK”。inspiration/overleaf是否读入该交付仍须其本人记录。
- inspiration：截至本轮三个分支快照未见receipts/inspiration-20261020.md或research/INSPIRATION_NOTES.md；不推断聊天未创建或用户没有讨论，仅记仓库接收未证实。
- 自动化：main工具当前enabled=true；last_run_time为2026-10-20 16:17:24.761501+08:00，仅为运行记录时间，无成功/交付证据，next_run_time未给明确值。其他四个Work接收器无本人automation登记，constructor本地runner未验证。完整自动闭环未通过。

## 10. instructor 历史审计更新（2026-10-20；用户授权追加）

历史保留：以下“无新READY/B3未授权/constructor待ACK”已被第5/8/9/12节与后续回执取代，不作为当前任务状态。

维护边界：以上 main 原快照完整保留；本节由 instructor 按本次用户明确要求更新项目记忆，不代表 main/constructor/overleaf 已接收。read_commit=`27c5303cd1bab4097b83582e13a96c88ce4f659c`。

- 003R 报告与 STATUS 已为 DONE；唯一最终配置 run_id=`5c84c3736225450eb5d0759cd1498f59`。当前审查结论：003R **ACCEPTED**，003 **ACCEPTED**（限 ROS API SEARCH/B2 工程）；详见 tasks/USV-20261020-003R.review.md 与更新后的 003.review。第 5/7/9 节关于“003R 未执行/最终时钟待运行”的旧快照已被本节取代，历史证据不删除。
- instructor 已只读核对实际 source/install hash、003R 本地详报与原始 time_series/manifest：77 条相关记录为 1–44 s、无 Unix epoch 量级污染，日志 hash 匹配 manifest；9/10 自主池、B2 中心与撤销链匹配。构建/58 tests、runtime 参数和推力观察窗按 constructor 报告审查，本轮未重跑。时间对照 0.024 s 为 Recorder 接收基准，与源 plan stamp 的差为 0.172 s，不作精确同步证据。
- 002 自然预算终态验收保留；003R 行政 STOP 不替代自然 BUDGET_EXPIRED。UI 点击、条件 Sampler 本次 runtime、B3 fallback、encounter、正式 FOUND/实验/RMST 仍未验证；全部科学 OPEN 保持。
- instructor 本轮接收 ACK 已写 receipts/instructor-20261020.md；constructor 本轮角色/记忆 ACK 仍 PENDING，旧 LOCAL_RECEIPT 是历史快照；不得假定远端发布已被读取。
- 无新增工程 READY、无追加运行预算、不重启或扩张 003R。constructor 下一次接续仅按 003R review 补角色回执、本人 STATUS 及时间差说明；PAPER–PLATFORM HANDOFF 已在 review 向 main 提供，B3 后续尚未授权。


写入前并发检查：重新读取 HEAD=`acb5760c0b7aba1b1fcfcaf92ebd5b1429714bd2`，相对首读基线仅新增 overleaf 角色回执，已读取并保留；本次所写四个路径无并发修改。overleaf 回执的接收/科学内容以其原文为准。


## 11. main 初审与裁决历史记录

历史保留：以下CHANGES_REQUESTED及四项待改状态已由第12节R1 ACCEPTED取代；科学裁决RC-v1.1仍有效。

本次以7ec7bb50通信快照和e1c5915c论文快照复核。第5/6/7/8/9节已经刷新为当前事实；第10节是instructor历史追加，其中constructor ACK待接收已由最新本人receipt解除。论文任务的DONE转入main定向CHANGES_REQUESTED，详见论文分支tasks/PAPER-20261020-001.review.md。新路由为handoffs/MAIN-20261020-002.md。

主线保持简单：主比较B2/B3；direct inhibition不列当前必做主实验，优先辅助replay候选。单binary/P_FA=0是理想化模型而非标定发现；同一p向量由观测生成器用于抽样、推断器用于likelihood，GT只留在生成器与遭遇评价器，不进入规划器。论文中“GT仅评价器”“operator位置”与未声明动作选择假设的完整后验表述需纠正。主张与证据的边界不因工程验收或编译通过而放宽。


## 12. main R1局部复审与联动更新

2026-10-20：PAPER-20261020-001的定向返修由main正式ACCEPTED，详见论文分支tasks/PAPER-20261020-001.review.md（评审提交f8de4da17dbc3cc70eeedca409376c530cf9547b）。审查正文27059ea8、报告5748cf31；独立匹配SHA256并编译6页，局部PDF检查覆盖修订公式、endpoint、§VI首段与全部参考文献。R1预测对象、R2两类GT合法用途、R3 sensor-evidence模型限定、R4引用顺序/局部版面全部通过；RC-v1.1对应段落一致。仍有7条Underfull，非零警告，不阻断本轮文本验收。

写前读到通信3ef5f2fa中的新事实：instructor已发004并本人ACK新交接，constructor已本人接收且RUNNING；overleaf的新交接ACK也已读。main未执行或验收004，不发竞争工程任务。004B公开历史索引已读取，保持“instructor亲读报告、main读公开摘要”的证据层次。

下一次收紧围绕004实际验收/参数依据表及独立encounter依赖；R/tau/B/H等OPEN数值不凭空补。当前论文文本验收不等于正式实验完成或可投稿。未改生产代码、未运行Gazebo/训练、未合并远端main；母稿仍由overleaf维护。


## 13. inspiration入口（2026-10-20用户新增分工）

历史记录：本节保留当时状态，当前状态以第1/5/8/9/17节及最新原负责人task/review/receipt为准。

用户将“分支 · 重审研究路线”分支为Work并命名inspiration，作为持续收紧研究和理解项目全貌的入口。main已建立仓库交接与角色分工；尚无inspiration本人ACK，不代表该聊天已创建/命名或自动读入。

该入口先解释研究问题、方法、已验证范围和下一缺口，再每轮一个关键问题；允许反例/质疑/新想法，也直接回应用户追问。实质结论才记简短研究笔记，交main同步；工程唯一派发仍instructor，实施constructor，母稿overleaf。当前PAPER-001 ACCEPTED、004 RUNNING等状态保持，未新增工程任务或扩大研究主线。

本轮直接读用户附件《1015-1115.pdf》，保留工程闭环→数据/预测→部署/pilot→正式实验/论文的计划方向；RF/参与者实验等是计划，不是既成结果。源对话历史检索失败，不能声称通读其全部内容；新分支继承的历史需按当前RC纠偏，尤其人控艇位置、encounter成功、B4非保证上界。


## 14. exploration文献预处理入口与收集结果

历史记录：本节保留当时状态，当前状态以第1/5/8/9/17节及最新原负责人task/review/receipt为准。

2026-10-20用户在inspiration前增设exploration（统一此拼法，曾写esploration），面向Related Work清点、去重、原文身份/证据核查，并直接向inspiration交付研究依据。main已创建交接与初始资料汇总，未代建聊天分支，未代签exploration ACK。

本轮清点并读取仓库26条catalog、论文分支31条bib/20项审计、历史长稿引用、Library六篇阅读卡与累计索引、历史20条台账/补充bib/后续三篇竞争矩阵，按DOI/版本关系合并为**46个作品记录**；仓库树有**22份PDF**，当前母稿引用**17个作品**；原文审计**20项对应19个作品**（Xie两项）。目录记录原文/开放入口、文件hash、引用别名、来源和阅读范围。不是46篇全文新下载/新精读；未证明遍历所有不可见聊天；旧Zotero包本体未定位但仓库相应书目已纳入。

新增入口：literature/EXPLORATION_INDEX.md与exploration_catalog.json。历史26条台账、RIS、novelty_boundary及paper目录保持；论文当前版本必须在paper/overleaf-20261020读取。六篇阅读卡原件已读，个人答题记录不搬入公开仓库；原文核查状态不因阅读卡结题而升级。

Costen/Yuan/MAC的后续历史矩阵比007初始建议更新，分别记录正式全文F/预印本P/摘要A；main本轮只读这些记录。Hsu正式版与arXiv合并；Bourgault2003/2004等版本保留区别；Jovan勘误待核；Rossano作者页IROS2026接收但要求先引预印本，本轮已核对身份，未假造正式DOI。Fang2026只核对arXiv身份/摘要；Li2026全文访问受限。新的目录不扩张当前17篇引文或主实验。

信息链：exploration文献证据→inspiration与用户讨论→main统一决策→instructor/constructor工程、overleaf正文。事实引用纠错可直接供overleaf使用；科研合同变更仍由main统一同步。PAPER-001 ACCEPTED保持；004已更新为constructor DONE / instructor REVIEW_PENDING，所有OPEN数值保持。不以46篇全读完阻塞inspiration或工程。


### 本轮写前并发更新（004）

读到c9bfa8b484f8e2f2ba5bd565d411fe9a95baa6f5：constructor新增004报告/STATUS/本人完成回执。报告称162项测试及构建通过、一次无模型运行f87fc7b8a1934a52ada1fbc1fd7d4828已记录SEARCH回退/CANCEL/STOP与Recorder收尾；20路实际thruster及第二次ACTIVE后的NAVIGATE/RELEASE/UI为NOT_OBSERVED，不拿003R历史记录代替。当前DONE / instructor REVIEW_PENDING，main通过公开compare读取，不独立验证本地原始记录、不代签验收。早先RUNNING表述保留作领取时历史。参数表中的10m、0.1s/实测间隔、H=5s等均仅报告来源/工程沿用，未据此冻结正式研究数值。此次角色和文献提交保留这三项并发文件，未改constructor产物。


## 15. main中心任务触发器（2026-10-20用户授权）

历史记录：本节保留当时状态，当前状态以第1/5/8/9/17节及最新原负责人task/review/receipt为准。

用户明确要求定时检查各Work的GitHub情况、下达命令、角色回执并闭环。本轮已实际创建main每小时定时任务（Asia/Shanghai），创建结果enabled=true；启用回执见receipts/automation-main.md，细则AUTOMATION.md，角色启用交接handoffs/MAIN-AUTO-20261020-001.md。只在实质进展/阻塞/待用户决定时通知，无变化不制造提交和新任务。

当前可用接口没有指定其他既有会话的参数；各Work须在本人会话各创建一次定时接收器并登记。constructor需要真实本地执行器，交instructor指导部署。main已启用不等于这些接收器已启动，不等于完整端到端自动闭环已验收。本轮未伪造其他角色ACK或修改其内部记忆。原协议只手动触发的条款由用户本次明确授权定向更新；科研合同、文件所有权、单一工程派发和运行预算不变。

## 16. 004 review已到达：CHANGES_REQUESTED

历史记录：本节保留当时状态，当前状态以第1/5/8/9/17节及最新原负责人task/review/receipt为准。

本轮人工检查读到c1f42e8a944e58cd222ee5161d51eeabdff9c37b中instructor的004.review和本人回执。其亲读本地原始日志/源码、核对hash；main读取公开review，不代其本地验证。确认局部fallback/CANCEL/STOP/Recorder运行事实保留，但接收时刻赋当前segment不能证明源输入属于当前段，同段位姿t2→t1倒退尚未拒绝。

按review先补确定性生产路径反例与最小离线修正/测试/构建、更新最终hash；无法证明来源的特征不得靠接收时刻伪装新鲜，可使依赖分支回退，不破坏原手控接口。20路实际推力及最终撤销覆盖仍需后继有界运行；004的一次额度已用尽，004R尚无READY。原报告DONE不升级ACCEPTED，不新增endpoint/正式实验，不更改H/R/tau/B。上文历史快照的“待review”仅代表当时状态。


## 17. main全角色检查与平台准备优先（2026-10-20）

用户本轮再次明确：按计划部分训练数据要由后续志愿者实际采样；第一周先把可操作、可记录、可导出、可接入训练的框架搭好，instructor重心为UI、按键和硬件联动，并要求main检查全部Work统一统筹。此为已明确用户方向，未再次请求批准。

本轮main本人读取通信f97997b3及三个分支HEAD、004最新review/004R READY、constructor/instructor/exploration/overleaf receipts、STATUS、RF合同/回复、PREP交接/本人回复/第一周计划、Xie证据笔记及交付、论文f8de4da1的最终review，并查询定时任务真实状态。main未重跑本地测试、Gazebo、训练或论文编译；本轮工程事实保持“instructor直接核查/constructor报告、main远端读入”的层级。

已解决共享状态漂移：
- 004离线两项修复已instructor核查，26项直接测试通过；166/build为constructor报告，整体仍RUNTIME_PENDING。
- 004R已独立READY，旧STATUS/记忆“尚无READY”过时；未见constructor新ACK或报告，不能升级RUNNING。
- RF合同和PREP本人回复早已发布，等待的是instructor读入，不是用户再批准或main再给同一合同。第一周计划已实际写入，现同步共享记忆。
- exploration已本人ACK并交付Xie证据包，main接收完成。main本轮读的是该证据包，不把其FULL_TEXT_REVIEWED冒充main本轮独立全文复核。接收支持既定克制边界和inspiration讨论，不等于验证本项目效果或新增主实验。
- inspiration仓库本人接收仍未证实；PAPER-001 ACCEPTED保持，overleaf后续只按新证据维护。
- main定时任务当前enabled=true（接口updated_at=2026-10-20T08:24:21.079645+00:00）；不推断先前停用原因、16:17运行成功或其他Work已唤醒。其余接收器/本地runner缺口保留，由本人接入登记。

新的handoffs/MAIN-20261020-003.md统一角色下一步与回执要求；复用现有RF/PREP/004R，不发竞争constructor READY、不改其他角色文件、不合并远端main、不增加实验预算。实际UI/硬件联调、源身份生产链、志愿者数据、训练模型、encounter及正式效能仍未验证。
