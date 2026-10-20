# 四角色协作补充 v1.1

日期：2026-10-20。由 main 按用户本轮明确角色分工发布。补充 PROTOCOL.md v1；不改变其公开信息、源码隔离、非强制更新和用户启动规则。传输可用不等于四角色已经 ACK。

## 1. 唯一负责人

| 产物 | 写入负责人 | 读取/评审 |
|---|---|---|
| docs/coordination/MAIN_MEMORY.md、科学决策和跨线 handoffs | main | 全角色 |
| docs/coordination/tasks/USV-*.md 与 *.review.md | instructor | constructor 执行；main/overleaf 读取结论 |
| docs/coordination/reports/USV-*.md、STATUS.md、LOCAL_RECEIPT.md | constructor | instructor 验收 |
| paper/manuscript/main.tex、references.bib、文献审计和修稿报告 | overleaf | main 审查科学边界；instructor 核对实现事实 |
| docs/coordination/receipts/<role>-<date>.md | 对应角色 | main 检查接收 |

main 本轮只发布统筹交接和论文任务，不新增与 instructor 冲突的工程 READY 任务。现有 003/003R 沿原负责人处理。报告作者不能自签 ACCEPTED；main 也不把远程摘要冒充自己完成的本地运行验证。

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
- 当前具体链：003.review → 003R READY（如已发布则直接复用）→ constructor 定向报告 → instructor 复验审查 → 003 最终裁决。不能跳到 B3，不能由 main 另开同名任务。

没有新增后台轮询、无限自主运行或跨对话自动唤醒。已授权且已启动的任务内可正常迭代；超出原运行预算由 instructor 写明新的有界任务后继续。用户触发规则仍按 v1，不将协议文件当脚本自动执行。

## 4. 平台与论文联动

每个工程 review 增补三项：可写入论文的实现事实、仍未验证内容、会影响指标/公式的变化。overleaf 按 commit 引用这些事实，方法设计与已实现/已验证状态分开。

每次论文报告增补三项：新增/收紧的科学主张、支持原文/实验的证据入口、向 main 提交的少量决策。文献若推翻现有新颖性叙述，先纠正叙述并报告 main，不为了保住贡献而弱化别人工作。

审计记录建议字段：claim_id、manuscript_location、claim、source_commit_or_DOI、source_location、evidence_level、limitation、owner、status。可用一张 Markdown 表，不引入新服务或数据库。

## 5. 写入和版本

写入前重新 fetch/读取 HEAD，审查同路径的新变更。不同负责人不覆盖对方任务、报告、状态；禁止 force push/reset。只上传精简研究/工程摘要，不上传凭据、参与者身份或原始语音/眼动/操纵数据。论文只渐进改论文路径，不整分支合并旧 platform/。

冲突裁决分开：研究定义按用户最新指令/已确认 RC/main 决策；工程完成度按匹配最终版本的证据和 review；论文引用按原文。任何一个维度的“更新”不能自动替代另一维度的证据。
