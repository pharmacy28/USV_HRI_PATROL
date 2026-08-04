#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WS="${VRX_WS:-$SCRIPT_DIR}"
export VRX_WS="$WS"
WORLD="air_crash_sar"
CONFIG_FILE="$WS/config/multi_wamv_10.yaml"
LOG_DIR="${VRX_LOG_DIR:-$WS/log/vrx_debug}"
JOY_DEV="/dev/input/js0"

HEADLESS=false
CLEAN=true
WITH_SIM=true
WITH_JOY=true
WITH_PAD=true
WITH_MUX=true
WITH_OVERVIEW=true
WITH_CONSOLE=true
WITH_VOICE=false
BRIDGE_ALL_PAYLOAD_CAMERAS=false

TARGET_NAMES="['wamv_01','wamv_02','wamv_03','wamv_04','wamv_05','wamv_06','wamv_07','wamv_08','wamv_09','wamv_10']"
INITIAL_TARGET="wamv_01"
MAP_PADDING_M="80.0"
MIN_MAP_SPAN_M="800.0"
GRID_SIZE_M="10.0"
CAMERA_RESOLUTION="640x360"
VOICE_MODEL="base"
VOICE_MODEL_DIR="$WS/bin/voice_models"
VOICE_PYTHON="${VRX_VOICE_PYTHON:-$(command -v python3)}"
VOICE_LANGUAGE="zh"
VOICE_AUDIO_BACKEND="auto"
VOICE_AUDIO_DEVICE=""
VOICE_UDP_BIND="0.0.0.0"
VOICE_UDP_PORT=15556
VOICE_UDP_SOURCE_IP=""
VOICE_UDP_TIMEOUT_SEC="1.0"
VOICE_UDP_PREROLL_SEC="0.15"
VOICE_CHUNK_SEC="1.5"
VOICE_ENERGY_THRESHOLD="0.02"
VOICE_AUDIO_GAIN="1.0"
VOICE_NO_SPEECH_THRESHOLD="0.8"
VOICE_SOURCE_VOLUME="100%"
VOICE_PUSH_TO_TALK="true"
VOICE_PTT_BUTTON=0
VOICE_CANCEL_BUTTON=1
VOICE_PTT_RELEASE_DEBOUNCE_SEC="0.2"

PAGE_NEXT_BUTTON=5
PAGE_PREV_BUTTON=7
PAGE_PREV_AXIS=5
GRID_TOGGLE_BUTTON=3

