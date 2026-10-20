# INSTRUCTOR-TO-MAIN-MANUAL-20261020-001 — 用户现有上位机手动验收优先
- role=instructor；接收main；2026-10-20；状态USER_DIRECTION_REPORTED / MAIN_NEXT_STEP_PENDING。
- 用户本轮明确询问何时能开始手动验收：“我用一键启动脚本开启仿真平台，只有我判断了UI也即这个上位机是合理的，给你进行UI的反馈，才能更好的指导constructor不是吗？”并要求向main汇报、让main判断接下来的建设。
- 用户要先实际操作现有平台形成反馈，不能把“005全建成/训练完成/额外API smoke”设成查看与评价当前UI的前置。这是一轮现有上位机使用评审，不等于用户已签整体工程/科学ACCEPTED。

## 新工程事实
004R2和004本轮由instructor审为限定工程ACCEPTED：最终hash与原始事件/20路直接STOP安全核对成立；004复验基线冻结解除。004R原失败保持历史；UI/设备/真实RF/encounter与科学结果未验证。
因此可安排用户现在启动现有一键平台做界面/操作走查，不需要再等待同类自动化复验。instructor本轮没有替用户启动进程。

## 请main决定并同步接下来建设
建议005第一步变为“现状展示与用户手动走查”，之后按用户反馈小步实施、再让用户复验：
1. constructor只准备当前版本启动入口、设备状态说明、已知缺口与一页最短操作说明，不先改整套UI；保留可回查版本，避免用户看到的版本与后续反馈不对应。
2. 用户用原一键启动脚本查看上位机，先评布局/信息密度/字体与地图/选艇、状态反馈/按钮语义/设备连接状态。全局START/STOP与单艇SEARCH区分，缺失功能如实显现，不拿ROS CLI替用户点击。
3. 收集用户自然反馈，截图或文字均可；只需“在哪个页面/做了什么/哪里不合理/想要怎样”，不强迫填写长表。instructor整理为缺陷/使用偏好/待解释项，确认理解后给constructor小批修改，不让用户重复向多角色转述。
4. 再检查接管/手动操纵/导航/释放/停止等实际操作与硬件；有活动任务的人工联调由005明确场景/时长/停止收尾，用户可随时停止。无设备项待现场，不把现有research-core/headless验收说成上位机已测。
5. 再衔接可信记录/导出与参数化训练入口，数据/训练/科学比较仍后续。用户对UI合理性的判断是交互建设主要依据；安全与状态因果证据仍由工程线负责，不要求用户替代底层审计。

## 已核对启动入口
实际/home/cyz/vrx_ws/run_vrx.sh为唯一顶层启动脚本，start包含Qt console/joy/pad/gaze/voice；--headless只关闭Gazebo窗口，不等于关闭Qt。**--research-core会排除console与硬件链，不能用它给用户做UI走查**。
默认profile为历史h5_command_aware，已验收的SEARCH/B2/B3语义不能据默认profile猜测；请constructor说明用户实际一键入口的精确命令、profile、DISPLAY与设备参数，不暗换旧快捷方式或混用无模型临时实验配置。若用户已有桌面入口沿现有入口核对，不要求重新搭建启动体系。
第一阶段只看现状可先不按任务START；要测主动操纵时核对已选模式与安全停止。这里不自动增加assistant/constructor无人值守Gazebo预算。

## 跨机桥接一并纳入现状反馈
已读MAIN-TO-INSTRUCTOR-BRIDGE交接并接收Linux核对要求：constructor负责Linux现有单接收与UI，Windows Codex负责C:\bridge/C:\EyeTrackerBridge，main中转。005纳入15555链、显示坐标映射、设备采样与接收新鲜度分开、原始身份缺失不倒填RF。文件审计不等于设备实测；不要求用户再找聊天ID或重贴接口。
请main本人回复阶段优先级与005范围，避免先大改再让用户第一次看到。instructor保持唯一工程派发，005暂不自行全量转READY；当前请求不授权招募/训练/正式科学实验。
