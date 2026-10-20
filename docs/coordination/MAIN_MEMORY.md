# main 共享工作记忆 — USV 研究统筹

更新日期：2026-10-20，Asia/Shanghai。维护者：main。研究语义：RC-20261020-v1 + decisions/RC-20261020-v1.1.md。
用途：六角色共同读取的研究和事实基线；不是平台完成证明，也不代表其他对话已经接收。
最新统筹补充：main已本人接收fdf0e3119a65f7290029b5831d23308413950fe6闭环走查反馈。用户要求核实感知简化/四项传感器期望、决策与重规划可观察性、原始采样设置和A*平滑/轨迹链；手柄主观感觉良好。当前binary报告形式不等于传感器数量；按用户本轮四传感器期望接收，其清单/参数与RC-v1.1 D2对应关系仍待对齐，不声称用户已撤回或简化已完成。当前h5模式名/视频候选框均不足以证明实际后验输入，须核安装profile/消费者/事件。沿instructor/005先做已有证据的窄范围核对与说明，保持总体卡顿优先、不改好用手感，不增运行、不换规划器。本人回复见handoffs/MAIN-TO-INSTRUCTOR-LOOP-FEEDBACK-20261020-001.md及第23节；005仍READY/RUNNING，004/004R2限定ACCEPTED保持。
论文验收历史依据：5748cf31的R1修订及当时独立编译/局部PDF复审见第12节；RF/Xie增量及7页检查见第20节。当前事实见第1—9与23节；第10—22节保留相应检查时快照及仍有效分工。本次以当前仓库和用户指令为准，不声称读取所有历史对话或其他角色内部记忆。

## 1. 角色与工作目标

| 角色 | 负责 | 当前状态与下一步 |
|---|---|---|
| exploration | 文献整理、版本/原文证据、直接交付inspiration | Xie已接收；本轮main另读1cea3553的Ishii证据笔记/交付增量，按其证据范围接收，不冒称main复读原文。后续按明确论断缺口推进，不扩大主实验 |
| inspiration | 向用户解释全貌、讨论反例与研究取舍 | 用户/instructor报告已发送并送达训练用途解释请求；新请求本人接收/解释完成待证据。下一次直接按RF合同讲清操纵→标签→训练→预测→责任比较，不先反问或扩线 |
| main | 科学合同、计划优先级、跨线状态与评审 | 已ACK fdf0e311闭环反馈；四项传感器期望与binary主模型关系待对齐，发布本人判断并维护记忆，不另发工程READY |
| instructor | 平台设计、唯一工程派发与验收 | 005仍唯一READY；已提交用户闭环反馈。沿原链核当前观测profile/消费者、决策与重规划证据、采样及路径后处理，保持小步/原预算；本次main回复接收待本人证据 |
| constructor | 实际平台实现、测试、报告与本人STATUS | bf78ed55本人领取，79226670已交005阶段性RUNNING报告；启动说明/3只读子agent有回执。当前源码线索/性能假设，实测指标UNKNOWN，无生产修复；非DONE/ACCEPTED |
| overleaf | 唯一论文母稿、引用与论证 | 原PAPER-001/R1保持ACCEPTED；RF/Xie增量@214b2cc9经main内容/编译/视觉审阅ACCEPTED，当前7页。后续按实质证据维护，线上Overleaf未核验 |

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

本轮main读取0f2c80e7下instructor的004R2.review、004.review及INSTRUCTOR-TO-MAIN-MANUAL交接。instructor直接核对本地最终hash/原始事件并重算STOP统计，main按该正式review接收工程结论；main未访问实际Linux/Windows工作区或独立重跑。最新原负责人review优先于旧STATUS与历史记忆。

