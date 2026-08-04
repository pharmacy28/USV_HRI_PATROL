#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64


def clamp(value, low, high):
    return max(low, min(high, value))


class Wamv8BitDoTeleop(Node):
    def __init__(self):
        super().__init__("wamv_8bitdo_teleop")

        self.declare_parameter("axis_throttle", 1)
        self.declare_parameter("axis_turn", 0)
        self.declare_parameter("deadman_button", 4)
        self.declare_parameter("max_thrust", 4000.0)
        self.declare_parameter("turn_scale", 0.8)
        self.declare_parameter("deadzone", 0.08)
        self.declare_parameter("joy_timeout", 0.5)

        self.axis_throttle = self.get_parameter("axis_throttle").value
        self.axis_turn = self.get_parameter("axis_turn").value
        self.deadman_button = self.get_parameter("deadman_button").value
        self.max_thrust = float(self.get_parameter("max_thrust").value)
        self.turn_scale = float(self.get_parameter("turn_scale").value)
        self.deadzone = float(self.get_parameter("deadzone").value)
        self.joy_timeout = float(self.get_parameter("joy_timeout").value)

        self.left_pub = self.create_publisher(
            Float64,
            "/wamv/thrusters/left/thrust",
            10,
        )
        self.right_pub = self.create_publisher(
            Float64,
            "/wamv/thrusters/right/thrust",
            10,
        )

        self.joy_sub = self.create_subscription(
            Joy,
            "/joy",
            self.joy_callback,
            10,
        )

        self.last_joy_time = 0.0
        self.timer = self.create_timer(0.05, self.safety_timer)

        self.get_logger().info("WAM-V 8BitDo teleop started.")
        self.get_logger().info(
            f"axis_throttle={self.axis_throttle}, "
            f"axis_turn={self.axis_turn}, "
            f"deadman_button={self.deadman_button}, "
            f"max_thrust={self.max_thrust}"
        )

    def apply_deadzone(self, value):
        if abs(value) < self.deadzone:
            return 0.0
        return value

    def publish_thrust(self, left, right):
        left_msg = Float64()
        right_msg = Float64()

        left_msg.data = float(left)
        right_msg.data = float(right)

        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)

    def stop(self):
        self.publish_thrust(0.0, 0.0)

    def joy_callback(self, msg):
        self.last_joy_time = time.time()

        if len(msg.axes) <= max(self.axis_throttle, self.axis_turn):
            self.get_logger().warn("Joy axes index out of range.")
            self.stop()
            return

        if len(msg.buttons) <= self.deadman_button:
            self.get_logger().warn("Joy button index out of range.")
            self.stop()
            return

        enabled = msg.buttons[self.deadman_button] == 1

        if not enabled:
            self.stop()
            return

        # 多数 Xbox / 8BitDo XInput 映射中：
        # axes[1]：左摇杆上下。向前通常是 +1 或 -1，若方向反了，改这里的负号。
        throttle = self.apply_deadzone(msg.axes[self.axis_throttle])
        turn = -self.apply_deadzone(msg.axes[self.axis_turn])

        throttle_cmd = throttle * self.max_thrust
        turn_cmd = turn * self.max_thrust * self.turn_scale

        left = clamp(throttle_cmd + turn_cmd, -self.max_thrust, self.max_thrust)
        right = clamp(throttle_cmd - turn_cmd, -self.max_thrust, self.max_thrust)

        self.publish_thrust(left, right)

    def safety_timer(self):
        if self.last_joy_time == 0.0:
            return

        if time.time() - self.last_joy_time > self.joy_timeout:
            self.stop()


def main():
    rclpy.init()
    node = Wamv8BitDoTeleop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()