# main 共享工作记忆 — USV 研究统筹

更新日期：2026-10-20，Asia/Shanghai。维护者：main。研究语义：RC-20261020-v1 + decisions/RC-20261020-v1.1.md。
用途：四角色共同读取的研究和事实基线；不是平台完成证明，也不代表其他对话已经接收。
本轮依据：当前可访问对话、用户提供的论文源文件、仓库决策/文献记录、001—003R 工程任务/报告/评审和 PAPER-20261020-001 实际修订。第1—9节由main本轮更新；第10节保留instructor历史追加。跨对话历史检索本轮报错；不能声称完整读取所有历史对话或其他角色的内部记忆。

## 1. 角色与工作目标

| 角色 | 原称 | 负责 | 当前交付 |
|---|---|---|---|
| main | 本统筹对话 | 科学问题、范围、指标、路线冻结、证据与论文一致性 | 本记忆、科学裁决、跨线交接 |
| instructor | 重构仿真平台 | 平台设计、唯一工程任务下发与验收 | 003/003R已验收，按main新补充发布独立B3门控/fallback任务 |
| constructor | 审计 VRX 仿真平台精简方案 agent | 读取实际本地源码、实现、测试、报告 | 代码/文件版本、运行证据、真实阻断 |
| overleaf | 撰写IEEEtran论文主干 | 唯一论文母稿、文献原文核查、数学和叙述、编译 | 修订 TeX、文献证据表、研究边界与决策建议 |

main 不与 instructor 同时向 constructor 下发实现任务。overleaf 发现工程缺口通过 main/instructor 提交，不直接改变平台定义。角色名不等于新的后台代理，任务发布不等于接收或执行。

## 2. 当前研究主线

在操作员可接管、导航、切艇和中断任务的多 USV 概率搜索中，**预测未来人工搜索责任，是否比只利用当前人工搜索责任改善协同？**

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

## 4. 简单成功判据与统计口径

任意**同一艘**艇距离真实目标不超过 R（论文 rho_E），连续保持 tau（论文 tau_E）即有效目标遭遇。离开则计时清零；不能跨访问或跨艇拼接时间。自主、人控、NAVIGATE 同等评价，不加朝向、FOV 或检测概率门槛。

这是 sustained-proximity / effective target encounter，不是视觉检测、人工确认或救援。真值位置和距离只供独立评价器；事件结果可供记录和终止，不向规划器/后验泄露目标位置。

拟定主指标：共同预算 B 下遭遇时间的 RMST；主效应 RMST_B3(B) − RMST_B2(B)，负值支持更快遭遇。预算内未遭遇的有效试验必须保留。行政 STOP、崩溃和无效时钟需另行处理，不能随意混作普通预算删失。

R、tau、正式 B 仍 OPEN。main新补充已冻结：主实验正常成功仅encounter；POSITIVE/旧Gamma确认不能独自宣告成功或提前替代终点；合法T_E<=B计成功，T_E=B时成功优先于自然预算。位姿采样不插值、不回填，缺测超间隔/无效/离开重置；具体采样节拍与最大间隔仍待配置核对。正式统计截止不能因消息延迟扩大。上述是研究要求，现有预算验收不等于encounter实现或删失验收。

## 5. 工程事实快照

快照依据通信分支7ec7bb50bdb7cb1ab8f1186483a01c3fb49f5e14（003/003R review与三角色本人ACK）。每次行动前读取最新文件；旧READY已消费，不能重领。

| 工作 | 当前可确认状态 | 证据与限制 |
|---|---|---|
| 通信及角色接收 | CONNECTED；instructor/constructor/overleaf本人receipt均已读取 | 完成角色交接，不等于新文件自动接收或后台执行 |
| USV-20261020-001 | DONE / ACCEPTED，静态审计 | 保留历史发现；不能据其“缺SEARCH”否定后来实现 |
| SLIM-004B | overleaf已读本地最终报告，报告183 tests/80事件 | main仅有本轮报告转述，未独立读取本地原报告/源码；UNKNOWN目标精确runtime分支未重现；无新增独立ACCEPTED |
| USV-20261020-002 / SLIM-004D | ACCEPTED，报告支持的工程验收 | 预算到期、安全STOP、Recorder；非正式实验 |
| USV-20261020-003 / 003R | instructor ACCEPTED，限ROS API SEARCH/B2 | 最终sim clock运行解除原阻断；UI未观察，非B3/encounter验收 |
| B3生产fallback | 尚未验收；main允许instructor发布独立后续任务 | 不是直接给constructor运行许可；不暗填H/阈值、不要求先训练RF |
| encounter、正式B2/B3、RMST | 未验证/未报告 | 主语义新冻结，数字和实现/统计证据仍需补齐 |

002 run_id=7904539e7ad44213b4baa971245e3bb9；start=42.540s、deadline=82.540s、发布=83.000s。0.460s发布延迟不能延长分析预算。10/10 path STOPPED、20/20 thruster=0，T_conf=null；encounter_censoring_validated=false。

