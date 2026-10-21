# 四传感器可执行建设提案（提交 main 定案）
日期：2026-10-21
Owner: instructor
状态：PROPOSED / MAIN_DECISION_PENDING（不是已实现、不是生产切换授权）

## 用户直接要求
四路传感器需要实际建设；真实目标检测暂关闭；视频预览帧率与低频科学采样分离；不能只列缺口。当前 R4 用户复验不得因建设工作被重启或增加摄像头负载。

## 已核实的可复用输入
现有 sensor_capabilities.json 只有 camera enabled，sonar/infrared/radar disabled，标签不等于真实传感器。
本地原生 VRX 已有 wamv_planar_lidar.xacro、wamv_3d_lidar.xacro、lidar.xacro、3d_lidar/model.sdf；先复用、核对实际 gz 版本与生成 SDF，不必先移植陌生项目。
平面 lidar 宏现值 256 rays/10 Hz/0.2–70m/±1.0472rad 仅是上游工程默认，不是新的科学参数裁决。
第四路建议明确为用户所需 lidar；保留 radar 为未启用独立能力，不能将 ray scan 冒充 RF radar。

## 建议分步交付
A. constructor 离线隔离实现统一能力状态与数据适配：RGB/IR 图像，sonar/lidar scan，topic/TF/header/源时间/到达时间/有效性；每路实际数据驱动，不用四色图标或复制 RGB 充数。先一艇可选 profile，默认用户会话不加载新负载。
B. RGB 复用现有 camera；IR 首选已安装、与运行 gz 版本匹配的原生 thermal camera（需真实 thermal 标记/温度模型）；否则只交付标明 auxiliary RGB view 的预览，不能验收 IR。lidar 复用原生宏并核验桥接 LaserScan/PointCloud 与 TF。sonar 必须明确本阶段为几何 ray/range 近似还是声学插件；辅助 RGB 镜头可帮助查看，但不能验收声呐测量或声学物理。
C. 在现有窗口复用图像/scan显示和按键切换，仅做必要布局，显示来源与未启用状态。检测节点默认仍关闭，不用框/置信度充当 binary 理想观测。
D. 视频源/选中预览/Qt 分别统计 FPS、header age、RTF；科学采样保持现有合法节奏。科学采样不随渲染帧数增加，不把四路相关观测乘为独立 likelihood。原始记录保留源序号、时间、缺测和实际模态。
E. 离线验证生成模型、topic/桥接配置、TF唯一性、禁用默认、模式切换及源信息不丢；独立预检通过后，再申请单艇有界运行验收（此提案不授权新 Gazebo）。先单艇真实数据/负载验收，再 main 决定是否全艇展开。

## main 本轮需写明的裁决
1. 第四路正式为 lidar 还是 radar；建议 lidar。
2. sonar 几何近似是否满足第一周工程准备，IR 原生 thermal 的工程范围；明确不能宣称的物理真实性。
3. 同意先一艇可选 profile 与现有 UI 小增量；生成器参数来源、待定科学量与后续四路观测模型分开。
请回复正式 handoff 的工程允许范围及验收件。instructor 随后发布 READY 实现任务，constructor 开始隔离编码与测试，而不是继续提交清单。
