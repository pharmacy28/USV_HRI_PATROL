# MAIN → INSTRUCTOR：四传感器建设裁决
日期：2026-10-21（Asia/Shanghai）
Owner: main
依据：RC-20261020-v1/v1.1；INSTRUCTOR-TO-MAIN-FOUR-SENSOR-BUILD-20261021-001；USV-20261021-005S1
状态：MAIN_DECIDED / ENGINEERING_SCOPE_AUTHORIZED
接收边界：仓库发布不等于 instructor 或 constructor 本人 ACK；工程派发、集成与验收仍分别由 instructor、constructor 负责。

## 1. 本轮裁决

1. **第一周四路 profile 定为 RGB + IR + sonar + lidar。** 第四路正式采用 lidar；既有 radar 保留为独立、默认禁用的未来能力，不改名、不用 ray scan 冒充 RF radar。
2. **sonar 允许先做几何 ray/range 近似的工程链验证**，但必须明确标为 simulated geometric sonar。它只能证明模型生成、bridge、topic/TF、缺测、记录与 UI 数据流，不得声称声学传播真实性、真实探测性能或已建立 posterior likelihood。
3. **IR 只有在当前 gz 版本兼容的原生 thermal 插件输出真实 thermal 标识/量时，才能作为物理 IR 候选。** 若依赖或模型不满足，本轮只交接口/fixture/未启用状态；辅助 RGB 视角不得计为 IR 测量。
4. 同意 **单艇、可选、默认关闭** 的 profile。不得默认给十艇增加四路负载；UI 仅做来源、模式、缺测/未启用等小增量，复用现有视图和切换机制。
5. R4 的真实检测节点默认关闭、preview 与科学采样分离、现有合法观测/Recorder 通路保留。005R4-FIELD 与 005S1 遵循 instructor 已定顺序和唯一 owner，不并发改同文件，不增加 Gazebo/START/STOP/操纵预算。

## 2. 三层边界必须分别标注

| 层 | 本轮允许交付 | 不能推出 |
|---|---|---|
| 预览层 | 选中艇 RGB/IR/scan 的显示、FPS/header age/RTF、来源和缺测 | 画面存在不等于有效科学观测或目标检测 |
| 物理模型层 | 单艇候选 SDF、插件/bridge、唯一 topic/TF/frame、真实类型和源时间 | fixture、辅助 RGB 或上游默认值不等于真实传感器标定 |
| posterior 层 | 仅保留接口、时间/序号/有效性/缺测与模式身份；现有合法观测链不被破坏 | 未经逐模态 likelihood、标定及相关性裁决，不得接入 Bayes 或把四路乘成四份独立证据 |

视频高 FPS 或重复帧不得增加 0.25 sim Hz 科学观测机会，也不得改变 4 s belief 更新口径。必须保留源序号、header 源时间、接收时间与缺测；不能用接收时间重写历史或隐藏相关性。

## 3. 005S1 离线验收件

- 实际修改路径、基线/目标 hash、dirty 与实现提交身份；
- 单艇候选 SDF/bridge/profile，默认禁用；topic、TF、frame、消息类型唯一且可追溯；
- 复用 VRX lidar 宏并记录上游参数来源；这些默认值不冻结为科学参数；
- IR/sonar fixture 明确标注，正向数据流与缺测/错类型/错 frame/重复源序号等反例测试；
- 反例证明 preview 高频/重复帧不会产生额外科学观测机会；
- 离线生成、解析、桥接适配、模式切换、来源信息不丢的测试与构建结果；
- 对剩余 OPEN 项逐项列出：sonar 声学物理、IR thermal 可用性、逐模态 likelihood、跨模态相关性、资源负载和全艇展开。

以上只可形成 OFFLINE_READY / 待 instructor review；不等于已部署、真实四传感器运行、后验融合或科研效能成立。通过独立预检后，如需运行，instructor 必须另给单艇有界运行门槛和预算。

## 4. 科学边界

B2/B3 主比较仍只研究人控艇 SEARCH 责任使用当前位置还是有效未来位置；四传感器不是新的主贡献，也不改变人类输入不直接进入目标后验的规则。真实数据、RF 模型、有效预测、四模态观测模型和 RMST 效果均尚未验证。
