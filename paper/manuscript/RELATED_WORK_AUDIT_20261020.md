# Related Work 与研究边界审计 — PAPER-20261020-001

- role=overleaf；2026-10-20，Asia/Shanghai；RC-20261020-v1。
- 论文读取基线：paper/overleaf-20261020@f38944669dce2cd45e124af5edc5f48a24608a00。
- 通信初读：27c5303cd1bab4097b83582e13a96c88ce4f659c；后读003R review所在HEAD：ea4e9bf8e946de6c653627b1d7b297e6318023fd。
- 本轮不是对26篇旧台账的全量精读。历史 FULLY_READ 标签保留为历史；本轮使用下列实际定位原文的段落，不从摘要推出排除性结论。
- 本轮将17条实际正文引文与 references.bib 对齐。编译仍采用main.tex内嵌bibliography，以免依赖额外BibTeX步骤。原bib中的其他历史候选保留，不代表本轮已核验或已被正文引用。

## 1. 来源与方法

优先读取本机既有论文PDF，实际入口为 /tmp/usv003coord.Wqcpj0/repo/literature/pdfs/（其他agent已有的仓库副本，未修改）；PDF对应仓库 literature/pdfs/ 同名文件。用 pdftotext -layout 提取，并以分页符确定PDF页序；页序从1开始，和印刷页分别标注。Xie PDF第3页另渲染并目视核对双栏，确认预测/抑制段落并未因文本提取顺序混乱而错读。每个所用PDF的SHA256列在本文件末尾。

出版社/作者HTML用于补充缺失PDF及核对版本；网页以实际章节标题定位，未取得印刷页时不编造页码。状态含 METADATA_ONLY、ABSTRACT_CHECKED、PASSAGE_CHECKED、FULL_TEXT_REVIEWED、UNRESOLVED。本轮主要为PASSAGE_CHECKED，不把读取全文的可访问性当逐字通读证明。

## 2. 逐主张证据表

