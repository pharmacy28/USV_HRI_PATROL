import sys
import cv2
import json
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile
from rclpy.qos import QoSReliabilityPolicy

from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo, Joy, LaserScan
from geometry_msgs.msg import Pose, PoseArray, PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from cv_bridge import CvBridge

from PyQt5.QtCore import Qt, QTimer, QRectF, QSize, QPointF
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QFont, QBrush, QPolygonF, QLinearGradient, QPainterPath, QRadialGradient
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QCheckBox,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
)


USV_NAMES = [f"wamv_{i:02d}" for i in range(1, 11)]

# 上位机固定监控四类传感器链路；基础版只会让已接入的 camera 亮起。
SENSOR_ORDER = ["camera", "sonar", "ir", "radar"]

SENSOR_LABELS = {
    "camera": "摄像头",
    "sonar": "前扫声纳",
    "ir": "红外摄像头",
    "radar": "射线雷达",
}

SENSOR_TITLES = {
    "camera": "第一人称摄像头视频流",
    "sonar": "前扫声纳数据流",
    "ir": "红外摄像头视频流",
    "radar": "射线雷达数据流",
}

SENSOR_PLACEHOLDERS = {
    "camera": "等待摄像头视频流",
    "sonar": "等待前扫声纳数据流",
    "ir": "等待红外摄像头视频流",
    "radar": "等待射线雷达数据流",
}


def sensor_topic(usv_name: str, sensor_name: str) -> str:
    if sensor_name == "camera":
        return f"/{usv_name}/sensors/cameras/front_camera_sensor/image_raw"

    if sensor_name == "sonar":
        return f"/{usv_name}/sensors/sonars/front_sonar_sensor/scan"

    if sensor_name == "ir":
        return f"/{usv_name}/sensors/cameras/ir_camera_sensor/image_raw"

    if sensor_name == "radar":
        return f"/{usv_name}/sensors/radars/ray_radar/scan"

    return ""


def sensor_status_topic(usv_name: str, sensor_name: str) -> str:
    if sensor_name == "camera":
        return f"/{usv_name}/sensors/cameras/front_camera_sensor/camera_info"

    if sensor_name == "sonar":
        return f"/{usv_name}/sensors/sonars/front_sonar_sensor/scan"

    if sensor_name == "ir":
        return f"/{usv_name}/sensors/cameras/ir_camera_sensor/camera_info"

    if sensor_name == "radar":
        return f"/{usv_name}/sensors/radars/ray_radar/scan"

    return ""


def sensor_image_topic(usv_name: str, sensor_name: str) -> str:
    if is_image_sensor(sensor_name):
        return sensor_topic(usv_name, sensor_name)

    return ""


def selected_camera_image_topic() -> str:
    return "/overview/selected_camera/image_raw"


def selected_camera_info_topic() -> str:
    return "/overview/selected_camera/camera_info"


def pose_topic(usv_name: str) -> str:
    return f"/{usv_name}/pose"


def odometry_topic(usv_name: str) -> str:
    return f"/{usv_name}/odometry"


def is_image_sensor(sensor_name: str) -> bool:
    return sensor_name in ["camera", "ir"]


