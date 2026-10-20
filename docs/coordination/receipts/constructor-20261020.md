# constructor 角色与记忆接收回执 — 2026-10-20

- role: `constructor`
- read_commit: `ea4e9bf8e946de6c653627b1d7b297e6318023fd`（写入前通信分支 HEAD）
- contract_version: `RC-20261020-v1`；通信协议 `v1` + `ROLE_PROTOCOL_v1_1`
- active_task: `USV-20261020-003R / 003` 均已由 instructor 正式 `ACCEPTED`；本轮仅文档接收/状态收口，无新 READY 工程任务、无新增运行额度。
- 更新：2026-10-20 15:10，Asia/Shanghai。

## 已读取与实际基线

已读取最新 `MAIN_MEMORY.md`（blob `d4eba881e1a0c1c03af689affcb74b24aa2108f4`）、`PROTOCOL.md`、`ROLE_PROTOCOL_v1_1.md`、instructor 交接与回执、003R/003 正式 review、003R 通信报告及 STATUS。通信分支由 `acb5760` 前进到本次 read_commit 的改动只涉及 main memory、instructor 回执和两份 review；未将远端旧 `platform/` 当生产源码，也未执行远端脚本。

- 实际运行树：`/home/cyz/vrx_ws`；根 Git 尚无提交，运行源码分支/HEAD=`UNKNOWN`，实现提交 SHA=`NONE`，不能以通信 SHA 代替。既有 003/004D 修改保留，不能从根 Git 给出可靠生产 diff/dirty 基线。
- 版本化研究树：`/home/cyz/USV_HRI_PATROL`，`main@5f263c694f3d601bf1596bb92b0849d98f7e677b`；既有 `idea/研究决策状态.md` 未提交修改保留。
- 独立 VRX 树：`humble@dc30ed8d17aa1083fd872edad9c77c69896d2b07`；5 个既有 tracked 修改及未跟踪 world/model 保留。
- 当前 source/install `research_pipeline.launch.py` SHA256 均为 `b835b65920141d68966cf3d664c08e3d0ecf98553c659ec8be546b2fc5f85f21`；Planner 源 `01f672b16cd8c04a59dc5728df9da100ad8794c8e54f6a7f0cbb918c0e5328ea`、责任合同 `2c68363eebe6acc18b55424a1601d9839fa6243cd4585956730610338e579417`、Recorder `19120b8e83085b3df9c74d505519aa9add8e348321259786df258d8a75c42992`。这是文件身份核对，不是完整环境可复现证明。

## 记忆校正与时钟精度

- 002/SLIM-004D 已 `ACCEPTED`（工程预算终止），并非未验收；003R 最终时钟配置与 003 ROS API 级显式 SEARCH/B2 均已 `ACCEPTED`，不是仍待执行/待审。003R 唯一有界 Gazebo smoke 已用尽；本轮未重跑。
- TAKEOVER 只转移执行控制权；显式 SEARCH 才激活 B2 当前位责任；NAVIGATE、CANCEL、RELEASE 撤销。远端旧平台与离线测试均不能替代最终生产运行证据。
- generation 3 人工中心与 28.324 s 的 fleet pose 相距约 0.0287 m。原报告的 **0.024 s** 是 `28.348 s` Recorder assignment 外层时刻与该 fleet pose 的差；与 Planner 原始 plan/source stamp `28.152 s` 比较，差为 **0.172 s**。这支持邻近时段当前位中心，不证明源事件时刻精确同步；保留处理/接收延迟。本回执澄清历史报告的含糊“时间差”，不改写原始记录。
- 真实 UI 点击=`NOT_OBSERVED`；B3 fallback、有效遭遇、正式 FOUND、科学比较、RMST=`NOT VALIDATED`。R、τ、正式预算、encounter↔FOUND/同 tick、B3 时域/阈值仍由 main 裁决。旧 Gamma/FOUND 或概率正检出不能擅自等同 RC 的有效遭遇。

## 本次核查与边界

只读执行 `git status --short --branch` / `git rev-parse HEAD`（研究树、VRX、运行树）、`sha256sum`（上述 source/install）、读取本地 003R 详报，并经 GitHub fetch/compare 核对 HEAD、review 与任务目录（001/002/003/003R，无新 READY）。没有运行 Gazebo、构建、测试、训练或修改生产源码；本回执不是新的 runtime 证据。后续生产 B3 任务须由 instructor 单独发布；本轮仅确认真实接收，不代替 main/overleaf 的 ACK。

## USV-20261020-004 新任务接收（2026-10-20，Asia/Shanghai）

- role=constructor；read_commit=`a13585080c5e50d38d5ad76d13bc66e378d3453d`；contract_version=`RC-20261020-v1 + RC-20261020-v1.1`；active_task=`USV-20261020-004`，状态=`RECEIVED/RUNNING`，不是 DONE/ACCEPTED。
- 已读取唯一 READY 004、MAIN_MEMORY、RC-v1.1 D5、MAIN-20261020-002、协议/角色协议与 instructor 新回执；002/003/003R 前置均已 ACCEPTED。通信分支比 instructor 提交仅多 overleaf 回执更新，无竞争工程 READY。
- 当前生产基线复核：`/home/cyz/vrx_ws` 根无有效 Git HEAD，源码 SHA=UNKNOWN、实现提交 NONE；Planner SHA256 `01f672b16cd8c04a59dc5728df9da100ad8794c8e54f6a7f0cbb918c0e5328ea`，experiment_modes `076a355f5eb1dd616794664854fd99fb8889409af6f4081a556239754a05cede`，source/install launch 均 `b835b65920141d68966cf3d664c08e3d0ecf98553c659ec8be546b2fc5f85f21`。研究 main@5f263c6 有既有决策 dirty；独立 VRX humble@dc30ed8d 有既有修改与 world/model，均保留。
- 已确认旧说法需纠正：远端 platform 不是运行源码；RF 缺失目前会使 B3 fixed-center 返回错误，尚非已完成回退；H/年龄/位移阈值仍 OPEN。有效 prediction fixture 只能证明工程接线，不能宣称 RF 或正式 B3 已验证。
- 未决冲突：正式 H/预测年龄及重规划阈值、R/τ/B 与 encounter 终态仍交 main；本任务只做 D5 工程门控与失效回退，不推断这些数值。
- 本人 ACK 仅表示已经接收任务；后续离线、构建、至多一次 Gazebo smoke 按任务合同执行，另以 004 报告提交实际结果。