| ID / 正文位置 | 原文身份与定位 | 实际支持 | 限制与修订决定 | 本轮状态 |
|---|---|---|---|---|
| RW-01 / II-A Bayesian search | Bourgault et al., Advanced Robotics 18(10):979–1000, 2004; DOI 10.1163/1568553042674707；出版社元数据/题名，全文入口本轮403 | 只保留协调Bayesian搜索这一宽背景 | 不以2003会议文替代2004版本；不引其具体滤波公式、性能或不存在性结论；全文仍需补查 | METADATA_ONLY |
| RW-02 / II-A PHD | Dames, Autonomous Robots 44:673–689, 2020; DOI 10.1007/s10514-019-09840-9；出版社全文“Sensor model”段、Introduction | FoV、false negatives、measurement/clutter及未知目标数的PHD搜索跟踪 | 明示与本稿单静止目标categorical belief不同；不称同一滤波器 | PASSAGE_CHECKED |
| RW-03 / II-A probabilistic planning | Hollinger et al., IJRR 28(2):201–219, 2009; DOI 10.1177/0278364908099853；PDF第1页摘要和Introduction | 移动目标的多机器人概率搜索 | 不借移动目标模型证明本稿静态模型或责任新颖性 | PASSAGE_CHECKED |
| RW-04 / II-A partition foundations | Cortés et al., IEEE TRA 20(2):243–255, 2004; DOI 10.1109/TRA.2004.824698；PDF第3–4页§II、§II-C；第4页§III开头 | locational coverage目标、CVT与Lloyd控制 | 固定中心/动态分区不能单列为新颖性；不把其收敛结论移植到本稿障碍投影算法 | PASSAGE_CHECKED |
| RW-05 / II-A local task regions | Fu et al., ICRA 2009:1935–1940; DOI 10.1109/ROBOT.2009.5152829；PDF第1页摘要/Introduction | local Voronoi任务分解与探索中的重叠避免 | 不从该段声称全文没有人工预测或任何特定撤销机制 | PASSAGE_CHECKED |
| RW-06 / II-A fixed resources | Mahboubi et al., ACC 2013; DOI 10.1109/ACC.2013.6580919；PDF第2页§III与后续FWV策略，第3页图1 | 静态传感器与移动传感器覆盖优化、移动资源再分布 | 已实现静态感知资源不同于不确定未来人工责任；不把“固定资源影响可动资源”当本稿首次 | PASSAGE_CHECKED |
| RW-07 / II-B next-place prediction | Xie et al., IROS 2011:3349–3354; DOI 10.1109/IROS.2011.6094688；PDF第3页=印刷3351，HMM段、步骤(1)–(4)、式(3)–(6) | HMM估计人工搜索状态/下一位置；inhibition message更新临时PDF并影响动作选择 | 明确承认预测位置与抑制互补搜索已有先例；不能泛称“首次预测人工搜索” | PASSAGE_CHECKED；第3页视觉核对 |
| RW-08 / II-B evidence boundary | 同Xie第3页右栏Learning from Demonstration，式(7)周围及左栏临时PDF描述 | 人工搜索活动密度用于对象先验，人工位置推断影响临时规划PDF | 本稿“人工输入不直接改posterior”是我们选择的模型边界，不是对原方法正确性的否定；不把P'_t和原始P_t混称 | PASSAGE_CHECKED |
| RW-09 / II-B anticipatory paths | Heintzman et al., ICRA 2021:8252–8258; DOI 10.1109/ICRA48506.2021.9562070；PDF第2页§II-A/B、第3页§II-C/III、风险目标式(6) | 预期地面搜索者路径、动态失踪者模型、GP后验风险及UAV路径优化 | 本稿操控同队艇和责任中心是比较轴，不能单以USV应用宣称创新；不声称它没有所有fallback机制 | PASSAGE_CHECKED |
| RW-10 / II-B preceding version | Cangan et al., arXiv:2009.03976 (2020)；作者arXiv题名、作者、摘要 | SAR anticipatory路径规划的前序工作 | 与2021五/四作者版本不混写作者、题名或页码；本轮未全文复核前序公式，不用其作细节差异证据 | ABSTRACT_CHECKED |
| RW-11 / II-B regions + dialog | Ishii et al., ICCVW 2023:1841–1848; DOI 10.1109/ICCVW60793.2023.00199；PDF第3页§3/4.1、第4页§4.2、后续dialog描述 | 过去已搜区域估计、未来区域预测，候选歧义时询问，互补搜索 | “预测未来搜索区域/避免重复”不是本稿独创；不从一个示例概括所有方法为硬删除 | PASSAGE_CHECKED |
| RW-12 / II-B bidirectional sharing | Nicholas Lim Hong Da, Miura, Hayashi, ECCV 2024 Workshops, LNCS 15634:20–35, published2025; DOI 10.1007/978-3-031-92591-7_2；PDF第6–8页=印刷25–27，§3.2、§4.1/4.2 | 继承人的路径估计/预测，按歧义与人发起询问双向沟通，更新区域图和计划；§5为虚拟环境实验 | 2024是workshop名，2025是出版年；主动双向询问属已有工作及本稿future scope，不声称提出首个空间共享系统 | PASSAGE_CHECKED |
| RW-13 / II-C same-team teleoperation | Krzysiak & Butail, IEEE THMS 52(1):52–63, 2022; DOI 10.1109/THMS.2021.3113642；PDF第4–5页§IV，算法与目标式(10) | 目标/遥控参考机器人信息的加权控制；独立搜索与协助接近混合 | 2021 DOI/在线登记不应代替2022卷期；本稿不能以“同队遥控成员”单独主张首次 | PASSAGE_CHECKED |
| RW-14 / II-C movement and replay | Krzysiak & Butail, ACM THRI14(2), Article27, 2025,29页; DOI10.1145/3706065；PDF第17–19页§5.1–5.3，式(6)、5.3 simulation setup；第1页摘要 | 运动线索到知识推断、自适应MI blending；真实实验的预录遥控轨迹用于模拟自主适配 | 回放不是我们的创新；无依据不概括各策略“平均时间都更优”；本稿不复用其视觉/识别终点 | PASSAGE_CHECKED |
| RW-15 / II-C UAV state adaptation | Bhattacharya & Butail, Complex & Intelligent Systems11:443,2025; DOI10.1007/s40747-025-02055-9；出版社全文“Estimating human prior knowledge and state based on movement cues”“Adaptive search based on prior knowledge and SA”，式(6)–(10)、“Simulation setup” | 遥控UAV运动到知识/SA估计，调节swarm吸引与分离；实验轨迹回放 | 不将其说成单纯界面研究；不据此推断没有某种责任/撤销功能；本文无其人因改善结论 | PASSAGE_CHECKED |
| RW-16 / II-C shared representation | Dalmasso et al., IJSR16:145–171,2024; DOI10.1007/s12369-023-01067-0；出版社§3.1、§3.3/3.4、§4 Multi-agent MCTS、摘要 | SRS共享表征、异质团队规划、多agent MCTS及collaborative search | 本文authority/commitment/responsibility是我们的分析分类，不能冒称原文三权限框架 | PASSAGE_CHECKED |
| RW-17 / II-C prediction in costs | Talebpour & Martinoli, IROS2018:3365–3372; DOI10.1109/IROS.2018.8593586；PDF第2页引言后半、第3页§III-C/D与式(3) | 人轨迹预测/误差进入social/risk bids，支持代价层预测比较 | “预测作用于bid”和本文“预测作为generator”是被审查机制的区别，不从全文缺词断言没有等价行为 | PASSAGE_CHECKED |
| RW-18 / I,II-C prediction background | Hoffman et al., Annual Review of Control, Robotics, and Autonomous Systems7:73–95,2024; DOI10.1146/annurev-control-071223-105834；出版社摘要/元数据 | 意图推断、动作预测是成熟HRI问题 | 综述只支撑背景，不代替最相近原始方法核查；无数字结论 | ABSTRACT_CHECKED |
| RW-19 / 删除旧b8 | Jovan et al., Autonomous Robots47:121–138,2023; DOI10.1007/s10514-022-10070-9；出版社摘要、§1，及Correction入口10.1007/s10514-023-10152-2 | 人活动计数、相关/不可靠传感器下POPP与长期探索 | 原稿泛用来支撑目标搜索，关联过宽；正文删除，不否定文献。勘误具体修改本轮未解析，保留UNRESOLVED，不写其公式 | ABSTRACT/PASSAGE_CHECKED；correction UNRESOLVED |
| RW-20 / 不引入成功FOV门槛 | Hsu et al., arXiv:2505.14805, Integrating Field of View in Human-Aware Collaborative Planning；作者摘要 | FoV对人的子任务理解/协作规划的背景候选 | 不改变本稿近距encounter终点；本轮不新增正文引文或扩展主贡献 | ABSTRACT_CHECKED |

