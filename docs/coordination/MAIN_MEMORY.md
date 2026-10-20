# main 共享工作记忆 — USV 研究统筹

更新日期：2026-10-20，Asia/Shanghai。维护者：main。研究语义：RC-20261020-v1 + decisions/RC-20261020-v1.1.md。
用途：六角色共同读取的研究和事实基线；不是平台完成证明，也不代表其他对话已经接收。
最新统筹补充：main已接收instructor本轮本人回报：已读FIELD2 blob f9120401471c876df9ed610f04b905f923f25fc0，接受FPV+08/09/10优先、四路三层/radar-lidar待裁决及暂不平滑；已沿005续派隔离补丁、测试与下一版切换准备。写前已读新提交7495731013d3d9dce0c4c0b13a0271b84be02d2d及005追加条款：续派已正式发布，constructor本批新领取/候选完成仍待本人证据。legacy逐艇动态monotonic freshness=2s与昂贵LOS可能造成同批后排超时，仍是instructor源码线索，待旧版反例证实；不能放宽TTL。FPV须定位源/relay/Qt最早瓶颈，不拿30Hz配置上限充实测。R1生产/用户会话保持，候选经instructor核查后再统一切换；005仍RUNNING、未称修复或部署完成。原只读总额度不续时，无新增Gazebo/操纵。见第29节；第27—28节保留R2/Windows和FIELD2证据边界。
论文验收历史依据：5748cf31的R1修订及当时独立编译/局部PDF复审见第12节；RF/Xie增量及7页检查见第20节。当前事实见第1—9与27—29节；第10—26节保留相应检查时快照及仍有效分工。本次以当前仓库和用户指令为准，不声称读取所有历史对话或其他角色内部记忆。

## 1. 角色与工作目标

| 角色 | 负责 | 当前状态与下一步 |
|---|---|---|
| exploration | 文献整理、版本/原文证据、直接交付inspiration | Xie已接收；本轮main另读1cea3553的Ishii证据笔记/交付增量，按其证据范围接收，不冒称main复读原文。后续按明确论断缺口推进，不扩大主实验 |
| inspiration | 向用户解释全貌、讨论反例与研究取舍 | 用户/instructor称已通知继续解释FIELD2：AUTO10/HUMAN0未展示B2/B3；责任≠覆盖，收益是假设，讲平台→SEARCH采样→按组RF→replay/live→encounter。本人新ACK/回复待证据，不先反问或扩线 |
| main | 科学合同、计划优先级、跨线状态与评审 | 接收instructor本轮FIELD2本人ACK与005隔离补丁/测试续派回报；同步记忆/计划，不重复工程READY。候选、核查、切换和现场效果分别记录；Windows接收/执行仍待证据 |
| instructor | 平台设计、唯一工程派发与验收 | 本轮本人报告已读FIELD2并续派005隔离实现/测试及下一版切换准备；优先FPV+08/09/10，动态freshness/LOS线索待反例。候选由其核查、统一切换；续派已在74957310发布，候选回传待证据 |
| constructor | 实际平台实现、测试、报告与本人STATUS | R2@3796d83f隔离候选26离线tests、未部署；4579f89a回传当前run 08/09/10 CAMERA_INFO_STALE、FPV约5.4—6.5回调/s及163次generation，根因/源Hz-RTF/同generation轨迹仍缺；生产R1保持 |
| Windows本地Codex（既有桥接agent） | C:\bridge / C:\EyeTrackerBridge本机采集与发送；沿instructor/005协作 | 原LOCAL_AUDIT_COMPLETE不等于本轮接收。main已发R2跨线交接；本人ACK/实际源链证据/候选patch待回传，无可调用接收入口证据 |
| overleaf | 唯一论文母稿、引用与论证 | 论文HEAD214b2cc9无增量；原R1/RF-Xie ACCEPTED保持。下一次仅校正确有过时的工程当前状态，勿把UI候选/四传感器待对齐写成已实现或扩科学合同 |

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

004/004R2依据main已读取的0f2c80e7下instructor正式review及INSTRUCTOR-TO-MAIN-MANUAL交接。当前005依据1ae7932f下R1 review和constructor报告。instructor直接核对本地最终hash/原始事件并重算STOP统计，main按该正式review接收工程结论；main未访问实际Linux/Windows工作区或独立重跑。最新原负责人review优先于旧STATUS与历史记忆。

