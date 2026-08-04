#!/usr/bin/env python3
import ast
import json
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from sensor_msgs.msg import CameraInfo, LaserScan
from std_msgs.msg import String


SENSORS = {
    'camera': {
        'label': '摄像头',
        'type': 'camera',
        'topic': '/{name}/sensors/cameras/front_camera_sensor/camera_info',
        'msg_type': CameraInfo,
    },
    'sonar': {
        'label': '前扫声纳',
        'type': 'sonar',
        'topic': '/{name}/sensors/sonars/front_sonar_sensor/scan',
        'msg_type': LaserScan,
    },
    'ir': {
        'label': '红外摄像头',
        'type': 'camera',
        'topic': '/{name}/sensors/cameras/ir_camera_sensor/camera_info',
        'msg_type': CameraInfo,
    },
    'radar': {
        'label': '射线雷达',
        'type': 'radar',
        'topic': '/{name}/sensors/radars/ray_radar/scan',
        'msg_type': LaserScan,
    },
}


class SensorLinkMonitor(Node):
    def __init__(self):
        super().__init__('overview_sensor_link_monitor')

        self.declare_parameter(
            'target_names',
            [f'wamv_{i:02d}' for i in range(1, 11)],
        )
        self.declare_parameter('publish_hz', 5.0)
        self.declare_parameter('online_timeout_sec', 2.0)

        self.target_names = self.parse_target_names(
            self.get_parameter('target_names').value
        )
        self.publish_hz = max(0.5, float(self.get_parameter('publish_hz').value))
        self.online_timeout_sec = max(
            0.1,
            float(self.get_parameter('online_timeout_sec').value),
        )

        self.last_seen = {}
        self.subs = []

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        for target in self.target_names:
            for sensor_name, spec in SENSORS.items():
                topic = spec['topic'].format(name=target)
                sub = self.create_subscription(
                    spec['msg_type'],
                    topic,
                    lambda msg, t=target, s=sensor_name: self.sensor_callback(t, s),
                    qos,
                )
                self.subs.append(sub)

        self.selected_camera_status_sub = self.create_subscription(
            String,
            '/overview/selected_camera/status',
            self.selected_camera_status_callback,
            10,
        )

        self.pub = self.create_publisher(String, '/overview/sensor_health', 10)
        self.timer = self.create_timer(1.0 / self.publish_hz, self.publish_health)

        self.get_logger().info(
            'sensor link monitor started for '
            f'{len(self.target_names)} WAM-Vs, sensors={list(SENSORS)}'
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

    def sensor_callback(self, target: str, sensor_name: str):
        self.last_seen[(target, sensor_name)] = time.time()

    def selected_camera_status_callback(self, msg: String):
        try:
            status = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        target = str(status.get('selected_target', '')).strip()
        if target not in self.target_names:
            return

        if bool(status.get('bridge_running', False)) and float(status.get('output_hz', 0.0) or 0.0) > 0.0:
            self.last_seen[(target, 'camera')] = time.time()

    def publish_health(self):
        now = time.time()
        vehicles = {}

        for target in self.target_names:
            sensors = {}
            for sensor_name, spec in SENSORS.items():
                last_seen = self.last_seen.get((target, sensor_name))
                age_sec = None if last_seen is None else max(0.0, now - last_seen)
                online = age_sec is not None and age_sec <= self.online_timeout_sec
                sensors[sensor_name] = {
                    'online': online,
                    'age_sec': age_sec,
                    'topic': spec['topic'].format(name=target),
                    'label': spec['label'],
                    'type': spec['type'],
                }

            vehicles[target] = sensors

        payload = {
            'stamp': now,
            'online_timeout_sec': self.online_timeout_sec,
            'sensor_order': list(SENSORS.keys()),
            'vehicles': vehicles,
        }

        msg = String()
        msg.data = json.dumps(payload, separators=(',', ':'))
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SensorLinkMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