## 3. 对本稿主张的压力检验

- 保留的研究问题：显式SEARCH有效时，未来位置信息作为全域信念加权责任分配的固定generator，相比当前位置的信息价值。它是待检验的组合机制，不是已被证明独有的范式。
- 删除/降调：首次预测人工搜索、首次减少未来重叠、首次把遥控成员纳入团队、首次用回放、首次固定资源影响重分配等表述均不成立或无充分依据。
- B2/B3只比较同一分配器的不同人工信息，不能证明该分配器优于所有预测避让/抑制方法。
- 建议main考虑“同预测器的直接抑制规划”作为机制对照。优点：回应Xie最直接压力；成本：须冻结被抑制的规划量、支持域和强度，且不能改posterior。未擅自列为正式必做实验。
- 不写“先前工作均无撤销/回退/显式承诺”。已读方法段落足以承认其具体机制，不足以证明排除性普遍命题。
- 不以别人应用不是USV作为唯一新颖性理由；本稿应用环境与控制切换只界定评价场景。
- Cortés、Fu、Mahboubi支持“标准空间方法与固定资源先例”；未替本稿的障碍投影或退化簇处理证明收敛。

## 4. 尚未完成的文献工作

- Bourgault2004全文未获得；目前只保留题名级宽背景。若投稿需要引用其具体公式/性能，必须取回该版本。
- Talebpour2019自适应重规划、其他fixed/mobile资源、Costen/Yuan/Wang等候选本轮未全量复查，未增加对它们的排除性比较。历史台账可继续用作检索线索。
- 本轮检查关键段落并非所有论文FULL_TEXT_REVIEWED；Lim实验细节、人的知识推断验证分组等如用于数值比较，仍须逐表逐协议复核。
- Jovan勘误具体内容未确认；由于正文不再依赖，不阻止此次修订。
- 当前文献未建立“我们的组合唯一”的证明，投稿新颖性须以最终机制对照和实验增益支撑，不能靠新增标签。

## 5. 公开原文入口

- Xie: https://doi.org/10.1109/IROS.2011.6094688
- Heintzman: https://doi.org/10.1109/ICRA48506.2021.9562070 （另有NSF作者稿10302700）
- Krzysiak2022: https://doi.org/10.1109/THMS.2021.3113642
- Krzysiak2025: https://doi.org/10.1145/3706065
- Ishii: https://doi.org/10.1109/ICCVW60793.2023.00199
- Lim: https://doi.org/10.1007/978-3-031-92591-7_2
- Bhattacharya: https://link.springer.com/article/10.1007/s40747-025-02055-9
- Dalmasso: https://link.springer.com/article/10.1007/s12369-023-01067-0
- Dames: https://link.springer.com/article/10.1007/s10514-019-09840-9
- Cortés: https://doi.org/10.1109/TRA.2004.824698
- Fu: https://doi.org/10.1109/ROBOT.2009.5152829
- Mahboubi: https://doi.org/10.1109/ACC.2013.6580919
- Talebpour: https://doi.org/10.1109/IROS.2018.8593586
- Hollinger: https://doi.org/10.1177/0278364908099853
- Hoffman: https://doi.org/10.1146/annurev-control-071223-105834

