# Related Work 审计起点 — 2026-10-20

维护：overleaf；本轮初始筛查：main。用途：给实际修稿提供可追溯原文入口；**不是已经完成的全部文献复核**。

当前正文七条 inline bibliography 是从原稿继承，之前的 TeX 收紧并未独立核查。已检索到的 verified_refs.bib 是候选清单；其文件名不代表以下比较论断已获得原文支持。

## 1. 三层证据应分开

| 层 | 当前材料 | 如何使用 |
|---|---|---|
| 历史阅读 | literature/LITERATURE_LEDGER.md 的 26 条与 FULLY_READ 等标签；novelty_boundary.md | 保留历史，不冒称本轮重读；找回原文和原章节再支持新增比较 |
| 本轮初筛 | 下列出版社/作者/机构入口和已查看摘要/部分段落 | 按实际范围标状态；不从 metadata 或摘要推出排除性“没有做 X” |
| 待完成审计 | PAPER-20261020-001 要求的逐 claim 原文表 | 由 overleaf 更新，支持最终 Related Work 与贡献措辞 |

旧 novelty_boundary.md 的“真实方向检测器标定—时间相关性—任务漏检校准”第二贡献不再是当前精简稿的承诺。其最相近研究列表仍有价值；旧 T_FD/confirmation 端点不可直接套到当前 encounter。

## 2. 当前七条引用初筛

