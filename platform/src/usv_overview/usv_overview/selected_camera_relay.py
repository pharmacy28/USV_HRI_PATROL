#!/usr/bin/env python3
import ast
import json
import os
import signal
import subprocess
import time

from ament_index_python.packages import get_package_prefix
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import String


def camera_image_topic(target: str) -> str:
    return f'/{target}/sensors/cameras/front_camera_sensor/image_raw'


def camera_info_topic(target: str) -> str:
    return f'/{target}/sensors/cameras/front_camera_sensor/camera_info'


def gz_camera_image_topic(world: str, target: str) -> str:
    return f'/world/{world}/model/{target}/link/wamv/base_link/sensor/front_camera_sensor/image'


def gz_camera_info_topic(world: str, target: str) -> str:
    return f'/world/{world}/model/{target}/link/wamv/base_link/sensor/front_camera_sensor/camera_info'


class SelectedCameraRelay(Node):
    def __init__(self):
        super().__init__('overview_selected_camera_relay')

        self.declare_parameter(
            'target_names',
            [f'wamv_{i:02d}' for i in range(1, 11)],
        )
        self.declare_parameter('world', 'air_crash_sar')
        self.declare_parameter('initial_target', 'wamv_01')
        self.declare_parameter('max_publish_hz', 30.0)

        self.world = str(self.get_parameter('world').value)
        self.target_names = self.parse_target_names(
            self.get_parameter('target_names').value
        )
        self.current_target = str(self.get_parameter('initial_target').value)
        if self.current_target not in self.target_names:
            self.current_target = self.target_names[0]

        self.max_publish_hz = max(1.0, float(self.get_parameter('max_publish_hz').value))
        self.min_publish_dt = 1.0 / self.max_publish_hz
        self.last_image_publish_time = 0.0
        self.frames_in = 0
        self.info_in = 0
        self.last_report_time = time.time()
        self.last_target_request_time = 0.0
        self.bridge_process = None
        self.bridge_executable = os.path.join(
            get_package_prefix('ros_gz_bridge'),
            'lib',
            'ros_gz_bridge',
            'parameter_bridge',
        )

        self.sensor_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.status_pub = self.create_publisher(
            String,
            '/overview/selected_camera/status',
            10,
        )
        self.image_monitor_sub = self.create_subscription(
            Image,
            '/overview/selected_camera/image_raw',
            self.image_callback,
            self.sensor_qos,
        )
        self.info_monitor_sub = self.create_subscription(
            CameraInfo,
            '/overview/selected_camera/camera_info',
            self.info_callback,
            self.sensor_qos,
        )

        self.target_sub = self.create_subscription(
            String,
            '/fleet/manual_target_state',
            self.target_state_callback,
            10,
        )
        self.target_request_sub = self.create_subscription(
            String,
            '/fleet/manual_target',
            self.target_request_callback,
            10,
        )

        self.start_selected_camera_bridge()
        self.status_timer = self.create_timer(1.0, self.publish_status)

        self.get_logger().info(
            f'selected camera bridge manager started: {self.current_target}, '
            f'max_publish_hz={self.max_publish_hz:.1f}'
        )

    def parse_target_names(self, value):
        if isinstance(value, str):
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed = [part.strip() for part in value.split(',')]
        else:
            parsed = value

        names = [str(name) for name in parsed if str(name)]
        return names or [f'wamv_{i:02d}' for i in range(1, 11)]

    def target_request_callback(self, msg: String):
        self.last_target_request_time = time.time()
        self.switch_target(msg.data.strip())

    def target_state_callback(self, msg: String):
        target = msg.data.strip()
        if (
            target
            and target != self.current_target
            and time.time() - self.last_target_request_time < 0.4
        ):
            return
        self.switch_target(target)

    def switch_target(self, target: str):
        target = target.strip()
        if not target or target == self.current_target:
            return

        if target not in self.target_names:
            self.get_logger().warn(f'reject unknown selected camera target: {target}')
            return

        old_target = self.current_target
        self.current_target = target
        self.last_image_publish_time = 0.0
        self.start_selected_camera_bridge()
        self.get_logger().info(f'selected camera target switched: {old_target} -> {target}')

    def start_selected_camera_bridge(self):
        self.stop_selected_camera_bridge()

        source_image = gz_camera_image_topic(self.world, self.current_target)
        source_info = gz_camera_info_topic(self.world, self.current_target)
        image_arg = (
            f'{source_image}@sensor_msgs/msg/Image'
            f'[ignition.msgs.Image'
        )
        info_arg = (
            f'{source_info}@sensor_msgs/msg/CameraInfo'
            f'[ignition.msgs.CameraInfo'
        )

        cmd = [
            self.bridge_executable,
            image_arg,
            info_arg,
            '--ros-args',
            '-r',
            f'{source_image}:=/overview/selected_camera/image_raw',
            '-r',
            f'{source_info}:=/overview/selected_camera/camera_info',
            '-r',
            '__node:=selected_camera_bridge',
        ]

        try:
            self.bridge_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as exc:
            self.bridge_process = None
            self.get_logger().error(f'failed to start selected camera bridge: {exc}')
            return

        self.get_logger().info(
            f'started selected camera bridge for {self.current_target}: '
            f'{source_image} -> /overview/selected_camera/image_raw'
        )

    def stop_selected_camera_bridge(self):
        if self.bridge_process is None:
            return

        proc = self.bridge_process
        self.bridge_process = None

        if proc.poll() is not None:
            return

        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            return

        try:
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                return
            proc.wait(timeout=2.0)

    def image_callback(self, msg: Image):
        self.frames_in += 1
        now = time.time()
        if now - self.last_image_publish_time < self.min_publish_dt:
            return

        self.last_image_publish_time = now

    def info_callback(self, msg: CameraInfo):
        self.info_in += 1

    def publish_status(self):
        now = time.time()
        dt = max(1e-6, now - self.last_report_time)
        payload = {
            'stamp': now,
            'selected_target': self.current_target,
            'source_image_topic': camera_image_topic(self.current_target),
            'source_camera_info_topic': camera_info_topic(self.current_target),
            'source_gz_image_topic': gz_camera_image_topic(self.world, self.current_target),
            'source_gz_camera_info_topic': gz_camera_info_topic(self.world, self.current_target),
            'relay_image_topic': '/overview/selected_camera/image_raw',
            'relay_camera_info_topic': '/overview/selected_camera/camera_info',
            'output_hz': self.frames_in / dt,
            'camera_info_hz': self.info_in / dt,
            'max_publish_hz': self.max_publish_hz,
            'bridge_pid': None if self.bridge_process is None else self.bridge_process.pid,
            'bridge_running': self.bridge_process is not None and self.bridge_process.poll() is None,
        }

        self.frames_in = 0
        self.info_in = 0
        self.last_report_time = now

        msg = String()
        msg.data = json.dumps(payload, separators=(',', ':'))
        self.status_pub.publish(msg)

        if self.bridge_process is not None and self.bridge_process.poll() is not None:
            self.get_logger().warn('selected camera bridge exited; restarting')
            self.start_selected_camera_bridge()


def main(args=None):
    rclpy.init(args=args)
    node = SelectedCameraRelay()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_selected_camera_bridge()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