| 工作 | 当前状态 | 证据与限制 |
|---|---|---|
| 001静态审计 | DONE / ACCEPTED | 历史审计，不用旧“缺SEARCH”否定后续实现 |
| 002 / SLIM-004D | instructor ACCEPTED | 预算/STOP/Recorder工程验收，非正式实验 |
| 003 / 003R | instructor ACCEPTED，限ROS API SEARCH/B2 | 最终sim clock阻断解除；实际UI未观察，非B3/encounter验收 |
| 004 | instructor ACCEPTED（限生产B3门控/无模型回退） | 最终Planner source/build SHA256=ad6b320e4ac9753019dcc84dc613e74d05fa3e53d6e9f3501b7dacb5f0541e84；004R2最终运行闭合fallback、撤销、直接STOP与Recorder。不是有效RF/正式效能验收 |
| 004R | instructor BLOCKED / RUN_CONSUMED | 唯一Gazebo已启动，临时START及cleanup错用example_interfaces/SetBool，真实为std_srvs/SetBool；未START。20路空闲零值不是STOP因果安全，旧额度不能重用 |
| 004R2 | instructor ACCEPTED（限定工程）；运行已完成、额度已消费 | run=448cd4ea97f64161bcaf9d850386bba5。instructor原始证据复核：STOP前20路均非零；STOP后各360条全零、最短11.634358088s，回执至保守屏障间689条亦零。任务活动约2.2s，非长期性能/预算删失验证 |
| 第一周平台准备 / 005 | 整体RUNNING；R1第二轮反馈取证、R2隔离未部署 | 4579f89a同run legacy链08/09/10 CAMERA_INFO_STALE 123/123，当前新事件0；FPV仍卡、眼动主观改善。R1离线证据有效但非现场整体通过；R2未部署/未有新review，Windows本人ACK待回传 |
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
| 005仍只有诊断/没有生产修改，或离屏快即现场已流畅 | R1已有代码并获CANDIDATE_READY；10000格70.05→0.89ms是合成离屏重复绘制耗时，不是现场FPS或用户体验通过；真实ASR/眼动端到端改善也未验证 |
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

1. **当前run FPV与08/09/10观测资格缺口优先，R1保持稳定**。4579f89a报告legacy链08/09/10在所查123次均CAMERA_INFO_STALE、01—07有效，源stamp/CameraInfo与consumer时间/参数根因待定位；不降低freshness掩盖，不用视觉帧或旧sampler PASS替代当前新binary/APPLIED。FPV源Hz/年龄/RTF仍缺，5.4—6.5回调/s和Qt均值不足以定唯一瓶颈。眼动主观快、手柄正向保留，无R2因果归属；现有R1进程/hash不动，无新smoke/渲染/部署，总只读额度不续时。
2. **继续实际语音/眼动修复**。原005 R2隔离实施，不仅提示诊断。语音逐块sd.rec/parec重开是已查源码机制，现场根因尚未证明；constructor已报连续PTT流候选。眼动UI既有depth1/latest_pending不重复当优化，需实际burst/队列年龄前后证据。main具名中转Windows新tracker/重复发包、本机单调分段/阻塞、UUV构建/15555及兼容候选要求；仅真用Windows音频15556才核该音频链。原始采样/记录/时间保留，跨机时钟未对齐仍UNALIGNED。热图美化/大布局/SEARCH大功能/轨迹优化后置。
3. **依赖顺序**。可操作/可记录/可导出平台→后续志愿者实际采样→RF开发训练/按组验证→模型与参数冻结→另行安排pilot/正式B2/B3评价。当前不招募、不启动正式采集/训练；工程联调样例不称志愿者数据或效能证据。
4. **RF接口已有合同**。decisions/RF-DATA-CONTRACT-v1.md明确人控艇t+H二维位置、最少运动状态/当前操纵、因果可用性和源身份、先按会话/参与者分组再造窗口、开发与正式评估分离。instructor不需等main再次给同一数据语义；具体接口/键位按实际资产设计。硬件联动不把眼动/语音自动扩为主实验特征。Windows Unity/Tobii桥接按第19节现有单接收链纳入准备，先核实真实收包/发布/记录与来源身份，不能用Linux接收时刻补写成Windows采样身份。
5. **inspiration先直接解释当前训练用途**。真人在VRX操纵艇→记录运动状态/当前命令→同艇同控制段且SEARCH连续有效的t+H位置标签→按参与者/完整会话分组训练→预测人控艇未来位置→B2当前位/B3有效未来位责任比较。不是训练语音、眼动、底层驾驶或目标探测器。眼动/语音非本版RF必需，但影响行为/时序的卡顿与输入失真须先修；不以反问/新文献扩线代替解释。文献/论文保持既定边界。
6. **四路与路径后继已给main判断**。当前注册表camera/sonar/infrared/radar仅camera启用；用户新增lidar候选与radar不同，先并列用途/接口/负载，不暗换第四路。每路分别标展示占位/传感仿真/后验观测实际或缺失，binary不取消四路也不自动批准独立融合。先FPV/观测问题再逐路方案。路径已有163次generation证据但未分离同generation实际摆动，复杂优化无必要性结论、最小净空简化仅候选，未授权本轮实施/变成本。H等科学数值与人数/时长仍OPEN，原采样与显示/记录/训练重采样分开。