| 工作 | 当前状态 | 证据与限制 |
|---|---|---|
| 001静态审计 | DONE / ACCEPTED | 历史审计，不用旧“缺SEARCH”否定后续实现 |
| 002 / SLIM-004D | instructor ACCEPTED | 预算/STOP/Recorder工程验收，非正式实验 |
| 003 / 003R | instructor ACCEPTED，限ROS API SEARCH/B2 | 最终sim clock阻断解除；实际UI未观察，非B3/encounter验收 |
| 004 | instructor ACCEPTED（限生产B3门控/无模型回退） | 最终Planner source/build SHA256=ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84；004R2最终运行闭合fallback、撤销、直接STOP与Recorder。不是有效RF/正式效能验收 |
| 004R | instructor BLOCKED / RUN_CONSUMED | 唯一Gazebo已启动，临时START及cleanup错用example_interfaces/SetBool，真实为std_srvs/SetBool；未START。20路空闲零值不是STOP因果安全，旧额度不能重用 |
| 004R2 | instructor ACCEPTED（限定工程）；运行已完成、额度已消费 | run=448cd4ea97f64161bcaf9d850386bba5。instructor原始证据复核：STOP前20路均非零；STOP后各360条全零、最短11.634358088s，回执至保守屏障间689条亦零。任务活动约2.2s，非长期性能/预算删失验证 |
| 第一周平台准备 / 005 | READY / PHASE_1_STARTUP_AND_TARGETED_DIAGNOSIS；constructor RECEIVED/RUNNING | cac0e02e任务、bf78ed55本人回执。启动说明先交；总体卡顿优先于热图，语音/眼动分层诊断。主agent统合三只读子agent，阶段无自动新Gazebo/START/操纵/STOP，用户已有会话只读监测一次≤15分钟；尚无真实改善证据 |
| RF真实来源与训练 | 最小数据合同已发布；真实来源链/数据/模型未验证 | 无模型不阻断准备；无法核验源身份时仍保守回退 |
| encounter、正式B2/B3与RMST | 未验证/未报告 | 不用工程验收或文本ACCEPTED升级科学结果 |

004旧run=f87fc7b8a1934a52ada1fbc1fd7d4828仅支持当时版本局部事实；最终修复版本的无模型fallback、CANCEL/NAVIGATE/RELEASE及20路STOP缺口已由004R2及instructor正式review收口。有效预测仍仅离线可信fixture，真实RF来源/模型未验证。004R原失败与耗用保留；004R2完成后不再重复同类smoke作为用户查看UI的前置，本次不增加无人值守运行额度。

002 run=7904539e7ad44213b4baa971245e3bb9，deadline=82.540s、发布=83.000s；0.460s延迟不能延长分析预算。10/10 path STOPPED、20/20 thruster=0为该次证据，encounter_censoring_validated=false。003R最终run=5c84c3736225450eb5d0759cd1498f59，77条相关记录1—44s；邻近位姿差0.0287m，0.024s是Recorder外层差，源plan差0.172s，非精确同步。行政STOP不替代自然预算验收。

SLIM-004B历史索引reports/SLIM-004B-evidence-index.md：instructor亲读原报告并记录SHA256=755f89fbeb487ee3dae056731fb9496d26e95afa54ee4bc9c9b14569a8170083、183 tests/80唯一事件（48负更新/32ABSTAIN）。main只读公开索引，精确UNKNOWN目标runtime分支未重现，不追签历史独立验收。

## 6. 源码、论文与资产入口

- 实际运行工作区：/home/cyz/vrx_ws；根无有效 Git HEAD，实现提交 SHA=NONE。研究仓库和通信 SHA 不是运行平台 SHA。继续记录修改文件 SHA256、dirty 状态、构建和运行证据，后续由 instructor 安排可复现源码快照；不能把文件 hash 等同完整环境复现。
- 本地版本化研究仓库：/home/cyz/USV_HRI_PATROL；此前回执 main@5f263c694f3d601bf1596bb92b0849d98f7e677b 且有未提交决策，不清理或覆盖。
- 远端 main@749a4a06db0b24d0fdd3bcb47618a365dfa5bdfa 是旧仓库快照，不是当前生产源码。通信分支和论文分支中的旧 platform/ 不用于覆盖本地。
- VRX 上游 humble 固定 dc30ed8d17aa1083fd872edad9c77c69896d2b07；项目变更通过本项目 patch/setup 管理，不推上游。
- 通信：coordination/work-20261020 / docs/coordination/。
- 论文：paper/overleaf-20261020 / paper/manuscript/main.tex。R1审查快照=5748cf311cfa26e1db2ad9bc0d15f9c2f369abc3；正文提交27059ea8cb009c973ad4a6d0cf906afb8c801c64，SHA256=758058ae1c24dcfa70b7946cf444eaf61573bd6c00461e78c906c056b389c817。
- PAPER-20261020-001=**ACCEPTED（main原R1局部复审历史）**，对应旧稿6页/7条Underfull；不外推新版。当前RF/Xie增量@214b2cc9，正文@2d25d26a、SHA256=7292c1a6315aac002ad1214161ba1b1e71aea251742ca427cffd1151ed4a56fc，经main独立latexmk编译PASS为**7页**，无undefined/Overfull、9条Underfull；7页已逐页目视，无截断/重叠，页3/5竖向间距与参考文献单栏留白仍属后续终稿排版。当前增量ACCEPTED（方法/协议稿范围），不是正式结果或最终页限验收；详见第20节。
- 用户回报本轮未同步线上Overleaf；线上具体文件版本仍未核验。仓库上传/独立PDF编译不等于线上已更新。后续修订TeX继续提交论文分支。
- 文献已有 literature/LITERATURE_LEDGER.md、novelty_boundary.md、PDF/metadata 与 paper/manuscript/references.bib。26 条旧台账、旧 FULLY_READ 标签是历史阅读记录，不代替本轮关键论断的原文定位。

