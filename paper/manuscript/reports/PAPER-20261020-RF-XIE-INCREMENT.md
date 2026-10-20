# RF合同、第一周计划与Xie证据的论文增量回报

- role=overleaf；2026-10-20，Asia/Shanghai；status=DONE / 待main增量审阅。
- 本轮由用户明确启动；原PAPER-20261020-001/R1保持ACCEPTED，不重领旧READY、不重开已完成小修。
- paper_read_commit=f8de4da17dbc3cc70eeedca409376c530cf9547b；communication_read_commit=87364b3ba616ab4925634a2d45d9fec4a3a0ae4f。
- 合同：RC-v1.1 + RF-DATA-CONTRACT-v1；接收MAIN-20261020-003及第一周准备计划。本人ACK提交c3c75966e5bcb85cc81c3f17fe195d04628430e5。
- 正文提交2d25d26ad029924f6cbb04a5dc0cb69368feca5f；原文审计增量提交88c96f195323fe76ba95f59d7916fb87371f3163。
- main.tex SHA256=7292c1a6315aac002ad1214161ba1b1e71aea251742ca427cffd1151ed4a56fc。

## 已读取的确切依据

| 文件 | blob SHA | 核对范围 |
|---|---|---|
| decisions/RF-DATA-CONTRACT-v1.md | 95ff2a93fdfd5387ccac2d969deafc4103b54113 | 全文；本版已包含第一周优先级更新 |
| plans/WEEK1_PLATFORM_PREP_20261020.md | 4f2af5b739b07db3bf25813afc8240fe3a937c69 | 全文；计划不是完成证明 |
| literature/related_work_notes/EXPLORATION-20261020-Xie2011.md | aa3565d398c4f322cd65b7cd36f5c0df630679c7 | 全文EX-XIE-01—05及缺口；本轮另核本地同hash PDF第5页漏检段 |
| MAIN-20261020-003 | 39e3627ae701d94f4ddae96275f636ca52e2bc6a | 本轮接收及论文增量权限；不执行附件中的自动化/工程路由 |
| STATUS.md | 82f8c8eb6ee789093ea76071ce4aa48ebd166403 | 比交接旧快照更新：004R阻断，004R2 RECEIVED/PRE-FLIGHT |
| 004R.review | a63bb1225a86e10f244ef500119b6ee854436d1f | START前服务类型驱动错误、BLOCKED及新复验边界 |
| PAPER-001.review | 323b956bad6d5b7d407d868c53115c425412a049 | main R1 ACCEPTED及旧版本局部PDF检查证据 |

RF合同、计划、Xie和STATUS均已用上述communication commit再读取，blob与首读一致。未把旧handoff中“004R未运行/尚有额度”覆盖更新review；本轮也不声称状态快照之后无新变化。

## 增量入稿内容

### RF方法与数据协议（IV-A、V新增predictor evaluation subsection）

- RF regression为首个开发候选，不是已训练或最终选定predictor。实际数据指VRX真实操作者输入/艇轨迹，与fixture/脚本及实艇海试区分；只有开发者数据时仅称pilot。
- 目标明确p_h(t+H)，不混同导航终点、目标物或人本体。输入必须在请求t前实际到达且源戳<=t；源戳早但晚收到不能离线回填。
- 保存base/target/generation stamp、mission/艇/段/版本；延迟生成不能顺延目标时刻，已过目标时刻拒绝。
- 当前最小候选特征为艇体系速度、yaw_rate、当前前进/转向命令及pose/command源年龄。命令与最终推力分开，缺测不静默补0。眼动、语音、导航目标、belief、GT/距离、未来命令/终局不是本版输入。
- 身份来自采集端并在接收处验证，不把无头旧输入以当前段/接收时刻重新标记为合法采集。
- 标签与输入隔离；同艇同epoch/控制段、持续SEARCH覆盖完整未来区间才有标签；取消/切艇/结束和缺测保留label_unavailable原因，不以未来完整性门控线上预测。
- 合法离线标签允许同段有效双端插值，但最大间隔须先冻结，缺端点/界限则无标签；不外推或无限填充。明确这不改变encounter禁止插值/倒签。
- 参考位姿有独立t_ref，允许艇体未来位移标签/世界坐标重建；不假装pose源戳恰为请求t。
- 按原始参与者/会话/轨迹组分区后再制样本，replay和派生副本同分区；跨人主张要participant holdout，单人不冒称跨人泛化；OOB/随机分行不替代分组评估。
- 同请求和标签比较RF/保持当前位置/恒速，恒速用真实参考戳到目标时刻的间隔；报每会话误差、全尝试/label覆盖、合法输出、回退/拒绝及部署输出误差，不只筛成功预测。无有效当前位姿也不能记零误差。
- 不把更小FDE等同协同收益；最终H、gap、年龄、阈值、样本量和树参数保持OPEN。