usage() {
  cat <<'EOF'
Usage:
  ./run_vrx.sh [start] [options]
  ./run_vrx.sh stop
  ./run_vrx.sh status
  ./run_vrx.sh diag
  ./run_vrx.sh voice-devices

Options:
  --headless          Start Gazebo without GUI.
  --no-clean         Do not kill old VRX/debug processes before start.
  --no-sim           Do not start Gazebo simulation.
  --no-joy           Do not start joy_node.
  --no-pad           Do not start pad_ctrl.
  --no-mux           Do not start manual_mux.
  --no-overview      Do not start usv_overview nodes.
  --no-console       Do not start operator_console.
  --voice            Start local Whisper ASR and voice command bridge.
  --voice-model NAME Whisper model name. Default: base.
  --voice-model-dir PATH
                     Whisper model cache directory. Default: platform/bin/voice_models.
  --voice-device ID  sounddevice input device index/name.
  --voice-backend NAME
                     Audio backend: auto, sounddevice, pulse, udp. Default: auto.
  --voice-udp-bind IP UDP listen address. Default: 0.0.0.0.
  --voice-udp-port N  UDP PCM port. Default: 15556.
  --voice-udp-source-ip IP
                     Only accept UDP audio from this Windows IP.
                     Protocol: VRXA v1, 16 kHz mono PCM16LE, UDP 15556.
  --voice-chunk SEC  ASR chunk length. Default: 1.5.
  --voice-threshold X
                     Microphone RMS threshold. Default: 0.02.
  --voice-gain X     Microphone gain before ASR/VAD. Default: 1.0.
  --voice-no-speech-threshold X
                     Whisper no-speech threshold. Default: 0.8.
  --voice-source-volume V
                     PulseAudio source volume when --voice is enabled. Default: 100%.
  --voice-open-mic   Disable push-to-talk and continuously listen.
  --voice-ptt-button N
                     A button index for push-to-talk. Default: 0.
  --voice-cancel-button N
                     B button index for cancelling ASR result. Default: 1.
  --voice-ptt-release-debounce SEC
                     Ignore short A-button release glitches. Default: 0.2.
  --bridge-all-cameras
                     Bridge every WAM-V camera stream. Default: selected camera only.
  --world NAME       Default: air_crash_sar.
  --config PATH      Default: platform/config/multi_wamv_10.yaml.
  --joy-dev PATH     Default: /dev/input/js0.
  --overview-span M  Minimum overview map span in meters. Default: 800.0.
  --overview-padding M
                     Padding around scanned world objects. Default: 80.0.
  --overview-grid M  Overview occupancy grid cell size in meters. Default: 10.0.
  --page-next-button N
                     RB button index for UI page next. Default: 5.
  --page-prev-button N
                     RT button index if RT is a button. Default: 7.
  --page-prev-axis N RT trigger axis index if RT is an axis. Default: 5.
  --grid-toggle-button N
                     Y button index for overview grid toggle. Default: 3.

Logs:
  platform/log/vrx_debug/*.log

Current defaults:
  world: air_crash_sar
  config: platform/config/multi_wamv_10.yaml
  WAM-V fleet: 10 identical camera-only boats from custom_wamv/generated/*.urdf
  camera bridge: selected camera only unless --bridge-all-cameras is used
EOF
}

stop_old() {
  echo "[run_vrx] stopping VRX/debug processes"

  if [ -d "$LOG_DIR" ]; then
    for pid_file in "$LOG_DIR"/*.pid; do
      [ -e "$pid_file" ] || continue
      local pid
      pid="$(cat "$pid_file" 2>/dev/null || true)"
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
      fi
    done
  fi

  stop_patterns TERM
  sleep 1
  stop_patterns KILL

  if [ -d "$LOG_DIR" ]; then
    rm -f "$LOG_DIR"/*.pid
  fi
  rm -f /tmp/vrx_voice_ptt_*.json 2>/dev/null || true
}

stop_patterns() {
  local signal="$1"
  pkill "-$signal" -f "ros2 launch vrx_gz competition.launch.py" || true
  pkill "-$signal" -f "ros2 launch usv_overview overview.launch.py" || true
  pkill "-$signal" -f "ros2 run joy joy_node" || true
  pkill "-$signal" -f "ros2 run pad_ctrl eightbitdo_pad" || true
  pkill "-$signal" -f "ros2 run usv_ctrl manual_mux" || true
  pkill "-$signal" -f "ros2 run usv_console operator_console" || true

  pkill "-$signal" -f "gz sim" || true
  pkill "-$signal" -f "gz gui" || true
  pkill "-$signal" -f "gz topic -e" || true
  pkill "-$signal" -f "gz topic.*dynamic_pose/info" || true
  pkill "-$signal" -f "ros_gz_sim" || true
  pkill "-$signal" -f "parameter_bridge" || true
  pkill "-$signal" -f "monitor_sim" || true
  pkill "-$signal" -f "ruby.*gz" || true
  pkill "-$signal" -f "ruby" || true

  pkill "-$signal" -f "joy_node" || true
  pkill "-$signal" -f "eightbitdo_pad" || true
  pkill "-$signal" -f "manual_mux" || true
  pkill "-$signal" -f "overview_server" || true
  pkill "-$signal" -f "fleet_state_node" || true
  pkill "-$signal" -f "sensor_link_monitor" || true
  pkill "-$signal" -f "selected_camera_relay" || true
  pkill "-$signal" -f "selected_camera_bridge" || true
  pkill "-$signal" -f "whisper_bridge_node" || true
  pkill "-$signal" -f "voice_command_node" || true
  pkill "-$signal" -f "mission_gateway_node" || true
  pkill "-$signal" -f "whisper_worker.py" || true
  pkill "-$signal" -f "operator_console" || true
  pkill "-$signal" -f "optical_frame_publisher" || true
  pkill "-$signal" -f "robot_state_publisher" || true
  pkill "-$signal" -f "pose_tf_broadcaster" || true
  pkill "-$signal" -f "frame_publisher" || true
}

status() {
  source_env
  echo "=== ROS nodes ==="
  ros2 node list --no-daemon --spin-time 5 || true
  echo
  echo "=== Duplicate-node audit ==="
  ros2 node list --no-daemon --spin-time 5 2>/dev/null | sort | uniq -c || true
  echo
  echo "=== Key topics ==="
  ros2 topic list | grep -E '(/fleet|/operator|/ui|/overview|/voice|/mission|/(wamv_0[1-9]|wamv_10)/(odometry|pose|thrusters/.*/thrust|sensors/.*/.*image_raw|sensors/.*/.*camera_info))' || true
  ros2 topic list | grep -E '^/tobii/gaze$' || true
  echo
  echo "=== One-shot checks ==="
  timeout 2 ros2 topic echo /overview/metadata --once 2>/dev/null || true
  timeout 2 ros2 topic echo /overview/fleet_state --once 2>/dev/null || true
  timeout 2 ros2 topic echo /overview/sensor_health --once 2>/dev/null || true
  timeout 2 ros2 topic echo /overview/selected_camera/status --once 2>/dev/null || true
  timeout 2 ros2 topic echo /voice/whisper_status --once 2>/dev/null || true
  timeout 2 ros2 topic echo /voice/transcript --once 2>/dev/null || true
  timeout 2 ros2 topic echo /voice/status --once 2>/dev/null || true
  timeout 2 ros2 topic echo /voice/intent --once 2>/dev/null || true
  timeout 2 ros2 topic echo /mission/request --once 2>/dev/null || true
  timeout 2 ros2 topic echo /mission/status --once 2>/dev/null || true
  ros2 topic info /tobii/gaze -v 2>/dev/null || true
  timeout 2 ros2 topic echo /tobii/gaze --once 2>/dev/null || true
  echo
  echo "=== Communication edges ==="
  ros2 topic info /fleet/manual_target -v 2>/dev/null || true
  ros2 topic info /fleet/manual_target_state -v 2>/dev/null || true
  ros2 topic info /operator/manual_cmd -v 2>/dev/null || true
  ros2 topic info /overview/fleet_state -v 2>/dev/null || true
  ros2 topic info /overview/selected_camera/image_raw -v 2>/dev/null || true
  ros2 topic info /voice/transcript -v 2>/dev/null || true
  ros2 topic info /voice/intent -v 2>/dev/null || true
  ros2 topic info /mission/request -v 2>/dev/null || true
  ros2 topic info /mission/status -v 2>/dev/null || true
}