## 7. 记忆审计：必须纠正的漂移

| 旧说法或风险 | 当前应记为 |
|---|---|
| 004D 一直未验收 | 002 已由 instructor ACCEPTED，限报告支持的预算/停止工程闭环 |
| 仍无SEARCH实现或003R尚未执行 | 003/003R已API级ACCEPTED，004最终无模型B3门控/回退也已ACCEPTED；实际UI、有效RF与encounter仍未验证 |
| 接管/给导航目的地就获得 fixed center | 只有显式 SEARCH 激活；NAVIGATE 撤销搜索责任 |
| 论文正文路径未知/仅占位，或PAPER-001仍待四项返修 | 母稿已在论文分支；R1已main ACCEPTED，本轮线上Overleaf未同步、线上具体版本未核验 |
| “少量预测/多模态 + Bayes + 规划”就是创新 | 核验最相近工作的已实现机制，收紧责任层的问题与可检验区别 |
| 真实感知标定是当前第二贡献 | 旧 literature/novelty_boundary.md 的候选，当前精简主线未承诺，也没有验证证据 |
| 旧T_FD/T_conf、Gamma或R_miss就是当前成功判据 | 主实验成功仅encounter，旧确认不得单独触发主实验正常成功；字段映射和实现仍待instructor落实 |
| B2/B3 始终同 posterior，B4 必然上界 | 共享更新规则，后验可随轨迹分化；B4 只作完美未来信息参考 |
| verified_refs.bib 或 FULLY_READ 代表所有新论断已验证 | 必须记录真实原文版本、页/节/公式、支持范围和不能推出的结论 |
| 自动通信已经建立跨对话持续调度 | 用户新授权已使main每小时统筹启用；各Work接收器/本地runner仍待真实登记与端到端验证，见AUTOMATION.md |
| GT只能在评价器使用；b是包含全部人类行为信息的真实后验 | GT仅允许生成器/独立评价器两用途；b是给定几何且忽略动作选择likelihood的sensor-evidence模型 |
| 离线修复/空闲零值即代表004完成，或004R额度可重用 | 004R仍BLOCKED/RUN_CONSUMED；004R2已实际运行并获instructor限定ACCEPTED，004据最终证据转ACCEPTED。不能倒改旧失败、重用额度或外推UI/有效RF/科学结论 |

本轮只审计可见的记忆载体/产物，不能读取或改写其他对话内部记忆。各角色需提交自己读取的 commit、纠正条目和当前任务回执。旧 idea/研究决策状态.md 的“人工目的地可作固定中心”、旧传感器第二贡献等，与本轮已确认语义冲突时，按用户较新指令与 RC-20261020-v1 处理；不恢复旧语义。原文献结论则不能被研究偏好覆盖，必须回原文核查。

## 8. 当前优先级与开放事项