### Xie研究边界（II-B、VI）

明确作者的P与临时P′区分及SAD prior路径；不把临时规划抑制说成永久目标后验清零。加录制轨迹仿真的组合策略time-to-detect与本项目B2/B3信息对照/encounter RMST的终点区别。

纳入EX-XIE-05漏检后抑制机器人到访、合作有时更差的原文限制；不单独归因预测误差、不抄原均值/分类精度作为本文参数或收益。本文的belief保留/full-domain责任也不自动保证及时回访，不声称解决该反例；inhibition仍辅助replay候选，无新增主实验条件。

exploration本轮FULL_TEXT_REVIEWED属于其本人；overleaf读取证据包并核关键段，不代签本轮全6页精读。原审计表新增第7节记录证据映射，17引用键/身份与首次顺序不变，无需改bib。

### 第一周计划与工程边界（VI）

正文只写复现相关的准备要求：UI/按钮/设备连接、源身份记录、导出和训练入口。未把工作日历和工程任务号塞进论文。明确API或fixture不证明UI/设备实测、志愿者采集或RF训练；无模型/可选设备不能阻塞核心操作；原始行为数据本地受控。

最新快照004R因临时动作脚本错误在START前阻断，后继004R2已本人领取PRE-FLIGHT、尚未运行；004总体仍RUNTIME_PENDING。因此生产B3“有离线证据但最终runtime未验收”可写，不能写全部功能已完成。002/003/003R既有ACCEPTED不被新失败撤回。004R失败不是生产服务故障证明，未在正文列其调试细节。

## 未入稿/不升级事项

UI真实点击、硬件断连恢复、真实采集、RF训练/精度、正式B3 predictor与门控runtime、encounter实现、正式B2/B3、RMST和人因收益都没有被升级为已完成。第一周计划不是完成依据；RF合同是方法设计依据，不是实证验证。

H/年龄/gap/节拍/阈值、R/tau/正式B、人数/会话/比例/样本量不填数值，不恢复历史5s或1-cell为正式参数。未训练/招募/采集/启动Gazebo，未修改平台/STATUS或发布constructor任务，未配置自动化。

## 验证、提交与后续

- 已在原编辑器paper/main.tex保存，compile_latex_document对该完整路径返回kind=success，对应本报告SHA；未切换标签、未编译独立PDF。
- 静态检查：首次cite顺序与17bibitem完全一致；missing_refs=[]；duplicate_labels=0；没有新增外部图片或文献键。
- main.tex和审计表写前读远端blob检查无同路径并发变更，提交后逐字读回与本地一致。既有main评审/报告原样保留，本轮增量待main审阅。
- 工具未提供返修后PDF导出/页数/完整log，本轮无逐页视觉QA结论；main原ACCEPTED时对旧精确稿6页的局部视觉检查不外推到当前更长版本。终稿分页与新段落版式需后续检查，未通过缩字体压页。
- 线上Overleaf同步UNKNOWN，本轮仅原位文件和GitHub论文分支。

向main的实质回报：已将合同和确切文献证据转为可审查协议/局限；没有新数值裁决请求或新主条件。后续只待最终配置/数据/匹配版本工程验收推进相应状态；保持原PAPER-001 ACCEPTED，不以新材料重做旧任务。