diag() {
  echo "=== CPU ==="
  lscpu | grep -E 'Model name|型号名称|CPU\\(s\\)|CPU:|Thread|线程|Core|核|MHz' || true
  echo
  echo "=== Memory ==="
  free -h || true
  echo
  echo "=== GPU ==="
  nvidia-smi || true
  echo
  echo "=== Top processes ==="
  ps -eo pid,comm,%cpu,%mem,rss --sort=-%cpu | head -35 || true
  echo
  echo "=== ROS status ==="
  source_env
  if command -v ros2 >/dev/null 2>&1; then
    ros2 node list || true
    ros2 topic list | grep -E '(/fleet|/operator|/ui|/overview|/voice|/mission|/tobii/gaze|/(wamv_0[1-9]|wamv_10)/odometry)' || true
  else
    echo "ros2 not found in PATH"
  fi
}

voice_devices() {
  source_env
  echo "=== USB devices ==="
  lsusb | grep -Ei '8bitdo|audio|camera|microphone|headset' || lsusb || true
  echo
  echo "=== Bluetooth controller/devices ==="
  rfkill list | grep -A2 -Ei 'bluetooth|hci' || true
  bluetoothctl devices || true
  echo
  echo "=== PulseAudio cards ==="
  pactl list cards short || true
  echo
  echo "=== ALSA capture hardware ==="
  arecord -l || true
  echo
  echo "=== ALSA PCM names ==="
  arecord -L | grep -E '^(default|pulse|hw:|plughw:|sysdefault:|front:|dsnoop:)' || true
  echo
  echo "=== PulseAudio/PipeWire sources ==="
  pactl list sources short || true
  echo
  echo "Use a PulseAudio source with:"
  echo "  ./run_vrx.sh --voice --voice-backend pulse --voice-device SOURCE_NAME"
  echo "For example, SOURCE_NAME may look like bluez_input.xx_xx_xx_xx_xx_xx.0 after a Bluetooth headset is connected in HFP/HSP mode."
  echo
  echo "=== voice conda / sounddevice ==="
  if [ -x "$VOICE_PYTHON" ]; then
    "$VOICE_PYTHON" \
      "$WS/src/usv_overview/usv_overview/whisper_worker.py" \
      --list-devices || true
  else
    echo "voice Python not found: $VOICE_PYTHON"
  fi
}