## 6. PDF身份（SHA256）
- Xie2011Intention.pdf: `a96e68582d1925304c6f93ca039aebb5542510a5a91f1d13681e450ca501a8f3`
- Heintzman2021Anticipatory.pdf: `c8b453bce9f084a40abf0de6655333173f52332cea0a7aba5885334f47071779`
- KrzysiakButail2022Information.pdf: `a150d1eabd94566d7b9a3ed31d1175ecb585cdf1913905458ac6142dde92bf7b`
- KrzysiakButail2025Movement.pdf: `77b94a6fb064e8c03cdc4b413b66dd6a8bd1452c655b0cd4410af7e8ef246a16`
- Ishii2023Enhancing.pdf: `c86fc333d347d6ae9eddc21f236cc4f188ce039621cdb0622a657e79b398a359`
- LimMiuraHayashi2025SpaceSharing.pdf: `84055dd2a052dfecf5aaac44e787261cd168c31606f999007b13596e49f7fd58`
- TalebpourMartinoli2018IROS.pdf: `29ac2f17c565e11b0f695e46610f4ab5c581d68136ebafc4ebc6c80253eeda5f`
- Cortes2004Coverage.pdf: `06af662e4bfa3d1447724a0093f9bb82fbef66be81b575652a8b50ab0889344c`
- Fu2009LocalVoronoi.pdf: `54dd0ba251a6ef158469fe6b3b230ec6401e02d0ad28aa3cd4ef25fa47c9bdc2`
- Mahboubi2013StaticMobile.pdf: `19286d2b8be96f90caad2b3811e3074dad32ce1d74229f9640d4f9492ae80d57`
- Hollinger2009Efficient.pdf: `ee5670e523170804d4fc4ddc4b5ef8152c96d303db20651431149328575ae5cd`

## 7. RF合同/第一周计划/Xie增量接收（2026-10-20）

来源快照：coordination/work-20261020@87364b3ba616ab4925634a2d45d9fec4a3a0ae4f。已验收母稿baseline paper/overleaf-20261020@f8de4da17dbc3cc70eeedca409376c530cf9547b；本轮只增量维护，不重开PAPER-001已ACCEPTED的R1–R4。

- exploration交付literature/related_work_notes/EXPLORATION-20261020-Xie2011.md，blob aa3565d398c4f322cd65b7cd36f5c0df630679c7，EX-XIE-01—05。已读证据包；其FULL_TEXT_REVIEWED状态归exploration本人，未冒称本轮overleaf重新通读6页。本轮另从已有同hash PDF提取文本核对第5页漏检/抑制段；第3页P/P′与HMM依据沿用上轮直接阅读和新证据。
- RW-07/08细化：明确临时规划PDF P′、观测更新的P与SAD prior是不同路径；不概括成预测直接永久清belief。增加录制轨迹仿真与组合time-to-detect对照这一评价边界，不搬运其数值为本项目收益。
- 新RW-21（II-B、VI）：Xie PDF第5页/印刷3353 §IV-B图6说明（EX-XIE-05）明确报告人漏检后抑制机器人到访、合作有时更差。正文只归因于作者讨论的组合估计/抑制，不声称隔离了预测误差因果效应。本文保留belief/full-domain并不因此保证及时回访；generator优于inhibition仍未被证明。
- EX-XIE-03的40s约75%活动分类结果未加入正文，不当下一位置精度或H依据；EX-XIE-04的人数/训练评价数量及时间均值未转为本文参数；ref[14]抑制核/幅度/恢复机制未获得可复现细节，不据此新增baseline或“前作无撤销”论断。
- RF-DATA-CONTRACT-v1（blob95ff2a93fdfd5387ccac2d969deafc4103b54113）是本项目方法/数据语义裁决，不是文献结果或实测模型。相关增量为计划协议，无新外部引文。
- WEEK1_PLATFORM_PREP_20261020（blob4f2af5b739b07db3bf25813afc8240fe3a937c69）是UI/设备/源身份/导出准备计划，不证明已完成、已采志愿者或已训练RF。论文不写工作日历或工程任务清单；只补必要的数据准备/验证边界。
- 沿用17条实际引文与首次引用顺序，无新文献身份或bib字段变化。新增机制表述的证据范围限上述段落，不扩大新颖性或成果主张。