003旧时钟run=35f88090997a482d818950ae26bc9eb9保留为历史业务证据。003R最终配置run=5c84c3736225450eb5d0759cd1498f59已由instructor核查文件hash及原始time_series/manifest：77条相关记录为1—44s，无Unix epoch污染；SEARCH当前位/撤销、9/10自主池成立。构建/58tests、参数与安全推力窗口依constructor报告，instructor未重新运行；main读取的是这些review与回执，未进入本地。

中心与28.324s fleet pose相距0.0287m；0.024s是对Recorder外层28.348s的差，源plan stamp28.152s对应差0.172s。只作邻近时段位置对照，不称源时刻精确同步。003R为行政STOP，不替代002自然预算验收。OPERATOR_UI_CLICK与该次条件sampler runtime均NOT_OBSERVED。

## 6. 源码、论文与资产入口

- 实际运行工作区：/home/cyz/vrx_ws；根无有效 Git HEAD，实现提交 SHA=NONE。研究仓库和通信 SHA 不是运行平台 SHA。继续记录修改文件 SHA256、dirty 状态、构建和运行证据，后续由 instructor 安排可复现源码快照；不能把文件 hash 等同完整环境复现。
- 本地版本化研究仓库：/home/cyz/USV_HRI_PATROL；此前回执 main@5f263c694f3d601bf1596bb92b0849d98f7e677b 且有未提交决策，不清理或覆盖。
- 远端 main@749a4a06db0b24d0fdd3bcb47618a365dfa5bdfa 是旧仓库快照，不是当前生产源码。通信分支和论文分支中的旧 platform/ 不用于覆盖本地。
- VRX 上游 humble 固定 dc30ed8d17aa1083fd872edad9c77c69896d2b07；项目变更通过本项目 patch/setup 管理，不推上游。
- 通信：coordination/work-20261020 / docs/coordination/。
- 论文：paper/overleaf-20261020 / paper/manuscript/main.tex。本轮审查HEAD=e1c5915c641606fb7996763f0ba7ea9f96817308；正文提交22104cbedafa662bb7b2feac9ee8d41e6eea2c3d，SHA256=41663e897bd48d22cfd5e3d9d6798d3f6e68fe65a47d28ab764c99b5c7edf361。
- 当前正文沿用户conference_latex.zip与此前3页稿实质修订，main独立编译为5页，无正式结果；无undefined/Overfull，16处Underfull，全部5页已目视核查，第5页首段字距待小修。PAPER-20261020-001=CHANGES_REQUESTED（定向小修），不是推翻本轮工作。原长稿在paper/archive/overleaf_20261020_main.tex。
- 线上 Overleaf 替换/同步 UNKNOWN。仓库上传不等于 Overleaf 已更新。用户明确要求后续修订 TeX 继续提交论文分支。
- 文献已有 literature/LITERATURE_LEDGER.md、novelty_boundary.md、PDF/metadata 与 paper/manuscript/references.bib。26 条旧台账、旧 FULLY_READ 标签是历史阅读记录，不代替本轮关键论断的原文定位。

## 7. 记忆审计：必须纠正的漂移

| 旧说法或风险 | 当前应记为 |
|---|---|
| 004D 一直未验收 | 002 已由 instructor ACCEPTED，限报告支持的预算/停止工程闭环 |
| 仍无SEARCH实现或003R尚未执行 | 003/003R已API级ACCEPTED；UI/B3/encounter仍未验证 |
| 接管/给导航目的地就获得 fixed center | 只有显式 SEARCH 激活；NAVIGATE 撤销搜索责任 |
| 论文正文路径未知/仓库仍只有占位 | 当前母稿已在论文分支；仅线上 Overleaf 同步未知 |
| “少量预测/多模态 + Bayes + 规划”就是创新 | 核验最相近工作的已实现机制，收紧责任层的问题与可检验区别 |
| 真实感知标定是当前第二贡献 | 旧 literature/novelty_boundary.md 的候选，当前精简主线未承诺，也没有验证证据 |
| 旧T_FD/T_conf、Gamma或R_miss就是当前成功判据 | 主实验成功仅encounter，旧确认不得单独触发主实验正常成功；字段映射和实现仍待instructor落实 |
| B2/B3 始终同 posterior，B4 必然上界 | 共享更新规则，后验可随轨迹分化；B4 只作完美未来信息参考 |
| verified_refs.bib 或 FULLY_READ 代表所有新论断已验证 | 必须记录真实原文版本、页/节/公式、支持范围和不能推出的结论 |
| 自动通信已经建立跨对话持续调度 | 已有可读写仓库通道；角色 ACK 和用户启动仍需真实发生 |

本轮只审计可见的记忆载体/产物，不能读取或改写其他对话内部记忆。各角色需提交自己读取的 commit、纠正条目和当前任务回执。旧 idea/研究决策状态.md 的“人工目的地可作固定中心”、旧传感器第二贡献等，与本轮已确认语义冲突时，按用户较新指令与 RC-20261020-v1 处理；不恢复旧语义。原文献结论则不能被研究偏好覆盖，必须回原文核查。

