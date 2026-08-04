#!/usr/bin/env python3
import ast
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import threading
import time

import rclpy
from geometry_msgs.msg import PoseArray
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from std_msgs.msg import String
import yaml


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class FleetStateNode(Node):
    def __init__(self):
        super().__init__('overview_fleet_state')

        self.declare_parameter(
            'target_names',
            [f'wamv_{i:02d}' for i in range(1, 11)],
        )
        self.declare_parameter('config_file', '')
        self.declare_parameter('world', 'air_crash_sar')
        self.declare_parameter('use_gz_named_pose', True)

        self.target_names = self.parse_target_names(
            self.get_parameter('target_names').value
        )
        self.config_file = str(self.get_parameter('config_file').value)
        self.world = str(self.get_parameter('world').value)
        self.use_gz_named_pose = bool(self.get_parameter('use_gz_named_pose').value)
        self.fleet = {}
        self.initial_positions = {}
        self.dynamic_pose_indices = {}
        self.dynamic_pose_samples = {}
        self.last_dynamic_pose_wall_time = {}
        self.smoothed_speed = {}
        self.named_pose_samples = {}
        self.last_named_pose_wall_time = 0.0
        self.state_lock = threading.Lock()
        self.gz_pose_process = None
        self.gz_pose_thread = None
        self.seed_from_config(self.config_file)

        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.subs = [
            self.create_subscription(
                Odometry,
                f'/{name}/odometry',
                lambda msg, n=name: self.odom_callback(n, msg),
                qos,
            )
            for name in self.target_names
        ]
        self.dynamic_pose_sub = self.create_subscription(
            PoseArray,
            '/overview/dynamic_pose',
            self.dynamic_pose_callback,
            qos,
        )

        self.pub = self.create_publisher(String, '/overview/fleet_state', 10)
        self.timer = self.create_timer(0.1, self.publish_fleet_state)
        self.start_gz_named_pose_stream()

    def parse_target_names(self, value):
        if isinstance(value, str):
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed = [part.strip() for part in value.split(',')]
        else:
            parsed = value

        names = [str(name) for name in parsed if str(name)]

        if not names:
            names = [f'wamv_{i:02d}' for i in range(1, 11)]

        return names

    def seed_from_config(self, config_file: str):
        if not config_file:
            return

        path = Path(config_file).expanduser()
        if not path.exists():
            self.get_logger().warn(f'fleet config file not found: {path}')
            return

        try:
            entries = yaml.safe_load(path.read_text()) or []
        except (OSError, yaml.YAMLError) as exc:
            self.get_logger().warn(f'failed to read fleet config {path}: {exc}')
            return

        for entry in entries:
            name = str(entry.get('model_name', ''))
            if name not in self.target_names:
                continue

            position = entry.get('position', {})
            xyz = position.get('xyz', [0.0, 0.0, 0.0])
            rpy = position.get('rpy', [0.0, 0.0, 0.0])

            self.fleet[name] = {
                'name': name,
                'x': float(xyz[0]) if len(xyz) > 0 else 0.0,
                'y': float(xyz[1]) if len(xyz) > 1 else 0.0,
                'z': float(xyz[2]) if len(xyz) > 2 else 0.0,
                'yaw': float(rpy[2]) if len(rpy) > 2 else 0.0,
                'speed': 0.0,
                'stamp_sec': 0,
                'stamp_nanosec': 0,
                'source': 'config',
            }
            self.initial_positions[name] = (
                self.fleet[name]['x'],
                self.fleet[name]['y'],
                self.fleet[name]['z'],
            )

        if self.fleet:
            self.get_logger().info(f'seeded fleet state from config: {path}')

    def odom_callback(self, name: str, msg: Odometry):
        pose = msg.pose.pose
        twist = msg.twist.twist
        raw_speed = (
            twist.linear.x * twist.linear.x
            + twist.linear.y * twist.linear.y
            + twist.linear.z * twist.linear.z
        ) ** 0.5
        speed = self.smooth_speed(name, raw_speed)

        with self.state_lock:
            self.fleet[name] = {
                'name': name,
                'x': pose.position.x,
                'y': pose.position.y,
                'z': pose.position.z,
                'yaw': yaw_from_quaternion(pose.orientation),
                'speed': speed,
                'stamp_sec': msg.header.stamp.sec,
                'stamp_nanosec': msg.header.stamp.nanosec,
                'source': 'odometry',
            }

    def dynamic_pose_callback(self, msg: PoseArray):
        if not msg.poses:
            return
        if time.time() - self.last_named_pose_wall_time < 2.0:
            return

        if not self.dynamic_pose_indices:
            self.dynamic_pose_indices = self.build_dynamic_pose_mapping(msg)
            if self.dynamic_pose_indices:
                mapping = ', '.join(
                    f'{name}:#{index}' for name, index in self.dynamic_pose_indices.items()
                )
                self.get_logger().info(f'dynamic pose mapping established: {mapping}')

        now = self.get_clock().now().nanoseconds / 1e9

        for name, index in self.dynamic_pose_indices.items():
            if index >= len(msg.poses):
                continue

            pose = msg.poses[index]
            previous_xyz = self.dynamic_pose_samples.get(name)
            previous_time = self.last_dynamic_pose_wall_time.get(name)
            raw_speed = self.smoothed_speed.get(name, 0.0)

            if previous_xyz is not None and previous_time is not None:
                dt = now - previous_time
                if 0.02 <= dt <= 1.0:
                    dx = pose.position.x - previous_xyz[0]
                    dy = pose.position.y - previous_xyz[1]
                    dz = pose.position.z - previous_xyz[2]
                    candidate_speed = math.sqrt(dx * dx + dy * dy + dz * dz) / dt
                    if 0.0 <= candidate_speed <= 20.0:
                        raw_speed = candidate_speed

            self.dynamic_pose_samples[name] = (
                pose.position.x,
                pose.position.y,
                pose.position.z,
            )
            self.last_dynamic_pose_wall_time[name] = now
            speed = self.smooth_speed(name, raw_speed)
            with self.state_lock:
                self.fleet[name] = {
                    'name': name,
                    'x': pose.position.x,
                    'y': pose.position.y,
                    'z': pose.position.z,
                    'yaw': yaw_from_quaternion(pose.orientation),
                    'speed': speed,
                    'stamp_sec': msg.header.stamp.sec,
                    'stamp_nanosec': msg.header.stamp.nanosec,
                    'source': 'dynamic_pose_fallback',
                }

    def start_gz_named_pose_stream(self):
        if not self.use_gz_named_pose:
            return

        topic = f'/world/{self.world}/dynamic_pose/info'
        cmd = ['gz', 'topic', '-e', '-t', topic]
        env = os.environ.copy()

        try:
            self.gz_pose_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                env=env,
                start_new_session=True,
            )
        except Exception as exc:
            self.gz_pose_process = None
            self.get_logger().warn(f'failed to start gz named pose stream: {exc}')
            return

        self.gz_pose_thread = threading.Thread(
            target=self.read_gz_named_pose_stream,
            daemon=True,
        )
        self.gz_pose_thread.start()
        self.get_logger().info(f'using named Gazebo pose stream: {topic}')

    def read_gz_named_pose_stream(self):
        proc = self.gz_pose_process
        if proc is None or proc.stdout is None:
            return

        current = None
        section = ''
        depth = 0

        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue

            if current is None:
                if line == 'pose {':
                    current = self.empty_named_pose()
                    section = ''
                    depth = 1
                continue

            if line.endswith('{'):
                key = line[:-1].strip()
                depth += 1
                if key in {'position', 'orientation'}:
                    section = key
                continue

            if line == '}':
                depth -= 1
                if depth <= 0:
                    self.accept_named_pose(current)
                    current = None
                    section = ''
                elif depth == 1:
                    section = ''
                continue

            if line.startswith('name: '):
                current['name'] = line.split('"', 2)[1] if '"' in line else ''
                continue

            if section in {'position', 'orientation'} and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                try:
                    current[section][key] = float(value.strip())
                except ValueError:
                    pass

    def empty_named_pose(self):
        return {
            'name': '',
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
        }

    def accept_named_pose(self, data):
        name = data.get('name', '')
        if name not in self.target_names:
            return

        position = data['position']
        orientation = data['orientation']
        now = time.time()
        previous = self.named_pose_samples.get(name)
        raw_speed = self.smoothed_speed.get(name, 0.0)

        if previous is not None:
            dt = now - previous['time']
            if 0.02 <= dt <= 1.0:
                dx = position['x'] - previous['x']
                dy = position['y'] - previous['y']
                dz = position['z'] - previous['z']
                candidate_speed = math.sqrt(dx * dx + dy * dy + dz * dz) / dt
                if 0.0 <= candidate_speed <= 20.0:
                    raw_speed = candidate_speed

        self.named_pose_samples[name] = {
            'x': position['x'],
            'y': position['y'],
            'z': position['z'],
            'time': now,
        }
        self.last_named_pose_wall_time = now
        speed = self.smooth_speed(name, raw_speed)
        yaw = yaw_from_quaternion(
            type(
                'QuaternionLike',
                (),
                {
                    'x': orientation.get('x', 0.0),
                    'y': orientation.get('y', 0.0),
                    'z': orientation.get('z', 0.0),
                    'w': orientation.get('w', 1.0),
                },
            )()
        )

        sec = int(now)
        nanosec = int((now - sec) * 1e9)
        with self.state_lock:
            self.fleet[name] = {
                'name': name,
                'x': position['x'],
                'y': position['y'],
                'z': position['z'],
                'yaw': yaw,
                'speed': speed,
                'stamp_sec': sec,
                'stamp_nanosec': nanosec,
                'source': 'gz_named_pose',
            }

    def smooth_speed(self, name: str, raw_speed: float) -> float:
        previous = self.smoothed_speed.get(name)
        if previous is None:
            self.smoothed_speed[name] = max(0.0, float(raw_speed))
            return self.smoothed_speed[name]

        raw_speed = max(0.0, float(raw_speed))
        # Low-speed finite differences tend to jitter downward frame by frame.
        # Let rises respond quickly, but let drops decay more gently.
        alpha = 0.25
        if raw_speed < previous:
            alpha = 0.08 if previous > 0.03 else 0.16

        smoothed = previous + alpha * (raw_speed - previous)
        if smoothed < 0.005:
            smoothed = 0.0
        self.smoothed_speed[name] = smoothed
        return smoothed

    def build_dynamic_pose_mapping(self, msg: PoseArray):
        candidates = []
        for index, pose in enumerate(msg.poses):
            # Model-level world poses live in the task area. Link-relative poses
            # are clustered near the local origin and should not drive the map.
            if abs(pose.position.x) < 40.0 and abs(pose.position.y) < 40.0:
                continue
            candidates.append(index)

        mapping = {}
        used = set()

        for name in self.target_names:
            ref = self.initial_positions.get(name)
            if ref is None and name in self.fleet:
                ref = (
                    float(self.fleet[name].get('x', 0.0)),
                    float(self.fleet[name].get('y', 0.0)),
                    float(self.fleet[name].get('z', 0.0)),
                )
            if ref is None:
                continue

            best_index = None
            best_dist = None
            for index in candidates:
                if index in used:
                    continue
                pose = msg.poses[index]
                dx = pose.position.x - ref[0]
                dy = pose.position.y - ref[1]
                dz = pose.position.z - ref[2]
                dist = dx * dx + dy * dy + dz * dz

                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_index = index

            if best_index is not None:
                mapping[name] = best_index
                used.add(best_index)

        return mapping

    def publish_fleet_state(self):
        msg = String()
        with self.state_lock:
            vehicles = [
                dict(self.fleet[name])
                for name in self.target_names
                if name in self.fleet
            ]
        msg.data = json.dumps(
            {
                'vehicles': vehicles,
                'pose_source': (
                    'gz_named_pose'
                    if time.time() - self.last_named_pose_wall_time < 2.0
                    else 'fallback'
                ),
            }
        )
        self.pub.publish(msg)

    def stop_gz_named_pose_stream(self):
        proc = self.gz_pose_process
        self.gz_pose_process = None
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=2.0)
        except Exception:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass


def main(args=None):
    rclpy.init(args=args)
    node = FleetStateNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_gz_named_pose_stream()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
