# VRX Operator-Station ROS Graph Notes

Generated after the 10 WAM-V camera-only split.

## Files

- `bin/ros_graph_review/ros_graph_current.dot`: current graph inferred from source and latest runtime logs.
- `bin/ros_graph_review/ros_graph_target.dot`: proposed operator-station boundary before refactoring.
- `bin/ros_graph_review/ros_graph_current.svg`: rendered current graph.
- `bin/ros_graph_review/ros_graph_target.svg`: rendered target graph.

These are temporary review artifacts kept under `bin/ros_graph_review/` so they
can be deleted in one step without touching the project packages.

## Runtime observations

- Gazebo advertises 10 `front_camera_sensor` streams at `1280x720 @ 30 Hz`.
- The UI subscribes directly to the selected WAM-V camera topic and odometry topic.
- `usv_overview` currently publishes map metadata and aggregated fleet state, but it is not yet the central communication gateway.
- `manual_mux` currently converts `/operator/manual_cmd` directly into thruster topics for every selected WAM-V.
- A manual waypoint publisher/debug script should have an explicit entry point in the target architecture, publishing `/operator/manual_waypoints` or a selected `/wamv_i/cmd/waypoints` stream through the operator-station task-dispatch layer.
- The latest logs show shutdown-time exceptions in `pad_ctrl` and `manual_mux` because they attempt to publish after the ROS context is already invalid.

## Interpretation

The current implementation mixes three roles:

- HRI/operator display rendering in `usv_console`.
- Communication aggregation in `usv_overview`.
- Manual command routing in `usv_ctrl`.

For an operator-station architecture, `usv_overview` should own the normalized fleet communication layer and task dispatch boundary. `usv_console` should mainly render state and issue operator intent, while each WAM-V namespace should own low-level control and waypoint tracking.