class RosInterface(Node):
    def __init__(self):
        super().__init__("operator_console_node")

        self.declare_parameter("gaze_topic", "/tobii/gaze")
        self.declare_parameter("heatmap_cols", 96)
        self.declare_parameter("heatmap_rows", 54)
        self.declare_parameter("heatmap_half_life_sec", 2.0)
        self.declare_parameter("heatmap_sigma_cells", 2.0)

        self.gaze_topic = str(self.get_parameter("gaze_topic").value)
        self.heatmap_cols = max(2, int(self.get_parameter("heatmap_cols").value))
        self.heatmap_rows = max(2, int(self.get_parameter("heatmap_rows").value))
        self.heatmap_half_life_sec = max(0.1, float(self.get_parameter("heatmap_half_life_sec").value))
        self.heatmap_sigma_cells = max(0.25, float(self.get_parameter("heatmap_sigma_cells").value))

        self.bridge = CvBridge()
        self.sensor_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.current_usv = "wamv_01"
        self.current_sensor = "camera"

        self.image_sub = None
        self.camera_info_sub = None
        self.latest_qimage = None
        self.last_image_time = 0.0
        self.image_min_interval_sec = 1.0 / 30.0

        self.sensor_status_subs = []
        self.last_sensor_seen = {}
        self.sensor_status_initialized = False

        self.speed_subs = []
        self.current_speed = 0.0
        self.speed_online = False
        self.last_speed_time = 0.0
        self.last_speed_sample_wall_time = 0.0
        self.last_pose_time = None
        self.last_pose_wall_time = None
        self.last_pose_xyz = None
        self.last_pose_warn_time = 0.0
        self.pose_fallback_warned = False

        self.online_timeout_sec = 2.0

        self.target_changed_callbacks = []
        self.sensor_changed_callbacks = []
        self.page_changed_callbacks = []
        self.grid_toggle_callbacks = []
        self.overview_metadata_callbacks = []
        self.overview_fleet_callbacks = []
        self.sensor_health_callbacks = []
        self.attention_heatmap_callbacks = []
        self.joy_callbacks = []
        self.voice_callbacks = []
        self.overview_metadata = {}
        self.overview_fleet_state = {}
        self.overview_sensor_health = {}
        self.attention_heatmap = {}
        self.joy_state = {"axes": [], "buttons": [], "stamp": 0.0}
        self.voice_state = {
            "asr_state": "offline",
            "command_state": "offline",
            "last_text": "",
            "last_intent": "",
            "last_error": "",
            "last_transcript_time": 0.0,
            "last_status_time": 0.0,
            "last_command_time": 0.0,
            "mission_state": "offline",
            "mission_detail": "",
            "mission_request_id": "",
        }
        self.heatmap_grid = [0.0 for _ in range(self.heatmap_cols * self.heatmap_rows)]
        self.heatmap_last_decay_time = time.monotonic()
        self.heatmap_total_samples = 0
        self.heatmap_valid_samples = 0
        self.heatmap_window_valid = 0
        self.heatmap_window_started = time.monotonic()
        self.heatmap_recent_valid_hz = 0.0
        self.heatmap_last_gaze = None
        self.heatmap_last_gaze_wall_time = None
        self.heatmap_publish_min_interval_sec = 1.0 / 30.0
        self.heatmap_last_publish_time = 0.0

        self.manual_target_pub = self.create_publisher(
            String,
            "/fleet/manual_target",
            10,
        )

        self.view_target_pub = self.create_publisher(
            String,
            "/ui/view_target",
            10,
        )

        self.target_state_sub = self.create_subscription(
            String,
            "/fleet/manual_target_state",
            self.target_state_callback,
            10,
        )

        self.view_sensor_sub = self.create_subscription(
            String,
            "/ui/view_sensor",
            self.view_sensor_callback,
            10,
        )

        self.view_page_sub = self.create_subscription(
            String,
            "/ui/view_page",
            self.view_page_callback,
            10,
        )

        self.grid_toggle_sub = self.create_subscription(
            String,
            "/ui/toggle_grid",
            self.grid_toggle_callback,
            10,
        )

        self.overview_metadata_sub = self.create_subscription(
            String,
            "/overview/metadata",
            self.overview_metadata_callback,
            10,
        )

        self.overview_fleet_sub = self.create_subscription(
            String,
            "/overview/fleet_state",
            self.overview_fleet_callback,
            self.sensor_qos,
        )

        self.sensor_health_sub = self.create_subscription(
            String,
            "/overview/sensor_health",
            self.sensor_health_callback,
            self.sensor_qos,
        )

        self.joy_sub = self.create_subscription(
            Joy,
            "/joy",
            self.joy_callback,
            10,
        )

        self.voice_transcript_sub = self.create_subscription(
            String,
            "/voice/transcript",
            self.voice_transcript_callback,
            10,
        )

        self.voice_whisper_status_sub = self.create_subscription(
            String,
            "/voice/whisper_status",
            self.voice_whisper_status_callback,
            10,
        )

        self.voice_command_status_sub = self.create_subscription(
            String,
            "/voice/status",
            self.voice_command_status_callback,
            10,
        )

        self.voice_intent_sub = self.create_subscription(
            String,
            "/voice/intent",
            self.voice_intent_callback,
            10,
        )

        self.mission_request_sub = self.create_subscription(
            String,
            "/mission/request",
            self.mission_request_callback,
            10,
        )

        self.mission_status_sub = self.create_subscription(
            String,
            "/mission/status",
            self.mission_status_callback,
            10,
        )

        self.gaze_sub = self.create_subscription(
            String,
            self.gaze_topic,
            self.gaze_callback,
            50,
        )
        self.local_heatmap_timer = self.create_timer(
            self.heatmap_publish_min_interval_sec,
            self.update_local_attention_heatmap,
        )
        self.get_logger().info(
            f"attention heatmap input: {self.gaze_topic} -> console panel"
        )

        self.set_current_usv(self.current_usv, publish_manual=True)

    def set_current_usv(self, usv_name: str, publish_manual: bool = True, notify: bool = True):
        if usv_name not in USV_NAMES:
            self.get_logger().warn(f"Unknown USV selected: {usv_name}")
            return

        changed = usv_name != self.current_usv
        self.current_usv = usv_name
        self.latest_qimage = None

        msg = String()
        msg.data = usv_name

        if publish_manual:
            self.manual_target_pub.publish(msg)

        self.view_target_pub.publish(msg)

        self.subscribe_main_sensor()
        self.subscribe_speed()

        if changed and notify:
            for callback in self.target_changed_callbacks:
                callback(usv_name)

    def set_current_sensor(self, sensor_name: str):
        if sensor_name not in SENSOR_ORDER:
            self.get_logger().warn(f"Unknown sensor selected: {sensor_name}")
            return

        self.current_sensor = sensor_name
        self.latest_qimage = None

        self.subscribe_main_sensor()

        for callback in self.sensor_changed_callbacks:
            callback(sensor_name)

    def add_target_changed_callback(self, callback):
        self.target_changed_callbacks.append(callback)

    def add_sensor_changed_callback(self, callback):
        self.sensor_changed_callbacks.append(callback)

    def add_page_changed_callback(self, callback):
        self.page_changed_callbacks.append(callback)

    def add_grid_toggle_callback(self, callback):
        self.grid_toggle_callbacks.append(callback)

    def add_overview_metadata_callback(self, callback):
        self.overview_metadata_callbacks.append(callback)

    def add_overview_fleet_callback(self, callback):
        self.overview_fleet_callbacks.append(callback)

    def add_sensor_health_callback(self, callback):
        self.sensor_health_callbacks.append(callback)

    def add_attention_heatmap_callback(self, callback):
        self.attention_heatmap_callbacks.append(callback)

    def add_joy_callback(self, callback):
        self.joy_callbacks.append(callback)

    def add_voice_callback(self, callback):
        self.voice_callbacks.append(callback)

    def notify_voice_callbacks(self):
        snapshot = dict(self.voice_state)
        for callback in self.voice_callbacks:
            callback(snapshot)

    def subscribe_main_sensor(self):
        if self.image_sub is not None:
            self.destroy_subscription(self.image_sub)
            self.image_sub = None
        if self.camera_info_sub is not None:
            self.destroy_subscription(self.camera_info_sub)
            self.camera_info_sub = None

        self.latest_qimage = None

        if not is_image_sensor(self.current_sensor):
            topic = sensor_topic(self.current_usv, self.current_sensor)
            self.get_logger().info(f"Switch main sensor to non-image stream: {topic}")
            return

        if self.current_sensor == "camera":
            topic = selected_camera_image_topic()
            info_topic = selected_camera_info_topic()
        else:
            topic = sensor_topic(self.current_usv, self.current_sensor)
            info_topic = sensor_status_topic(self.current_usv, self.current_sensor)

        self.get_logger().info(f"Switch main sensor to: {topic}")

        self.image_sub = self.create_subscription(
            Image,
            topic,
            self.image_callback,
            self.sensor_qos,
        )
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            info_topic,
            lambda msg, u=self.current_usv, s=self.current_sensor: self.sensor_status_callback(u, s),
            self.sensor_qos,
        )

    def now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def subscribe_sensor_status(self):
        if self.sensor_status_initialized:
            return

        for sub in self.sensor_status_subs:
            try:
                self.destroy_subscription(sub)
            except Exception:
                pass

        self.sensor_status_subs = []
        self.last_sensor_seen = {}

        for usv_name in USV_NAMES:
            for sensor_name in SENSOR_ORDER:
                topic = sensor_status_topic(usv_name, sensor_name)

                if not topic:
                    continue

                if sensor_name in ["camera", "ir"]:
                    sub = self.create_subscription(
                        CameraInfo,
                        topic,
                        lambda msg, u=usv_name, s=sensor_name: self.sensor_status_callback(u, s),
                        self.sensor_qos,
                    )
                    self.sensor_status_subs.append(sub)

                elif sensor_name in ["sonar", "radar"]:
                    sub = self.create_subscription(
                        LaserScan,
                        topic,
                        lambda msg, u=usv_name, s=sensor_name: self.sensor_status_callback(u, s),
                        self.sensor_qos,
                    )
                    self.sensor_status_subs.append(sub)

        self.sensor_status_initialized = True

    def sensor_status_callback(self, usv_name: str, sensor_name: str):
        self.last_sensor_seen[(usv_name, sensor_name)] = self.now_sec()

    def is_sensor_online(self, sensor_name: str, usv_name: str = None) -> bool:
        target_usv = usv_name or self.current_usv

        vehicles = self.overview_sensor_health.get("vehicles", {})
        if vehicles:
            sensor_state = vehicles.get(target_usv, {}).get(sensor_name, {})
            return bool(sensor_state.get("online", False))

        last = self.last_sensor_seen.get((target_usv, sensor_name))

        if last is None:
            return False

        return (self.now_sec() - last) <= self.online_timeout_sec

    def sensor_status_snapshot(self):
        vehicles = self.overview_sensor_health.get("vehicles", {})
        if vehicles:
            snapshot = {}
            for usv_name in USV_NAMES:
                vehicle = vehicles.get(usv_name, {})
                snapshot[usv_name] = {
                    sensor_name: bool(vehicle.get(sensor_name, {}).get("online", False))
                    for sensor_name in SENSOR_ORDER
                }
            return snapshot

        return {
            usv_name: {
                sensor_name: self.is_sensor_online(sensor_name, usv_name)
                for sensor_name in SENSOR_ORDER
            }
            for usv_name in USV_NAMES
        }

    def subscribe_speed(self):
        for sub in self.speed_subs:
            try:
                self.destroy_subscription(sub)
            except Exception:
                pass

        self.speed_subs = []
        self.current_speed = 0.0
        self.speed_online = False
        self.last_speed_time = 0.0
        self.last_speed_sample_wall_time = 0.0
        self.last_pose_time = None
        self.last_pose_wall_time = None
        self.last_pose_xyz = None
        self.last_pose_warn_time = 0.0
        self.pose_fallback_warned = False

        odom_topic = odometry_topic(self.current_usv)
        topic = pose_topic(self.current_usv)
        topic_types = dict(self.get_topic_names_and_types())
        msg_types = topic_types.get(topic, [])

        odom_sub = self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            self.sensor_qos,
        )
        self.speed_subs.append(odom_sub)

        if "geometry_msgs/msg/PoseArray" in msg_types:
            sub = self.create_subscription(
                PoseArray,
                topic,
                self.pose_array_callback,
                self.sensor_qos,
            )
            type_name = "geometry_msgs/msg/PoseArray"
        elif "geometry_msgs/msg/PoseStamped" in msg_types:
            sub = self.create_subscription(
                PoseStamped,
                topic,
                self.pose_stamped_callback,
                self.sensor_qos,
            )
            type_name = "geometry_msgs/msg/PoseStamped"
        elif "geometry_msgs/msg/PoseWithCovarianceStamped" in msg_types:
            sub = self.create_subscription(
                PoseWithCovarianceStamped,
                topic,
                self.pose_with_covariance_callback,
                self.sensor_qos,
            )
            type_name = "geometry_msgs/msg/PoseWithCovarianceStamped"
        elif "geometry_msgs/msg/Pose" in msg_types:
            sub = self.create_subscription(
                Pose,
                topic,
                self.pose_callback,
                self.sensor_qos,
            )
            type_name = "geometry_msgs/msg/Pose"
        elif "nav_msgs/msg/Odometry" in msg_types:
            sub = self.create_subscription(
                Odometry,
                topic,
                self.odom_callback,
                self.sensor_qos,
            )
            type_name = "nav_msgs/msg/Odometry"
        else:
            sub = self.create_subscription(
                TFMessage,
                topic,
                self.pose_tf_callback,
                self.sensor_qos,
            )
            type_name = "tf2_msgs/msg/TFMessage"

        self.speed_subs.append(sub)

        if msg_types and type_name not in msg_types:
            self.get_logger().warn(
                f"Unsupported pose topic type(s) {msg_types} on {topic}; "
                "falling back to TFMessage"
            )

        self.get_logger().info(
            f"Speed estimated from {odom_topic}, fallback {topic} [{type_name}]"
        )

    def pose_tf_callback(self, msg: TFMessage):
        if not msg.transforms:
            return

        if not self.should_sample_speed():
            return

        target_tf = self.pick_usv_transform(msg.transforms)
        if target_tf is None:
            target_tf = msg.transforms[0]

            if not self.pose_fallback_warned:
                self.get_logger().warn(
                    f"{pose_topic(self.current_usv)} only contains relative TF frames; "
                    "speed gauge will stay online but may remain 0.00 m/s"
                )
                self.pose_fallback_warned = True

        x = target_tf.transform.translation.x
        y = target_tf.transform.translation.y
        z = target_tf.transform.translation.z
        stamp = self.stamp_to_sec(target_tf.header.stamp)

        self.update_speed_from_position(x, y, z, stamp)

    def pick_usv_transform(self, transforms):
        exact_child_frames = {
            self.current_usv,
            f"{self.current_usv}/wamv",
            f"{self.current_usv}/base_link",
            f"{self.current_usv}/wamv/base_link",
            f"{self.current_usv}/wamv_01/base_link",
            f"{self.current_usv}/wamv_02/base_link",
            f"{self.current_usv}/wamv_03/base_link",
        }

        preferred = []
        fallback = []

        for tf in transforms:
            child = (tf.child_frame_id or "").strip("/")
            frame = (tf.header.frame_id or "").strip("/")

            if self.current_usv not in child and self.current_usv not in frame:
                continue

            if self.is_attachment_frame(child):
                continue

            # Skip static sensor/link mounting transforms such as
            # wamv_01/wamv/base_link -> wamv_01/wamv/base_link/front_camera_sensor.
            if "base_link" in frame and child.startswith(frame + "/"):
                continue

            if child in exact_child_frames:
                preferred.append(tf)
                continue

            if child.endswith("/base_link") or child == "base_link":
                fallback.append(tf)
                continue

            if "base_link" not in frame:
                fallback.append(tf)

        if preferred:
            return preferred[0]
        if fallback:
            return fallback[0]
        return None

    def is_attachment_frame(self, frame_id: str) -> bool:
        attachment_names = [
            "camera",
            "sonar",
            "radar",
            "lidar",
            "sensor",
            "contact",
            "imu",
            "gps",
            "thruster",
            "propeller",
        ]
        return any(name in frame_id for name in attachment_names)

    def stamp_to_sec(self, stamp) -> float:
        sec = float(stamp.sec) + float(stamp.nanosec) / 1e9
        if sec <= 0.0:
            return self.now_sec()
        return sec

    def should_sample_speed(self) -> bool:
        now = self.now_sec()
        if now - self.last_speed_sample_wall_time < 0.05:
            return False

        self.last_speed_sample_wall_time = now
        return True

    def pose_array_callback(self, msg: PoseArray):
        if not msg.poses:
            return

        if not self.should_sample_speed():
            return

        pose = msg.poses[0]
        stamp = self.stamp_to_sec(msg.header.stamp)
        self.update_speed_from_position(
            pose.position.x,
            pose.position.y,
            pose.position.z,
            stamp,
        )

    def pose_stamped_callback(self, msg: PoseStamped):
        if not self.should_sample_speed():
            return

        stamp = self.stamp_to_sec(msg.header.stamp)
        self.update_speed_from_position(
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z,
            stamp,
        )

    def pose_with_covariance_callback(self, msg: PoseWithCovarianceStamped):
        if not self.should_sample_speed():
            return

        stamp = self.stamp_to_sec(msg.header.stamp)
        self.update_speed_from_position(
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
            stamp,
        )

    def pose_callback(self, msg: Pose):
        if not self.should_sample_speed():
            return

        self.update_speed_from_position(
            msg.position.x,
            msg.position.y,
            msg.position.z,
            self.now_sec(),
        )

    def odom_callback(self, msg: Odometry):
        if not self.should_sample_speed():
            return

        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        vz = msg.twist.twist.linear.z
        speed = ((vx * vx + vy * vy + vz * vz) ** 0.5)

        if 0.0 <= speed <= 20.0:
            self.current_speed = speed
            self.speed_online = True
            self.last_speed_time = self.now_sec()
            return

        stamp = self.stamp_to_sec(msg.header.stamp)
        self.update_speed_from_position(
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
            stamp,
        )

    def update_speed_from_position(
        self,
        x: float,
        y: float,
        z: float,
        stamp: float,
    ):
        now = self.now_sec()

        self.speed_online = True
        self.last_speed_time = now

        if self.last_pose_time is not None and self.last_pose_xyz is not None:
            dt = stamp - self.last_pose_time

            if dt <= 1e-4 and self.last_pose_wall_time is not None:
                dt = now - self.last_pose_wall_time

            if dt > 1e-4:
                x0, y0, z0 = self.last_pose_xyz
                dx = x - x0
                dy = y - y0
                dz = z - z0

                speed = ((dx * dx + dy * dy + dz * dz) ** 0.5) / dt

                # 避免首次订阅、仿真跳帧或切换 WAM-V 时速度瞬间乱跳
                if 0.0 <= speed <= 20.0:
                    self.current_speed = speed

        self.last_pose_time = stamp
        self.last_pose_wall_time = now
        self.last_pose_xyz = (x, y, z)

    def is_speed_online(self) -> bool:
        if self.current_fleet_vehicle() is not None:
            return True

        if not self.speed_online:
            return False

        return (self.now_sec() - self.last_speed_time) <= self.online_timeout_sec

    def current_fleet_vehicle(self):
        fleet_state = self.overview_fleet_state or {}
        for vehicle in fleet_state.get("vehicles", []):
            if vehicle.get("name") == self.current_usv:
                return vehicle
        return None

    def current_display_speed(self) -> float:
        vehicle = self.current_fleet_vehicle()
        if vehicle is not None:
            try:
                return float(vehicle.get("speed", 0.0))
            except (TypeError, ValueError):
                return 0.0

        return self.current_speed

    def target_state_callback(self, msg: String):
        usv_name = msg.data

        if usv_name not in USV_NAMES:
            return

        if usv_name == self.current_usv:
            return

        self.set_current_usv(usv_name, publish_manual=False, notify=True)

    def view_sensor_callback(self, msg: String):
        self.set_current_sensor(msg.data)

    def view_page_callback(self, msg: String):
        page_name = msg.data.strip().lower()

        for callback in self.page_changed_callbacks:
            callback(page_name)

    def grid_toggle_callback(self, msg: String):
        for callback in self.grid_toggle_callbacks:
            callback()

    def joy_callback(self, msg: Joy):
        self.joy_state = {
            "axes": [float(value) for value in msg.axes],
            "buttons": [int(value) for value in msg.buttons],
            "stamp": time.time(),
        }

        for callback in self.joy_callbacks:
            callback(self.joy_state)

    def decode_json_payload(self, payload: str):
        text = payload.strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"text": text}

    def voice_transcript_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        if payload.get("type") == "cancel":
            now = time.time()
            self.voice_state.update(
                {
                    "asr_state": "cancelled",
                    "last_text": "",
                    "last_intent": "",
                    "last_error": "",
                    "last_transcript_time": 0.0,
                    "last_status_time": now,
                }
            )
            self.notify_voice_callbacks()
            return

        text = str(payload.get("text") or payload.get("transcript") or "").strip()
        if not text:
            return

        now = time.time()
        self.voice_state.update(
            {
                "asr_state": "transcribed",
                "last_text": text,
                "last_error": "",
                "last_transcript_time": now,
                "last_status_time": now,
                "model": payload.get("model", self.voice_state.get("model", "")),
                "rms": payload.get("rms"),
                "latency_sec": payload.get("latency_sec"),
            }
        )
        self.notify_voice_callbacks()

    def voice_whisper_status_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        now = time.time()
        state = str(payload.get("state") or payload.get("type") or "status")

        updates = {
            "asr_state": state,
            "last_status_time": now,
            "model": payload.get("model", self.voice_state.get("model", "")),
        }
        if payload.get("type") == "error" or "error" in payload:
            updates["last_error"] = str(payload.get("error") or payload.get("message") or "")
        elif state in [
            "ready",
            "running",
            "transcribed",
            "vad",
            "audio_ready",
            "transcribing",
            "no_text",
            "ptt_waiting",
            "ptt_listening",
            "ptt_stopped",
            "cancelled",
        ]:
            updates["last_error"] = ""
        if payload.get("type") == "vad" or "rms" in payload:
            updates["rms"] = payload.get("rms")
        if "audio_sec" in payload or "duration_sec" in payload:
            updates["audio_sec"] = payload.get("audio_sec", payload.get("duration_sec"))
        if "latency_sec" in payload:
            updates["latency_sec"] = payload.get("latency_sec")

        self.voice_state.update(updates)
        self.notify_voice_callbacks()

    def voice_command_status_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        now = time.time()
        self.voice_state.update(
            {
                "command_state": str(payload.get("state") or "ready"),
                "last_command_time": now,
                "last_command_text": payload.get("last_transcript", self.voice_state.get("last_command_text", "")),
            }
        )
        self.notify_voice_callbacks()

    def voice_intent_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        now = time.time()
        actions = payload.get("actions")
        if isinstance(actions, list) and actions:
            labels = []
            for action in actions[:3]:
                if not isinstance(action, dict):
                    continue
                action_type = str(action.get("type") or "").strip()
                target = str(action.get("target") or "").strip()
                page = str(action.get("page") or "").strip()
                sensor = str(action.get("sensor") or "").strip()
                detail = target or page or sensor
                labels.append(f"{action_type}:{detail}" if detail else action_type)
            intent_text = " ".join(label for label in labels if label)
        else:
            intent_type = str(payload.get("type") or payload.get("intent") or "").strip()
            target = str(payload.get("target") or payload.get("usv") or "").strip()
            intent_text = f"{intent_type} {target}".strip() if target else intent_type
        if not intent_text:
            intent_text = msg.data.strip()

        self.voice_state.update(
            {
                "command_state": "intent",
                "last_intent": intent_text,
                "last_command_time": now,
            }
        )
        self.notify_voice_callbacks()

    def mission_request_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        goal = payload.get("goal")
        if not isinstance(goal, dict):
            goal = {}
        vehicle = str(payload.get("vehicle") or "").strip()
        cell = str(goal.get("cell") or "").strip()
        detail = " → ".join(value for value in [vehicle, cell] if value)
        self.voice_state.update(
            {
                "mission_state": "requested",
                "mission_detail": detail,
                "mission_request_id": str(payload.get("request_id") or ""),
                "last_command_time": time.time(),
            }
        )
        self.notify_voice_callbacks()

    def mission_status_callback(self, msg: String):
        payload = self.decode_json_payload(msg.data)
        state = str(payload.get("state") or "status").strip()
        vehicle = str(payload.get("vehicle") or "").strip()
        reason = str(
            payload.get("reason_code") or payload.get("detail") or ""
        ).strip()
        current_detail = str(
            self.voice_state.get("mission_detail") or ""
        ).strip()
        if vehicle and vehicle not in current_detail:
            current_detail = vehicle
        if reason:
            current_detail = f"{current_detail} · {reason}".strip(" ·")
        self.voice_state.update(
            {
                "mission_state": state,
                "mission_detail": current_detail,
                "mission_request_id": str(
                    payload.get("request_id")
                    or self.voice_state.get("mission_request_id")
                    or ""
                ),
                "last_command_time": time.time(),
            }
        )
        self.notify_voice_callbacks()

    def overview_metadata_callback(self, msg: String):
        try:
            metadata = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f"Invalid overview metadata: {exc}")
            return

        self.overview_metadata = metadata

        for callback in self.overview_metadata_callbacks:
            callback(metadata)

    def overview_fleet_callback(self, msg: String):
        try:
            fleet_state = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f"Invalid overview fleet state: {exc}")
            return

        self.overview_fleet_state = fleet_state

        for callback in self.overview_fleet_callbacks:
            callback(fleet_state)

    def sensor_health_callback(self, msg: String):
        try:
            sensor_health = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f"Invalid sensor health: {exc}")
            return

        self.overview_sensor_health = sensor_health

        for callback in self.sensor_health_callbacks:
            callback(sensor_health)

    def set_attention_heatmap(self, heatmap: dict):
        self.attention_heatmap = heatmap

        for callback in self.attention_heatmap_callbacks:
            callback(heatmap)

    def gaze_callback(self, msg: String):
        self.heatmap_total_samples += 1

        try:
            gaze = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f"Invalid Tobii gaze JSON: {exc}")
            return

        if not bool(gaze.get("valid", False)):
            return

        x_norm = self.safe_float(gaze.get("x_norm"))
        y_norm = self.safe_float(gaze.get("y_norm"))

        if not self.is_unit_value(x_norm) or not self.is_unit_value(y_norm):
            return

        self.heatmap_valid_samples += 1
        self.heatmap_window_valid += 1
        now = time.monotonic()
        self.decay_local_heatmap(now)
        self.add_local_heatmap_sample(x_norm, y_norm)

        wall_time = time.time()
        self.heatmap_last_gaze_wall_time = wall_time
        self.heatmap_last_gaze = {
            "x_norm": x_norm,
            "y_norm": y_norm,
            "x_px": self.safe_float(gaze.get("x_px")),
            "y_px": self.safe_float(gaze.get("y_px")),
            "recv_time": self.safe_float(gaze.get("stamp"), wall_time),
            "latency_sec": self.safe_optional_float(gaze.get("latency_sec")),
        }

        if now - self.heatmap_last_publish_time >= self.heatmap_publish_min_interval_sec:
            self.update_local_attention_heatmap(now=now)

    def safe_float(self, value, default=math.nan):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def safe_optional_float(self, value):
        parsed = self.safe_float(value)
        return parsed if math.isfinite(parsed) else None

    def is_unit_value(self, value: float) -> bool:
        return math.isfinite(value) and 0.0 <= value <= 1.0

    def decay_local_heatmap(self, now: float):
        dt = max(0.0, now - self.heatmap_last_decay_time)
        if dt <= 0.0:
            return

        decay = math.pow(0.5, dt / self.heatmap_half_life_sec)
        if decay < 0.999999:
            self.heatmap_grid = [value * decay for value in self.heatmap_grid]

        self.heatmap_last_decay_time = now

    def add_local_heatmap_sample(self, x_norm: float, y_norm: float):
        cx = x_norm * (self.heatmap_cols - 1)
        cy = y_norm * (self.heatmap_rows - 1)
        sigma = self.heatmap_sigma_cells
        radius = max(1, int(math.ceil(sigma * 3.0)))
        x0 = max(0, int(math.floor(cx)) - radius)
        x1 = min(self.heatmap_cols - 1, int(math.floor(cx)) + radius)
        y0 = max(0, int(math.floor(cy)) - radius)
        y1 = min(self.heatmap_rows - 1, int(math.floor(cy)) + radius)
        two_sigma_sq = 2.0 * sigma * sigma

        for row in range(y0, y1 + 1):
            dy = row - cy
            for col in range(x0, x1 + 1):
                dx = col - cx
                weight = math.exp(-(dx * dx + dy * dy) / two_sigma_sq)
                self.heatmap_grid[row * self.heatmap_cols + col] += weight

    def update_local_attention_heatmap(self, now=None):
        if now is None:
            now = time.monotonic()
        self.decay_local_heatmap(now)
        self.update_local_heatmap_rate(now)
        self.heatmap_last_publish_time = now

        max_value = max(self.heatmap_grid) if self.heatmap_grid else 0.0
        if max_value > 1e-9:
            cells = [round(value / max_value, 4) for value in self.heatmap_grid]
        else:
            cells = [0.0 for _ in self.heatmap_grid]

        last_gaze = None
        if self.heatmap_last_gaze is not None:
            last_gaze = dict(self.heatmap_last_gaze)
            if self.heatmap_last_gaze_wall_time is not None:
                last_gaze["age_sec"] = max(0.0, time.time() - self.heatmap_last_gaze_wall_time)

        self.set_attention_heatmap(
            {
                "stamp": time.time(),
                "source_topic": self.gaze_topic,
                "coordinate_frame": "unity_window_normalized",
                "origin": "top-left",
                "cols": self.heatmap_cols,
                "rows": self.heatmap_rows,
                "cells": cells,
                "max_value": max_value,
                "total_samples": self.heatmap_total_samples,
                "valid_samples": self.heatmap_valid_samples,
                "recent_valid_hz": self.heatmap_recent_valid_hz,
                "last_gaze": last_gaze,
            }
        )

    def update_local_heatmap_rate(self, now: float):
        dt = now - self.heatmap_window_started
        if dt < 1.0:
            return

        self.heatmap_recent_valid_hz = self.heatmap_window_valid / dt
        self.heatmap_window_valid = 0
        self.heatmap_window_started = now

    def image_callback(self, msg: Image):
        now = self.now_sec()
        if now - self.last_image_time < self.image_min_interval_sec:
            return
        self.last_image_time = now

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, ch = frame.shape
            max_w = 1280
            max_h = 720
            scale = min(max_w / w, max_h / h, 1.0)

            if scale < 1.0:
                frame = cv2.resize(
                    frame,
                    (max(1, int(w * scale)), max(1, int(h * scale))),
                    interpolation=cv2.INTER_AREA,
                )
                h, w, ch = frame.shape

            bytes_per_line = ch * w

            qimg = QImage(
                frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888,
            ).copy()

            self.latest_qimage = qimg

        except Exception as e:
            self.get_logger().warn(f"Image conversion failed: {e}")


