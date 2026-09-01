# USV_HRI_PATROL

面向海上搜救区域覆盖搜索的多无人船人机协同研究项目。本仓库将工程平台、论文材料和研究构想分开维护，避免把平台功能、论文贡献与尚待验证的想法混在一起。

## 仓库结构

| 目录 | 内容 | 状态 |
| --- | --- | --- |
| [`platform/`](platform/) | 基于 VRX 的 ROS 2 / Gazebo 多 USV 仿真与多模态交互平台 | 持续开发 |
| [`algo/`](algo/) | 多 USV 覆盖搜索路径规划算法包（Unity 实现规格说明 + 无依赖参考代码） | 已加入 |
| [`paper/`](paper/) | 论文正文、图表和投稿材料 | 待加入 |
| [`idea/`](idea/) | 头脑风暴、研究备忘录和待验证方案 | 持续整理 |

## 平台来源

仿真平台基于 [OSRF VRX](https://github.com/osrf/vrx) 的 Humble 版本二次开发。仓库将上游 VRX 固定在提交 `dc30ed8d17aa1083fd872edad9c77c69896d2b07`，并以子模块和可审查补丁记录本项目的改动，避免重复提交整套上游资源，同时保证版本和功能可复现。

## 获取项目

```bash
git clone --recurse-submodules https://github.com/pharmacy28/USV_HRI_PATROL.git
cd USV_HRI_PATROL/platform
./scripts/setup_vrx.sh
```

如果克隆时没有使用 `--recurse-submodules`，`setup_vrx.sh` 会补充初始化 VRX，并幂等地应用二次开发补丁。构建和运行方法见 [`platform/README.md`](platform/README.md)。

## 内容边界

- `platform` 只维护可运行、可复现的实验基础设施及工程文档。
- `paper` 只维护进入论文或投稿流程的正式材料。
- `idea` 允许保留尚未验证的假设、备选方法和讨论记录；其中内容不等同于最终论文结论。
- `algo` 记录 Unity 工程中路径规划算法的当前真实实现（规格说明 + 参考代码），包括与 CONFIRMED 研究决策的已知差异；其中实现不等同于论文结论。

除 VRX 自带许可证所覆盖的上游文件外，本仓库暂未声明统一的开源许可证；复用前请分别核对各组件的许可证。