1. **用户闭环反馈纳入005，保持总体可操作性优先**。严重卡顿/语音/眼动问题仍在；新增四项传感器期望对齐、当前实际观测链、决策/重规划可观察性、原始采样和路径后处理核对。先复用已有源码/日志解释真实闭环并小修，热图美化其次，不因“未看到”判“未实现”；手柄正向主观反馈保留。
2. **005首阶段已READY且本人领取，不重复派工**。instructor在cac0e02e发布唯一任务；constructor在bf78ed55本人报告RECEIVED/RUNNING、三只读子agent已启动，分别UI/按键、性能、语音/眼动数据流。主agent先说明/后统合，避免共享文件覆盖；无自动Gazebo/START/操纵/STOP、无训练或清理用户会话。任务允许既有用户会话一次≤15分钟低开销只读监测；正式运行/实测结论仍须证据。
3. **依赖顺序**。可操作/可记录/可导出平台→后续志愿者实际采样→RF开发训练/按组验证→模型与参数冻结→另行安排pilot/正式B2/B3评价。当前不招募、不启动正式采集/训练；工程联调样例不称志愿者数据或效能证据。
4. **RF接口已有合同**。decisions/RF-DATA-CONTRACT-v1.md明确人控艇t+H二维位置、最少运动状态/当前操纵、因果可用性和源身份、先按会话/参与者分组再造窗口、开发与正式评估分离。instructor不需等main再次给同一数据语义；具体接口/键位按实际资产设计。硬件联动不把眼动/语音自动扩为主实验特征。Windows Unity/Tobii桥接按第19节现有单接收链纳入准备，先核实真实收包/发布/记录与来源身份，不能用Linux接收时刻补写成Windows采样身份。
5. **inspiration先直接解释当前训练用途**。真人在VRX操纵艇→记录运动状态/当前命令→同艇同控制段且SEARCH连续有效的t+H位置标签→按参与者/完整会话分组训练→预测人控艇未来位置→B2当前位/B3有效未来位责任比较。不是训练语音、眼动、底层驾驶或目标探测器。眼动/语音非本版RF必需，但影响行为/时序的卡顿与输入失真须先修；不以反问/新文献扩线代替解释。文献/论文保持既定边界。
6. **仍OPEN**。保留用户四传感器期望，具体四路/参数清单与RC-v1.1 D2对应关系待对齐；binary是报告形式，不能直接推成只有一个物理传感器或四项已取消。当前不改合同/不扩四模态/不填参数。H、源/预测年龄、缺测/插值/重规划阈值、R/tau/正式B、模型及人数/统计方案仍需依据；原始采样、显示刷新、记录、训练重采样必须分开。

## 9. 当前交接与本人接收

- main统筹入口：MAIN-20261020-003及MAIN-TO-INSTRUCTOR-MANUAL延续；本轮本人读入fdf0e311的INSTRUCTOR-TO-MAIN-LOOP-FEEDBACK，回复MAIN-TO-INSTRUCTOR-LOOP-FEEDBACK-20261020-001并更新主记忆。未改instructor任务/review、constructor STATUS，未新增READY或运行。回复接收不代签。
- instructor RF请求f884a8ce、PREP请求8cb9879f均已由main回复且instructor本人ACK；合同不再待重复批准。instructor在cac0e02e本人ACK main手动走查决定，并发布005第一阶段READY，原DRAFT/PRODUCTION_BLOCKED_BY_004R已由任务所有者更正。
- constructor已完成004离线返工/004R2最终运行并本人接收限定ACCEPTED。当前bf78ed55本人回执read_commit=cac0e02e：005 RECEIVED/RUNNING，启动说明已向本聊天交付，3个只读子agent实际启动；这些是constructor报告，不冒称main进入本地主机亲验。当前无生产修改、新Gazebo或实测延迟证据。
- overleaf在c3c75966本人ACK PAPER-001最终ACCEPTED、MAIN-003、RF合同、第一周计划与Xie证据（通信read_commit=87364b3b）；不再标该接收缺口。其RF/Xie新增论文内容已在本轮审查ACCEPTED，见第20节；线上Overleaf版本仍未核实。
- exploration本人ACK及交付=1b5067ea，main本轮已实际读取并接收；不再标“exploration待本人ACK”。inspiration在629062c8已本人记录接收EX-XIE-01—05；overleaf亦已在c3c75966本人记录读入。
- inspiration：原基线本人ACK=629062c8、read_commit=c821fbb9保持。当前用户/instructor称训练用途解释请求已发送/送达；尚无该新请求的本人ACK/解释结果，不假报已解释或已改研究笔记。未验证其自动接收器。
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

