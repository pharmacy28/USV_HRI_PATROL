# main → instructor：Windows桥接接口接收与第一周整合

2026-10-20，Asia/Shanghai；作者main；接收instructor，实施经instructor交constructor。状态：MAIN_ACK / HANDOFF_PUBLISHED，非工程READY，无新增运行额度。

main本人已读取并ACK reports/WINDOWS-BRIDGE-20261020-001.md@c636b7fd11c6daabb5c1287ff823b2c0b1251fe7。用户要求将Windows桥接与现有main/constructor统合；本交接及已更新plans/WEEK1_PLATFORM_PREP_20261020.md落实该方向，不等待重复RF合同。

请instructor将现有Windows Unity/Tobii→UDP 15555→Linux生产单接收→/tobii/gaze→UI/Recorder纳入005准备，沿原工程链转交constructor核对Linux实际接收器、启动入口、source/install hash、字段转换、失效传播和唯一发布者。不恢复旧双LSL，不用仓库旧platform覆盖生产树。005仍DRAFT；生产更改与004R2冻结基线串行，当前独立UI设计/文档/只读接口核对可继续。

需保留的接口限制：
- t实现等同更新时Unity时间，不能证明真实采集年龄；Update重复最近tracker_us，传输包率不等于设备采样率。
- 坐标参考Windows Unity窗口；Linux显示映射、DPI/内容区/黑边/Y翻转须现场验证。
- 缺可信源session/epoch/vehicle/authority等身份，不接收端倒填为RF证据。UI分开接收与采样新鲜度，Recorder记录重复/无效/配置/hash/源身份缺失。
- Windows进程命令行读取被拒且日志为空；有效采样、Linux实时接收、ROS发布、坐标映射及端到端通过均未观察。

当前004R=BLOCKED/RUN_CONSUMED；004R2已由constructor本人领取RECEIVED/PRE-FLIGHT，但尚无预检PASS/新运行证据。全部原预检门槛满足后才可按该原任务一次新会话，本交接不增加额度、不启动设备/Gazebo、不招募/采样、不改变科学合同。

请在下一份实质回执/报告中合并记录接收、Linux接口匹配与缺口，避免为逐条ACK另开完整审查。main发布本交接不等于instructor/constructor已收到。constructor真实聊天ID/链接本轮未检得，保持UNKNOWN；未声称直接聊天送达。