source_env() {
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
  if [ -f "$WS/install/setup.bash" ]; then
    # shellcheck disable=SC1091
    source "$WS/install/setup.bash"
  else
    echo "[run_vrx] warning: $WS/install/setup.bash not found"
  fi
  set -u
}

launch_bg() {
  local name="$1"
  shift
  local log_file="$LOG_DIR/${name}.log"

  echo "[run_vrx] starting $name"
  echo "[run_vrx] log: $log_file"
  (
    cd "$WS"
    exec setsid "$@"
  ) >"$log_file" 2>&1 &

  echo $! >"$LOG_DIR/${name}.pid"
}

wait_for_topic() {
  local topic="$1"
  local timeout_sec="$2"
  local start_sec
  start_sec="$(date +%s)"

  while true; do
    if ros2 topic list 2>/dev/null | grep -qx "$topic"; then
      return 0
    fi

    if (( $(date +%s) - start_sec >= timeout_sec )); then
      echo "[run_vrx] warning: timed out waiting for $topic"
      return 1
    fi

    sleep 1
  done
}

start_all() {
  mkdir -p "$LOG_DIR"

  if [ "$CLEAN" = true ]; then
    echo "[run_vrx] cleaning old VRX/debug processes"
    stop_old
    sleep 1
  fi

  validate_inputs
  source_env

  export QT_AUTO_SCREEN_SCALE_FACTOR=0
  export QT_SCALE_FACTOR=1
  export QT_FONT_DPI=96
  export QT_XCB_GL_INTEGRATION=xcb_glx
  export VRX_BRIDGE_ALL_PAYLOAD_CAMERAS="$BRIDGE_ALL_PAYLOAD_CAMERAS"

  if [ "$WITH_SIM" = true ]; then
    local sim_cmd=(
      ros2 launch vrx_gz competition.launch.py
      "world:=$WORLD"
      "config_file:=$CONFIG_FILE"
    )

    if [ "$HEADLESS" = true ]; then
      sim_cmd+=("headless:=True")
    fi

    launch_bg sim "${sim_cmd[@]}"
    wait_for_topic "/clock" 45 || true
  fi

  if [ "$WITH_JOY" = true ]; then
    launch_bg joy ros2 run joy joy_node --ros-args \
      -p "dev:=$JOY_DEV" \
      -p deadzone:=0.08 \
      -p autorepeat_rate:=30.0
    sleep 1
  fi

  if [ "$WITH_PAD" = true ]; then
    launch_bg pad ros2 run pad_ctrl eightbitdo_pad --ros-args \
      -p "target_names:=$TARGET_NAMES" \
      -p "initial_target:=$INITIAL_TARGET" \
      -p invert_turn:=true \
      -p target_axis:=7 \
      -p sensor_axis:=6 \
      -p switch_debounce:=0.45 \
      -p switch_release_time:=0.15 \
      -p "page_next_button:=$PAGE_NEXT_BUTTON" \
      -p "page_prev_button:=$PAGE_PREV_BUTTON" \
      -p "page_prev_axis:=$PAGE_PREV_AXIS" \
      -p "grid_toggle_button:=$GRID_TOGGLE_BUTTON"
    sleep 1
  fi

  if [ "$WITH_MUX" = true ]; then
    launch_bg manual_mux ros2 run usv_ctrl manual_mux --ros-args \
      -p "target_names:=$TARGET_NAMES" \
      -p "initial_target:=$INITIAL_TARGET" \
      -p max_thrust:=2000.0 \
      -p turn_scale:=0.5 \
      -p publish_rate:=30.0 \
      -p cmd_timeout:=0.5
    sleep 1
  fi

  if [ "$WITH_OVERVIEW" = true ]; then
    local voice_args=("enable_voice:=$WITH_VOICE")
    if [ "$WITH_VOICE" = true ]; then
      mkdir -p "$VOICE_MODEL_DIR"
      if [ "$VOICE_AUDIO_BACKEND" != "udp" ] && command -v pactl >/dev/null 2>&1; then
        local source_name="$VOICE_AUDIO_DEVICE"
        if [ -z "$source_name" ]; then
          source_name="$(pactl get-default-source 2>/dev/null || true)"
        elif [[ "$source_name" == pulse:* ]]; then
          source_name="${source_name#pulse:}"
        fi
        if [ -n "$source_name" ] && [ -n "$VOICE_SOURCE_VOLUME" ]; then
          pactl set-source-volume "$source_name" "$VOICE_SOURCE_VOLUME" 2>/dev/null || true
        fi
      fi
      voice_args+=(
        "voice_python:=$VOICE_PYTHON"
        "voice_model:=$VOICE_MODEL"
        "voice_model_dir:=$VOICE_MODEL_DIR"
        "voice_language:=$VOICE_LANGUAGE"
        "voice_audio_backend:=$VOICE_AUDIO_BACKEND"
        "voice_chunk_sec:=$VOICE_CHUNK_SEC"
        "voice_energy_threshold:=$VOICE_ENERGY_THRESHOLD"
        "voice_audio_gain:=$VOICE_AUDIO_GAIN"
        "voice_no_speech_threshold:=$VOICE_NO_SPEECH_THRESHOLD"
        "voice_udp_bind:=$VOICE_UDP_BIND"
        "voice_udp_port:=$VOICE_UDP_PORT"
        "voice_udp_timeout_sec:=$VOICE_UDP_TIMEOUT_SEC"
        "voice_udp_preroll_sec:=$VOICE_UDP_PREROLL_SEC"
        "voice_push_to_talk:=$VOICE_PUSH_TO_TALK"
        "voice_ptt_button:=$VOICE_PTT_BUTTON"
        "voice_cancel_button:=$VOICE_CANCEL_BUTTON"
        "voice_ptt_release_debounce_sec:=$VOICE_PTT_RELEASE_DEBOUNCE_SEC"
      )
      if [ -n "$VOICE_AUDIO_DEVICE" ]; then
        voice_args+=("voice_audio_device:=$VOICE_AUDIO_DEVICE")
      fi
      if [ -n "$VOICE_UDP_SOURCE_IP" ]; then
        voice_args+=("voice_udp_source_ip:=$VOICE_UDP_SOURCE_IP")
      fi
    fi

    launch_bg overview ros2 launch usv_overview overview.launch.py \
      "world:=$WORLD" \
      "target_names:=$TARGET_NAMES" \
      "config_file:=$CONFIG_FILE" \
      "map_padding_m:=$MAP_PADDING_M" \
      "min_map_span_m:=$MIN_MAP_SPAN_M" \
      "grid_size_m:=$GRID_SIZE_M" \
      "${voice_args[@]}"
    sleep 1
  fi

  if [ "$WITH_CONSOLE" = true ]; then
    launch_bg console ros2 run usv_console operator_console
  fi

  echo
  echo "[run_vrx] started. Logs are in $LOG_DIR"
  echo "[run_vrx] world=$WORLD headless=$HEADLESS overview_span=${MIN_MAP_SPAN_M}m camera=$CAMERA_RESOLUTION voice=$WITH_VOICE"
  echo "[run_vrx] useful checks:"
  echo "  ros2 topic echo /fleet/manual_target_state"
  echo "  ros2 topic echo /overview/fleet_state --once"
  echo "  ros2 topic echo /tobii/gaze --once"
  echo "  ros2 topic echo /voice/whisper_status --once"
  echo "  ros2 topic echo /voice/transcript --once"
  echo "  ros2 topic echo /mission/request --once"
  echo "  ros2 topic echo /mission/status --once"
  echo "  ros2 topic echo /wamv_01/odometry --once"
  echo "  ros2 topic info /operator/manual_cmd -v"
  echo "[run_vrx] attention heatmap:"
  echo "  operator_console reads /tobii/gaze directly."
  echo "  Start gaze_lsl_bridge.py and gaze_receiver.py manually when needed."
  echo
  echo "[run_vrx] stop with:"
  echo "  ./run_vrx.sh stop"
}