## 9. 当前交接与本人接收

- main统筹入口：已本人接收9e8bc6c7 R2及8e03631b FIELD2、读取3796d83f隔离候选；两份main交接分别中转Windows协作和回复四路/路径判断，均沿原005、非新READY。Windows无可调用入口及本人ACK/执行证据，不把仓库发布当即时通知。
- instructor RF请求f884a8ce、PREP请求8cb9879f均已由main回复且instructor本人ACK；合同不再待重复批准。instructor在cac0e02e本人ACK main手动走查决定，并发布005第一阶段READY，原DRAFT/PRODUCTION_BLOCKED_BY_004R已由任务所有者更正。
- constructor已完成004/004R2且限定ACCEPTED保留；R1第二轮反馈及4579f89a同run取证已回传，005仍RUNNING未整体ACCEPTED。R2隔离候选@3796d83f已报、未部署/未见R2 review。不把当前legacy资格缺口写成已解决或将R2fixture当现场麦克风/Windows数据。
- overleaf在c3c75966本人ACK PAPER-001最终ACCEPTED、MAIN-003、RF合同、第一周计划与Xie证据（通信read_commit=87364b3b）；不再标该接收缺口。其RF/Xie新增论文内容已在本轮审查ACCEPTED，见第20节；线上Overleaf版本仍未核实。
- exploration本人ACK及交付=1b5067ea，main本轮已实际读取并接收；不再标“exploration待本人ACK”。inspiration在629062c8已本人记录接收EX-XIE-01—05；overleaf亦已在c3c75966本人记录读入。
- inspiration：原基线本人ACK=629062c8、read_commit=c821fbb9保持。当前用户/instructor称训练用途解释请求已发送/送达；尚无该新请求的本人ACK/解释结果，不假报已解释或已改研究笔记。未验证其自动接收器。
- 自动化：本轮peek核现有main任务enabled=true，last_run_time仍2026-10-20T09:34:08.095942+00:00、next_run_time=null，不是运行成功/交付证明；本轮未另建或修改自动化。可见登记中无Windows接收器，constructor本地runner及其余Work接收闭环仍未验证。

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

## 24. 全角色统筹、子agent状态核对与复验候选版（2026-10-20）

用户要求继续统筹并更新认知/必要文件，检查constructor子agent，建设后由用户运行仿真检查UI、流畅性、语义。main实际读三分支HEAD（通信b3ede718、论文214b2cc9、main旧749a4a06），本轮首读无新提交；读各角色本人回执/005报告和计划/协议。没有新报告不等于各远端会话没工作，main未访问Linux子agent管理器。

现有constructor证据仅到bf78ed55/79226670：三只读子agent启动并有UI/性能/数据流线索；尚无各agent当前运行/完成/阻塞时间、最终产出、集成改动或性能实测。新统筹MAIN-20261020-004沿instructor/005要求主agent在下一实际报告合并一次状态/成果快照，并把有依据的小修做成可复验候选版。不新增工程READY、不另启同名agent、不让已确认语义缺口被所有实时测量阻塞。用户未来自己跑平台不扩助手自动运行额度。

修正main自有文件：第一周计划的005 DRAFT已过时，更新READY/RUNNING及首轮反馈后交付；角色协议当前工程/模型升档口径改为005与实际难题，补子agent证据和唯一集成；保留他人历史回执，不代改其内部认知或任务。inspiration训练解释新回执仍无；overleaf论文HEAD无变且已验收结果保留，下一次只做必要状态增量；exploration已有证据保留，不给无具体问题的扩搜任务。

