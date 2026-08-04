#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64, String


def clamp(value, low, high):
    return max(low, min(high, value))


class ManualMux(Node):
    def __init__(self):
        super().__init__("manual_mux")

        self.declare_parameter(
            "target_names",
            [
                "wamv_01", "wamv_02", "wamv_03", "wamv_04", "wamv_05",
                "wamv_06", "wamv_07", "wamv_08", "wamv_09", "wamv_10",
            ],
        )
        self.declare_parameter("initial_target", "wamv_01")
        self.declare_parameter("max_thrust", 4000.0)
        self.declare_parameter("turn_scale", 0.5)
        self.declare_parameter("cmd_timeout", 0.5)
        self.declare_parameter("publish_rate", 20.0)
        self.declare_parameter("stop_old_on_switch", True)

        self.target_names = list(self.get_parameter("target_names").value)
        self.current_target = str(self.get_parameter("initial_target").value)

        if self.current_target not in self.target_names:
            self.target_names.insert(0, self.current_target)

        self.max_thrust = float(self.get_parameter("max_thrust").value)
        self.turn_scale = float(self.get_parameter("turn_scale").value)
        self.cmd_timeout = float(self.get_parameter("cmd_timeout").value)
        self.publish_rate = float(self.get_parameter("publish_rate").value)
        self.stop_old_on_switch = bool(self.get_parameter("stop_old_on_switch").value)

        self.left_pubs = {}
        self.right_pubs = {}

        for name in self.target_names:
            self.left_pubs[name] = self.create_publisher(
                Float64,
                f"/{name}/thrusters/left/thrust",
                10,
            )
            self.right_pubs[name] = self.create_publisher(
                Float64,
                f"/{name}/thrusters/right/thrust",
                10,
            )

        self.manual_cmd = Twist()
        self.last_cmd_time = 0.0

        self.cmd_sub = self.create_subscription(
            Twist,
            "/operator/manual_cmd",
            self.manual_cmd_callback,
            10,
        )

        self.target_sub = self.create_subscription(
            String,
            "/fleet/manual_target",
            self.target_callback,
            10,
        )

        self.target_state_pub = self.create_publisher(
            String,
            "/fleet/manual_target_state",
            10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_rate,
            self.timer_callback,
        )

        self.get_logger().info("usv_ctrl manual mux started.")
        self.get_logger().info(f"Targets: {self.target_names}")
        self.get_logger().info(f"Current target: {self.current_target}")
        self.get_logger().info(
            f"max_thrust={self.max_thrust}, turn_scale={self.turn_scale}"
        )
        self.publish_target_state()

    def publish_thrust(self, target, left, right):
        if target not in self.left_pubs:
            self.get_logger().warn(f"Unknown target: {target}")
            return

        left_msg = Float64()
        right_msg = Float64()
        left_msg.data = float(left)
        right_msg.data = float(right)

        self.left_pubs[target].publish(left_msg)
        self.right_pubs[target].publish(right_msg)

    def stop_target(self, target):
        self.publish_thrust(target, 0.0, 0.0)

    def stop_all(self):
        for name in self.target_names:
            self.stop_target(name)

    def target_callback(self, msg):
        new_target = msg.data.strip()

        if not new_target:
            return

        if new_target not in self.target_names:
            self.get_logger().warn(f"Reject unknown manual target: {new_target}")
            return

        if new_target == self.current_target:
            return

        old_target = self.current_target

        if self.stop_old_on_switch:
            self.stop_target(old_target)

        self.current_target = new_target
        self.publish_target_state()
        self.get_logger().info(f"Manual target switched: {old_target} -> {self.current_target}")

    def manual_cmd_callback(self, msg):
        self.manual_cmd = msg
        self.last_cmd_time = time.time()

    def twist_to_thrust(self, cmd):
        throttle = clamp(cmd.linear.x, -1.0, 1.0)
        turn = clamp(cmd.angular.z, -1.0, 1.0)

        throttle_cmd = throttle * self.max_thrust
        turn_cmd = turn * self.max_thrust * self.turn_scale

        left = clamp(throttle_cmd + turn_cmd, -self.max_thrust, self.max_thrust)
        right = clamp(throttle_cmd - turn_cmd, -self.max_thrust, self.max_thrust)

        return left, right

    def publish_target_state(self):
        msg = String()
        msg.data = self.current_target
        self.target_state_pub.publish(msg)

    def timer_callback(self):
        self.publish_target_state()

        if self.last_cmd_time == 0.0:
            return

        if time.time() - self.last_cmd_time > self.cmd_timeout:
            self.stop_target(self.current_target)
            return

        left, right = self.twist_to_thrust(self.manual_cmd)
        self.publish_thrust(self.current_target, left, right)


def main():
    rclpy.init()
    node = ManualMux()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            try:
                node.stop_all()
            except Exception:
                pass

        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