class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = None
        self.placeholder_text = "等待摄像头视频流"

        self.setMinimumSize(800, 450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet(
            """
            QWidget {
                background-color: black;
                border: 1px solid #555555;
            }
            """
        )

    def sizeHint(self):
        return QSize(900, 520)

    def set_placeholder_text(self, text: str):
        self.placeholder_text = text
        self.update()

    def set_image(self, qimage: QImage):
        self.image = qimage
        self.update()

    def clear_image(self):
        self.image = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if self.image is None:
            painter.setPen(Qt.white)
            font = QFont()
            font.setPointSize(20)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.placeholder_text)
            return

        scaled = self.image.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation,
        )

        x = int((self.width() - scaled.width()) / 2)
        y = int((self.height() - scaled.height()) / 2)

        painter.drawImage(x, y, scaled)


class SpeedGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.speed = 0.0
        self.max_speed = 10.0
        self.offline = True

        self.setFixedHeight(165)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_speed(self, speed: float):
        self.speed = max(0.0, min(speed, self.max_speed))
        self.offline = False
        self.update()

    def set_offline(self):
        self.offline = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        painter.fillRect(self.rect(), Qt.black)

        rect = QRectF(25, 25, w - 50, h * 1.55)

        pen_bg = QPen(Qt.darkGray, 14)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0 * 16, 180 * 16)

        if not self.offline:
            ratio = self.speed / self.max_speed
            angle = int(180 * ratio)
            pen_fg = QPen(Qt.white, 14)
            painter.setPen(pen_fg)
            painter.drawArc(rect, 180 * 16, -angle * 16)

        painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)

        if self.offline:
            text = "SPEED\nOFFLINE"
        else:
            text = f"{self.speed:.2f}\nm/s"

        painter.drawText(self.rect(), Qt.AlignCenter, text)


def make_panel(title: str, subtitle: str = "", min_height: int = 120, fixed_height=None):
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setStyleSheet(
        """
        QFrame {
            background-color: #08131e;
            border: 1px solid #263f55;
            border-radius: 4px;
        }
        QLabel {
            color: #e7f2fb;
        }
        """
    )

    if fixed_height is not None:
        frame.setFixedHeight(fixed_height)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    else:
        frame.setMinimumHeight(min_height)

    layout = QVBoxLayout(frame)

    title_label = QLabel(title)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setAlignment(Qt.AlignCenter)
    subtitle_label.setStyleSheet("font-size: 12px; color: #8fa9bd;")

    layout.addStretch()
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    layout.addStretch()

    return frame


class HeatmapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.heatmap = {}
        self.setMinimumHeight(142)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_heatmap(self, heatmap: dict):
        self.heatmap = heatmap or {}
        self.update()

    def screen_aspect_ratio(self) -> float:
        screen = self.screen()
        if screen is None and QApplication.instance() is not None:
            screen = QApplication.primaryScreen()

        if screen is None:
            return 16.0 / 9.0

        geometry = screen.geometry()
        if geometry.height() <= 0:
            return 16.0 / 9.0

        return max(0.5, min(4.0, geometry.width() / geometry.height()))

    def plot_rect_for_view(self) -> QRectF:
        inner = QRectF(self.rect()).adjusted(8, 6, -8, -6)
        if inner.width() <= 1.0 or inner.height() <= 1.0:
            return inner

        target_aspect = self.screen_aspect_ratio()
        inner_aspect = inner.width() / inner.height()

        if inner_aspect > target_aspect:
            width = inner.height() * target_aspect
            return QRectF(
                inner.left() + (inner.width() - width) / 2.0,
                inner.top(),
                width,
                inner.height(),
            )

        height = inner.width() / target_aspect
        return QRectF(
            inner.left(),
            inner.top() + (inner.height() - height) / 2.0,
            inner.width(),
            height,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(5, 12, 20))

        cells = self.heatmap.get("cells") or []
        cols = int(self.heatmap.get("cols", 0) or 0)
        rows = int(self.heatmap.get("rows", 0) or 0)

        plot_rect = self.plot_rect_for_view()
        painter.setPen(QPen(QColor(48, 76, 98), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(plot_rect)

        if cols <= 0 or rows <= 0 or len(cells) != cols * rows:
            painter.setPen(QColor(120, 146, 165))
            painter.drawText(plot_rect, Qt.AlignCenter, "WAITING")
            return

        image = QImage(cols, rows, QImage.Format_ARGB32_Premultiplied)
        image.fill(QColor(0, 0, 0, 0))
        for row in range(rows):
            for col in range(cols):
                value = float(cells[row * cols + col])
                if value <= 0.002:
                    continue

                image.setPixelColor(col, row, self.heat_color(value))

        scaled = image.scaled(
            max(1, int(plot_rect.width())),
            max(1, int(plot_rect.height())),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )
        painter.drawImage(plot_rect, scaled)

        last_gaze = self.heatmap.get("last_gaze") or {}
        x_norm = last_gaze.get("x_norm")
        y_norm = last_gaze.get("y_norm")
        age_sec = float(last_gaze.get("age_sec", 999.0) or 999.0)

        if isinstance(x_norm, (int, float)) and isinstance(y_norm, (int, float)) and age_sec <= 2.5:
            x = plot_rect.left() + float(x_norm) * plot_rect.width()
            y = plot_rect.top() + float(y_norm) * plot_rect.height()
            painter.setPen(QPen(QColor(245, 250, 255, 225), 1))
            painter.drawLine(int(x - 7), int(y), int(x + 7), int(y))
            painter.drawLine(int(x), int(y - 7), int(x), int(y + 7))
            painter.setBrush(QBrush(QColor(255, 255, 255, 55)))
            painter.drawEllipse(QPointF(x, y), 5.0, 5.0)

        painter.setPen(QPen(QColor(88, 120, 145, 135), 1))
        for i in range(1, 4):
            x = plot_rect.left() + plot_rect.width() * i / 4.0
            painter.drawLine(int(x), int(plot_rect.top()), int(x), int(plot_rect.bottom()))
        for i in range(1, 3):
            y = plot_rect.top() + plot_rect.height() * i / 3.0
            painter.drawLine(int(plot_rect.left()), int(y), int(plot_rect.right()), int(y))

    def heat_color(self, value: float):
        value = max(0.0, min(1.0, value))

        if value < 0.45:
            t = value / 0.45
            return QColor(
                int(35 + 35 * t),
                int(155 + 55 * t),
                int(230 - 80 * t),
                int(35 + 95 * t),
            )

        if value < 0.75:
            t = (value - 0.45) / 0.30
            return QColor(
                int(70 + 185 * t),
                int(210 + 35 * t),
                int(150 - 95 * t),
                int(130 + 65 * t),
            )

        t = (value - 0.75) / 0.25
        return QColor(
            255,
            int(245 - 95 * t),
            int(55 - 35 * t),
            int(195 + 45 * t),
        )


class AttentionHeatmapPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #e7f2fb;
                border: 0;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(5)

        self.title = QLabel("注意力热力图")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFixedHeight(20)
        self.title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")

        self.canvas = HeatmapCanvas()

        self.status = QLabel("WAITING  /tobii/gaze")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedHeight(18)
        self.status.setStyleSheet("font-size: 11px; color: #8fa9bd;")

        layout.addWidget(self.title)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(self.status)

    def set_heatmap(self, heatmap: dict):
        self.canvas.set_heatmap(heatmap)

        source_topic = str(heatmap.get("source_topic", "/tobii/gaze"))
        total_samples = int(heatmap.get("total_samples", 0) or 0)
        valid_samples = int(heatmap.get("valid_samples", 0) or 0)
        hz = float(heatmap.get("recent_valid_hz", 0.0) or 0.0)
        last_gaze = heatmap.get("last_gaze") or {}

        if valid_samples <= 0 or not last_gaze:
            if total_samples > 0:
                self.status.setText(f"NO VALID GAZE  {source_topic}  total={total_samples}")
                self.status.setStyleSheet("font-size: 11px; color: #e0aa4c;")
                return

            self.status.setText(f"WAITING  {source_topic}")
            self.status.setStyleSheet("font-size: 11px; color: #8fa9bd;")
            return

        x_norm = float(last_gaze.get("x_norm", 0.0) or 0.0)
        y_norm = float(last_gaze.get("y_norm", 0.0) or 0.0)
        self.status.setText(f"{hz:.1f}Hz  gaze=({x_norm:.2f}, {y_norm:.2f})  samples={valid_samples}")
        self.status.setStyleSheet("font-size: 11px; color: #45df91;")


class GamepadCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.joy_state = {"axes": [], "buttons": [], "stamp": 0.0}
        self.setMinimumHeight(204)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_joy_state(self, joy_state: dict):
        self.joy_state = joy_state or {"axes": [], "buttons": [], "stamp": 0.0}
        self.update()

    def axis(self, index: int, default: float = 0.0) -> float:
        axes = self.joy_state.get("axes", [])
        if 0 <= index < len(axes):
            return max(-1.0, min(1.0, float(axes[index])))
        return default

    def button(self, index: int) -> bool:
        buttons = self.joy_state.get("buttons", [])
        return 0 <= index < len(buttons) and int(buttons[index]) != 0

    def trigger_value(self, axis_index: int) -> float:
        raw = self.axis(axis_index, 1.0)
        return max(0.0, min(1.0, (1.0 - raw) / 2.0))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(5, 12, 20))

        bounds = QRectF(self.rect()).adjusted(8, 4, -8, -5)
        if bounds.width() <= 20 or bounds.height() <= 20:
            return

        trigger_w = 92
        trigger_h = 16
        shoulder_w = 74
        shoulder_h = 17
        top = bounds.top()
        self.draw_trigger(
            painter,
            QRectF(bounds.left() + 26, top, trigger_w, trigger_h),
            "LT",
            self.trigger_value(2),
        )
        self.draw_trigger(
            painter,
            QRectF(bounds.right() - 26 - trigger_w, top, trigger_w, trigger_h),
            "RT",
            self.trigger_value(5),
        )
        self.draw_shoulder(
            painter,
            QRectF(bounds.left() + 44, top + 20, shoulder_w, shoulder_h),
            "LB",
            self.button(4),
        )
        self.draw_shoulder(
            painter,
            QRectF(bounds.right() - 44 - shoulder_w, top + 20, shoulder_w, shoulder_h),
            "RB",
            self.button(5),
        )

        body_rect = QRectF(
            bounds.left() + 2,
            bounds.top() + 38,
            bounds.width() - 4,
            bounds.height() - 39,
        )

        body = self.body_path(body_rect)
        body_gradient = QLinearGradient(body_rect.topLeft(), body_rect.bottomLeft())
        body_gradient.setColorAt(0.0, QColor(45, 49, 54))
        body_gradient.setColorAt(0.56, QColor(21, 24, 28))
        body_gradient.setColorAt(1.0, QColor(10, 12, 15))
        painter.setBrush(QBrush(body_gradient))
        painter.setPen(QPen(QColor(79, 91, 103), 1))
        painter.drawPath(body)
        self.draw_body_details(painter, body_rect)

        self.draw_home(painter, QPointF(body_rect.center().x(), body_rect.top() + body_rect.height() * 0.18))
        self.draw_small_button(painter, QPointF(body_rect.center().x() - 34, body_rect.top() + body_rect.height() * 0.36), self.button(6))
        self.draw_small_button(painter, QPointF(body_rect.center().x() + 34, body_rect.top() + body_rect.height() * 0.36), self.button(7))

        left_stick = QPointF(body_rect.left() + body_rect.width() * 0.22, body_rect.top() + body_rect.height() * 0.32)
        right_stick = QPointF(body_rect.left() + body_rect.width() * 0.62, body_rect.top() + body_rect.height() * 0.66)
        self.draw_stick(painter, left_stick, -self.axis(0), -self.axis(1))
        self.draw_stick(painter, right_stick, -self.axis(3), -self.axis(4))

        dpad_center = QPointF(body_rect.left() + body_rect.width() * 0.34, body_rect.top() + body_rect.height() * 0.69)
        self.draw_dpad(painter, dpad_center)

        buttons_center = QPointF(body_rect.left() + body_rect.width() * 0.80, body_rect.top() + body_rect.height() * 0.37)
        self.draw_face_buttons(painter, buttons_center)

    def body_path(self, rect: QRectF) -> QPainterPath:
        path = QPainterPath()
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()
        w = rect.width()
        h = rect.height()

        path.moveTo(left + w * 0.16, top + h * 0.08)
        path.cubicTo(left + w * 0.05, top + h * 0.10, left + w * 0.02, top + h * 0.34, left + w * 0.06, top + h * 0.70)
        path.cubicTo(left + w * 0.08, bottom + h * 0.08, left + w * 0.28, bottom, left + w * 0.39, bottom - h * 0.12)
        path.lineTo(left + w * 0.61, bottom - h * 0.12)
        path.cubicTo(left + w * 0.72, bottom, left + w * 0.92, bottom + h * 0.08, right - w * 0.06, top + h * 0.70)
        path.cubicTo(right - w * 0.02, top + h * 0.34, right - w * 0.05, top + h * 0.10, right - w * 0.16, top + h * 0.08)
        path.cubicTo(left + w * 0.69, top, left + w * 0.31, top, left + w * 0.16, top + h * 0.08)
        path.closeSubpath()
        return path

    def draw_body_details(self, painter: QPainter, rect: QRectF):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(110, 122, 132, 48), 1))
        painter.drawArc(
            int(rect.left() + rect.width() * 0.31),
            int(rect.top() + rect.height() * 0.72),
            int(rect.width() * 0.38),
            int(rect.height() * 0.30),
            0,
            180 * 16,
        )

        painter.setPen(QPen(QColor(210, 220, 228, 70), 2))
        cx = rect.center().x()
        y0 = rect.top() + rect.height() * 0.50
        for i in range(4):
            painter.drawPoint(QPointF(cx, y0 + i * 9))

    def draw_shoulder(self, painter: QPainter, rect: QRectF, label: str, active: bool):
        shadow = QRectF(rect).translated(0, 2)
        painter.setBrush(QBrush(QColor(0, 0, 0, 105)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow, 7, 7)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        if active:
            gradient.setColorAt(0.0, QColor(122, 210, 255, 235))
            gradient.setColorAt(1.0, QColor(28, 98, 158, 230))
        else:
            gradient.setColorAt(0.0, QColor(62, 70, 78, 235))
            gradient.setColorAt(1.0, QColor(19, 23, 28, 235))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(126, 147, 160, 150), 1))
        painter.drawRoundedRect(rect, 7, 7)
        painter.setPen(QPen(QColor(255, 255, 255, 38), 1))
        painter.drawLine(int(rect.left() + 8), int(rect.top() + 3), int(rect.right() - 8), int(rect.top() + 3))
        painter.setPen(QColor(230, 242, 250, 230))
        painter.drawText(rect, Qt.AlignCenter, label)

    def draw_trigger(self, painter: QPainter, rect: QRectF, label: str, value: float):
        shadow = QRectF(rect).translated(0, 2)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow, 6, 6)

        base = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        base.setColorAt(0.0, QColor(58, 66, 74, 235))
        base.setColorAt(1.0, QColor(12, 15, 20, 235))
        painter.setBrush(QBrush(base))
        painter.setPen(QPen(QColor(94, 112, 126, 150), 1))
        painter.drawRoundedRect(rect, 6, 6)

        if value > 0.02:
            fill = QRectF(rect)
            fill.setWidth(rect.width() * value)
            fill_gradient = QLinearGradient(fill.topLeft(), fill.bottomLeft())
            fill_gradient.setColorAt(0.0, QColor(128, 220, 255, 205))
            fill_gradient.setColorAt(1.0, QColor(30, 105, 170, 205))
            painter.setBrush(QBrush(fill_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill, 6, 6)

        painter.setPen(QPen(QColor(255, 255, 255, 36), 1))
        painter.drawLine(int(rect.left() + 8), int(rect.top() + 3), int(rect.right() - 8), int(rect.top() + 3))
        painter.setPen(QColor(230, 242, 250, 230))
        painter.drawText(rect, Qt.AlignCenter, label)

    def draw_home(self, painter: QPainter, center: QPointF):
        painter.setBrush(QBrush(QColor(230, 236, 241, 210)))
        painter.setPen(QPen(QColor(24, 30, 36), 2))
        painter.drawEllipse(center, 12, 12)
        painter.setPen(QPen(QColor(42, 50, 58), 2))
        painter.drawLine(int(center.x() - 5), int(center.y() - 5), int(center.x() + 5), int(center.y() + 5))
        painter.drawLine(int(center.x() + 5), int(center.y() - 5), int(center.x() - 5), int(center.y() + 5))

    def draw_small_button(self, painter: QPainter, center: QPointF, active: bool):
        painter.setBrush(QBrush(QColor(0, 0, 0, 95)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center + QPointF(0, 2), 10, 10)

        gradient = QRadialGradient(center - QPointF(3, 4), 16)
        if active:
            gradient.setColorAt(0.0, QColor(132, 204, 255, 235))
            gradient.setColorAt(1.0, QColor(32, 88, 132, 235))
        else:
            gradient.setColorAt(0.0, QColor(78, 88, 96, 235))
            gradient.setColorAt(1.0, QColor(17, 20, 24, 235))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(95, 112, 126, 150), 1))
        painter.drawEllipse(center, 9, 9)

    def draw_stick(self, painter: QPainter, center: QPointF, x_axis: float, y_axis: float):
        base_radius = 25
        knob_radius = 15
        offset = QPointF(x_axis * 9.0, y_axis * 9.0)

        gradient = QRadialGradient(center, base_radius)
        gradient.setColorAt(0.0, QColor(42, 46, 51))
        gradient.setColorAt(1.0, QColor(8, 10, 13))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(95, 105, 112, 135), 1))
        painter.drawEllipse(center, base_radius, base_radius)

        knob_center = center + offset
        painter.setBrush(QBrush(QColor(22, 24, 27)))
        painter.setPen(QPen(QColor(116, 126, 132, 150), 1))
        painter.drawEllipse(knob_center, knob_radius, knob_radius)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(150, 164, 171, 80), 1))
        painter.drawEllipse(knob_center, knob_radius - 5, knob_radius - 5)

    def draw_dpad(self, painter: QPainter, center: QPointF):
        x = self.axis(6)
        y = self.axis(7)
        active_left = x > 0.5
        active_right = x < -0.5
        active_up = y > 0.5
        active_down = y < -0.5

        size = 20
        thickness = 13
        rects = [
            (QRectF(center.x() - size - thickness / 2, center.y() - thickness / 2, size, thickness), active_left),
            (QRectF(center.x() + thickness / 2, center.y() - thickness / 2, size, thickness), active_right),
            (QRectF(center.x() - thickness / 2, center.y() - size - thickness / 2, thickness, size), active_up),
            (QRectF(center.x() - thickness / 2, center.y() + thickness / 2, thickness, size), active_down),
            (QRectF(center.x() - thickness / 2, center.y() - thickness / 2, thickness, thickness), False),
        ]

        for rect, active in rects:
            painter.setBrush(QBrush(QColor(82, 180, 255, 210) if active else QColor(18, 21, 25, 232)))
            painter.setPen(QPen(QColor(95, 105, 112, 145), 1))
            painter.drawRoundedRect(rect, 3, 3)

    def draw_face_buttons(self, painter: QPainter, center: QPointF):
        buttons = [
            ("Y", 3, QPointF(0, -27), QColor(196, 238, 52)),
            ("B", 1, QPointF(27, 0), QColor(255, 84, 92)),
            ("A", 0, QPointF(0, 27), QColor(73, 238, 92)),
            ("X", 2, QPointF(-27, 0), QColor(45, 222, 236)),
        ]

        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)

        for label, index, offset, accent in buttons:
            active = self.button(index)
            pos = center + offset
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos + QPointF(0, 3), 16, 16)

            gradient = QRadialGradient(pos - QPointF(5, 6), 26)
            if active:
                gradient.setColorAt(0.0, QColor(255, 255, 255, 225))
                gradient.setColorAt(0.38, QColor(accent.red(), accent.green(), accent.blue(), 235))
                gradient.setColorAt(1.0, QColor(max(0, accent.red() - 80), max(0, accent.green() - 80), max(0, accent.blue() - 80), 235))
            else:
                gradient.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 128))
                gradient.setColorAt(1.0, QColor(18, 22, 27, 235))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(130, 143, 153, 155), 1))
            painter.drawEllipse(pos, 16, 16)
            painter.setPen(QPen(QColor(255, 255, 255, 70), 1))
            painter.drawArc(int(pos.x() - 10), int(pos.y() - 11), 16, 12, 30 * 16, 120 * 16)
            painter.setPen(QColor(accent.red(), accent.green(), accent.blue(), 245))
            painter.drawText(QRectF(pos.x() - 16, pos.y() - 16, 32, 32), Qt.AlignCenter, label)


class GamepadProjectionPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(258)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #e7f2fb;
                border: 0;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(4)

        title = QLabel("手柄虚拟投影")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(20)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")

        self.canvas = GamepadCanvas()
        self.status = QLabel("WAITING  /joy")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFixedHeight(16)
        self.status.setStyleSheet("font-size: 11px; color: #8fa9bd;")

        layout.addWidget(title)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(self.status)

    def set_joy_state(self, joy_state: dict):
        self.canvas.set_joy_state(joy_state)
        age = max(0.0, time.time() - float(joy_state.get("stamp", 0.0) or 0.0))
        axes = len(joy_state.get("axes", []))
        buttons = len(joy_state.get("buttons", []))
        if axes <= 0 and buttons <= 0:
            self.status.setText("WAITING  /joy")
            self.status.setStyleSheet("font-size: 11px; color: #8fa9bd;")
            return

        self.status.setText(f"/joy  axes={axes} buttons={buttons} age={age:.1f}s")
        self.status.setStyleSheet("font-size: 11px; color: #45df91;")


class SensorStatusPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(115)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #e7f2fb;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self.title_label = QLabel("传感器")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: bold;")

        self.topic_label = QLabel("")
        self.topic_label.setAlignment(Qt.AlignCenter)
        self.topic_label.setStyleSheet("font-size: 10px; color: #8fa9bd;")

        self.status_label = QLabel("● OFFLINE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 13px; color: #cc3333; font-weight: bold;"
        )
        self.sensor_name = None
        self.usv_name = None
        self.online = None

        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addWidget(self.topic_label)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def set_sensor(self, usv_name: str, sensor_name: str):
        if self.usv_name == usv_name and self.sensor_name == sensor_name:
            return

        label = SENSOR_LABELS.get(sensor_name, sensor_name)
        topic = sensor_topic(usv_name, sensor_name)

        self.usv_name = usv_name
        self.sensor_name = sensor_name
        self.title_label.setText(label)
        self.topic_label.setText(topic)
        self.online = None

    def set_online_state(self, online: bool):
        if self.online == online:
            return

        self.online = online

        if online:
            self.status_label.setText("● ONLINE")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #33cc66; font-weight: bold;"
            )
        else:
            self.status_label.setText("● OFFLINE")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #cc3333; font-weight: bold;"
            )


class SensorIconStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.statuses = {sensor_name: False for sensor_name in SENSOR_ORDER}
        self.setFixedHeight(32)
        self.setMinimumWidth(156)

    def set_statuses(self, statuses: dict):
        changed = False

        for sensor_name in SENSOR_ORDER:
            value = bool(statuses.get(sensor_name, False))
            if self.statuses.get(sensor_name) != value:
                self.statuses[sensor_name] = value
                changed = True

        if changed:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        slot_w = max(34, self.width() // len(SENSOR_ORDER))
        center_y = self.height() / 2.0

        for index, sensor_name in enumerate(SENSOR_ORDER):
            center_x = index * slot_w + slot_w / 2.0
            online = self.statuses.get(sensor_name, False)
            color = QColor(72, 225, 146) if online else QColor(225, 74, 82)
            bg = QColor(color.red(), color.green(), color.blue(), 42)

            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 125), 1))
            painter.drawRoundedRect(
                QRectF(center_x - 13, center_y - 11, 26, 22),
                4,
                4,
            )

            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(color, 2))

            if sensor_name == "camera":
                self.draw_camera_icon(painter, center_x, center_y)
            elif sensor_name == "sonar":
                self.draw_sonar_icon(painter, center_x, center_y)
            elif sensor_name == "ir":
                self.draw_ir_icon(painter, center_x, center_y)
            elif sensor_name == "radar":
                self.draw_radar_icon(painter, center_x, center_y)

    def draw_camera_icon(self, painter: QPainter, x: float, y: float):
        painter.drawRect(QRectF(x - 6, y - 4, 12, 8))
        painter.drawLine(int(x + 6), int(y - 2), int(x + 10), int(y - 5))
        painter.drawLine(int(x + 6), int(y + 2), int(x + 10), int(y + 5))
        painter.drawEllipse(QPointF(x, y), 2.0, 2.0)

    def draw_sonar_icon(self, painter: QPainter, x: float, y: float):
        painter.drawLine(int(x - 7), int(y + 6), int(x + 7), int(y + 6))
        painter.drawArc(QRectF(x - 8, y - 7, 16, 16), 35 * 16, 110 * 16)
        painter.drawArc(QRectF(x - 5, y - 4, 10, 10), 35 * 16, 110 * 16)

    def draw_ir_icon(self, painter: QPainter, x: float, y: float):
        points = QPolygonF(
            [
                QPointF(x, y - 8),
                QPointF(x + 7, y),
                QPointF(x, y + 8),
                QPointF(x - 7, y),
            ]
        )
        painter.drawPolygon(points)
        painter.drawLine(int(x - 3), int(y), int(x + 3), int(y))

    def draw_radar_icon(self, painter: QPainter, x: float, y: float):
        painter.drawEllipse(QPointF(x, y), 7.0, 7.0)
        painter.drawLine(int(x), int(y), int(x + 6), int(y - 4))
        painter.drawPoint(int(x), int(y))


class UsvListItemWidget(QWidget):
    def __init__(self, usv_name: str, parent=None):
        super().__init__(parent)

        self.usv_name = usv_name
        self.selected = False
        self.setFixedHeight(82)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        self.name_label = QLabel(usv_name)
        self.name_label.setFixedHeight(20)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #dbeaf5;")

        self.icon_strip = SensorIconStrip()
        self.icon_strip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(self.name_label)
        layout.addWidget(self.icon_strip)

    def set_selected(self, selected: bool):
        if self.selected == selected:
            return

        self.selected = selected
        self.update_style()

    def set_sensor_statuses(self, statuses: dict):
        self.icon_strip.set_statuses(statuses)

    def update_style(self):
        if self.selected:
            self.setStyleSheet(
                """
                QWidget {
                    background-color: #2d6fb8;
                    border: 1px solid #83caff;
                }
                """
            )
            self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        else:
            self.setStyleSheet(
                """
                QWidget {
                    background-color: transparent;
                    border: 1px solid transparent;
                }
                """
            )
            self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #dbeaf5;")


class VoiceStatusPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = {}
        self.setFixedHeight(202)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #dbeaf5;
                border: none;
                background: transparent;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        title = QLabel("语音输入识别")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(22)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")

        self.asr_label = QLabel("ASR  OFFLINE")
        self.command_label = QLabel("指令  等待")
        self.text_label = QLabel("识别结果：等待语音输入")
        self.intent_label = QLabel("解析意图：--")
        self.mission_label = QLabel("任务映射：--")
        self.meta_label = QLabel("model --")

        for label in [
            self.asr_label,
            self.command_label,
            self.text_label,
            self.intent_label,
            self.mission_label,
            self.meta_label,
        ]:
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.asr_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #ff5964;")
        self.command_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #8fa9bd;")
        self.text_label.setStyleSheet("font-size: 12px; color: #dbeaf5;")
        self.intent_label.setStyleSheet("font-size: 12px; color: #9fd9ff;")
        self.mission_label.setStyleSheet("font-size: 12px; color: #8fa9bd;")
        self.meta_label.setStyleSheet("font-size: 11px; color: #28c786;")

        layout.addWidget(title)
        layout.addWidget(self.asr_label)
        layout.addWidget(self.command_label)
        layout.addWidget(self.text_label, stretch=1)
        layout.addWidget(self.intent_label)
        layout.addWidget(self.mission_label)
        layout.addWidget(self.meta_label)

    def set_voice_state(self, state: dict):
        self.state = dict(state or {})
        now = time.time()

        asr_state = str(self.state.get("asr_state") or "offline")
        command_state = str(self.state.get("command_state") or "offline")
        last_status = float(self.state.get("last_status_time") or 0.0)
        last_text_time = float(self.state.get("last_transcript_time") or 0.0)
        status_age = now - last_status if last_status > 0.0 else None

        online = status_age is not None and status_age <= 4.0
        state_labels = {
            "offline": "离线",
            "started": "启动中",
            "loading_model": "加载模型",
            "ready": "就绪",
            "audio_ready": "监听中",
            "running": "运行中",
            "vad": "监听中",
            "transcribing": "识别中",
            "no_text": "未成句",
            "ptt_waiting": "按住A说话",
            "ptt_listening": "录音中",
            "ptt_stopped": "停止录音",
            "cancelled": "已取消",
            "transcribed": "已识别",
            "exited": "已退出",
            "start_failed": "启动失败",
        }
        if not online:
            asr_text = "语音识别：离线"
            asr_color = "#ff5964"
        elif asr_state in ["ready", "running", "transcribed", "vad", "ptt_waiting", "ptt_stopped"]:
            asr_text = f"语音识别：{state_labels.get(asr_state, asr_state)}"
            asr_color = "#28c786"
        elif asr_state in ["loading_model", "started", "audio_ready", "transcribing", "no_text", "ptt_listening"]:
            asr_text = f"语音识别：{state_labels.get(asr_state, asr_state)}"
            asr_color = "#ffd45c"
        else:
            asr_text = f"语音识别：{state_labels.get(asr_state, asr_state)}"
            asr_color = "#ff5964" if "error" in asr_state else "#8fd4ff"

        self.asr_label.setText(asr_text)
        self.asr_label.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {asr_color};")

        command_online = (now - float(self.state.get("last_command_time") or 0.0)) <= 4.0
        command_color = "#28c786" if command_online else "#8fa9bd"
        command_labels = {
            "offline": "离线",
            "ready": "就绪",
            "intent": "已解析",
            "waiting": "等待",
        }
        self.command_label.setText(f"指令解析：{command_labels.get(command_state, command_state)}")
        self.command_label.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {command_color};"
        )

        text = str(self.state.get("last_text") or "").strip()
        if text:
            text_age = now - last_text_time if last_text_time > 0.0 else 0.0
            self.text_label.setText(f"识别结果：{self.compact(text, 42)}  {text_age:.1f}s")
        elif asr_state == "no_text":
            self.text_label.setText("识别结果：未识别到有效语音")
        elif asr_state == "vad":
            self.text_label.setText("识别结果：音量低于阈值")
        else:
            self.text_label.setText("识别结果：等待语音输入")

        intent = str(self.state.get("last_intent") or "").strip()
        self.intent_label.setText(f"解析意图：{self.compact(intent, 32) if intent else '--'}")

        mission_state = str(self.state.get("mission_state") or "offline")
        mission_detail = str(self.state.get("mission_detail") or "").strip()
        mission_labels = {
            "offline": "等待",
            "requested": "已生成",
            "accepted": "已接受",
            "rejected": "已拒绝",
            "planning": "规划中",
            "executing": "执行中",
            "succeeded": "已完成",
            "failed": "失败",
            "cancelled": "已取消",
        }
        mission_color = {
            "accepted": "#28c786",
            "succeeded": "#28c786",
            "requested": "#9fd9ff",
            "planning": "#ffd45c",
            "executing": "#ffd45c",
            "rejected": "#ff5964",
            "failed": "#ff5964",
            "cancelled": "#ff5964",
        }.get(mission_state, "#8fa9bd")
        mission_text = mission_labels.get(mission_state, mission_state)
        if mission_detail:
            mission_text = (
                f"{mission_text} · {self.compact(mission_detail, 30)}"
            )
        self.mission_label.setText(f"任务映射：{mission_text}")
        self.mission_label.setStyleSheet(
            f"font-size: 12px; color: {mission_color};"
        )

        error = str(self.state.get("last_error") or "").strip()
        model = str(self.state.get("model") or "--")
        rms = self.state.get("rms")
        audio_sec = self.state.get("audio_sec")
        latency = self.state.get("latency_sec")
        if error:
            self.meta_label.setText(f"错误：{self.compact(error, 36)}")
            self.meta_label.setStyleSheet("font-size: 11px; color: #ff5964;")
            return

        parts = [f"模型 {model}"]
        if isinstance(rms, (int, float)):
            parts.append(f"rms {float(rms):.3f}")
        if isinstance(audio_sec, (int, float)):
            parts.append(f"录音 {float(audio_sec):.1f}s")
        if isinstance(latency, (int, float)):
            parts.append(f"延迟 {float(latency):.1f}s")
        self.meta_label.setText(" | ".join(parts))
        self.meta_label.setStyleSheet("font-size: 11px; color: #28c786;")

    def compact(self, text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[: max(1, limit - 1)] + "…"


class UsvSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.on_usv_selected = None
        self.syncing = False
        self.items_by_usv = {}
        self.widgets_by_usv = {}

        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("USV 选择")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(36)
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #f2f8ff;")

        self.usv_list = QListWidget()
        self.usv_list.setStyleSheet(
            """
            QListWidget {
                background-color: #08131e;
                color: #dbeaf5;
                border: 1px solid #263f55;
                font-size: 15px;
                outline: 0;
            }
            QListWidget::item {
                height: 86px;
                padding: 0;
                border-bottom: 1px solid #132232;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #14263a;
            }
            """
        )

        for name in USV_NAMES:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, name)
            item.setSizeHint(QSize(190, 86))
            widget = UsvListItemWidget(name)
            self.usv_list.addItem(item)
            self.usv_list.setItemWidget(item, widget)
            self.items_by_usv[name] = item
            self.widgets_by_usv[name] = widget

        self.usv_list.setCurrentRow(0)
        self.refresh_selection_styles()
        self.usv_list.currentItemChanged.connect(self.handle_current_item_changed)

        self.voice_panel = VoiceStatusPanel()

        layout.addWidget(title)
        layout.addWidget(self.usv_list, stretch=1)
        layout.addWidget(self.voice_panel)

    def handle_current_item_changed(self, current, previous):
        self.refresh_selection_styles()

        if self.syncing or current is None:
            return

        usv_name = current.data(Qt.UserRole)

        if self.on_usv_selected is not None:
            self.on_usv_selected(usv_name)

    def set_current_usv(self, usv_name: str):
        item = self.items_by_usv.get(usv_name)

        if item is None:
            return

        self.syncing = True
        self.usv_list.setCurrentItem(item)
        self.syncing = False
        self.refresh_selection_styles()

    def set_sensor_statuses(self, snapshot: dict):
        for usv_name, widget in self.widgets_by_usv.items():
            widget.set_sensor_statuses(snapshot.get(usv_name, {}))

    def set_voice_state(self, state: dict):
        self.voice_panel.set_voice_state(state)

    def refresh_selection_styles(self):
        current_item = self.usv_list.currentItem()

        for usv_name, item in self.items_by_usv.items():
            widget = self.widgets_by_usv.get(usv_name)
            if widget is not None:
                widget.set_selected(item is current_item)


