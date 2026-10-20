# SLIM-004B 历史证据索引（非新增验收）

2026-10-20；role=instructor；read_commit=b6f0b81e3d66f2cd9081efe60a516c437317c43d；回应 MAIN-20261020-002。
本轮直接只读原详报：`src/workspace/reports/SLIM_004B_GT_INDEPENDENT_OBSERVATION_REPORT.md`（相对 /home/cyz/vrx_ws）；SHA256=`755f89fbeb487ee3dae056731fb9496d26e95afa54ee4bc9c9b14569a8170083`。

原报告证据摘要（未在本轮重跑测试或重做运行）：
- 183 passed、0 skipped；覆盖 observation/Recorder/probability/static visibility/negative audit/GT boundary/terminal/planner/coverage/authority/MUX。生产 _sample_vehicle 四个GT位置对照在修复前失败，修复后 validity/reason 不随GT变；同一p向量、RNG一次抽样、UNKNOWN中性、CameraInfo fail-closed、START两种回调顺序有定向覆盖。
- run_id=023836a48e1144daa20961a4621ae7d9；本地 log/experiments/run_1792373794562000388/；index0–7、10艇、80唯一事件；48 VALID NEGATIVE更新、32 CAMERA_INFO_STALE ABSTAIN不更新，80事件ID在source/GENERATED/APPLIED对齐。初次零事件诊断run保留，不用于PASS。
- 历史 wamv_05/index12、17 的目标GT UNKNOWN精确runtime分支未刻意重现，NOT_OBSERVED。运行reason计数0不能单独证明分支消除；依据是直接生产路径四位置确定性测试。有效snapshot含UNKNOWN不等于真实目标恰落UNKNOWN的runtime证据。
- 原报告称构建/安装一致、10/10 STOPPED、20/20实际推进器零、Recorder STOPPED。以上为历史报告支持的工程结果，本轮未独立重算原run全部统计。
- UNKNOWN→p_i=0是显式理想化约定，不能沿用旧报告“保守”一词声称真实未知LOS推断保守；不等于标定。无runtime POSITIVE、正式FOUND/encounter/RMST、四模态验证；历史报告的“自动预算未验证”仅为当时状态，后续002另有工程验收。
- 本索引不补造历史独立ACCEPTED，不把报告作者PASS改称instructor历史签收。当前源代码和最终观测manifest仍需后续配置核对，不能由旧报告数值冻结RC-v1.1。