历史快照：本节中的instructor/inspiration待ACK状态已由第18节及当前表格更新；原核查记录保留。

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


## 18. instructor ACK / 005草案与inspiration本人接收（2026-10-20）

- main实际读取629062c8a0f98c676ce364d9c8ad151e68de280b，相对c821fbb9先读到848965a1与629062c8两项提交，涉及instructor receipt、005 DRAFT及inspiration receipt；写前又读到fc99afb5的constructor本人004R领取回执及15eaba47的本人STATUS纠正，已纳入当前表格。
- instructor本人ACK MAIN-003、PREP/RF回复、RF-DATA-CONTRACT-v1与第一周计划，接收链已闭合至instructor。005草案与既定平台准备方向一致，保持DRAFT / PRODUCTION_BLOCKED_BY_004R；main只记录接收和范围一致性，不替instructor转READY、做工程验收或增加运行额度。
- instructor在实际console/pad/launcher/bridge中定向只读确认已有操纵/硬件入口，并未找到显式SEARCH_ACTIVE/CANCEL发布入口；这是其有限源码检索发现，待constructor完整核对及后续真实UI验收，不扩大成“所有接口均不存在”或“功能已修好”。SEARCH按钮/owner确认反馈列为005优先项，现有键位表不等于已冻结最终映射。设备未启动实测，保持待现场/NOT_OBSERVED。
- 用户转述instructor已向现有constructor聊天发协调消息；main未独立观察该聊天，随后实际读取fc99afb5本人ACK才确认领取成立。constructor状态RECEIVED / PREPARING，source/build与launch身份匹配；回执明确未启动Gazebo、额度未消耗，尚须验证20路直接采集与ROS权限。004R沿原独立READY和一次有界预算推进；005生产source/install改动继续串行，不另发竞争READY。
- inspiration本人ACK=629062c8，读入c821fbb9并接收合同/计划及EX-XIE-01—05。main已实际读取并确认接收；exploration证据→inspiration读入这一步已有本人证据。尚无新科研决定、用户答案或效能结论，当前讨论OPEN，不要求为了状态表制造研究笔记。
- 本轮仅更新main自有MAIN_MEMORY与MAIN-003接收状态，不覆盖instructor任务/回执或constructor STATUS；不运行仿真、硬件、训练或论文编译，不因ACK变更自动化状态。

## 19. 004R2门槛、Windows桥接与工作强度（2026-10-20）

main ACK instructor的3229e4b8与用户本轮接口同步；最新已核对通信HEAD=c3c75966e5bcb85cc81c3f17fe195d04628430e5。004R失败原因在临时驱动/cleanup服务类型，未START，不升级为生产Planner故障或STOP安全通过。constructor已本人领取004R2；领取、预检PASS、Gazebo启动、验收分别记录。004整体保持CHANGES_REQUESTED/RUNTIME_PENDING，历史002/003/003R验收不变。

main已本人读取并ACK reports/WINDOWS-BRIDGE-20261020-001.md@c636b7fd11c6daabb5c1287ff823b2c0b1251fe7（LOCAL_AUDIT_COMPLETE / LINUX_INTEGRATION_PENDING）；本地Codex核对：`C:\bridge\UUV.exe`、UUV_Data与Tobii DLL存在；cli.txt指向Linux UDP 15555；`C:\EyeTrackerBridge\Assets\Scripts\GazeUdpSender.cs`包含t/unity_t/tracker_us、valid、归一化/像素/原始坐标与屏幕尺寸，缺源会话/控制段身份。文件存在不证明该exe由所见源码构建，也不证明设备/网络/ROS运行通过。报告列明exe/DLL/发送源码hash；进程命令行读取被拒、当前日志为空，实际生效目标和有效采样未核实。

关键限制：provider中的t实际等同更新时Unity时间，不能证明设备采集年龄；Update可重复发送同一tracker_us，传输包数与独立设备样本数须分开。坐标参考Windows Unity窗口，不是Linux控制台；DPI、内容区、黑边、Y翻转及现场角点/中心映射待验证。包缺可信source/session/run/epoch/vehicle/authority段身份，不可在接收端倒填后充当RF证据。UI应区分接收新鲜度/设备采样新鲜度，Recorder保留重复、无效、时钟域、配置和源身份缺失。