class OperatorPage(QWidget):
    def __init__(self, ros_node: RosInterface):
        super().__init__()

        self.ros_node = ros_node
        self.current_sensor = self.ros_node.current_sensor

        self.ros_node.add_target_changed_callback(self.sync_usv_list_from_ros)
        self.ros_node.add_sensor_changed_callback(self.sync_sensor_from_ros)
        self.ros_node.add_overview_metadata_callback(self.update_minimap_metadata)
        self.ros_node.add_overview_fleet_callback(self.update_minimap_fleet)
        self.ros_node.add_sensor_health_callback(self.update_sensor_health)
        self.ros_node.add_attention_heatmap_callback(self.update_attention_heatmap)
        self.ros_node.add_joy_callback(self.update_joy_state)
        self.ros_node.add_voice_callback(self.update_voice_status)

        self.video_widget = VideoWidget()
        self.video_widget.set_placeholder_text(SENSOR_PLACEHOLDERS[self.current_sensor])

        self.speed_gauge = SpeedGauge()
        self.speed_gauge.set_offline()
        self.minimap_panel = None
        self.heatmap_panel = None
        self.gamepad_panel = None

        self.sensor_panels = []
        self.last_status_refresh_time = 0.0
        self.last_rendered_qimage = None

        self.build_layout()
        self.update_voice_status(self.ros_node.voice_state)
        self.refresh_sensor_panels()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_console)
        self.timer.start(33)

    def build_layout(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        self.sidebar = UsvSidebar()
        self.sidebar.on_usv_selected = self.on_usv_selected

        # 中间：主传感器显示 + 底部四路通信状态
        center_widget = QWidget()
        center_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        self.camera_title = QLabel(SENSOR_TITLES[self.current_sensor])
        self.camera_title.setAlignment(Qt.AlignCenter)
        self.camera_title.setFixedHeight(36)
        self.camera_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

        sensor_row = QHBoxLayout()
        sensor_row.setSpacing(8)

        self.sensor_panels = [SensorStatusPanel() for _ in SENSOR_ORDER]

        for panel in self.sensor_panels:
            sensor_row.addWidget(panel)

        center_layout.addWidget(self.camera_title)
        center_layout.addWidget(self.video_widget, stretch=1)
        center_layout.addLayout(sensor_row)

        # 右侧：速度、小地图、热力图、手柄映射
        right_widget = QWidget()
        right_widget.setFixedWidth(360)
        right_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        gauge_frame = QFrame()
        gauge_frame.setFixedHeight(190)
        gauge_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        gauge_frame.setStyleSheet(
            """
            QFrame {
                background-color: #050505;
                border: 1px solid #444444;
                border-radius: 6px;
            }
            QLabel {
                color: white;
            }
            """
        )

        gauge_layout = QVBoxLayout(gauge_frame)

        gauge_title = QLabel("WAM-V 速度")
        gauge_title.setAlignment(Qt.AlignCenter)
        gauge_title.setFixedHeight(26)
        gauge_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        gauge_layout.addWidget(gauge_title)
        gauge_layout.addWidget(self.speed_gauge)

        self.minimap_panel = MiniMapPanel()
        self.minimap_panel.set_current_usv(self.ros_node.current_usv)
        if self.ros_node.overview_metadata:
            self.minimap_panel.set_metadata(self.ros_node.overview_metadata)
        if self.ros_node.overview_fleet_state:
            self.minimap_panel.set_fleet_state(self.ros_node.overview_fleet_state)

        self.heatmap_panel = AttentionHeatmapPanel()

        self.gamepad_panel = GamepadProjectionPanel()

        right_layout.addWidget(gauge_frame)
        right_layout.addWidget(self.minimap_panel)
        right_layout.addWidget(self.heatmap_panel)
        right_layout.addWidget(self.gamepad_panel)
        right_layout.addStretch()

        root.addWidget(self.sidebar)
        root.addWidget(center_widget, stretch=1)
        root.addWidget(right_widget)

    def on_usv_selected(self, usv_name: str):
        if not usv_name:
            return

        self.video_widget.clear_image()
        self.last_rendered_qimage = None
        self.ros_node.set_current_usv(usv_name, publish_manual=True)
        self.refresh_sensor_panels()

    def sync_usv_list_from_ros(self, usv_name: str):
        self.sidebar.set_current_usv(usv_name)
        if self.minimap_panel is not None:
            self.minimap_panel.set_current_usv(usv_name)
        self.video_widget.clear_image()
        self.last_rendered_qimage = None
        self.refresh_sensor_panels()

    def sync_sensor_from_ros(self, sensor_name: str):
        if sensor_name not in SENSOR_ORDER:
            return

        self.current_sensor = sensor_name
        self.video_widget.clear_image()
        self.last_rendered_qimage = None

        self.camera_title.setText(SENSOR_TITLES.get(sensor_name, sensor_name))
        self.video_widget.set_placeholder_text(
            SENSOR_PLACEHOLDERS.get(sensor_name, "等待传感器数据流")
        )

        self.refresh_sensor_panels()

    def refresh_sensor_panels(self):
        current_usv = self.ros_node.current_usv
        self.sidebar.set_sensor_statuses(self.ros_node.sensor_status_snapshot())

        for panel, sensor_name in zip(self.sensor_panels, SENSOR_ORDER):
            panel.set_sensor(current_usv, sensor_name)
            panel.set_online_state(self.ros_node.is_sensor_online(sensor_name))

    def update_console(self):
        if not rclpy.ok():
            self.timer.stop()
            return

        try:
            for _ in range(5):
                rclpy.spin_once(self.ros_node, timeout_sec=0.0)
        except (ExternalShutdownException, RuntimeError, Exception) as e:
            print(f"[operator_console] ROS spin stopped: {e}")
            self.timer.stop()
            return

        qimg = self.ros_node.latest_qimage
        if qimg is not None and qimg is not self.last_rendered_qimage:
            self.video_widget.set_image(qimg)
            self.last_rendered_qimage = qimg

        now = self.ros_node.now_sec()
        if now - self.last_status_refresh_time >= 0.2:
            self.refresh_sensor_panels()
            self.update_voice_status(self.ros_node.voice_state)
            self.last_status_refresh_time = now

        if self.ros_node.is_speed_online():
            self.speed_gauge.set_speed(self.ros_node.current_display_speed())
        else:
            self.speed_gauge.set_offline()

    def update_attention_heatmap(self, heatmap: dict):
        if self.heatmap_panel is not None:
            self.heatmap_panel.set_heatmap(heatmap)

    def update_joy_state(self, joy_state: dict):
        if self.gamepad_panel is not None:
            self.gamepad_panel.set_joy_state(joy_state)

    def update_voice_status(self, voice_state: dict):
        if hasattr(self, "sidebar") and self.sidebar is not None:
            self.sidebar.set_voice_state(voice_state)

    def update_sensor_health(self, sensor_health: dict):
        self.refresh_sensor_panels()

    def update_minimap_metadata(self, metadata: dict):
        if self.minimap_panel is not None:
            self.minimap_panel.set_metadata(metadata)

    def update_minimap_fleet(self, fleet_state: dict):
        if self.minimap_panel is not None:
            self.minimap_panel.set_fleet_state(fleet_state)


class OverviewMapWidget(QWidget):
    def __init__(self, parent=None, compact: bool = False):
        super().__init__(parent)

        self.compact = bool(compact)
        self.grid_visible = False
        self.min_x = -500.0
        self.max_x = 500.0
        self.min_y = -500.0
        self.max_y = 500.0
        self.tick_step_m = 200.0
        self.world_name = "air_crash_sar"
        self.obstacles = []
        self.markers = []
        self.occupancy = {}
        self.sector_grid = {}
        self.fleet = {}
        self.trails = {}
        self.current_usv = "wamv_01"
        self.local_view_size_m = 200.0
        self.trail_duration_sec = 90.0
        self.static_cache = None
        self.static_cache_key = None
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.update)
        self.pulse_timer.start(80)

        if self.compact:
            self.setMinimumSize(318, 318)
        else:
            self.setMinimumSize(800, 520)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #06111c;
                border: 1px solid #33556e;
            }
            """
        )

    def set_grid_visible(self, visible: bool):
        self.grid_visible = bool(visible)
        self.invalidate_static_cache()
        self.update()

    def set_current_usv(self, usv_name: str):
        if usv_name in USV_NAMES:
            self.current_usv = usv_name
            self.update()

    def set_world_bounds(self, min_x: float, max_x: float, min_y: float, max_y: float):
        if max_x <= min_x or max_y <= min_y:
            return

        self.min_x = float(min_x)
        self.max_x = float(max_x)
        self.min_y = float(min_y)
        self.max_y = float(max_y)
        self.invalidate_static_cache()
        self.update()

    def invalidate_static_cache(self):
        self.static_cache = None
        self.static_cache_key = None

    def set_metadata(self, metadata: dict):
        bounds = metadata.get("bounds", {})

        self.world_name = metadata.get("world", self.world_name)
        self.obstacles = metadata.get("obstacles", [])
        self.markers = metadata.get("markers", [])
        self.occupancy = metadata.get("occupancy", {})
        self.sector_grid = metadata.get("sector_grid", {})
        grid_size = metadata.get("grid_size_m")

        self.set_world_bounds(
            float(bounds.get("min_x", self.min_x)),
            float(bounds.get("max_x", self.max_x)),
            float(bounds.get("min_y", self.min_y)),
            float(bounds.get("max_y", self.max_y)),
        )
        self.expand_bounds_for_fleet()

        if grid_size is not None:
            self.tick_step_m = self.choose_tick_step(float(grid_size))
            self.invalidate_static_cache()
            self.update()

    def set_fleet_state(self, fleet_state: dict):
        vehicles = fleet_state.get("vehicles", [])
        now_names = set()
        now = time.monotonic()

        for vehicle in vehicles:
            name = vehicle.get("name")
            if not name:
                continue

            now_names.add(name)
            self.fleet[name] = vehicle

            trail = self.trails.setdefault(name, [])
            point = (float(vehicle.get("x", 0.0)), float(vehicle.get("y", 0.0)))

            if not trail or self.distance_xy((trail[-1][0], trail[-1][1]), point) >= 0.4:
                trail.append((point[0], point[1], now))

            while trail and now - trail[0][2] > self.trail_duration_sec:
                trail.pop(0)

        for name in list(self.fleet):
            if name not in now_names:
                self.fleet.pop(name, None)

        self.expand_bounds_for_fleet()
        self.update()

    def expand_bounds_for_fleet(self):
        if not self.fleet:
            return

        min_x = self.min_x
        max_x = self.max_x
        min_y = self.min_y
        max_y = self.max_y
        padding = 35.0

        for vehicle in self.fleet.values():
            x = float(vehicle.get("x", 0.0))
            y = float(vehicle.get("y", 0.0))
            min_x = min(min_x, x - padding)
            max_x = max(max_x, x + padding)
            min_y = min(min_y, y - padding)
            max_y = max(max_y, y + padding)

        if min_x < self.min_x or max_x > self.max_x or min_y < self.min_y or max_y > self.max_y:
            self.min_x = min_x
            self.max_x = max_x
            self.min_y = min_y
            self.max_y = max_y
            self.tick_step_m = self.choose_tick_step(10.0)
            self.invalidate_static_cache()

    def distance_xy(self, a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    def choose_tick_step(self, grid_size_m: float) -> float:
        world_span = max(self.world_width(), self.world_height())

        for step in [10.0, 20.0, 50.0, 100.0, 200.0, 500.0]:
            if world_span / step <= 8.0:
                return max(step, grid_size_m)

        return max(1000.0, grid_size_m)

    def world_width(self) -> float:
        return max(1.0, self.max_x - self.min_x)

    def world_height(self) -> float:
        return max(1.0, self.max_y - self.min_y)

    def view_bounds(self):
        if self.compact:
            vehicle = self.fleet.get(self.current_usv)
            if vehicle is not None:
                cx = float(vehicle.get("x", 0.0))
                cy = float(vehicle.get("y", 0.0))
                half = self.local_view_size_m / 2.0
                return cx - half, cx + half, cy - half, cy + half

        return self.min_x, self.max_x, self.min_y, self.max_y

    def view_width(self) -> float:
        min_x, max_x, _, _ = self.view_bounds()
        return max(1.0, max_x - min_x)

    def view_height(self) -> float:
        _, _, min_y, max_y = self.view_bounds()
        return max(1.0, max_y - min_y)

    def map_rect_for_view(self) -> QRectF:
        if self.compact:
            margin_left = 10
            margin_bottom = 10
            margin_top = 10
            margin_right = 10
        else:
            margin_left = 64
            margin_bottom = 48
            margin_top = 18
            margin_right = 48

        available = QRectF(
            margin_left,
            margin_top,
            self.width() - margin_left - margin_right,
            self.height() - margin_top - margin_bottom,
        )

        if self.compact:
            side = max(1.0, min(available.width(), available.height()))
            available = QRectF(
                available.left() + (available.width() - side) / 2.0,
                available.top() + (available.height() - side) / 2.0,
                side,
                side,
            )

        meters_per_pixel = min(
            available.width() / self.view_width(),
            available.height() / self.view_height(),
        )

        map_width = self.view_width() * meters_per_pixel
        map_height = self.view_height() * meters_per_pixel

        return QRectF(
            available.left() + (available.width() - map_width) / 2.0,
            available.top() + (available.height() - map_height) / 2.0,
            map_width,
            map_height,
        )

    def world_to_pixel(self, x: float, y: float, map_rect: QRectF):
        min_x, max_x, min_y, max_y = self.view_bounds()
        width = max(1.0, max_x - min_x)
        height = max(1.0, max_y - min_y)
        px = map_rect.left() + (x - min_x) / width * map_rect.width()
        py = map_rect.bottom() - (y - min_y) / height * map_rect.height()
        return px, py

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        static_map = self.static_map_image()
        painter.drawImage(0, 0, static_map)

        map_rect = self.map_rect_for_view()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipRect(map_rect)
        self.draw_pulsing_targets(painter, map_rect)
        self.draw_fleet(painter, map_rect)
        painter.setClipping(False)

    def resizeEvent(self, event):
        self.invalidate_static_cache()
        super().resizeEvent(event)

    def static_map_image(self):
        view_min_x, view_max_x, view_min_y, view_max_y = self.view_bounds()
        key = (
            self.width(),
            self.height(),
            round(view_min_x, 3),
            round(view_max_x, 3),
            round(view_min_y, 3),
            round(view_max_y, 3),
            self.grid_visible,
            len(self.obstacles),
        )

        if self.static_cache is not None and self.static_cache_key == key:
            return self.static_cache

        image = QImage(max(1, self.width()), max(1, self.height()), QImage.Format_RGB32)
        image.fill(Qt.black)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        map_rect = self.map_rect_for_view()
        self.draw_sea_background(painter, map_rect)

        self.draw_obstacles(painter, map_rect)

        if self.grid_visible:
            self.draw_chess_grid(painter, map_rect)

        self.draw_distance_ticks(painter, map_rect)

        painter.setPen(QPen(QColor(205, 215, 215), 1))
        painter.drawRect(map_rect)
        painter.end()

        self.static_cache = image
        self.static_cache_key = key
        return image

    def draw_sea_background(self, painter: QPainter, map_rect: QRectF):
        painter.fillRect(map_rect, QColor(13, 78, 118))

        painter.setClipRect(map_rect)

        for i in range(28):
            y = map_rect.top() + (i + 0.35) * map_rect.height() / 46.0
            offset = ((i * 53) % 131) - 65
            alpha = 6 + (i % 4) * 2
            painter.setPen(QPen(QColor(120, 190, 225, alpha), 1))
            painter.drawLine(
                int(map_rect.left() + offset),
                int(y),
                int(map_rect.right() + offset * 0.35),
                int(y + math.sin(i * 0.57) * 6),
            )

        if not self.compact:
            for i in range(220):
                u = self.hash01(i, 17)
                v = self.hash01(i, 41)
                x = map_rect.left() + u * map_rect.width()
                y = map_rect.top() + v * map_rect.height()
                tone = int(105 + self.hash01(i, 73) * 60)
                alpha = int(5 + self.hash01(i, 97) * 10)
                painter.setPen(QPen(QColor(tone, min(230, tone + 45), 245, alpha), 1))
                painter.drawPoint(int(x), int(y))

        for i in range(36 if not self.compact else 10):
            u = self.hash01(i, 17)
            v = self.hash01(i, 173)
            x = map_rect.left() + u * map_rect.width()
            y = map_rect.top() + v * map_rect.height()
            length = 20 + self.hash01(i, 211) * 85
            dy = math.sin(i * 0.91) * 4
            painter.setPen(QPen(QColor(170, 220, 238, 14), 1))
            painter.drawLine(int(x), int(y), int(x + length), int(y + dy))

        painter.setClipping(False)

    def hash01(self, i: int, salt: int) -> float:
        value = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
        return value - math.floor(value)

    def draw_distance_ticks(self, painter: QPainter, map_rect: QRectF):
        if self.compact:
            return

        painter.setPen(QPen(QColor(210, 210, 210), 1))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)

        metrics = painter.fontMetrics()

        view_min_x, view_max_x, view_min_y, view_max_y = self.view_bounds()

        y_value = self.first_tick(view_min_y)
        while y_value <= view_max_y + 1e-6:
            _, y = self.world_to_pixel(view_min_x, y_value, map_rect)
            painter.drawLine(
                int(map_rect.left() - 6),
                int(y),
                int(map_rect.left()),
                int(y),
            )

            # 左下角刻度和下边框起点刻度重合时，只保留下边框那一个。
            if abs(y_value - view_min_y) > 1e-6:
                label = self.format_meter(y_value)
                painter.drawText(
                    int(map_rect.left() - metrics.horizontalAdvance(label) - 9),
                    int(y + 4),
                    label,
                )

            y_value += self.tick_step_m

        x_value = self.first_tick(view_min_x)
        while x_value <= view_max_x + 1e-6:
            x, _ = self.world_to_pixel(x_value, view_min_y, map_rect)
            painter.drawLine(
                int(x),
                int(map_rect.bottom()),
                int(x),
                int(map_rect.bottom() + 6),
            )
            label = self.format_meter(x_value)
            painter.drawText(
                int(x - metrics.horizontalAdvance(label) / 2),
                int(map_rect.bottom() + 24),
                label,
            )
            x_value += self.tick_step_m

    def first_tick(self, minimum: float) -> float:
        return ((minimum + self.tick_step_m - 1e-6) // self.tick_step_m) * self.tick_step_m

    def format_meter(self, value: float) -> str:
        if abs(value) < 1e-6:
            value = 0.0

        if abs(value - round(value)) < 1e-6:
            return f"{int(round(value))}m"

        return f"{value:.1f}m"

    def draw_obstacles(self, painter: QPainter, map_rect: QRectF):
        for obstacle in self.obstacles:
            if obstacle.get("kind") == "target":
                continue

            polygon = obstacle.get("polygon", [])
            if len(polygon) < 3:
                continue

            raw_color = obstacle.get("color", [120, 130, 132])
            base = QColor(
                int(raw_color[0]),
                int(raw_color[1]),
                int(raw_color[2]),
            )

            fill = QColor(max(30, base.red()), max(42, base.green()), max(48, base.blue()), 205)
            edge = QColor(168, 190, 198, 150)

            points = QPolygonF()
            for x, y in polygon:
                px, py = self.world_to_pixel(float(x), float(y), map_rect)
                points.append(QPointF(px, py))

            shadow = QPolygonF()
            for point in points:
                shadow.append(QPointF(point.x() + 2.5, point.y() + 3.5))

            painter.setBrush(QBrush(QColor(0, 10, 16, 72)))
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(shadow)

            painter.setBrush(QBrush(fill))
            painter.setPen(QPen(QColor(4, 11, 17, 2), 2))
            painter.drawPolygon(points)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(edge, 1))
            painter.drawPolygon(points)

            if len(points) >= 2:
                painter.setPen(QPen(QColor(255, 255, 255, 34), 1))
                painter.drawLine(points[0], points[1])

    def polygon_center(self, polygon: QPolygonF) -> QPointF:
        if len(polygon) <= 0:
            return QPointF(0.0, 0.0)

        sx = 0.0
        sy = 0.0
        for point in polygon:
            sx += point.x()
            sy += point.y()
        return QPointF(sx / len(polygon), sy / len(polygon))

    def draw_pulsing_targets(self, painter: QPainter, map_rect: QRectF):
        now = time.monotonic()
        targets = []

        for marker in self.markers[:4]:
            targets.append((float(marker.get("x", 0.0)), float(marker.get("y", 0.0))))

        for obstacle in self.obstacles:
            if obstacle.get("kind") != "target":
                continue

            polygon = obstacle.get("polygon", [])
            if len(polygon) < 3:
                continue

            sx = 0.0
            sy = 0.0
            for x, y in polygon:
                sx += float(x)
                sy += float(y)
            targets.append((sx / len(polygon), sy / len(polygon)))

        for x, y in targets:
            px, py = self.world_to_pixel(x, y, map_rect)

            max_radius = 16.0 if self.compact else 22.0
            for offset in [0.0, 0.5]:
                phase = (now * 1.15 + offset) % 1.0
                radius = 4.0 + phase * max_radius
                alpha = int(180 * (1.0 - phase))
                width = max(1, int(3 - phase * 2))

                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(255, 42, 48, alpha), width))
                painter.drawEllipse(QPointF(px, py), radius, radius)

            painter.setBrush(QBrush(QColor(255, 28, 36, 235)))
            painter.setPen(QPen(QColor(255, 205, 205, 210), 1))
            painter.drawEllipse(QPointF(px, py), 3.3 if self.compact else 4.0, 3.3 if self.compact else 4.0)

    def draw_fleet(self, painter: QPainter, map_rect: QRectF):
        now = time.monotonic()

        for name, trail in self.trails.items():
            if len(trail) < 2:
                continue

            color = self.vehicle_color(name)
            points = []
            fades = []
            for x, y, stamp in trail:
                px, py = self.world_to_pixel(x, y, map_rect)
                age = max(0.0, now - stamp)
                fade = max(0.0, 1.0 - age / self.trail_duration_sec)
                points.append(QPointF(px, py))
                fades.append(fade)

            if len(points) < 2:
                continue

            for index in range(1, len(trail)):
                fade = fades[index]
                if fade <= 0.02:
                    continue

                previous = points[index - 1]
                current = points[index]
                segment = QPainterPath(previous)
                if index < len(points) - 1:
                    mid = QPointF(
                        (current.x() + points[index + 1].x()) / 2.0,
                        (current.y() + points[index + 1].y()) / 2.0,
                    )
                    segment.quadTo(current, mid)
                else:
                    segment.lineTo(current)

                alpha = int(118 * fade)
                width = max(1.0, (4.6 if self.compact else 3.6) * fade)
                pen = QPen(QColor(210, 242, 255, alpha), width)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawPath(segment)

                if index % 2 != 0:
                    continue

                dx = current.x() - previous.x()
                dy = current.y() - previous.y()
                length = max(1.0, math.hypot(dx, dy))
                nx = -dy / length
                ny = dx / length
                spread = (1.0 - fade) * (7.0 if self.compact else 5.0)
                side = -1.0 if index % 4 == 0 else 1.0
                dot = QPointF(current.x() + nx * spread * side, current.y() + ny * spread * side)
                radius = max(0.8, (2.2 if self.compact else 1.7) * fade)
                painter.setBrush(QBrush(QColor(214, 245, 255, int(75 * fade))))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(dot, radius, radius)

        for name, vehicle in self.fleet.items():
            self.draw_vehicle(painter, map_rect, name, vehicle)

    def draw_vehicle(self, painter: QPainter, map_rect: QRectF, name: str, vehicle: dict):
        x = float(vehicle.get("x", 0.0))
        y = float(vehicle.get("y", 0.0))
        yaw = float(vehicle.get("yaw", 0.0))
        color = self.vehicle_color(name)

        is_current = name == self.current_usv
        scale = 8.0 if self.compact else 10.5
        local_points = [
            (scale * 0.72, 0.0),
            (-scale * 0.38, scale * 0.28),
            (-scale * 0.62, scale * 0.10),
            (-scale * 0.50, 0.0),
            (-scale * 0.62, -scale * 0.10),
            (-scale * 0.38, -scale * 0.28),
        ]
        polygon = QPolygonF()

        for lx, ly in local_points:
            rx, ry = self.rotate_local(lx, ly, yaw)
            px, py = self.world_to_pixel(x + rx, y + ry, map_rect)
            polygon.append(QPointF(px, py))

        center_x, center_y = self.world_to_pixel(x, y, map_rect)
        nose_x, nose_y = self.world_to_pixel(
            x + math.cos(yaw) * scale * 0.92,
            y + math.sin(yaw) * scale * 0.92,
            map_rect,
        )

        if is_current:
            painter.setBrush(QBrush(QColor(255, 255, 255, 28)))
            painter.setPen(QPen(QColor(245, 250, 255, 120), 1))
            painter.drawEllipse(QPointF(center_x, center_y), scale * 0.80, scale * 0.80)

        painter.setBrush(QBrush(QColor(0, 8, 14, 120)))
        painter.setPen(Qt.NoPen)
        shadow = QPolygonF([QPointF(point.x() + 1.6, point.y() + 2.0) for point in polygon])
        painter.drawPolygon(shadow)

        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 222 if is_current else 194)))
        painter.setPen(QPen(QColor(2, 7, 10), 2))
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(245, 250, 255, 230 if is_current else 170), 1))
        painter.drawPolygon(polygon)
        painter.setPen(QPen(QColor(245, 250, 255, 210), 1))
        painter.drawLine(int(center_x), int(center_y), int(nose_x), int(nose_y))

        label = self.vehicle_label(name)
        font = QFont()
        font.setPointSize(7 if self.compact else 8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(235, 248, 255, 230))
        offset = scale * 0.52
        painter.drawText(int(center_x + offset), int(center_y - offset), label)

    def vehicle_label(self, name: str) -> str:
        prefix = "wamv_"
        if name.startswith(prefix):
            suffix = name[len(prefix):]
            if suffix.isdigit():
                return str(int(suffix))
        return name

    def rotate_local(self, x: float, y: float, yaw: float):
        c = math.cos(yaw)
        s = math.sin(yaw)
        return x * c - y * s, x * s + y * c

    def vehicle_color(self, name: str):
        palette = [
            QColor(88, 181, 255),
            QColor(80, 224, 155),
            QColor(255, 177, 86),
            QColor(220, 132, 255),
            QColor(255, 105, 126),
            QColor(116, 222, 230),
            QColor(202, 226, 92),
            QColor(255, 143, 205),
            QColor(165, 194, 255),
            QColor(238, 238, 238),
        ]
        label = self.vehicle_label(name)
        try:
            return palette[(int(label) - 1) % len(palette)]
        except (TypeError, ValueError):
            return QColor(220, 220, 220)

    def draw_chess_grid(self, painter: QPainter, map_rect: QRectF):
        painter.setPen(QPen(QColor(230, 244, 255, 95), 1))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        bounds = self.sector_grid.get("bounds", {})
        min_x = float(bounds.get("min_x", self.min_x))
        max_x = float(bounds.get("max_x", self.max_x))
        min_y = float(bounds.get("min_y", self.min_y))
        max_y = float(bounds.get("max_y", self.max_y))

        left, top = self.world_to_pixel(min_x, max_y, map_rect)
        right, bottom = self.world_to_pixel(max_x, min_y, map_rect)
        grid_rect = QRectF(left, top, right - left, bottom - top)

        for i in range(1, 8):
            x = grid_rect.left() + grid_rect.width() * i / 8.0
            y = grid_rect.top() + grid_rect.height() * i / 8.0
            painter.drawLine(
                int(x),
                int(grid_rect.top()),
                int(x),
                int(grid_rect.bottom()),
            )
            painter.drawLine(
                int(grid_rect.left()),
                int(y),
                int(grid_rect.right()),
                int(y),
            )

        letters = "ABCDEFGH"
        label_font = QFont()
        label_font.setPointSize(11)
        label_font.setBold(True)
        painter.setFont(label_font)
        painter.setPen(QColor(235, 247, 255, 92))

        cell_w = grid_rect.width() / 8.0
        cell_h = grid_rect.height() / 8.0
        for row in range(8):
            for col, letter in enumerate(letters):
                label = f"{letter}{row + 1}"
                cell = QRectF(
                    grid_rect.left() + col * cell_w,
                    grid_rect.top() + row * cell_h,
                    cell_w,
                    cell_h,
                )
                painter.drawText(cell.adjusted(8, 6, -8, -6), Qt.AlignLeft | Qt.AlignTop, label)


class MiniMapPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(356)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #e7f2fb;
                border: 0;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)

        title = QLabel("小地图")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(22)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")

        self.map_widget = OverviewMapWidget(compact=True)

        layout.addWidget(title)
        layout.addWidget(self.map_widget, stretch=1)

    def set_metadata(self, metadata: dict):
        self.map_widget.set_metadata(metadata)

    def set_fleet_state(self, fleet_state: dict):
        self.map_widget.set_fleet_state(fleet_state)

    def set_current_usv(self, usv_name: str):
        self.map_widget.set_current_usv(usv_name)


class OverviewPage(QWidget):
    def __init__(self, ros_node: RosInterface):
        super().__init__()

        self.ros_node = ros_node
        self.ros_node.add_target_changed_callback(self.sync_usv_list_from_ros)
        self.ros_node.add_overview_metadata_callback(self.update_overview_metadata)
        self.ros_node.add_overview_fleet_callback(self.update_overview_fleet)
        self.ros_node.add_attention_heatmap_callback(self.update_attention_heatmap)

        self.sidebar = UsvSidebar()
        self.sidebar.on_usv_selected = self.on_usv_selected
        self.map_widget = OverviewMapWidget()
        self.heatmap_panel = None
        self.grid_toggle = None

        self.build_layout()
        self.sidebar.set_current_usv(self.ros_node.current_usv)
        self.map_widget.set_current_usv(self.ros_node.current_usv)
        self.refresh_sidebar_statuses()

        self.sidebar_timer = QTimer()
        self.sidebar_timer.timeout.connect(self.refresh_sidebar_statuses)
        self.sidebar_timer.start(200)

    def build_layout(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet("QFrame { background-color: transparent; border: 0; }")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title = QLabel("全局态势概览")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f2f8ff;")

        self.grid_toggle = QCheckBox("网格")
        self.grid_toggle.setFixedWidth(86)
        self.grid_toggle.setChecked(False)
        self.grid_toggle.toggled.connect(self.map_widget.set_grid_visible)
        self.grid_toggle.setStyleSheet(
            """
            QCheckBox {
                color: #dbeaf5;
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #5c7893;
                background-color: #07111c;
            }
            QCheckBox::indicator:checked {
                background-color: #2d6fb8;
                border: 1px solid #8fd4ff;
            }
            """
        )

        header_layout.addSpacing(86)
        header_layout.addWidget(title, stretch=1)
        header_layout.addWidget(self.grid_toggle)

        center_layout.addWidget(header)
        center_layout.addWidget(self.map_widget, stretch=1)

        right_widget = QWidget()
        right_widget.setFixedWidth(310)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.heatmap_panel = AttentionHeatmapPanel()
        right_layout.addWidget(self.heatmap_panel)
        right_layout.addWidget(make_panel("配置区", "WAITING", fixed_height=155))
        right_layout.addStretch()

        root.addWidget(self.sidebar)
        root.addWidget(center_widget, stretch=1)
        root.addWidget(right_widget)

    def on_usv_selected(self, usv_name: str):
        self.ros_node.set_current_usv(usv_name, publish_manual=True)

    def sync_usv_list_from_ros(self, usv_name: str):
        self.sidebar.set_current_usv(usv_name)
        self.map_widget.set_current_usv(usv_name)
        self.refresh_sidebar_statuses()

    def update_overview_metadata(self, metadata: dict):
        self.map_widget.set_metadata(metadata)

    def update_overview_fleet(self, fleet_state: dict):
        self.map_widget.set_fleet_state(fleet_state)

    def update_attention_heatmap(self, heatmap: dict):
        if self.heatmap_panel is not None:
            self.heatmap_panel.set_heatmap(heatmap)

    def toggle_grid(self):
        if self.grid_toggle is None:
            self.map_widget.set_grid_visible(not self.map_widget.grid_visible)
            return

        self.grid_toggle.setChecked(not self.grid_toggle.isChecked())

    def refresh_sidebar_statuses(self):
        self.sidebar.set_sensor_statuses(self.ros_node.sensor_status_snapshot())


class PlaceholderPage(QWidget):
    def __init__(self, title: str):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(title + "\n\nPLACEHOLDER")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 28px;
                background-color: #111111;
                border: 1px solid #444444;
            }
            """
        )

        layout.addWidget(label)


