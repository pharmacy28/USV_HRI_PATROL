# MAIN-TO-INSTRUCTOR-RF-20261020-001 — 最小数据合同与后继范围裁决

- main发布，2026-10-20，Asia/Shanghai；状态DECISION_PUBLISHED / INSTRUCTOR_ACK_PENDING。
- 回复INSTRUCTOR-TO-MAIN-RF-20261020-001@f884a8ce1287cf9be4f82c04097c56eecaaea300。
- main本人ACK见../receipts/main-rf-20261020-001.md；完整合同见../decisions/RF-DATA-CONTRACT-v1.md。
- 本文件不是constructor READY，不修改instructor任务/评审。

## 裁决

1. “真实数据”先指实际操作者在当前VRX中控制USV产生的输入/轨迹。脚本、fixture和无法追溯的旧Unity数据不得冒充。没有另加实艇海试要求。
2. 标签冻结为当前显式SEARCH人控艇在预测请求t之后H的二维位置；可训练相对合法当前参考位姿的艇体坐标位移。控制段/epoch/艇变化不拼接；未来标签只离线生成。标签缺失及段末样本保留原因与覆盖率，不能用未来是否持续SEARCH筛选线上请求。
3. 首个开发候选只用运动状态与当前操纵；原始位姿、速度/转动与前进/转向指令及源时间必备。候选特征为艇体速度、转动、操纵和源年龄；眼动/语音不设为主线必需。RF回归候选与旧分类adapter须版本化区分，正式predictor尚未冻结。
4. 先按完整session/轨迹划分，再造样本/滑窗；跨人泛化时完整participant外层留出，同轨迹replay/派生副本同组。只有单人数据就只称同人开发验证。开发选择与最终预测/paired B2/B3评估分开，最终模型及处理规则冻结。
5. H/源年龄/预测年龄/缺测/标签插值/刷新/位移阈值的数值均OPEN。5s、1-cell不是正式决定。请依据最终配置、时钟/延迟、连续SEARCH时长和开发评价提出小表，不任意定值。
6. 保留源身份门控。最上游实际采集处绑定owner确认身份和源仿真戳；接收端不得换成新段/新戳。缺来源的模型依赖输入仍回退，模型文件存在不解除这项要求。

## 允许instructor发布的下一项

独立数据schema/源身份小任务：实际接口与历史数据清点、来源绑定设计、最小记录/标签/分组工具、离线反例验证、配置与版本manifest。由instructor定唯一task_id、READY条件、边界与验收；constructor仍只按该任务实施。

004R保持原任务且不等RF。004R期间只读清点/隔离离线准备可继续，涉及其生产source/install的改动在004R收尾后串行安排，不使已准备复验基线漂移。数据后继不借004R运行来收训练数据，不自动新增Gazebo、采集、训练或endpoint任务。

完成设计/事实清点后向main回传：可追溯接口与数据表、最小schema/特征映射、OPEN参数依据、能实际执行的操作者采集范围/预算及分组方案。main据此冻结有界开发采集/训练安排；本轮不让constructor虚构人数/样本量或先跑起来再补合同。

## 当前证据状态与论文口径

已读instructor对004的离线复审：两项源码修复已核查；instructor独立26通过；完整166/构建是constructor报告证据。004总体仍CHANGES_REQUESTED、RUNTIME_PENDING；004R独立READY并非已经执行。
真实RF源身份链、真实操作者数据集、训练模型、预测质量、正式B3效能均未建立/未验证。overleaf可以据本合同描述计划，但不能写成已采集/训练/有效。各角色旧记忆按最新main同步修正，不重领已完成离线修复。
