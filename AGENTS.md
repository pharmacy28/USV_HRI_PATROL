# USV_HRI_PATROL Agent Rules

These rules apply to the entire repository.

## Repository roles

- `/home/cyz/USV_HRI_PATROL` is the authoritative versioned research repository.
- `platform/` is the reproducible ROS 2 / Gazebo / VRX platform representation.
- `idea/` contains research notes, mathematical frameworks, candidate designs, and research-state documentation.
- `paper/` contains formal paper material.
- `/home/cyz/vrx_ws` is the authoritative currently runnable ROS 2 / Gazebo / VRX workspace.

The two roots have an explicit mapping, but they are not the same Git working tree. Never treat `/home/cyz/vrx_ws` as the GitHub repository root. Map runtime `run_vrx.sh`, `config/`, `custom_wamv/`, `src/`, and `bin/` to their counterparts under `platform/`. Do not synchronize generated or local runtime artifacts such as `build/`, `install/`, `log/`, `.TobiiBridge/`, Whisper model weights, Unity archives, or caches.

## VRX rule

`/home/cyz/vrx_ws/src/vrx` is an independent OSRF VRX Git repository. Do not commit project-specific changes upstream. Reproduce project-specific VRX changes through:

```text
platform/patches/vrx-humble.patch
platform/scripts/setup_vrx.sh
```

Any future VRX change must keep the pinned upstream revision, patch, setup script, build, and runtime behavior consistent.

## Required reading

Before research-sensitive work, read the relevant parts of:

```text
README.md
platform/README.md
platform/docs/工作环境交接说明.md
idea/研究决策状态.md
idea/人机协同USV覆盖搜索_研究备忘录.md
idea/单静止目标_多WAMV传感器融合与路径规划框架.md
```

The older idea documents contain historical and candidate material. They are not automatically final research decisions. When they conflict with `idea/研究决策状态.md`, the explicit status in `idea/研究决策状态.md` takes precedence.

## Scientific discipline

- Never silently resolve an `OPEN` research question.
- Never introduce arbitrary scientific parameters merely to make an implementation work.
- Important parameters must eventually be justified by physics, sensor calibration, map resolution, validation data, explicit optimization, or sensitivity analysis.
- Do not change scientific definitions merely to make tests pass.
- Do not present Random Forest, K-means, Hungarian assignment, A*, or other standard components as scientific contributions merely because they are used.
- The central research hypothesis must be tested experimentally, not assumed true. Never fabricate results.

## Bayesian belief rule

Human commands, gaze, voice, joystick input, selected destinations, and predicted destinations must not directly modify target posterior belief unless a defensible probabilistic human-observation model has explicitly been introduced. Target observations require a probabilistically justified detection and missed-detection likelihood model.

## Re-clustering rule

When a human-commanded or predicted destination is treated as a fixed center:

- keep fixed centers fixed;
- include all searchable, non-obstacle free cells again in clustering;
- update only autonomous centers;
- do not merely transform previous autonomous clusters;
- do not manually remove residual search regions.

## Planning and assignment rule

Search-center generation and USV–center assignment are separate stages. The required dependency is:

```text
belief-aware clustering
→ centers
→ A* path for eligible USV–center pairs
→ path-dependent assignment cost
→ optimal assignment
```

Do not use `clustering → Euclidean/Hungarian assignment → A*` when path-dependent assignment is required. Locked human USV–destination pairs remain excluded from autonomous reassignment during the active command interval.

## Experimental and implementation rules

- Keep experimental baselines, ablations, random seeds, metrics, and statistical methods explicit.
- Record build, test, and experiment commands and outcomes for implementation work.
- Prefer small, reviewable changes.
- Do not implement candidate or open research choices as if they were confirmed requirements.