class SystemStatusPage(QWidget):
    def __init__(self, ros_node: RosInterface):
        super().__init__()

        self.ros_node = ros_node
        self.value_labels = {}
        self.sensor_labels = {}
        self.fleet_labels = {}

        self.build_layout()
        self.update_status()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

    def build_layout(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        left = QWidget()
        left.setFixedWidth(360)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        control_card, control_layout = self.make_status_card("控制链路")
        for key, label in [
            ("current_usv", "当前 WAM-V"),
            ("current_sensor", "主显示传感器"),
            ("speed", "速度仪表"),
            ("image", "FPV 图像缓存"),
        ]:
            self.add_value_row(control_layout, key, label)

        overview_card, overview_layout = self.make_status_card("全局态势")
        for key, label in [
            ("world", "World"),
            ("bounds", "地图范围"),
            ("obstacles", "障碍物"),
            ("occupancy", "栅格地图"),
        ]:
            self.add_value_row(overview_layout, key, label)

        left_layout.addWidget(control_card)
        left_layout.addWidget(overview_card)
        left_layout.addStretch()

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        sensor_card, sensor_layout = self.make_status_card("传感器在线矩阵")
        for usv_name in USV_NAMES:
            label = QLabel()
            label.setTextFormat(Qt.RichText)
            label.setMinimumHeight(46)
            label.setStyleSheet(
                """
                QLabel {
                    background-color: #07111c;
                    border: 1px solid #20384d;
                    border-radius: 4px;
                    padding: 8px;
                    color: #dbeaf5;
                    font-size: 13px;
                }
                """
            )
            sensor_layout.addWidget(label)
            self.sensor_labels[usv_name] = label

        fleet_card, fleet_layout = self.make_status_card("舰队定位状态")
        for usv_name in USV_NAMES:
            label = QLabel()
            label.setMinimumHeight(38)
            label.setStyleSheet(
                """
                QLabel {
                    background-color: #07111c;
                    border: 1px solid #20384d;
                    border-radius: 4px;
                    padding: 8px;
                    color: #dbeaf5;
                    font-size: 13px;
                }
                """
            )
            fleet_layout.addWidget(label)
            self.fleet_labels[usv_name] = label

        center_layout.addWidget(sensor_card)
        center_layout.addWidget(fleet_card)
        center_layout.addStretch()

        right = QWidget()
        right.setFixedWidth(330)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        bus_card, bus_layout = self.make_status_card("平台数据总线")
        for key, label in [
            ("manual_target", "/fleet/manual_target_state"),
            ("view_target", "/ui/view_target"),
            ("overview_metadata", "/overview/metadata"),
            ("overview_fleet", "/overview/fleet_state"),
            ("sensor_health", "/overview/sensor_health"),
            ("attention_heatmap", "/tobii/gaze"),
            ("mission_request", "/mission/request"),
            ("mission_status", "/mission/status"),
            ("alert_bus", "/alerts/events"),
        ]:
            self.add_value_row(bus_layout, key, label)

        right_layout.addWidget(bus_card)
        right_layout.addWidget(make_panel("告警接口", "RESERVED\n/alerts/events", fixed_height=150))
        right_layout.addWidget(
            make_panel(
                "任务 / 规划接口",
                "REQUEST  /mission/request\nSTATUS   /mission/status\nPLAN     /mission/plan",
                fixed_height=150,
            )
        )
        right_layout.addStretch()

        root.addWidget(left)
        root.addWidget(center, stretch=1)
        root.addWidget(right)

    def make_status_card(self, title: str):
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #08131e;
                border: 1px solid #263f55;
                border-radius: 4px;
            }
            QLabel {
                color: #e7f2fb;
                border: 0;
            }
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(26)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #f2f8ff;")
        layout.addWidget(title_label)

        return frame, layout

    def add_value_row(self, layout: QVBoxLayout, key: str, name: str):
        row = QFrame()
        row.setStyleSheet(
            """
            QFrame {
                background-color: #07111c;
                border: 1px solid #20384d;
                border-radius: 4px;
            }
            """
        )
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 5, 8, 5)
        row_layout.setSpacing(8)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 12px; color: #8fa9bd;")

        value_label = QLabel("--")
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #e7f2fb;")

        row_layout.addWidget(name_label)
        row_layout.addWidget(value_label, stretch=1)
        layout.addWidget(row)
        self.value_labels[key] = value_label

    def set_value(self, key: str, text: str, online: bool = True):
        label = self.value_labels.get(key)
        if label is None:
            return

        color = "#45df91" if online else "#e0525a"
        label.setText(text)
        label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")

    def update_status(self):
        self.set_value("current_usv", self.ros_node.current_usv, True)
        sensor_label = SENSOR_LABELS.get(self.ros_node.current_sensor, self.ros_node.current_sensor)
        self.set_value("current_sensor", sensor_label, True)

        speed_online = self.ros_node.is_speed_online()
        speed_text = f"{self.ros_node.current_display_speed():.2f} m/s" if speed_online else "OFFLINE"
        self.set_value("speed", speed_text, speed_online)

        image_online = self.ros_node.latest_qimage is not None
        self.set_value("image", "READY" if image_online else "WAITING", image_online)

        metadata = self.ros_node.overview_metadata or {}
        bounds = metadata.get("bounds", {})
        self.set_value("world", str(metadata.get("world", "--")), bool(metadata))

        if bounds:
            bounds_text = (
                f"x {float(bounds.get('min_x', 0.0)):.0f}..{float(bounds.get('max_x', 0.0)):.0f}, "
                f"y {float(bounds.get('min_y', 0.0)):.0f}..{float(bounds.get('max_y', 0.0)):.0f}"
            )
        else:
            bounds_text = "--"
        self.set_value("bounds", bounds_text, bool(bounds))

        obstacles = metadata.get("obstacles", [])
        markers = metadata.get("markers", [])
        self.set_value("obstacles", f"{len(obstacles)} obs / {len(markers)} alerts", bool(metadata))

        occupancy = metadata.get("occupancy", {})
        resolution = occupancy.get("resolution")
        width = occupancy.get("width")
        height = occupancy.get("height")
        occ_text = f"{width}x{height} @ {float(resolution):.1f}m" if resolution else "--"
        self.set_value("occupancy", occ_text, bool(resolution))

        self.set_value("manual_target", "ACTIVE", True)
        self.set_value("view_target", "ACTIVE", True)
        self.set_value("overview_metadata", "ONLINE" if metadata else "WAITING", bool(metadata))

        fleet_state = self.ros_node.overview_fleet_state or {}
        vehicles = fleet_state.get("vehicles", [])
        self.set_value("overview_fleet", f"{len(vehicles)} vehicles", bool(vehicles))
        sensor_health = self.ros_node.overview_sensor_health or {}
        health_vehicles = sensor_health.get("vehicles", {})
        self.set_value("sensor_health", f"{len(health_vehicles)} vehicles", bool(health_vehicles))
        heatmap = self.ros_node.attention_heatmap or {}
        heatmap_samples = int(heatmap.get("valid_samples", 0) or 0)
        heatmap_hz = float(heatmap.get("recent_valid_hz", 0.0) or 0.0)
        heatmap_text = f"{heatmap_hz:.1f}Hz / {heatmap_samples} samples" if heatmap_samples else "WAITING"
        self.set_value("attention_heatmap", heatmap_text, heatmap_samples > 0)
        mission_state = str(self.ros_node.voice_state.get("mission_state") or "offline")
        mission_online = mission_state != "offline"
        self.set_value(
            "mission_request",
            "READY" if mission_online else "WAITING",
            mission_online,
        )
        self.set_value(
            "mission_status",
            mission_state.upper() if mission_online else "WAITING",
            mission_state in {"requested", "accepted", "planning", "executing", "succeeded"},
        )
        self.set_value("alert_bus", "RESERVED", False)

        self.update_sensor_matrix()
        self.update_fleet_rows(vehicles)

    def update_sensor_matrix(self):
        snapshot = self.ros_node.sensor_status_snapshot()

        for usv_name in USV_NAMES:
            statuses = snapshot.get(usv_name, {})
            parts = []

            for sensor_name in SENSOR_ORDER:
                online = bool(statuses.get(sensor_name, False))
                color = "#45df91" if online else "#e0525a"
                state = "ON" if online else "OFF"
                title = SENSOR_LABELS.get(sensor_name, sensor_name)
                parts.append(
                    f"<span style='color:{color}; font-weight:bold;'>{title}:{state}</span>"
                )

            current_mark = " ●" if usv_name == self.ros_node.current_usv else ""
            label = self.sensor_labels.get(usv_name)
            if label is not None:
                label.setText(f"<b>{usv_name}{current_mark}</b><br>" + " &nbsp; ".join(parts))

    def update_fleet_rows(self, vehicles: list):
        by_name = {vehicle.get("name"): vehicle for vehicle in vehicles}

        for usv_name in USV_NAMES:
            vehicle = by_name.get(usv_name)
            label = self.fleet_labels.get(usv_name)
            if label is None:
                continue

            if not vehicle:
                label.setText(f"{usv_name}    pose: OFFLINE")
                label.setStyleSheet(
                    """
                    QLabel {
                        background-color: #07111c;
                        border: 1px solid #20384d;
                        border-radius: 4px;
                        padding: 8px;
                        color: #e0525a;
                        font-size: 13px;
                        font-weight: bold;
                    }
                    """
                )
                continue

            x = float(vehicle.get("x", 0.0))
            y = float(vehicle.get("y", 0.0))
            speed = float(vehicle.get("speed", 0.0))
            label.setText(f"{usv_name}    x {x:.1f}m    y {y:.1f}m    v {speed:.2f}m/s")
            label.setStyleSheet(
                """
                QLabel {
                    background-color: #07111c;
                    border: 1px solid #20384d;
                    border-radius: 4px;
                    padding: 8px;
                    color: #45df91;
                    font-size: 13px;
                    font-weight: bold;
                }
                """
            )