main自动化发现真实停用并恢复：原id=6ad720ead3cc8191abc79a66100726cc，更新后peek enabled=true，当前last_run_time为17:34:08.095942+08:00，无后台成功证据；原每小时schedule不变。未重复创建，不推测停用原因、不宣称其他Work被唤醒。细节见receipts/automation-main.md。

本轮交付仅统筹/计划/协议/自动化回执等main文件，尚无生产优化版本。下次可交用户的候选版应有实际source/install版本/hash、可见改动/已知缺口、必要定向验证和一两项复验操作；可体验不等于005整体、硬件或科学ACCEPTED。新交接接收/改动落地以本人证据更新。

## 25. 005 R1实施批接收：三子agent全部关闭（2026-10-20）

main本人读入6c51a0c9a3e0cf3d79fa92a39f9d9fe27d2ef2e0：仅原005任务R1追加及instructor本人回执变化。instructor已ACK MAIN-004/LOOP、直接读constructor及3子agent最终输出并确认全完成close；这更新第24节“当前状态未核实”历史快照，不是main亲看远端管理器。constructor首报没有生产修复。

原005立即实施R1，复用既有调查：整体卡顿以隔离Qt/合成帧回放和聚合计时取得可重复基线，针对证实热点修最小显示链；语音补已证实last_result.errors漏显、事件关联的ASR/解析/策略/执行反馈及明确等义/歧义反例；眼动分设备样本和UDP包计数、Linux接收/发布/Qt阶段耗时、UNALIGNED/积压，有证据才改队列。不能用parser测试当ASR通过、UDP包率当独立设备采样率或无时钟映射的端到端延迟；不改源采样/洗时间/恢复双LSL/越权修改Windows。

console主agent单人整合，受影响测试/构建/source-install hash和真实前后证据随候选报告；尚无实测的现场项保留待用户。首批热图美化、布局、SEARCH大功能、轨迹优化不抢前三优先，四传感器期望/binary区别已接收且不改科学合同。无新自动Gazebo/控制许可，005仍RUNNING，不自签ACCEPTED。主agent已被通知继续实施，main不再派重复调查或另开READY；本轮仅同步主记忆和第一周当前批次。

## 26. 005 R1实际候选版接收：交用户现场复验（2026-10-20）

main本人读取review提交1ae7932f7d84cb3bc16c719e7fe83a7e8db6efb0下tasks/USV-20261020-005.R1.review.md及reports/USV-20261020-005.md的R1段；instructor复核基点b1d5a4a5385fc893c7e8f9552c0ac240184fcdac。当前结论CANDIDATE_READY / FIELD_FEEDBACK_PENDING，005整体仍RUNNING。第24—25节“尚无候选/生产修复”的历史状态不再作当前结论。

证据归属：instructor亲核console/parser/gaze导入经build symlink解析到源码、字节/hash相同，独立五文件53tests通过（2.37s，0 skip）及bash-n通过；三包colcon build通过依据constructor回传，instructor未重复build。main只读上述报告，不冒称亲入Linux重跑。三模块完整SHA256见review；运行根Git HEAD UNKNOWN、实现提交NONE，通信SHA不是完整运行源码快照。原三只读子agent已结束，本批两代码子agent已回传关闭，主agent完成console集成。

实际改动：概率图变化时重建/重复绘制复用，视频缩放缓存与BGR直拷，每10秒聚合image/spin/cycle/video/map耗时；constructor同尺寸合成离屏10000格重复绘制70.05→0.89ms（新首帧27.62ms），不能换称Gazebo FPS或现场已流畅。语音补ASR无文本/错误、parser错误、同命令策略/执行分层，失败不被ready抹掉；E5/E 5/E区5/E，5/E、5等义，多艇/多目的地继续拒绝。Whisper/PTT/VAD未改，真实ASR质量与声学时延未知。眼动独立统计UDP包与tracker唯一/重复/倒退/缺失，显示Linux阶段和UNALIGNED；未改Windows采集/时钟、未证明端到端提速，队列深度/丢包仍未知。

下一步由用户在保存/结束需保留的旧会话后，使用原入口`cd /home/cyz/vrx_ws && ./run_vrx.sh start`；默认h5_command_aware含Qt/joy/pad/voice/gaze，不加--research-core。start会清理旧进程；旧进程不会自动加载改动，不在需保留的会话中盲目重启。先切FPV/全局页、切艇/鼠标感受流畅性；用户可控场景中做一次语音并看原文/失败层/执行反馈；Windows发送端在场时看眼动点位、新tracker/重复/包率与Linux分段。短文字或截图即可，卡顿时一条ui_timing_10s可辅助定位。总端到端时钟未对齐继续UNALIGNED，不补造数字。全套结束用`./run_vrx.sh stop`，本轮助手未代运行。

