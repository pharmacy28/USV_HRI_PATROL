# main 定时统筹状态与人工核查回执

- role: main
- automation_id: 6ad720ead3cc8191abc79a66100726cc
- checked_date: 2026-10-20，Asia/Shanghai
- enabled: true（本轮peek真实返回）
- timezone: Asia/Shanghai
- cadence: 每小时；有实质变化才汇报
- timing_mode: condition_watch
- schedule: DTSTART=20261020T080702Z；RRULE:FREQ=HOURLY
- automation_updated_at: 2026-10-20T08:24:21.079645+00:00（接口字段）
- last_run_time: 2026-10-20T08:17:24.761501+00:00（北京时间16:17:24.761501）
- next_run_time: null（接口未给明确值）
- last_successful_scheduled_run: NOT_VERIFIED；last_run_time不等于成功/交付证据
- read_commit: f97997b3c55c49feb9cd69dd5cfd3091d0124711
- paper_read_commit: f8de4da17dbc3cc70eeedca409376c530cf9547b
- last_successful_manual_check: 本轮已读取任务/review/回执/计划及论文最终review，完成全角色状态核对；见handoffs/MAIN-20261020-003.md。本记录不是后台运行验收。
- active_task: main仓库增量统筹/回执评审/按所有权派发
- limitation: 其他四Work无本人接收器登记；constructor本地runner未验证；完整自动闭环未通过
- mutation_this_round: NONE；原任务当前已启用，无需重复创建或再次启用

## 历史创建与状态说明

首次创建登记时间为2026-10-20T16:06:03+08:00，创建返回success/is_enabled=true；setup_document_commit=e5baa950304c0e13c945741057e75145695bbca1。此前会话曾查到停用，当前接口显示enabled=true；本轮不推断停用原因或将状态恢复归因于本轮操作。

工具返回的conversation_id是当前运行上下文元数据，本回执不以该字段替代后台执行/交付证据。实际成功运行后再记录对应产物、提交和审查结果。