class MainWindow(QMainWindow):
    def __init__(self, ros_node: RosInterface):
        super().__init__()

        self.ros_node = ros_node
        self.page_names = ["fpv", "overview", "status", "record"]

        self.setWindowTitle("Multi-USV Operator Console")
        self.resize(1500, 900)
        self.setMinimumSize(1200, 720)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121820;
            }
            QWidget {
                background-color: #121820;
            }
            QPushButton {
                background-color: #182330;
                color: #dce8f2;
                border: 1px solid #35506a;
                padding: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #203348;
            }
            QPushButton:checked {
                background-color: #2d6fb8;
                border: 1px solid #78b8f6;
                color: white;
            }
            """
        )

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        nav = QHBoxLayout()
        nav.setSpacing(6)

        self.btn_operator = QPushButton("FPV")
        self.btn_mission = QPushButton("全局态势概览")
        self.btn_status = QPushButton("系统状态")
        self.btn_record = QPushButton("数据记录")

        self.buttons = [
            self.btn_operator,
            self.btn_mission,
            self.btn_status,
            self.btn_record,
        ]

        for btn in self.buttons:
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            nav.addWidget(btn)

        self.btn_operator.setChecked(True)

        self.pages = QStackedWidget()
        self.pages.addWidget(OperatorPage(self.ros_node))
        self.pages.addWidget(OverviewPage(self.ros_node))
        self.pages.addWidget(SystemStatusPage(self.ros_node))
        self.pages.addWidget(PlaceholderPage("数据记录页面"))

        self.btn_operator.clicked.connect(lambda: self.switch_page(0))
        self.btn_mission.clicked.connect(lambda: self.switch_page(1))
        self.btn_status.clicked.connect(lambda: self.switch_page(2))
        self.btn_record.clicked.connect(lambda: self.switch_page(3))

        self.ros_node.add_page_changed_callback(self.switch_page_by_name)
        self.ros_node.add_grid_toggle_callback(self.toggle_overview_grid)

        root.addLayout(nav)
        root.addWidget(self.pages)

        self.setCentralWidget(central)

    def switch_page(self, index: int):
        if index < 0 or index >= self.pages.count():
            return

        self.pages.setCurrentIndex(index)

        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

    def switch_page_by_name(self, page_name: str):
        aliases = {
            "operator": "fpv",
            "mission": "overview",
            "planning": "overview",
            "map": "overview",
            "system": "status",
            "data": "record",
        }
        normalized = aliases.get(page_name, page_name)

        if normalized in self.page_names:
            self.switch_page(self.page_names.index(normalized))
            return

        try:
            self.switch_page(int(normalized))
        except ValueError:
            self.ros_node.get_logger().warn(f"Unknown UI page: {page_name}")

    def toggle_overview_grid(self):
        overview_page = self.pages.widget(1)

        if hasattr(overview_page, "toggle_grid"):
            overview_page.toggle_grid()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return

        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            return

        super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            operator_page = self.pages.widget(0)
            if hasattr(operator_page, "timer"):
                operator_page.timer.stop()
            overview_page = self.pages.widget(1)
            if hasattr(overview_page, "sidebar_timer"):
                overview_page.sidebar_timer.stop()
            status_page = self.pages.widget(2)
            if hasattr(status_page, "timer"):
                status_page.timer.stop()
        except Exception:
            pass

        event.accept()


def main():
    rclpy.init(args=None)

    ros_node = RosInterface()
    app = QApplication(sys.argv)

    win = MainWindow(ros_node)
    win.showFullScreen()

    ret = 0

    try:
        ret = app.exec_()
    finally:
        try:
            win.close()
        except Exception:
            pass

        try:
            ros_node.destroy_node()
        except Exception:
            pass

        if rclpy.ok():
            try:
                rclpy.shutdown()
            except Exception:
                pass

    sys.exit(ret)


if __name__ == "__main__":
    main()
