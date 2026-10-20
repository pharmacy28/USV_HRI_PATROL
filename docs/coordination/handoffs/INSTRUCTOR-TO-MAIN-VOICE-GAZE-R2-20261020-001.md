# INSTRUCTOR-TO-MAIN-VOICE-GAZE-R2-20261020-001
2026-10-20；instructor→main；用户明确授权继续语音识别率/眼动延迟实际修复，Windows端需配合由main协调，不大改界面。read_commit=2976da1d123f87442947a2ddfc65033c91733d47。

用户将启动005 R1体验。本轮保持R1生产source/install稳定；005同任务追加R2隔离实现，未允许在用户测试中覆盖/重启。R1绘制/反馈改善不等于ASR与眼动延迟已解决。

## Linux已定向核查与后继
whisper_worker本地音频按chunk调用sd.rec/sd.wait，Pulse每块新建parec再terminate，可能块间丢音，需实际连续性/PTT首尾测试；constructor将以隔离R2准备连续采音/缓冲修复，不能凭猜降VAD/能量阈值或称识别率已升。已有zh初始提示/beam5，不重复当新方案。
眼动console gaze订阅已depth1、UI已有latest-pending，因此不重复添加；查UDP处理/发布/Qt消费等上游实际积压。保留原始数据/时间，不以“包率高”冒充设备新样本或端到端低延迟。

## 请main协调Windows现有agent（不是请求用户再找聊天ID）
按既有C:\bridge/C:\EyeTrackerBridge分工，请Windows agent提供一小段**不含坐标/身份映射的聚合或去标识时间链证据**及现有发送实现的针对性修改方案：
1. Tobii实际新tracker_us到达次数、Unity每Update发包次数、重复tracker比率，分设备回调/读取和发送环节；不能把Update时间t当设备采集年龄。
2. Windows源采集→进入发送队列→socket发送的本机单调时间、队列/发送阻塞/主线程停顿，保留tracker_us与clock映射已知/未知。序号高水位/时钟回退/重连重置须明确。
3. 若确认反复发送旧tracker或阻塞FIFO，提出并在Windows侧本地隔离测试“只对新设备样本发送或显示通道优先最新”的最小修复；原始采样/录制路径不删，不改变有效性为凑顺滑。不能直接据本文件假定根因。
4. 数据包schema/version、source session、tracker_us、send sequence、Windows单调clock、采集/发送时间语义保持兼容；Linux不倒填源身份。
5. 目前正在用的UUV.exe是否由所见源码构建、实际生效目标IP/15555与进程/端口对应；修改编译包先作为候选，**不在用户R1测试期间静默替换正在跑的exe或改协议**。
6. 声音若实际用Windows UDP音频15556，请明确其采样率/格式/PTT/帧序号与发送连续性；若用户使用Linux本地麦克风则不无故扩Windows音频任务。
涉及真实设备/录音/跨机测量须沿用户本轮人工联调安排，不自动启动志愿者采样、RF训练或无人值守仿真；不公开原始音频/眼动/身份。main可将已有Windows审计增量中转，不重做全平台审计。

请main明确让Windows agent响应上述实际修复协作，回传可用聚合证据/候选patch与切换条件；接收与执行需本人证据。本交接不是constructor第二份READY，不增加运行额度，不改变当前RF最少特征或研究合同。
