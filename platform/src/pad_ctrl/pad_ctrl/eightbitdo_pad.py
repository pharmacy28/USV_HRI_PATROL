#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class EightBitDoPad(Node):
    def __init__(self):
        super().__init__("eightbitdo_pad")

        self.declare_parameter(
            "target_names",
            [f"wamv_{i:02d}" for i in range(1, 11)],
        )
        self.declare_parameter("initial_target", "wamv_01")

        self.declare_parameter("linear_axis", 1)
        self.declare_parameter("angular_axis", 0)
        self.declare_parameter("deadman_button", 4)

        self.declare_parameter("invert_linear", False)
        self.declare_parameter("invert_turn", True)

        # D-pad:
        # axis 7: 上下，切 WAM-V
        # axis 6: 左右，切传感器
        self.declare_parameter("target_axis", 7)
        self.declare_parameter("sensor_axis", 6)

        self.declare_parameter("axis_threshold", 0.5)
        self.declare_parameter("switch_debounce", 0.35)
        self.declare_parameter("switch_release_time", 0.25)
        self.declare_parameter("page_next_button", 5)
        self.declare_parameter("page_prev_button", 7)
        self.declare_parameter("page_prev_axis", 5)
        self.declare_parameter("grid_toggle_button", 3)

        self.target_names = list(self.get_parameter("target_names").value)
        self.current_target = str(self.get_parameter("initial_target").value)

        if self.current_target not in self.target_names:
            self.current_target = self.target_names[0]

        self.target_index = self.target_names.index(self.current_target)

        self.linear_axis = int(self.get_parameter("linear_axis").value)
        self.angular_axis = int(self.get_parameter("angular_axis").value)
        self.deadman_button = int(self.get_parameter("deadman_button").value)

        self.invert_linear = bool(self.get_parameter("invert_linear").value)
        self.invert_turn = bool(self.get_parameter("invert_turn").value)

        self.target_axis = int(self.get_parameter("target_axis").value)
        self.sensor_axis = int(self.get_parameter("sensor_axis").value)

        self.axis_threshold = float(self.get_parameter("axis_threshold").value)
        self.switch_debounce = float(self.get_parameter("switch_debounce").value)
        self.switch_release_time = float(self.get_parameter("switch_release_time").value)

        self.sensor_names = ["camera", "sonar", "ir", "radar"]
        self.sensor_index = 0
        self.current_sensor = self.sensor_names[self.sensor_index]

        self.page_names = ["fpv", "overview", "status", "record"]
        self.page_index = 0
        self.current_page = self.page_names[self.page_index]

        self.page_next_button = int(self.get_parameter("page_next_button").value)
        self.page_prev_button = int(self.get_parameter("page_prev_button").value)
        self.page_prev_axis = int(self.get_parameter("page_prev_axis").value)
        self.grid_toggle_button = int(self.get_parameter("grid_toggle_button").value)

        self.last_target_switch = 0
        self.last_sensor_switch = 0
        self.last_target_time = 0.0
        self.last_sensor_time = 0.0
        self.last_target_neutral_time = time.monotonic()
        self.last_sensor_neutral_time = time.monotonic()
        self.last_page_next_pressed = False
        self.last_page_prev_pressed = False
        self.last_grid_toggle_pressed = False
        self.last_page_time = 0.0
        self.last_grid_toggle_time = 0.0

        self.joy_sub = self.create_subscription(
            Joy,
            "/joy",
            self.joy_callback,
            10,
        )

        self.manual_cmd_pub = self.create_publisher(
            Twist,
            "/operator/manual_cmd",
            10,
        )

        self.manual_target_pub = self.create_publisher(
            String,
            "/fleet/manual_target",
            10,
        )

        self.view_sensor_pub = self.create_publisher(
            String,
            "/ui/view_sensor",
            10,
        )

        self.view_page_pub = self.create_publisher(
            String,
            "/ui/view_page",
            10,
        )

        self.grid_toggle_pub = self.create_publisher(
            String,
            "/ui/toggle_grid",
            10,
        )

        self.publish_target()
        self.publish_sensor()
        self.publish_page()

        self.get_logger().info("eightbitdo_pad started")
        self.get_logger().info(f"Initial target: {self.current_target}")
        self.get_logger().info(f"Initial sensor: {self.current_sensor}")
        self.get_logger().info(f"Initial UI page: {self.current_page}")
        self.get_logger().info("D-pad up/down: switch WAM-V")
        self.get_logger().info("D-pad left/right: switch sensor stream")
        self.get_logger().info("RB/RT: switch UI page")
        self.get_logger().info("Y: toggle overview grid")

    def get_axis(self, axes, index: int) -> float:
        if index < 0 or index >= len(axes):
            return 0.0
        return float(axes[index])

    def get_button(self, buttons, index: int) -> int:
        if index < 0 or index >= len(buttons):
            return 0
        return int(buttons[index])

    def axis_to_switch(self, axes, axis_index: int) -> int:
        value = self.get_axis(axes, axis_index)

        if value > self.axis_threshold:
            return 1
        if value < -self.axis_threshold:
            return -1
        return 0

    def axis_pressed(self, axes, axis_index: int) -> bool:
        return self.get_axis(axes, axis_index) < -self.axis_threshold

    def debounce_ok(self, last_time: float) -> bool:
        return (time.monotonic() - last_time) >= self.switch_debounce

    def publish_target(self):
        msg = String()
        msg.data = self.current_target
        self.manual_target_pub.publish(msg)
        self.get_logger().info(f"Current target: {self.current_target}")

    def switch_target(self, step: int):
        self.target_index = (self.target_index + step) % len(self.target_names)
        self.current_target = self.target_names[self.target_index]
        self.publish_target()

    def publish_sensor(self):
        msg = String()
        msg.data = self.current_sensor
        self.view_sensor_pub.publish(msg)
        self.get_logger().info(f"Current sensor: {self.current_sensor}")

    def switch_sensor(self, step: int):
        self.sensor_index = (self.sensor_index + step) % len(self.sensor_names)
        self.current_sensor = self.sensor_names[self.sensor_index]
        self.publish_sensor()

    def publish_page(self):
        msg = String()
        msg.data = self.current_page
        self.view_page_pub.publish(msg)
        self.get_logger().info(f"Current UI page: {self.current_page}")

    def switch_page(self, step: int):
        self.page_index = (self.page_index + step) % len(self.page_names)
        self.current_page = self.page_names[self.page_index]
        self.publish_page()

    def publish_grid_toggle(self):
        msg = String()
        msg.data = "toggle"
        self.grid_toggle_pub.publish(msg)
        self.get_logger().info("Toggle overview grid")

    def joy_callback(self, msg: Joy):
        # 1. 左摇杆 + deadman 输出手动控制
        deadman = self.get_button(msg.buttons, self.deadman_button)

        cmd = Twist()

        if deadman:
            linear = self.get_axis(msg.axes, self.linear_axis)
            angular = self.get_axis(msg.axes, self.angular_axis)

            if self.invert_linear:
                linear = -linear

            if self.invert_turn:
                angular = -angular

            cmd.linear.x = linear
            cmd.angular.z = angular
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.manual_cmd_pub.publish(cmd)

        now = time.monotonic()

        # 2. 上下键：切 WAM-V
        target_switch = self.axis_to_switch(msg.axes, self.target_axis)

        if target_switch == 0 and self.last_target_switch != 0:
            self.last_target_neutral_time = now

        if (
            target_switch != 0
            and self.last_target_switch == 0
            and self.debounce_ok(self.last_target_time)
            and now - self.last_target_neutral_time >= self.switch_release_time
        ):
            # 目前你的“上键”对应 target_switch > 0
            # 上：正向切换；下：反向切换
            if target_switch > 0:
                self.switch_target(+1)
            else:
                self.switch_target(-1)

            self.last_target_time = now

        self.last_target_switch = target_switch

        # 3. 左右键：切传感器
        sensor_switch = self.axis_to_switch(msg.axes, self.sensor_axis)

        if sensor_switch == 0 and self.last_sensor_switch != 0:
            self.last_sensor_neutral_time = now

        if (
            sensor_switch != 0
            and self.last_sensor_switch == 0
            and self.debounce_ok(self.last_sensor_time)
            and now - self.last_sensor_neutral_time >= self.switch_release_time
        ):
            # 你的“左键”对应 sensor_switch > 0
            # 左：反向切换；右：正向切换
            if sensor_switch > 0:
                self.switch_sensor(-1)
            else:
                self.switch_sensor(+1)

            self.last_sensor_time = now

        self.last_sensor_switch = sensor_switch

        # 4. RB / RT：切 UI 页面
        page_next_pressed = bool(self.get_button(msg.buttons, self.page_next_button))
        page_prev_pressed = bool(self.get_button(msg.buttons, self.page_prev_button))
        page_prev_pressed = page_prev_pressed or self.axis_pressed(msg.axes, self.page_prev_axis)

        if (
            page_next_pressed
            and not self.last_page_next_pressed
            and self.debounce_ok(self.last_page_time)
        ):
            self.switch_page(+1)
            self.last_page_time = now

        if (
            page_prev_pressed
            and not self.last_page_prev_pressed
            and self.debounce_ok(self.last_page_time)
        ):
            self.switch_page(-1)
            self.last_page_time = now

        self.last_page_next_pressed = page_next_pressed
        self.last_page_prev_pressed = page_prev_pressed

        # 5. Y：开关全局态势概览网格
        grid_toggle_pressed = bool(self.get_button(msg.buttons, self.grid_toggle_button))

        if (
            grid_toggle_pressed
            and not self.last_grid_toggle_pressed
            and self.debounce_ok(self.last_grid_toggle_time)
        ):
            self.publish_grid_toggle()
            self.last_grid_toggle_time = now

        self.last_grid_toggle_pressed = grid_toggle_pressed


def main(args=None):
    rclpy.init(args=args)
    node = EightBitDoPad()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            try:
                zero = Twist()
                node.manual_cmd_pub.publish(zero)
            except Exception:
                pass

        try:
            node.destroy_node()
        except Exception:
            pass

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