validate_inputs() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "[run_vrx] error: config file not found: $CONFIG_FILE" >&2
    exit 1
  fi

  if [ ! -f "$WS/install/setup.bash" ]; then
    echo "[run_vrx] error: install/setup.bash not found. Run colcon build first." >&2
    exit 1
  fi

  if [ "$WITH_JOY" = true ] && [ ! -e "$JOY_DEV" ]; then
    echo "[run_vrx] warning: joystick device not found: $JOY_DEV"
    echo "[run_vrx]          use --no-joy --no-pad, or --joy-dev PATH"
  fi

  if [ "$WITH_VOICE" = true ]; then
    if [ "$WITH_OVERVIEW" != true ]; then
      echo "[run_vrx] error: --voice requires overview; remove --no-overview" >&2
      exit 1
    fi
    if [ "$WITH_JOY" != true ] && [ "$VOICE_PUSH_TO_TALK" = "true" ]; then
      echo "[run_vrx] error: --voice with --no-joy requires --voice-open-mic" >&2
      exit 1
    fi
    case "$VOICE_AUDIO_BACKEND" in
      auto|sounddevice|pulse|udp) ;;
      *)
        echo "[run_vrx] error: invalid voice backend: $VOICE_AUDIO_BACKEND" >&2
        exit 1
        ;;
    esac
    if [ "$VOICE_AUDIO_BACKEND" = "udp" ]; then
      if ! [[ "$VOICE_UDP_PORT" =~ ^[0-9]+$ ]] || [ "$VOICE_UDP_PORT" -lt 1 ] || [ "$VOICE_UDP_PORT" -gt 65535 ]; then
        echo "[run_vrx] error: invalid UDP audio port: $VOICE_UDP_PORT" >&2
        exit 1
      fi
    fi
    if [ ! -x "$VOICE_PYTHON" ]; then
      echo "[run_vrx] error: voice Python not found: $VOICE_PYTHON" >&2
      exit 1
    fi
    if [ ! -f "$WS/src/usv_overview/usv_overview/whisper_worker.py" ]; then
      echo "[run_vrx] error: whisper worker not found in usv_overview package" >&2
      exit 1
    fi
  fi
}