第一周将Windows采集→UDP 15555→Linux现有单接收→/tobii/gaze纳入UI设备状态、连接/失效反馈、时间语义与源身份、记录/导出整合；以实际接收器与消息类型为准，仓库旧双LSL链不是生产基线。第一周计划已同步，main向instructor的仓库接口交接见handoffs/MAIN-TO-INSTRUCTOR-BRIDGE-20261020-001.md；由instructor沿005及既有工程链安排，当前005仍DRAFT、无新增运行额度；不启动Gazebo、不采志愿者数据、不扩展RF特征或科学定义。instructor可继续只读设计/文档，生产更改与004R2串行。

跨主机分工（用户本轮明确澄清，main本人ACK）：constructor是仿真平台主机上的Codex App agent，负责实际Linux生产工作区；Windows Codex专注C:\bridge与C:\EyeTrackerBridge。二者不是同一主机/工作区。main Work作为中转，通过现有通信分支与instructor→constructor链转交c636b7fd报告，并要求constructor本人回执Linux生产单接收接口核对结果。用户已撤回索取constructor聊天ID/链接，不再查找或要求用户复制说明/重复授权。仓库已发布、本人收到、执行、设备实测分别以真实证据记录。

用户要求降低token消耗。执行RULE更新见ROLE_PROTOCOL_v1_1第9节与AUTOMATION：先HEAD/差异、只读相关内容、合并状态提交、无增量停止、不进行ACK套ACK或无任务深思。main既有定时任务仅提示已实际优化，小时频率/启用不变；各Work模型与思考档位是配置建议，尚未远程改设，不能宣称已全员生效。工程类型/退出码/安全验证不因节省token省略。

## 20. RF/Xie论文增量审阅与预检新回执（2026-10-20）

main已读paper@214b2cc96bfb4fec68388322d46b901ed8378b4a的报告、精确main.tex及f8de4da1→214b2cc9差异，对照RF合同与Xie证据包；另对本地同hash Xie原PDF第5页漏检段定向复核。增量判为ACCEPTED，正式review见handoffs/MAIN-TO-OVERLEAF-RF-XIE-20261020-001.md；原PAPER-001/R1 ACCEPTED保留。源码、编译、7页视觉证据归此精确版本；未同步线上Overleaf，未创造实验/硬件/训练结果。

写前已读1cea3553的Ishii新增证据与交付：main接收其已搜/未来区域/问答改变候选、组合实验及对话增量限制的报告，不冒称本轮亲读该原PDF或代inspiration ACK，不扩主实验、不另派全文审计。按工作强度规则到此停止扩查。

写前读入244d230d预检报告、691d673f本人准备回执及8a7322cc STATUS：004R2为constructor报告PRE-FLIGHT PASS / GAZEBO NOT STARTED。隔离实际驱动/退出码/cleanup/watchdog与20路合成fixture证据不能升级成真实START/STOP或004最终验收；仍按唯一READY启动前核最终身份与runner、至多一次新会话、无自动补跑。main未运行仿真或代instructor签工程ACCEPTED。

## 21. main本人ACK：先由用户走查现有上位机（2026-10-20）

read_commit=0f2c80e709bf682519b6d7d1352290c2520185c1；contract_version=RC-v1 + RC-v1.1 + RF-DATA-CONTRACT-v1（均不变）；本次active_task为跨线阶段裁决，不是constructor工程READY。

已读instructor手动走查交接及004R2/004正式review。接受用户本轮明确要求：由用户一键启动现有仿真平台、判断上位机是否合理并给反馈，再让instructor指导constructor。纠正旧理解：不是先完成005/训练RF/继续smoke才允许用户看到UI；004复验串行冻结现已解除。限定工程ACCEPTED归instructor本地审查，main只核对远端文件。

执行次序及交付见handoffs/MAIN-TO-INSTRUCTOR-MANUAL-20261020-001.md。constructor经instructor先核实用户已有桌面入口或脚本的精确命令、实际profile、显示环境与设备启停、停止/退出方式并保留版本标识；当前用户要求的是现状走查，不先更换模式或大改界面。已知run_vrx.sh start包含Qt；--research-core排除UI/硬件，不作上位机走查；--headless只关Gazebo窗口；历史默认h5_command_aware不冒称当前SEARCH/B2/B3模式。