原始采样/Recorder、手柄映射、科学合同和规划未改；四传感器期望与binary区别、单艇SEARCH入口及其余005后继仍保留。无本轮自动Gazebo/主动操纵/硬件实测，不以本批候选升级全部UI/硬件/RF/效能验收。沿instructor/005根据现场反馈小步继续，不另发READY。

## 27. R1现场复验期间的R2隔离修复与Windows中转（2026-10-20）

main本人读9e8bc6c7d429cea00916c7a8322a08a7d3d96cb6的INSTRUCTOR-TO-MAIN-VOICE-GAZE-R2交接及005 R2条款，并读后继3796d83fef253b4da5add7369aa362e25b868b05的constructor报告增量。用户要求继续实际语音识别/眼动延迟修复，Windows由main协调，不大改UI；当前R1用户体验保持生产hash/进程稳定，R2隔离实现与切换分开。

constructor报告R2在/tmp/usv_005_r2_hvSJ6a/：每PTT会话连续采音，模型/阈值/prompt/beam不变；UDP fixture 302包首轮256、余46，原始发布保留300递增序号包（含重复/倒退tracker），候选Qt同source/session拒绝已知重复/倒退进入UI/attention，眼动接收生产源码不变；直接反例R1 FAIL/候选PASS、26离线tests通过。上述是constructor本人报告，main未亲跑，也未见R2 instructor review；计数/过滤通过不能换称队列年龄或端到端延迟已改善。运行根无实现提交，通信SHA非生产完整快照。

main已具名发Windows跨线handoff：源设备唯一tracker与Unity重复发送分别计数；本机采集/回调到达、队列与socket单调时间/阻塞；当前UUV.exe/DLL/源构建、实际15555目标；证据充分后做隔离源新样本发送/显示通道最新优先候选，保留原始采样/记录/时间与协议兼容。原协议缺source session/序号等则列缺失，不接收端倒填为科研来源；音频仅实际15556时核。详见handoffs/MAIN-TO-WINDOWS-VOICE-GAZE-R2-20261020-001.md。

本人执行证据限读取、通信入口核查与仓库中转：可用agent列表只有/root，既有Windows报告/仓库/历史线索无可调用session/runner，peek未见Windows接收器。Windows本人ACK、开始执行、候选和设备数据均PENDING；本轮未访问Windows、未替换exe或操作R1、未启动录音/仿真/训练。路由缺口已写回instructor，不要求用户再找聊天ID，不新建云端agent冒充Windows。沿原005等待真实本人回执，接收/执行/切换/验收分别更新。

## 28. R1第二轮现场反馈、四路三层与路径必要性（2026-10-20）

main本人ACK FIELD2@8e03631b5181485d762bc4b5aeb435ee69ded269，读RC-v1.1 D2/D6并接收instructor对当前主链的源码核查摘要；main未亲看原截图/实际Linux源码或run。FPV仍卡；09/10区域长期红为疑点而非已判源故障；眼动“快不少”是R1主观正向，不归因未部署R2、无跨机毫秒数。逐艇01—10机会/ABSTAIN/freshness/APPLIED与FPV源Hz/RTF/Qt证据已由instructor沿005派发，不重复工程READY。

main正式判断见handoffs/MAIN-TO-INSTRUCTOR-FIELD2-20261020-001.md：四路建设期望保留；当前注册表camera/sonar/infrared/radar仅camera启用，lidar为用户本轮候选，需并列radar/lidar差异、不静默替换第四路；分别列视觉占位、仿真传感器/物理近似、进入后验的理想化观测。允许提出camera占位方案，但不得冒充声学/红外模型；lidar迁移先核版本/消息/TF/外参/许可与负载。当前binary主profile不等于只有一传感器，也不因四路展示自动增加独立likelihood。先实际manifest/逐路预算，FPV/观测缺口优先，不在用户会话盲增渲染或改科学合同。

路径复杂优化当前无必要证据；先看同generation格栅折线、换代跳变与实际航迹/航向。必要时净空检查的最小简化可作候选，但须先解释收益/边界再决定实施；不把lookahead当完整优化、不用画圆遮掩跟踪/重规划原因。执行路径若改变需保持安全和成本/assignment一致，本轮不改规划器/成本、不部署平滑。

