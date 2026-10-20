# Windows 眼动桥接与无人船平台整合交接

- 日期：2026-10-20，Asia/Shanghai。
- 作者：本地 Windows Codex；接收角色：main、constructor；工程范围由现有 instructor 链路衔接。
- 用户要求：将本机 `C:\bridge` 的 Unity/Tobii 眼动桥接纳入无人船 Work 的 constructor 与 main 统筹。眼动仪由 Windows 采集，Linux 接收数据。
- 状态：**LOCAL_AUDIT_COMPLETE / LINUX_INTEGRATION_PENDING**。这是本地接口核查报告，不是新的 READY 任务或硬件验收。
- 读入通信基线：`b758f6dd1906a2db8213f9b9f7f5f1d14e1f8ed0`，并核对后继 `7ce60e3ca4d53390b48e8ac105624d172597a830`。后者已有 constructor 本人领取 004R2 的预检回执；004R 已 BLOCKED/RUN_CONSUMED，005 仍 DRAFT。后续以最新 task/review/receipt 为准。

## 已核实的本地资产

| 资产 | 位置或身份 | 证据范围 |
| --- | --- | --- |
| Windows Unity 发行目录 | `C:\bridge`，程序 `UUV.exe`，含 `UUV_Data`、UnityPlayer 和 Tobii 原生 DLL | 文件存在 |
| UUV.exe SHA256 | `059c313352892718258a120b87bdc6fc7c23ce67181084abe14f86f204f5dddb` | 本轮直接计算 |
| Assembly-CSharp.dll SHA256 | `5070cc5bc922fa0dc7a0244f100362404c00bf20259fe9b70f8370a767e5378b` | 本轮直接计算 |
| Unity 源工程 | `C:\EyeTrackerBridge` | 本轮找到并读取发送脚本与 Tobii provider |
| 发送源码 | `Assets\Scripts\GazeUdpSender.cs` | 原始文件 SHA256 `066e1c2bf06fb27bbc83af13250e26c1ff36fcb0f97cc2f91229a59407b5fc4c` |
| 本机启动说明 | `C:\bridge\cli.txt` | 已配置一个局域网 Linux 目标，UDP 15555；具体地址留在本地 |

发送源码具备命令行参数 `--gaze-host`、`--gaze-port`、`--gaze-flip-y` 和 `--gaze-no-flip-y`，也支持发行目录下 `gaze_udp_config.json` 与 `TOBII_GAZE_*` 环境变量。优先级为命令行高于环境变量，高于配置文件，高于序列化默认值；默认目标是本机回环地址，跨机启动必须设置 Linux 主机地址。

本轮在发行 DLL 中找到上述发送类、运行配置方法、命令行和主要数据字段标记；这不能替代重现构建或真实接收验证。当前 UUV 窗口被系统枚举到，但进程命令行读取被拒，当前 Player.log 为空，实际生效目标地址和有效眼动状态未核实。本轮未启动、停止或重配该进程，未采集原始眼动。

## 统一接入方向

```text
Windows Tobii 驱动与校准
  → C:\bridge\UUV.exe
  → UDP JSON，目标为 Linux 主机的 15555 端口
  → Linux 当前生产单接收链（由 constructor 核对实际文件与 source/install 身份）
  → /tobii/gaze
  → 现有 operator_console、设备状态与会话记录
```

005 草案明确生产 `gaze.launch` 采用单进程 UDP 接收，不恢复双 LSL 链。通信分支的 `platform/src/eyetrackerbridge/`、README 和 tips 仍包含旧 UDP→LSL→ROS 路径，只作历史源码参考；不得复制它们覆盖 `/home/cyz/vrx_ws`，也不能把它们当作生产已验证链。Windows 继续负责依赖 Tobii 的采集；Linux 无须安装 Windows 眼动驱动。

## 发送包接口与语义

