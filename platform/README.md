# USV HRI 仿真平台

这是基于 VRX Humble 二次开发的多 USV 人机协同仿真工作区，集成了十艇 VRX/Gazebo 场景、ROS 2 控制链、全局态势与 FPV 控制台、8BitDo 手柄、Tobii 眼动桥接和本地 Whisper 中文语音命令。

## 组成

| 路径 | 作用 |
| --- | --- |
| `src/vrx/` | 固定版本的上游 VRX 子模块；项目改动由 `patches/` 管理 |
| `src/usv_overview/` | 舰队状态、传感器监测、相机选择、语音意图与任务网关 |
| `src/usv_console/` | 操作员态势、FPV、传感器和注意力热力图界面 |
| `src/usv_ctrl/`、`src/pad_ctrl/` | 多艇手动控制选择、复用和手柄映射 |
| `src/eyetrackerbridge/` | Windows/Unity → UDP → LSL → ROS 眼动链路 |
| `src/voicebridge/` | Windows 麦克风 UDP 音频发送端 |
| `custom_wamv/`、`config/` | 自定义 WAM-V 与三艇/十艇编队配置 |
| `run_vrx.sh` | 启动、停止、状态和诊断入口 |

## 1. 初始化 VRX

从仓库的 `platform/` 目录执行：

```bash
./scripts/setup_vrx.sh
```

脚本会把 `src/vrx` 固定到本项目验证过的上游提交，并应用 `patches/vrx-humble.patch`。重复运行不会重复打补丁。

本项目对 VRX 的主要改动包括：多艇配置分别加载 URDF、多实例状态发布、里程计桥接、按传感器类型整理雷达/声呐话题，以及按需桥接相机以控制资源占用。

## 2. 环境与构建

基准环境为 Ubuntu 22.04、ROS 2 Humble 与 VRX Humble 所需的 Gazebo/ROS 依赖。安装 ROS 2 和 VRX 系统依赖后：

```bash
cd /path/to/USV_HRI_PATROL/platform
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --merge-install
source install/setup.bash
```

## 3. 启动

```bash
./run_vrx.sh                 # 完整仿真、手柄、态势节点和控制台
./run_vrx.sh --headless      # 无 Gazebo GUI
./run_vrx.sh status          # 节点、话题与关键通信边
./run_vrx.sh diag            # 系统与设备诊断
./run_vrx.sh stop            # 停止相关进程
```

脚本默认以自身目录作为工作区，因此无需克隆到固定的 `~/vrx_ws`。也可以用 `VRX_WS=/path/to/platform` 显式覆盖。

## 4. 可选多模态输入

### 语音

语音进程所用 Python 可通过 `VRX_VOICE_PYTHON` 指定；默认自动使用 `~/miniconda3/envs/voice/bin/python`（若存在）。音频后端 `auto` 在 Linux 上优先使用 PulseAudio，并自动绑定系统默认输入源；也可手动指定：

```bash
export VRX_VOICE_PYTHON=/path/to/voice-env/bin/python
./run_vrx.sh --voice --voice-backend pulse --voice-device SOURCE_NAME
```

Whisper 模型位于 `bin/voice_models/`，首次使用时自动下载缺失权重。Windows 麦克风也可通过 `src/voicebridge/windows_audio_udp_sender.py` 发送 16 kHz 单声道 PCM 音频到默认 UDP 15556 端口。

### 眼动

仓库保留自研 UDP/LSL/ROS 桥接源码，不提交本机 `.TobiiBridge` 虚拟环境、Unity 缓存或打包归档。Unity 端将 `src/eyetrackerbridge/GazeUdpSender.cs` 加入已安装 Tobii SDK 的工程；Linux 端分别运行：

```bash
python src/eyetrackerbridge/gaze_lsl_bridge.py
python src/eyetrackerbridge/gaze_receiver.py --reconnect --publish-invalid
```

完整操作、话题核查与故障定位见 [`docs/操作与调试笔记.md`](docs/操作与调试笔记.md)。

## 5. 上游与许可证

VRX 子模块来源于 [osrf/vrx](https://github.com/osrf/vrx)，固定提交为 `dc30ed8d17aa1083fd872edad9c77c69896d2b07`，其文件继续受 VRX 自带的 Apache-2.0 许可证约束。Tobii、Unity、Whisper 及其他第三方组件需按各自条款安装和使用。