inspiration应直接解释责任是未来任务分配、不是已感知证明；AUTO10/HUMAN0未展示人工SEARCH/有效预测，不是B2/B3效果演示。按平台与身份/流程→真实SEARCH操纵→同段t+H标签→参与者/会话分组RF验证→冻结后配对replay及另行live→encounter评价讲明。replay条件化在给定人工轨迹，不能证明live人机效能；收益待检验、数值/人数时长OPEN。本人新解释完成尚无回执，不假称已交付。

写前收到constructor新报告4579f89a065fecbf4751962cb1e30bda07172593：run=05e99147b14b4ce59f2892fd3acffe3d，manifest未finalize，实际command_aware / LEGACY_ASSUMED_BATCH；仿真20—508秒123次更新，08/09/10均CAMERA_INFO_STALE、01—07有效，新离散事件seen/applied/rejected=0，09/10 pose正常。main据此将当前疑点更新为“该窗口legacy几何资格缺口有报告证据，根因未定”；视觉候选/旧004C sampler PASS不可补成当前binary证据，不能暗切profile或放宽freshness。FPV约5.4—6.5回调/s、转换均值0.32—0.44ms/paint6.7—7.6ms/cycle1.7—1.8ms，同窗源Hz/年龄/RTF未记录；不认定Qt唯一瓶颈。同run163次generation提交仅提示检查换代，未证真实艇摆动。当前注册表第四路radar与用户lidar建议不同，先列差异/候选，未裁决替换。上述按constructor本人报告接收，不冒称main直接测量；未覆盖其文件。

## 29. FIELD2本人接收与005隔离补丁、测试、切换准备（2026-10-20）

- role=main；read_commit=7495731013d3d9dce0c4c0b13a0271b84be02d2d；active_task=005统筹状态同步；contract_version=RC-v1 + RC-v1.1（不变）。main核对FIELD2正文与blob f9120401471c876df9ed610f04b905f923f25fc0一致；首读35838c34的005任务/报告、instructor回执及计划，写前发现新HEAD，复核差异只改005并读取新增条款（blob 2e345ab2f78cddf1d6da7f2f54ce294873b52fef）。instructor本人ACK与续派已正式发布，不再仅记对话回报；constructor本批新领取/候选完成尚未见新证据。本次main两个目标文件未被并发修改，保留新的005。
- 接收优先级：FPV与08/09/10观测资格；四路按展示/物理近似/二值观测三层列清单，radar/lidar待裁决；暂不实施平滑。用户要求实际补丁+测试和下一版切换，沿现有005隔离推进，不只停留于诊断。main不另发竞争READY，也不覆盖instructor任务/review或constructor报告/STATUS。
- 新根因线索归属instructor亲读Linux源码：legacy target_search_node逐艇resolve后执行昂贵LOS，CameraPoseSource每次使用动态monotonic判定2s freshness；怀疑同批运算耗时令后排艇超时。源码机制不等于现场根因已证实，main未亲读Linux源码/重跑。按instructor已发布条款先用假时钟/调换艇序让旧版反例失败，再冻结同批几何与判定时间；保持原TTL和源时间，不能让批开始已陈旧/缺失的输入因冻结变合法，也不能把快照重复用作后续批的新样本。
- FPV沿同窗source→relay→Qt查最早瓶颈；配置30Hz仅上限，既有约5.4—6.5回调/s也不能单独定位源端。证据缺项继续UNKNOWN；如需新被动采样仅一次最多30秒且须在原15分钟总额度剩余内，额度用尽改用既有记录/离线链，不重新计时续额。离线反例/补丁测试与现场FPS分开，不因显示修复降低科研源采样、洗时间或刷后验颜色。
- 下一交付应为隔离补丁及基线/候选hash、旧版失败→候选通过的直接证据、必要回归/隔离构建与source/install一致性、剩余现场项，以及持久可取候选/备份/切换/回退说明；由主agent唯一集成已有R2语音/眼动候选与本批修复。先由instructor核查，部署程序在用户会话仍存活时必须拒绝且不杀进程，用户保存退出后再统一切换。R1源码/build/install、用户进程及Windows当前exe保持稳定；本轮未实际切换、未运行仿真/操纵/录音/训练。005仍RUNNING，补丁完成、部署完成与现场效果均未被本回报证明。

本轮main只更新自有记忆和阶段计划，既有Windows中转和未部署语音/眼动R2证据保持；不产生ACK套ACK或另行催派。后续有实际候选/review/切换证据再增量更新。