cmd="start"
if [ "${1:-}" = "start" ] || [ "${1:-}" = "stop" ] || [ "${1:-}" = "status" ] || [ "${1:-}" = "diag" ] || [ "${1:-}" = "voice-devices" ] || [ "${1:-}" = "help" ]; then
  cmd="$1"
  shift || true
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --headless)
      HEADLESS=true
      ;;
    --no-clean)
      CLEAN=false
      ;;
    --no-sim)
      WITH_SIM=false
      ;;
    --no-joy)
      WITH_JOY=false
      ;;
    --no-pad)
      WITH_PAD=false
      ;;
    --no-mux)
      WITH_MUX=false
      ;;
    --no-overview)
      WITH_OVERVIEW=false
      ;;
    --no-console)
      WITH_CONSOLE=false
      ;;
    --voice)
      WITH_VOICE=true
      ;;
    --voice-model)
      VOICE_MODEL="$2"
      shift
      ;;
    --voice-model-dir)
      VOICE_MODEL_DIR="$2"
      shift
      ;;
    --voice-device)
      VOICE_AUDIO_DEVICE="$2"
      shift
      ;;
    --voice-backend)
      VOICE_AUDIO_BACKEND="$2"
      shift
      ;;
    --voice-udp-bind)
      VOICE_UDP_BIND="$2"
      shift
      ;;
    --voice-udp-port)
      VOICE_UDP_PORT="$2"
      shift
      ;;
    --voice-udp-source-ip)
      VOICE_UDP_SOURCE_IP="$2"
      shift
      ;;
    --voice-chunk)
      VOICE_CHUNK_SEC="$2"
      shift
      ;;
    --voice-threshold)
      VOICE_ENERGY_THRESHOLD="$2"
      shift
      ;;
    --voice-gain)
      VOICE_AUDIO_GAIN="$2"
      shift
      ;;
    --voice-no-speech-threshold)
      VOICE_NO_SPEECH_THRESHOLD="$2"
      shift
      ;;
    --voice-source-volume)
      VOICE_SOURCE_VOLUME="$2"
      shift
      ;;
    --voice-open-mic)
      VOICE_PUSH_TO_TALK="false"
      ;;
    --voice-ptt-button)
      VOICE_PTT_BUTTON="$2"
      shift
      ;;
    --voice-cancel-button)
      VOICE_CANCEL_BUTTON="$2"
      shift
      ;;
    --voice-ptt-release-debounce)
      VOICE_PTT_RELEASE_DEBOUNCE_SEC="$2"
      shift
      ;;
    --bridge-all-cameras)
      BRIDGE_ALL_PAYLOAD_CAMERAS=true
      ;;
    --world)
      WORLD="$2"
      shift
      ;;
    --config)
      CONFIG_FILE="$2"
      shift
      ;;
    --joy-dev)
      JOY_DEV="$2"
      shift
      ;;
    --overview-span)
      MIN_MAP_SPAN_M="$2"
      shift
      ;;
    --overview-padding)
      MAP_PADDING_M="$2"
      shift
      ;;
    --overview-grid)
      GRID_SIZE_M="$2"
      shift
      ;;
    --page-next-button)
      PAGE_NEXT_BUTTON="$2"
      shift
      ;;
    --page-prev-button)
      PAGE_PREV_BUTTON="$2"
      shift
      ;;
    --page-prev-axis)
      PAGE_PREV_AXIS="$2"
      shift
      ;;
    --grid-toggle-button)
      GRID_TOGGLE_BUTTON="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[run_vrx] unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

case "$cmd" in
  start)
    start_all
    ;;
  stop)
    stop_old
    ;;
  status)
    status
    ;;
  diag)
    diag
    ;;
  voice-devices)
    voice_devices
    ;;
  help)
    usage
    ;;
esac
