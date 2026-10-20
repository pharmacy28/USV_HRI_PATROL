# exploration — USV项目文献总入口

2026-10-20；main按用户授权建立，后续由exploration维护。规范角色名为exploration（用户首次亦写esploration）。

## 收集结果与适用范围

- **46个去重作品记录**：并集来自仓库26条catalog、论文分支31条canonical bib、当前20项原文审计、历史长稿7条引用，以及Library历史20条台账、补充bib、六篇阅读卡和后续竞争工作矩阵。
- 仓库树实际列有**22份PDF**，逐条链接并保留既有SHA256及本次读到的Git blob；没有把本轮文件清点称为重新下载/逐页审阅22份全文。其余24条含开放网页/作者稿入口或获取缺口，不等于全部无全文。
- 当前母稿实际引用**17个作品**；审计有**20项主张、对应19个作品**（Xie两项），不能把20行当20篇；六篇阅读卡都是历史阅读记录，本轮读了卡本身，不等于重做全部原文核查/代码复现。
- 这是目前可定位材料的汇总，不保证遍历了所有不可见历史聊天。未检索到旧ICRA_USV_HRI_Zotero_and_Platform_Audit包本体；仓库中已有26条书目/元数据资产已纳入，不伪造该包已打开。
- 通信来源固定于`c98bbc71a5e3d3d75b612163c7a6d26f5eb8447d`，论文来源固定于`f8de4da17dbc3cc70eeedca409376c530cf9547b`。元数据/原文结论按各条证据来源使用，工程与研究状态以最新MAIN_MEMORY/RC为准。

## 使用顺序

1. 先读[交付inspiration的证据摘要](../docs/coordination/research/EXPLORATION_TO_INSPIRATION.md)，理解哪些研究边界已有证据。
2. 优先查P1八篇最接近工作及其原文定位；按当前问题补P2基础/机制文献。P3保留为扩展背景，不自动扩为主实验或论文引文。
3. 查[本表机器可读目录](exploration_catalog.json)：作者、venue、DOI/别名、来源版本、PDF路径/hash、历史阅读范围、当前核查范围、RW逐主张定位及限制。
4. 正文的具体陈述仍从[原文审计表](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/paper/manuscript/RELATED_WORK_AUDIT_20261020.md)定位回原文。投稿引用键/参考文献由overleaf唯一维护，本目录不替换canonical references.bib。

P1/P2/P3是本次整理的讨论优先级，不是创新性分数、全文核验等级或工程任务优先级。

## 去重与版本原则

- 按DOI/明确arXiv身份合并重复记录；Hsu arXiv:2505.14805与其ICRA2025作品合并，保留两入口。
- Bourgault2003与2004、Cangan2020与Heintzman2021、Hollinger2011与2015、Dalmasso2021与2024各自保留；同一谱系不代表可互换作者、公式、实验或页码。
- Rossano：arXiv首次提交2025，作者页称IROS2026接收并要求先引用预印本，目录保留作者引用年2026和版本说明，未虚构正式论文集DOI。
- Jovan关联勘误10.1007/s10514-023-10152-2列为待核关联，不增加研究作品计数；该文已从当前正文删除。
- 历史FULLY_READ、阅读卡结题、PDF存在均不能代替某个新论断的页/节/公式核查。旧novelty_boundary.md与007启动包中的候选机制/额外实验不自动成为当前要求。

## 作品目录

“本轮审计”栏引用的是已存在的论文审计记录，不表示main今天重新读了对应原文。没有RW条目的历史作品按原来源保留，具体内容待exploration定向核对。