| 字段 | 本地源码行为 | Linux 接入要求 |
| --- | --- | --- |
| `x_norm`, `y_norm` | 默认按左上角原点，范围 0 至 1；已执行一次 Y 翻转 | 优先使用这两个字段，不再次翻转；实际 flip 配置须记入会话 |
| `x_px`, `y_px`, `screen_w`, `screen_h` | 相对 Windows Unity 渲染窗口内容区域 | 不能直接解释成 Linux 控制台像素或世界坐标 |
| `sx`, `sy`, `vx`, `vy` | Tobii/Unity 原始 screen/viewport；SDK 为左下角原点 | 保留原始含义，不与已转换字段混用 |
| `valid` | JSON 数字 0/1；无效坐标为 JSON null | 仍应接收并记录无效帧，不能沿用上次有效点伪装持续有效 |
| `t`, `unity_t` | Unity 进程内秒时间；无效时 t 使用 Unity 当前时间 | 不当 Unix 时间、ROS /clock 或跨机同步时间 |
| `tracker_us` | 直接来自 SDK `TimeStampMicroSeconds`；无效时 -1 | 保留整数与原始时钟域，不能直接与 Linux 时间相减 |

脚本在每次 Unity Update 发送最近一点；包率取决于渲染帧率，不能称为固定 60 Hz 的设备采样率。连续包可能含同一 `tracker_us`，应将传输帧计数与设备采样计数分开；跨重启需要发送实例身份，不能只按时间数值全局去重。

本地 SDK 的 GazePoint 注释曾将 PreciseTimestamp 写为毫秒，但实际 provider 将 `TimeStampMicroSeconds` 直接传入，需按实现保留原值并记录单位来源。provider 还存在 TODO：用同一个设备时间戳作差后赋值 `Time.unscaledTime`，因此 t 的现有实现不能证明真实采集年龄。UI 中的接收新鲜度与设备采样新鲜度应分开。

## 与第一周平台准备的接合点

1. constructor 在实际 Linux 运行树核对唯一接收器、bind 地址/端口、启动入口、字段转换、失效传播和 `/tobii/gaze` 发布者数量，回报文件路径及 hash。此项先做只读接口核对；生产变更沿 instructor 对 005 的有效授权，与 004R2 冻结基线串行。
2. UI 至少区分发送进程可见、收到 UDP、最近有效眼动、坐标映射可用四种事实；超时/无效/恢复分别显示。进程存在或 UDP 发出不等于 Linux 收到或眼动有效。
3. 确认操作员实际观看的屏幕、Unity 窗口、远程/镜像 Linux 控制台内容区域、DPI 与黑边。只有映射得到现场验证后，才可把点叠加到控制台；角点与中心校准、窗口变化和断连恢复列为待现场项。
4. 现有包没有 source_id、发送实例、序号、session/run/epoch/vehicle/authority segment、可信源采集时间与切段握手。可继续用于带明确限制的显示/诊断；不可在接收端倒填当前控制段后作为 RF 可信证据。源身份补齐需绑定 owner 确认并保留采集与接收时间两个时钟域，具体工程格式由 instructor/constructor 决定。
5. Recorder 保留坐标配置、代码/DLL hash、源身份及其缺失状态、无效/缺测/重复/重启/时序异常和接收统计。时钟偏差未经测量时，不报告跨机端到端延迟。原始眼动与参与者数据保留本地，公开仓库只放摘要。
6. main 将本机桥接登记到第一周硬件/UI/记录准备；眼动暂非 RF 首个候选的必需特征，不等待志愿者数据、训练模型或最终 H 才做接口准备。不改 posterior、SEARCH 语义或研究参数。

## 回执与完成条件

- main：本人 ACK 本报告，将 Windows 采集入口与 Linux 生产链的差异纳入统筹，并沿现有 instructor 链衔接 005；不新增竞争 READY。
- constructor：本人 ACK，提供实际 Linux 单接收器接口、启动命令及 hash，并标明与本包匹配或缺失的字段；未经新的有效任务范围，不重启设备或追加 Gazebo。
- 现场联调：Windows→Linux UDP→ROS→UI→Recorder 同次会话有逐层证据；实际显示映射、无效/超时/恢复及记录身份可核验，才可报告端到端通过。

本报告仅证明本地文件与源接口核查完成。Linux 实时接收、ROS 发布、UI 坐标映射、设备有效采样、跨机时钟对齐和完整采样导出均 **NOT_OBSERVED**；角色是否已收到以其本人回执为准。

