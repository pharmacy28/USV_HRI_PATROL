# 角色协作补充 v1.1

日期：2026-10-20。由 main 按用户本轮明确角色分工发布。补充 PROTOCOL.md v1；不改变其公开信息、源码隔离、非强制更新和用户启动规则。传输可用不等于各角色已经 ACK。2026-10-20追加用户指定的inspiration研究讨论入口，原四角色所有权保持。同日按用户追加exploration文献预处理入口，形成六角色协作。

## 1. 唯一负责人

| 产物 | 写入负责人 | 读取/评审 |
|---|---|---|
| docs/coordination/MAIN_MEMORY.md、科学决策和跨线 handoffs | main | 全角色 |
| docs/coordination/tasks/USV-*.md 与 *.review.md | instructor | constructor 执行；main/overleaf 读取结论 |
| docs/coordination/reports/USV-*.md、STATUS.md、LOCAL_RECEIPT.md | constructor | instructor 验收 |
| paper/manuscript/main.tex、references.bib、文献审计和修稿报告 | overleaf | main 审查科学边界；instructor 核对实现事实 |
| literature/EXPLORATION_INDEX.md、exploration_catalog.json、本角色related_work_notes与research/EXPLORATION_TO_INSPIRATION.md | exploration | inspiration使用研究证据；main/overleaf读取 |
| docs/coordination/research/INSPIRATION_NOTES.md（有实质讨论结果后创建） | inspiration | main接收；相关角色读取 |
| docs/coordination/receipts/<role>-<date>.md | 对应角色 | main 检查接收 |

main发布统筹交接和论文任务，不新增与instructor冲突的工程READY任务。工程沿当前唯一任务及原负责人处理；历史任务编号不是长期阻断。报告作者不能自签 ACCEPTED；main 也不把远程摘要冒充自己完成的本地运行验证。

## 2. 每次接续工作

1. 读取通信分支最新 HEAD、MAIN_MEMORY、当前任务/报告/review，再读取与本任务相关的实际本地源码或论文分支。仓库旧代码不是生产基线。
2. 在本轮首份报告或独立 receipt 写明 role、read_commit、contract_version、active_task、纠正的旧记忆、仍有的冲突。尚未回执标 PENDING，不伪造别人的 ACK。
3. 若只是 topic 名、文件拆分、接口实现等已授权范围内工程细节，由 instructor/constructor 决定并记录；不逐项返回 main 请示。
4. 若会改成功事件、科学参数、基线对比、目标证据或贡献边界，提交 main 决策项，带建议/依据/影响。可以继续不依赖该项的工作。

## 3. instructor ↔ constructor 闭环

- instructor 写唯一 READY 任务：目标、当前实际基线、允许改动、禁区、验收证据、运行预算、报告路径。
- constructor 在用户已启动的执行会话内领取任务，核对依赖和旧 report/review 后工作。旧任务文件仍写 READY，但已 DONE/BLOCKED/待复验时，不重复领取或重跑。
- constructor 报告必须区分科学设计、源码存在、离线测试、真实运行、正式比较实验；最终代码/参数改变之后，旧运行只能支持旧版本。
- instructor 逐项给 ACCEPTED / CHANGES_REQUESTED / BLOCKED；需要修复时发布最小返工或后继任务，不要求违反原任务运行限制。
- constructor 的 STOP、日志、时间、版本问题首先回 instructor；main 只接收科学口径冲突及完成摘要。
- 当前工程链按最新MAIN_MEMORY、STATUS及task/review确定。2026-10-20更新：003/003R已API级ACCEPTED；004（B3生产门控/fallback）已由constructor提交DONE报告，等待instructor正式review；尚未ACCEPTED。原“不能跳到B3”仅适用于此前003R尚未收口阶段，不能作为当前阻断；不得重领旧任务或由main另开竞争任务。

没有新增后台轮询、无限自主运行或跨对话自动唤醒。已授权且已启动的任务内可正常迭代；超出原运行预算由 instructor 写明新的有界任务后继续。用户触发规则仍按 v1，不将协议文件当脚本自动执行。