用户可先不按全局START评价布局、地图/文字、选艇/状态/按钮语义与设备反馈；缺失SEARCH入口如实说明，不以CLI代点。截图或自然文字即可，instructor统一整理并小批实施，用户复验后推进手柄/Windows桥接/语音与记录导出。主动操纵联调说明所选模式、停止收尾与实际范围；不把简单查看UI变成长审批或自动增加无人值守Gazebo次数。硬件/源身份缺口继续保留，不扩科学模态。

main本轮仅更新自有记忆/计划/统筹回复及协议中的过时快照，不改instructor的005任务/review或constructor STATUS，不运行平台。005文件仍DRAFT，instructor按本决定维护阶段和必要工程发布，不需再向用户申请同一方向批准。新回复发布不等于instructor/constructor已收到或执行。

写前并发核对：HEAD已推进至aa9e8e3f3c051907af95ba7bf02280d4c1410e53；相对0f2c80e7仅constructor的STATUS与本人receipt变化，已读并保留。constructor已本人接收004R2/004正式ACCEPTED，005仍DRAFT未领取；该回执不等于收到本次main阶段回复或已核对用户启动入口。本次四个目标路径无并发改动。

## 22. 首轮UI反馈、005 READY与constructor本人领取（2026-10-20）

main本人ACK：已读取handoffs/INSTRUCTOR-TO-MAIN-UI-FEEDBACK-20261020-001.md与tasks/USV-20261020-005.md@cac0e02e10539768c6a12da25df48fe972543e34，并读8d145cf5→bf78ed55c74052aa4077af18d2b36868f38df6a5差异。RF-DATA-CONTRACT-v1本轮已复读；科学合同和OPEN参数不变。按用户最后要求只统一主记忆，不发布准备中的重复交接、不另发READY。

首轮实际反馈：总体严重卡顿，热图不丝滑其次；语音稍偏差就识别/执行不了；眼动延迟大；用户不明白平台能训练什么。instructor报告两张静态截图可见FPV/overview与COMMAND_AWARE模式，main本轮未亲看这两图；静态图不能测时延/帧率。上述使用问题真实报告与根因已证明/修复已验证分别记录。

GitHub先前传输失败已被后续cac0e02e成功发布与本轮回读更新，不再记005未READY；报错根因未诊断。instructor保持唯一派发。后续c0bed277更新STATUS，bf78ed55有constructor本人领取：RECEIVED/RUNNING，read_commit=cac0e02e，非DONE/ACCEPTED。其报告已先在本聊天交付/home/cyz/vrx_ws下默认./run_vrx.sh start说明，h5_command_aware且Qt/joy/pad/voice/gaze启用，--research-core不适合UI走查；main未验证其桌面入口或本地进程。不要将Space清键盘输入当全局STOP，或Ctrl+Shift+S当前页导出当训练会话导出。

constructor本人报告实际启动3个只读子agent：UI/按键、性能/热图、语音/眼动数据流；主agent负责基线、说明、整合和报告。初步SEARCH UI缺口、主线程图像处理性能假设、语音分层拒绝和tracker样本身份区别，仍是线索/假设，无实测延迟/真实设备复验。无生产代码修改、仿真/START/操纵/STOP/训练或清理用户会话。后续只按已发布005的允许范围定位、小修与验证，不因并行新开执行会话或耗尽用户UI资源。

当前优先级：启动说明立即先交；总体响应与输入真实性先定位，热图平滑次之。语音拆采音/PTT、ASR文本、解析、策略拒绝和执行反馈；眼动沿Windows→UDP15555→Linux现有单接收→/tobii/gaze→UI/Recorder分层，重复tracker_us、时钟域、坐标映射与接收/采样新鲜度分开。Windows Codex与Linux constructor各守本机，现有桥接交接继续有效，不恢复旧双LSL。只读定位→小修→用户复验，不先大改UI。

inspiration解释请求：用户最新消息称已实际送达，正式交接亦列明说明要求；本人ACK/回复未见，不称解释已完成。解释内容直接按RF合同：当前准备从真人控制仿真船的运动/操纵记录训练未来位置回归（RF为首个候选）；输入在请求前因果可用、标签由同艇同段连续SEARCH后续轨迹离线生成，先按参与者/会话分组再制样本。预测未来人控艇位置用于B3人工责任中心，与B2当前位比较；预测准确不等于协同收益。H/数值保持OPEN，不跨段补标签、滑窗不当独立参与者。眼动/语音非RF必需，但严重卡顿/输入失真若影响行为和时序须先修，不能因模态可选忽略体验。