## 8. 仍开放与推进顺序

- main：已发布RC-v1.1，冻结单binary理想化观测范围（四模态不扩入）、真值两类合法用途、encounter唯一成功/边界同tick、缺测操作语义和统计单位原则。R/tau/B/H及配置阈值/样本量仍OPEN，待最小配置依据表，不暗填数字。
- instructor/constructor：003R已收口；main允许instructor下发独立B3门控/fallback接线任务，再按依赖拆分encounter。无模型回退不需等待RF训练/正式样本量；constructor按唯一新READY执行，不重做003R。
- overleaf：PAPER-001已实质修订；main抽查五篇关键原文与20项审计，保留主体成果。按review定向修正人控艇/操作者位置、GT用途矛盾、几何条件下sensor-evidence belief假设、引用顺序/版式，并同步新科学补充。
- 实验：先完成工程和日志可测性，再开发集预测验证、配对 replay、必要的 live pilot/正式研究；不能把 calendar 目标当已完成事实。
- 10/15—11/15 原月度计划保留为路线参考（工程整合→数据/预测→部署/pilot→合格正式实验/论文）；实际验收依赖优先，不编造样本、训练、结果或伦理审批。

## 9. 本轮入口与接收状态

- 协作补充：ROLE_PROTOCOL_v1_1.md。
- instructor 交接：handoffs/INSTRUCTOR-20261020-001.md。
- overleaf 任务：论文分支 paper/manuscript/tasks/PAPER-20261020-001.md。
- main已真实读取instructor / constructor / overleaf三份本人角色回执；本轮角色交接完成。新MAIN-20261020-002/RC-v1.1的接收尚PENDING，不代签。
- 本文后续由 main 按已接收报告/review 更新；修订不抹掉先前快照与证据限制。


## 10. instructor 审计更新（2026-10-20；用户授权追加）

维护边界：以上 main 原快照完整保留；本节由 instructor 按本次用户明确要求更新项目记忆，不代表 main/constructor/overleaf 已接收。read_commit=`27c5303cd1bab4097b83582e13a96c88ce4f659c`。

- 003R 报告与 STATUS 已为 DONE；唯一最终配置 run_id=`5c84c3736225450eb5d0759cd1498f59`。当前审查结论：003R **ACCEPTED**，003 **ACCEPTED**（限 ROS API SEARCH/B2 工程）；详见 tasks/USV-20261020-003R.review.md 与更新后的 003.review。第 5/7/9 节关于“003R 未执行/最终时钟待运行”的旧快照已被本节取代，历史证据不删除。
- instructor 已只读核对实际 source/install hash、003R 本地详报与原始 time_series/manifest：77 条相关记录为 1–44 s、无 Unix epoch 量级污染，日志 hash 匹配 manifest；9/10 自主池、B2 中心与撤销链匹配。构建/58 tests、runtime 参数和推力观察窗按 constructor 报告审查，本轮未重跑。时间对照 0.024 s 为 Recorder 接收基准，与源 plan stamp 的差为 0.172 s，不作精确同步证据。
- 002 自然预算终态验收保留；003R 行政 STOP 不替代自然 BUDGET_EXPIRED。UI 点击、条件 Sampler 本次 runtime、B3 fallback、encounter、正式 FOUND/实验/RMST 仍未验证；全部科学 OPEN 保持。
- instructor 本轮接收 ACK 已写 receipts/instructor-20261020.md；constructor 本轮角色/记忆 ACK 仍 PENDING，旧 LOCAL_RECEIPT 是历史快照；不得假定远端发布已被读取。
- 无新增工程 READY、无追加运行预算、不重启或扩张 003R。constructor 下一次接续仅按 003R review 补角色回执、本人 STATUS 及时间差说明；PAPER–PLATFORM HANDOFF 已在 review 向 main 提供，B3 后续尚未授权。


写入前并发检查：重新读取 HEAD=`acb5760c0b7aba1b1fcfcaf92ebd5b1429714bd2`，相对首读基线仅新增 overleaf 角色回执，已读取并保留；本次所写四个路径无并发修改。overleaf 回执的接收/科学内容以其原文为准。


## 11. main 本轮评审与裁决记录

本次以7ec7bb50通信快照和e1c5915c论文快照复核。第5/6/7/8/9节已经刷新为当前事实；第10节是instructor历史追加，其中constructor ACK待接收已由最新本人receipt解除。论文任务的DONE转入main定向CHANGES_REQUESTED，详见论文分支tasks/PAPER-20261020-001.review.md。新路由为handoffs/MAIN-20261020-002.md。

主线保持简单：主比较B2/B3；direct inhibition不列当前必做主实验，优先辅助replay候选。单binary/P_FA=0是理想化模型而非标定发现；同一p向量由观测生成器用于抽样、推断器用于likelihood，GT只留在生成器与遭遇评价器，不进入规划器。论文中“GT仅评价器”“operator位置”与未声明动作选择假设的完整后验表述需纠正。主张与证据的边界不因工程验收或编译通过而放宽。