## 4. 平台与论文联动

每个工程 review 增补三项：可写入论文的实现事实、仍未验证内容、会影响指标/公式的变化。overleaf 按 commit 引用这些事实，方法设计与已实现/已验证状态分开。

每次论文报告增补三项：新增/收紧的科学主张、支持原文/实验的证据入口、向 main 提交的少量决策。文献若推翻现有新颖性叙述，先纠正叙述并报告 main，不为了保住贡献而弱化别人工作。

审计记录建议字段：claim_id、manuscript_location、claim、source_commit_or_DOI、source_location、evidence_level、limitation、owner、status。可用一张 Markdown 表，不引入新服务或数据库。

## 5. 写入和版本

写入前重新 fetch/读取 HEAD，审查同路径的新变更。不同负责人不覆盖对方任务、报告、状态；禁止 force push/reset。只上传精简研究/工程摘要，不上传凭据、参与者身份或原始语音/眼动/操纵数据。论文只渐进改论文路径，不整分支合并旧 platform/。

冲突裁决分开：研究定义按用户最新指令/已确认 RC/main 决策；工程完成度按匹配最终版本的证据和 review；论文引用按原文。任何一个维度的“更新”不能自动替代另一维度的证据。

## 6. inspiration 研究讨论入口（2026-10-20用户授权补充）

inspiration由用户从“分支 · 重审研究路线”创建Work分支，面向用户解释项目全貌、持续提问、检查假设和贡献边界，讨论反例与简单可检验设计。每轮优先一个有价值的问题，直接回答用户的追问；不机械重开已冻结事项，不让科研讨论变成审批或测试题。

接续读最新MAIN_MEMORY及相关RC/review；新角色本人ACK后才算已接收。首次交接见handoffs/INSPIRATION-20261020-001.md。实质结论可写research/INSPIRATION_NOTES.md：用户原意/决定、依据、OPEN/CANDIDATE/USER_DECIDED、影响。无需每轮产生报告。

用户在inspiration中的明确决定按最新用户授权处理，交main统一记录和同步，不要求用户在main重复批准。助手建议或未决讨论不能自升级为冻结合同；真实文献和工程证据不能被偏好替代。main将工程影响交instructor、论文影响交overleaf。inspiration不直接给constructor派发工程任务，不代写母稿或其他角色验收。

新入口发布不等于聊天已创建或被唤醒；沿用用户启动和真实ACK规则，不新增自动后台调度。仓库所有权与公开信息边界继续有效。

## 7. exploration → inspiration 文献证据交付（2026-10-20用户授权补充）

规范角色名exploration（用户亦曾写esploration）：收集/去重既有相关工作，核对原文身份与版本，对重要论断给页/节/公式和实验范围，维护证据缺口。入口handoffs/EXPLORATION-20261020-001.md；初始汇总literature/EXPLORATION_INDEX.md共46个作品记录、22份仓库PDF入口，非全量全文新审计。

exploration负责文献事实与证据载体；inspiration据证据与用户讨论问题、反例和研究候选；main统一用户决定与科学合同；overleaf负责母稿措辞和引用采用。exploration可直接通过research/EXPLORATION_TO_INSPIRATION.md交付，inspiration在实质记录中注明来源/claim_id与处理意见，无需每条资料经过main许可。改变研究合同的决定仍交main统一同步。事实性纠错可供overleaf修订后回报，不要求重复全量阅读。

母稿main.tex、canonical references.bib、正文RELATED_WORK_AUDIT仍由overleaf维护；exploration不直接覆盖这些文件，不向constructor下发工程任务。历史FULLY_READ、阅读卡结题、已存PDF与某条新主张的核验分别记录。文献结果不随本项目偏好改变；没有某个词不等于不存在等价机制。

新Work由用户创建/命名并启动；本人ACK前保持接收PENDING。已建立文件交付链不等于后台自动对话。旧主线/已在途004不因新增角色而重启或扩张。