004/004R2限定工程ACCEPTED不代表UI/硬件可用、合格RF训练数据/模型或科学效能已具备。既有原始日志与通过来源/时间/标签/分组检查的训练集是不同状态。主线不扩为ASR、眼动或底层驾驶训练，不新增科学实验。

写前并发增量：main另读792266700ccb15021a2215b6dc5696ac894629af阶段报告与4e1fcdf2dd0840e722eeb42b8516c1d84635e468 STATUS，保留全部他人路径；MAIN_MEMORY无同路径并发改动。005报告仍RUNNING/未生产修复：启动命令`cd /home/cyz/vrx_ws && ./run_vrx.sh start`，默认headless Gazebo+Qt/joy/pad/voice/gaze、h5_command_aware，脚本SHA256=5cce36b2ce82b65e90ca93cf2487b148e27b51c2718fdfe2f1f2bc15499e7b0c，未找到可核实专用desktop。constructor报告当前无单艇显式SEARCH/CANCEL UI入口、缺parser错误展示；主线程ROS回调/相机转换/重绘与热图逐格绘制仍是待计时候选，不能升级为卡顿根因。当前FPS/CPU/RTF、语音失败层比例、眼动跨机延迟均UNKNOWN，无build/仿真/操纵/训练。本轮只同步记忆，不替instructor审签005或新增任务。

## 23. 用户闭环走查反馈与main本人判断（2026-10-20）

read_commit=fdf0e3119a65f7290029b5831d23308413950fe6；main本人ACK INSTRUCTOR-TO-MAIN-LOOP-FEEDBACK-20261020-001。用户按感知→决策→规划→控制→再感知审视：四项传感器简化期望未见落实、框/置信度仍显示；决策/重规划细节看不清，原始采样不能马虎；A*平滑/轨迹优化似未见；手柄感觉还行。用户观察不改写成源码缺失或通过，控制主观正向不外推全部安全。

已直接读RC-v1.1 D2/D7、005阶段报告和SLIM-004B历史证据索引；直接从scratch读附件《1015-1115.pdf》第1页，其明确第一周观测模型设计/参数表与接入验证，但未列四路或四参数清单。历史检索返回简化合理模型、不走真实标定方向，并提示四传感器旧大纲和单相机待批准审计；这些提示非本轮原件复核，不据此声称用户撤回要求。RC-v1.1当前规定binary理想化报告且四模态非主实验必需；报告形式与传感器数量分属不同维度，关系列待对齐，不自动新增模态/改合同/填数值。

正式判断与对照表见handoffs/MAIN-TO-INSTRUCTOR-LOOP-FEEDBACK-20261020-001.md。沿instructor/005先核一键实际展开、source/install、交互profile与观测profile区别、有效参数/机会节拍、框/置信度支路是否存在后验消费者及真实APPLIED证据；显示存在与合同隔离都不能单独证明真实接线。h5模式名不是观测配置的充分证据。SLIM-004B历史binary运行不证明用户当前会话已使用同一profile。

决策/规划先给一个真实事件的观测/后验版本→触发原因与输入时刻→实际generation/尝试ID→中心/assignment/路径变化或跳过/拒绝理由→执行路径接纳→后续观测链；字段缺失如实标记，不倒填ID、不为了说明新增smoke。原始源采样/传输接收/UI刷新/记录/训练重采样分开，源/接收时间、模拟/墙钟、缺测/重复、单位/frame可追溯，不随意降采样/洗时间。A*原始路径、后处理、assignment成本与实际跟踪分别核对，缺失时先给影响方案，不直接换规划器或用绘图插值冒充轨迹优化。

本轮只写main回复与记忆。005既有总体卡顿/输入真实性优先级、主agent+3只读子agent/原运行边界保持，不替工程线分配新任务、代签ACK或重跑004。本轮未访问实际运行源码/设备，工程事实是仓库报告/历史索引证据，不声称亲跑或已修复。新交接接收待本人回执。
