# 本地 Codex 首次连接回执

- 回执版本：`v1`
- 更新时间：`2026-10-20`（`Asia/Shanghai`）
- 连接结论：`CONNECTED`

## 1. 通信入口

| 项目 | 值 |
|---|---|
| 仓库 | `https://github.com/pharmacy28/USV_HRI_PATROL` |
| 分支 | `coordination/work-20261020` |
| 协议 | `docs/coordination/PROTOCOL.md` |
| Work 任务 | `docs/coordination/tasks/<task_id>.md` |
| 本地报告 | `docs/coordination/reports/<task_id>.md` |

本次使用独立临时 clone 读写通信分支，没有切换、重置、清理或覆盖现有研究仓库和 ROS 运行工作区。
远端读取和推送能力均已实际验证。`CONNECTED` 表示传输通道可读写；Work 是否已收到本回执，仍应以
后续提交或验收回执为准。

## 2. 当前源码身份

| 对象 | 分支 | SHA | 说明 |
|---|---|---|---|
| 实际 ROS/平台运行工作区 | `UNKNOWN` | `UNKNOWN` | 工作区根没有有效 Git commit，不能伪造平台基线 |
| 版本化研究仓库 | `main` | `5f263c694f3d601bf1596bb92b0849d98f7e677b` | 含既有未提交研究决策修改；不是当前运行源码完整快照 |
| VRX 上游子仓库 | `humble` | `dc30ed8d17aa1083fd872edad9c77c69896d2b07` | 含既有修改及未跟踪 world/model 资产 |

运行工作区存在会影响后续任务的未提交修改，其中包含尚未完成验收的 SLIM-004D 工作；本次未改动、
未提交、未迁移这些内容。

## 3. 最新阶段与报告索引

最新完成且可核验的阶段为 **SLIM-004C**。可共享本地报告索引：

- `workspace/reports/SLIM_004C_CAMERAINFO_CONSISTENCY_REPORT.md`
- `workspace/reports/SLIM_004B_GT_INDEPENDENT_OBSERVATION_REPORT.md`
- `workspace/reports/SLIM_004A_OBSERVATION_ALIGNMENT_AUDIT.md`
- `workspace/reports/SLIM_003B_R_REPORT.md`

这些报告当前仅位于本地运行工作区，本次没有复制其原始日志或平台代码到公开通信分支。

### SLIM-004C

- 验收证据：`存在`
- 报告结论：CameraInfo stale 根因、十艇资格一致性、ROS build、真实 Gazebo smoke、STOP 与 Recorder
  均有对应证据；工程运行验证为 PASS。
- 共享摘要：70 个唯一观测事件，10 艘艇各 7 次，0 ABSTAIN；事件、Bayesian application ID 集合一致；
  STOP 后 20 路推力为零。
- 边界：正式实验、统计独立性、calibrated perception、FOUND/Gamma 和 RMST 未验证。

### SLIM-004D

- 验收证据：`不存在完整验收证据`
- `workspace/reports/SLIM_004D_REPORT.md`：不存在。
- 当前只有本地进行中的实现/离线检查和不完整运行尝试，尚无自然 `BUDGET_EXPIRED`、右删失、
  Recorder finalize 全链路的完整运行验收；不得视为 DONE 或 ACCEPTED。

## 4. 当前功能状态（只读摘要）

| 项目 | 实现状态 | 验收边界 |
|---|---|---|
| 控制权 | 已实现 `AUTONOMOUS`、`HUMAN_CONTROLLED`、`COMMAND_LOCKED` 三态及 planner-owned revision/epoch 校验；H0 禁止人工接管，MUX 保留 STOP barrier | 工程合同已实现；不等同于 B2/B3 正式实验通过 |
| SEARCH | 已实现显式 START/STOP、mission epoch、规划/覆盖执行与终止状态传播 | B0 完整科学实验和正式终止统计未验证 |
| NAVIGATE | 已实现语音导航意图、车辆×目标区域/坐标解析和显式目标锁定；与 SEARCH 是不同合同 | 不是目标存在观测，不得直接改变 posterior |
| 人工责任中心 | 代码支持当前位置、显式目的地和预测位置作为 fixed center，并从自主分配池排除人工控制艇 | B2 责任语义及正式比较仍需研究合同裁决/验收 |
| 预测模块 | constant-velocity 与 random-forest 代码/配置及候选 fallback contract helper 存在；当前 production planner 在 RF prediction 不可用时会报告错误 | RF 与 fallback 的生产集成仍属候选；M1/M2、B3 正式贡献与性能均未确认 |

## 5. 论文源文件

- 本地仓库中的论文边界文件：`paper/README.md`。
- 实际论文正文源文件相对路径：`UNKNOWN`（本地未发现 `.tex` 或 `.bib` 正文源）。
- Overleaf 同步状态：`UNKNOWN`；本次没有访问或修改 Overleaf。

## 6. 本次检查

| 检查 | 结果 |
|---|---|
| 阅读工作区及研究仓库 `AGENTS.md` | 完成；确认研究仓库与运行工作区是不同树 |
| 研究仓库 `git branch --show-current` / `git rev-parse HEAD` / `git status --short` | `main` / `5f263c...` / 存在既有研究决策修改 |
| 运行工作区 Git 检查 | 根目录无有效 commit；平台 branch/SHA 记为 `UNKNOWN` |
| VRX 子仓库 Git 检查 | `humble` / `dc30ed8...` / 存在既有修改和未跟踪资产 |
| `git ls-remote` 通信分支 | 成功读取远端分支 |
| 独立 clone + `git fetch` + HEAD 对照 | 写入前本地与远端均为 `7e96fad5df5ab044f49e30c2d7792b3673f6fc0a` |
| 报告与源码只读核查 | 确认 004C 报告存在、004D 报告不存在及上述工程状态 |
| 论文文件检索 | 仅发现 `paper/README.md`；Overleaf 状态不可核验 |
| 仿真/训练 | 未启动 |

## 7. 当前阻塞项

1. 实际平台运行工作区无可用 Git SHA，后续 READY 任务必须记录文件级工作区状态或先由负责人确定快照策略。
2. SLIM-004D 尚无完整运行验收及报告。
3. 本地论文正文与 Overleaf 同步状态不可核验。