| ID / 优先级 | 年份与作品（原文身份入口） | 文件/公开入口 | 阅读与审计来源 | 当前正文 |
|---|---|---|---|---|
| EXP-001 / P1 | 2011 · [Intention-Based Coordination and Interface Design for Human-Robot Cooperative Search](https://doi.org/10.1109/iros.2011.6094688) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Xie2011Intention.pdf) | RW-07 PASSAGE_CHECKED；第3页视觉核对, RW-08 PASSAGE_CHECKED | 是 |
| EXP-002 / P1 | 2021 · [Anticipatory Planning and Dynamic Lost Person Models for Human-Robot Search and Rescue](https://doi.org/10.1109/icra48506.2021.9562070) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Heintzman2021Anticipatory.pdf) | RW-09 PASSAGE_CHECKED; 历史阅读卡003 | 是 |
| EXP-003 / P1 | 2022 · [Information-Based Control of Robots in Search-and-Rescue Missions With Human Prior Knowledge](https://doi.org/10.1109/thms.2021.3113642) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/KrzysiakButail2022Information.pdf) | RW-13 PASSAGE_CHECKED; 历史阅读卡001 | 是 |
| EXP-004 / P1 | 2023 · [Enhancing Human-Robot Collaborative Object Search through Human Behavior Observation and Dialog](https://doi.org/10.1109/iccvw60793.2023.00199) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Ishii2023Enhancing.pdf) | RW-11 PASSAGE_CHECKED | 是 |
| EXP-005 / P1 | 2024 · [Shared Task Representation for Human--Robot Collaborative Navigation: The Collaborative Search Case](https://doi.org/10.1007/s12369-023-01067-0) | 无仓库PDF；[已有外部入口](https://link.springer.com/content/pdf/10.1007/s12369-023-01067-0.pdf) | RW-16 PASSAGE_CHECKED; 历史阅读卡004 | 是 |
| EXP-006 / P1 | 2025 · [Enhancing Human-Robot Collaborative Search Through Efficient Space Sharing with On-Demand Bidirectional Interaction](https://doi.org/10.1007/978-3-031-92591-7_2) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/LimMiuraHayashi2025SpaceSharing.pdf) | RW-12 PASSAGE_CHECKED | 是 |
| EXP-007 / P1 | 2025 · [Human Prior Knowledge Estimation from Movement Cues for Information-Based Control of Mobile Robots during Search](https://doi.org/10.1145/3706065) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/KrzysiakButail2025Movement.pdf) | RW-14 PASSAGE_CHECKED; 历史阅读卡002 | 是 |
| EXP-008 / P1 | 2025 · [Robot movement based inference of teleoperator state for multi-robot search](https://doi.org/10.1007/s40747-025-02055-9) | 无仓库PDF；[已有外部入口](https://link.springer.com/content/pdf/10.1007/s40747-025-02055-9.pdf) | RW-15 PASSAGE_CHECKED; 历史阅读卡006 | 是 |
| EXP-009 / P2 | 2003 · [Constrained Centroidal Voronoi Tessellations for Surfaces](https://doi.org/10.1137/s1064827501391576) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Du2003ConstrainedCVT.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-010 / P2 | 2003 · [Coordinated Decentralized Search for a Lost Target in a Bayesian World](https://doi.org/10.1109/iros.2003.1250604) | 无仓库PDF | 历史来源记录；新主张需原文定位 | 否 |
| EXP-011 / P2 | 2004 · [Coordinated search for a lost target in a Bayesian world](https://doi.org/10.1163/1568553042674707) | 无仓库PDF | RW-01 METADATA_ONLY | 是 |
| EXP-012 / P2 | 2004 · [Coverage Control for Mobile Sensing Networks](https://doi.org/10.1109/tra.2004.824698) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Cortes2004Coverage.pdf) | RW-04 PASSAGE_CHECKED | 是 |
| EXP-013 / P2 | 2009 · [Efficient Multi-Robot Search for a Moving Target](https://doi.org/10.1177/0278364908099853) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Hollinger2009Efficient.pdf) | RW-03 PASSAGE_CHECKED | 是 |
| EXP-014 / P2 | 2009 · [Local Voronoi Decomposition for Multi-Agent Task Allocation](https://doi.org/10.1109/robot.2009.5152829) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Fu2009LocalVoronoi.pdf) | RW-05 PASSAGE_CHECKED | 是 |
| EXP-015 / P2 | 2011 · [Distributed Coordination and Data Fusion for Underwater Search](https://doi.org/10.1109/icra.2011.5979685) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Hollinger2011Underwater.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-016 / P2 | 2013 · [Decentralized Multi-Robot Cooperation with Auctioned POMDPs](https://doi.org/10.1177/0278364913483345) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Capitan2013Auctioned.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-017 / P2 | 2015 · [Bayesian Intention Inference for Trajectory Prediction with an Unknown Goal Destination](https://doi.org/10.1109/iros.2015.7354203) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/BestFitch2015Bayesian.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-018 / P2 | 2015 · [Distributed Data Fusion for Multirobot Search](https://doi.org/10.1109/tro.2014.2378411) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Hollinger2015Fusion.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-019 / P2 | 2015 · [Shared Autonomy via Hindsight Optimization](https://doi.org/10.15607/rss.2015.xi.032) | 无仓库PDF；[已有外部入口](https://roboticsproceedings.org/rss11/p32.html) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-020 / P2 | 2018 · [Risk-Based Human-Aware Multi-Robot Coordination in Dynamic Environments Shared with Humans](https://doi.org/10.1109/iros.2018.8593586) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/TalebpourMartinoli2018IROS.pdf) | RW-17 PASSAGE_CHECKED | 是 |
| EXP-021 / P2 | 2019 · [Adaptive Risk-Based Replanning for Human-Aware Multi-Robot Task Allocation With Local Perception](https://doi.org/10.1109/lra.2019.2926966) | 无仓库PDF | 历史来源记录；新主张需原文定位 | 否 |
| EXP-022 / P2 | 2020 · [Anticipatory Human-Robot Path Planning for Search and Rescue](https://arxiv.org/abs/2009.03976) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2009.03976) | RW-10 ABSTRACT_CHECKED | 是 |
| EXP-023 / P2 | 2020 · [Distributed multi-target search and tracking using the PHD filter](https://doi.org/10.1007/s10514-019-09840-9) | 无仓库PDF | RW-02 PASSAGE_CHECKED | 是 |
| EXP-024 / P2 | 2020 · [Scaled Autonomy: Enabling Human Operators to Control Robot Fleets](https://doi.org/10.1109/icra40945.2020.9196792) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Swamy2020Scaled.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-025 / P2 | 2021 · [Human-robot collaborative multi-agent path planning using Monte Carlo tree search and Social Reward Sources](https://doi.org/10.1109/icra48506.2021.9560995) | 无仓库PDF；[已有外部入口](https://www.iri.upc.edu/publications/show/2475) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-026 / P2 | 2022 · [Risk-aware Decision-making in Human-multi-robot Collaborative Search: A Regret Theory Approach](https://doi.org/10.1007/s10846-022-01642-z) | 无仓库PDF | 历史来源记录；新主张需原文定位 | 否 |
| EXP-027 / P2 | 2023 · [A Task Allocation Framework for Human Multi-Robot Collaborative Settings](https://doi.org/10.1109/icra48891.2023.10161458) | 无仓库PDF | 历史来源记录；新主张需原文定位 | 否 |
| EXP-028 / P2 | 2023 · [Spatio-Temporal Avoidance of Predicted Occupancy in Human-Robot Collaboration](https://doi.org/10.1109/ro-man57019.2023.10309469) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2307.03909) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-029 / P2 | 2024 · [Inferring Human Intent and Predicting Human Action in Human--Robot Collaboration](https://doi.org/10.1146/annurev-control-071223-105834) | 无仓库PDF | RW-18 ABSTRACT_CHECKED | 是 |
| EXP-030 / P2 | 2024 · [Multi-Robot Allocation of Assistance from a Shared Uncertain Operator](https://doi.org/10.5555/3635637.3662889) | 无仓库PDF；[已有外部入口](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p400.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-031 / P2 | 2025 · [Adaptive Task Allocation in Multi-Human Multi-Robot Teams Under Team Heterogeneity and Dynamic Information Uncertainty](https://doi.org/10.1109/icra55743.2025.11127646) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2409.13824) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-032 / P2 | 2025 · [Coordinated Informative Path Planning for Multi-Robot Search in Open Fields](https://doi.org/10.1007/s10846-025-02270-z) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/KimKim2025OpenFields.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-033 / P2 | 2025 · [Efficient Human-Aware Task Allocation for Multi-Robot Systems in Shared Environments](https://doi.org/10.1109/iros60139.2025.11246701) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2508.19731) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-034 / P2 | 2025 · [HMPCC: Human-Aware Model Predictive Coverage Control](https://arxiv.org/abs/2512.12717) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/CatellaniGabbiSabattini2025HMPCC.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-035 / P2 | 2025 · [Integrating Field of View in Human-Aware Collaborative Planning](https://doi.org/10.1109/icra55743.2025.11127371) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2505.14805) | RW-20 ABSTRACT_CHECKED; 历史阅读卡005 | 否 |
| EXP-036 / P2 | 2025 · [MAC-Planner: A Novel Task Allocation and Path Planning Framework for Multi-Robot Online Coverage Processes](https://doi.org/10.1109/lra.2025.3551078) | 无仓库PDF | 历史来源记录；新主张需原文定位 | 否 |
| EXP-037 / P2 | 2026 · [Uncertainty-Aware Multi-Robot Task Allocation With Strongly Coupled Inter-Robot Rewards](https://arxiv.org/abs/2509.22469) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2509.22469) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-038 / P3 | 2007 · [Bidding Protocols for Deploying Mobile Sensors](https://doi.org/10.1109/tmc.2007.1022) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Wang2007Bidding.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-039 / P3 | 2013 · [Distributed Coverage Optimization in a Network of Static and Mobile Sensors](https://doi.org/10.1109/acc.2013.6580919) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Mahboubi2013StaticMobile.pdf) | RW-06 PASSAGE_CHECKED | 是 |
| EXP-040 / P3 | 2018 · [Multi-Robot Coordination in Dynamic Environments Shared with Humans](https://doi.org/10.1109/icra.2018.8460978) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/TalebpourMartinoli2018ICRA.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-041 / P3 | 2021 · [Collaborative human-autonomy semantic sensing through structured POMDP planning](https://doi.org/10.1016/j.robot.2021.103753) | 无仓库PDF；[已有外部入口](https://par.nsf.gov/servlets/purl/10222332) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-042 / P3 | 2021 · [Spatial Intention Maps for Multi-Agent Mobile Manipulation](https://doi.org/10.1109/icra48506.2021.9561359) | [仓库PDF](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/literature/pdfs/Wu2021Spatial.pdf) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-043 / P3 | 2023 · [Efficiently exploring for human robot interaction: partially observable Poisson processes](https://doi.org/10.1007/s10514-022-10070-9) | 无仓库PDF | RW-19 ABSTRACT/PASSAGE_CHECKED；correction UNRESOLVED | 否 |
| EXP-044 / P3 | 2024 · [InteRACT: Transformer Models for Human Intent Prediction Conditioned on Robot Actions](https://doi.org/10.1109/icra57147.2024.10610681) | 无仓库PDF；[已有外部入口](https://portal-cornell.github.io/interact/) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-045 / P3 | 2026 · [Knowing When to Ask: Resolving Uncertainty in Human-Robot Joint Planning via Explicit Dialogue and Implicit Intent Cues](https://arxiv.org/abs/2603.07822) | 无仓库PDF；[已有外部入口](https://arxiv.org/abs/2603.07822) | 历史来源记录；新主张需原文定位 | 否 |
| EXP-046 / P3 | 2026 · [Proactive collaboration via autonomous interaction](https://doi.org/10.1038/s41467-026-72797-8) | 无仓库PDF；[已有外部入口](https://www.nature.com/articles/s41467-026-72797-8) | 历史来源记录；新主张需原文定位 | 否 |

## 历史材料与当前来源导航

| 来源 | 内容与使用限制 |
|---|---|
| [旧26条catalog](catalog.json)、[旧台账](LITERATURE_LEDGER.md)、[旧优先级](reading-priorities.md) | 文件与历史阅读证据入口；旧优先级/排除性新颖性文字不是本轮新结论 |
| [旧新颖性候选](novelty_boundary.md) | 保留研究谱系；真实感知标定第二贡献、强制inhibition、更多机制实验等不属于当前已冻结主线 |
| [Zotero RIS](metadata/USV_HRI_core_literature.ris) | 原26条导入资产，不等于新46条全部已导入 |
| [canonical bib](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/paper/manuscript/references.bib)、[当前原文审计](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/paper/manuscript/RELATED_WORK_AUDIT_20261020.md)、[main评审](https://github.com/pharmacy28/USV_HRI_PATROL/blob/f8de4da17dbc3cc70eeedca409376c530cf9547b/paper/manuscript/tasks/PAPER-20261020-001.review.md) | 论文分支准确版本；通信分支旧paper目录不是当前母稿 |
| Library /月报/00_累计论文阅读索引.md及001—006六张阅读卡 | 本轮读过现有原件；涉及图像、补充材料、代码的OPEN独立保留；个人答题记录不搬入公开仓库 |
| Library /月报/01_三篇原文核验_文献谱系与重叠矩阵.md | 后于007初始建议：Costen正式全文F、Yuan预印本P、MAC摘要A是历史记录；本轮仅读取记录本身 |
| Library /月报/04_related_works_文献台账.csv、verified_refs.bib、007_创新边界与复现基线综合审查_启动包.md | 补入遗漏作品/别名与开放入口；“verified”文件名不是全量可靠性证明，旧T_confirm/候选扩展不覆写RC-v1.1 |

## 当前缺口与停止条件

先按inspiration的具体论证问题，补原文身份/版本或关键段落；不以无限扩表为目标。优先缺口：Bourgault2004具体方法全文；MAC-Planner全文；Talebpour2019重规划细节；Krzysiak2025/Bhattacharya2025补充与代码入口；Jovan勘误仅在拟恢复引用时处理。其余未存仓库全文逐条按需要获取合法开放版本，访问受限就保留缺口。

本轮未宣称46篇全文已下载、读完或复现，未新增正文引文/工程实验。以后新增条目保留稳定ID、来源和获取日期，不按排序重新编号；论文审计/实际文件改变后由exploration增量更新。