| 正文键 | 身份/入口 | 本轮核查范围 | 修稿注意 |
|---|---|---|---|
| b1 Bourgault et al. 2004 | [出版社 DOI](https://doi.org/10.1163/1568553042674707) | 搜索返回的出版社条目题名/作者；METADATA_ONLY，未重读全文 | 与历史 Bourgault 2003 条目不是同一发表版本；不能互换页码/论断 |
| b2 Xie et al. 2011 | 旧仓库 PDF/台账；完整 DOI/正式页码待从原文确认 | 本轮尚未完成一级原文复核；旧台账称 FULLY_READ | 高优先级，核对 HMM/下一搜索位置/抑制机制，不只引题名 |
| b3 Heintzman et al. 2021 | [IEEE](https://ieeexplore.ieee.org/document/9562070/)，[NSF 作者稿入口](https://par.nsf.gov/servlets/purl/10302700) | 元数据可查；本轮 IEEE 打开受限、NSF 打开 502；FULL_TEXT_REVIEW_PENDING | 旧台账称地面人类搜索者/UAV 互补；须定位原文，区分预测搜索者与动态失踪者模型 |
| b4 Hoffman et al. 2024 | [Annual Reviews](https://www.annualreviews.org/content/journals/10.1146/annurev-control-071223-105834) | 题名、作者、7:73–95、摘要；ABSTRACT_CHECKED | 综述可支撑研究背景，不能替代具体竞争方法的原始证据 |
| b5 Dalmasso et al. 2024 | [Springer 全文](https://link.springer.com/article/10.1007/s12369-023-01067-0) | 摘要与 §1–§3 开头；PASSAGE_CHECKED，未通读 | 已见 SRS、多人/机器人 MCTS、协作搜索和手机界面；不能只写成泛泛“共享任务”或归入我们的术语 |
| b7 Dames 2020 | 原稿条目；正式 DOI 与内容待核 | 本轮未完成，UNRESOLVED | PHD 多目标搜索与本研究单目标归一化 belief 区别需明示，不能借引用推出同一建模 |
| b8 Jovan et al. 2023 | [Springer](https://link.springer.com/article/10.1007/s10514-022-10070-9)，[勘误](https://link.springer.com/article/10.1007/s10514-023-10152-2) | 出版社摘要/检索内容，ABSTRACT_CHECKED | 研究人类活动计数/探索，非直接的同队 USV 责任方法；核对勘误。其背景引用是否必要由正文论证决定 |

以上“可查/已查看”不代表所有字段、结果或缺失性主张已经确认。工具访问错误是本轮访问结果，不表示全文不存在；优先检查仓库已有 PDF。

## 3. 最重要的补查与差异轴

### 直接压力集

| 工作 | 已有入口/来源 | 本轮证据范围 | 需要比较的问题 |
|---|---|---|---|
| Xie 2011 | 旧台账与 PDF | 历史 FULLY_READ，待本轮定位 | 预测下一搜索位置并抑制重复搜索，和未来责任中心是否有可实验区分的差别？ |
| Heintzman 2021 / Cangan 2020 前序 | 旧台账、IEEE/作者稿 | 历史已读；本轮全文待取 | 人/机器角色、预测对象、路径优化与本稿责任分区输入的异同 |
| Krzysiak & Butail 2022 | [DOI](https://doi.org/10.1109/THMS.2021.3113642) | 来自候选清单及历史台账，待原文复核 | 人遥控参考机器人，信息控制怎样适配人先验知识；不能声称同队遥操作首次 |
| Krzysiak & Butail 2025 | [ACM DOI](https://doi.org/10.1145/3706065) | 搜索可见条目；本轮 DOI 打开失败；旧台账 FULLY_READ | 运动线索、知识推断、搜索/辅助混合与未来空间责任的区别；核对用户验证/回放设计 |
| Ishii 2023 | 仓库 Ishii2023Enhancing 条目/PDF | 历史 FULLY_READ，待本轮定位 | 已搜索/未来搜索区域、对话和互补搜索，不能忽略其区域预测 |
| Lim / Miura / Hayashi 2025 | [Springer 章节](https://link.springer.com/chapter/10.1007/978-3-031-92591-7_2) | 出版社元数据；METADATA_ONLY | 空间共享与按需双向交互；ECCV 2024 Workshops 与 2025 出版日期分开；未读全文不写排除性结论 |
| Bhattacharya & Butail 2025 | [Springer 全文](https://link.springer.com/article/10.1007/s40747-025-02055-9) | 摘要、Introduction/Related Work 开头；PASSAGE_CHECKED | 已研究从遥控 UAV 运动估计操作者知识/状态并调整其他机器人的搜索，需与未来位责任机制直接比较 |
| Dalmasso 2024 | 上述全文 | 部分段落已查 | 共享表征/联合规划/协作角色/界面，与本稿承诺、控制权、责任定义逐项对应 |

Bhattacharya & Butail 的摘要和引言明确涉及人类实验，以及由运动估计先验知识/态势信息后调整自主机器人的分离/靠近策略。本轮仅据这些段落判定它是必须比较的近邻；尚不能据此断言其全文没有本研究的所有要素。不要把“缺少我们给出的名称”当“缺少相应机制”。

Dalmasso 的 SRS 与 multi-agent MCTS 是原文方法，不应为了凸显本研究而略去。当前“目标选择权/执行权/责任承诺”的分析可由我们定义，不能未经核实称为其原文三种权限。

### 支撑与候选集

- Cortés/Fu/固定与移动资源：空间责任、CVT/Lloyd、固定资源影响移动资源重分配都是已有基础，不作为独立新颖性。
- Talebpour/Martinoli：预测轨迹进入分配风险/重规划，必须分清“改变任务成本”与“生成搜索责任几何”的比较依据；是否缺失后者需要原文章节支持。
- Bourgault/Hollinger：概率搜索、负观测和漏检等经典基础；当前不承诺新滤波或真实相机标定贡献。
- Hsu et al. 2025 [作者预印本](https://arxiv.org/abs/2505.14805)：摘要已核，有限视野下的子任务意图与协作规划，实验涉及烹饪域/VR。可作为人的信息局限背景；不能拿来改本研究简单近距成功门槛。
- 其他候选清单包括 Costen et al. AAMAS 2024（10.5555/3635637.3662889）、Yuan et al. ICRA 2025（10.1109/ICRA55743.2025.11127646）、Wang et al. MAC-Planner（10.1109/LRA.2025.3551078）、Rossano et al. arXiv:2509.22469。**本轮未独立核验其全部身份/内容/接受状态**；按相关性核实后决定是否引入。旧清单的“accepted IROS 2026”不能直接复制。

## 4. overleaf 需要维护的逐主张表

| claim_id | 正文位置与待写主张 | 来源版本/DOI | 原文页/节/公式 | 原文支持内容 | 不支持/限制 | 核验状态 | 决定 |
|---|---|---|---|---|---|---|---|
| RW-001 | 预测人搜索行为已有先例 | Xie/Heintzman/Ishii | 待定位 | 历史台账已有线索 | 不能凭一个引文泛化全部方法 | UNRESOLVED | 核原文后改写 |
| RW-002 | 同队遥操作与自主搜索适配已有先例 | Krzysiak/Butail；Bhattacharya/Butail | 2025 Springer 摘要与 Introduction 已查看；其余待定位 | 后者明确研究运动线索到操作者状态，再到搜索策略适配 | 尚无完整机制差异审计 | PASSAGE_CHECKED / 部分待核 | 必须纳入近邻比较 |
| RW-003 | 责任中心机制相对当前位有额外决策价值 | 本研究 B2/B3 | 待正式实验 | 当前只能提出假设 | 不是文献推出的实证结论；也不证明优于所有预测抑制方法 | HYPOTHESIS | 用假设措辞 |
| RW-004 | 先前工作没有某种撤销/fallback/全域分区 | 对应被比较的每篇原文 | 待定位 | 需方法/协议证据 | 摘要与关键词未提及不足以证明不存在 | UNRESOLVED | 不支持则删除或收窄 |

论文修订应更新本表，完成度以证据记录为准，不以参考文献条数或语言润色量衡量。
