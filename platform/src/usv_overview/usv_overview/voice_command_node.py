#!/usr/bin/env python3
import json
import math
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from .voice_intent import is_manual_selection, parse_grid_assignment, parse_vehicle


PAGE_ALIASES = {
    "fpv": ["fpv", "第一人称", "视频", "摄像头画面", "主画面"],
    "overview": ["overview", "全局", "态势", "地图", "全局态势"],
    "status": ["status", "状态", "系统状态"],
    "record": ["record", "记录", "数据记录"],
}


SENSOR_ALIASES = {
    "camera": ["camera", "摄像头", "相机", "视频"],
    "sonar": ["sonar", "声纳", "前扫"],
    "ir": ["ir", "红外"],
    "radar": ["radar", "雷达"],
}


class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__("voice_command_node")

        self.declare_parameter("target_names", [f"wamv_{i:02d}" for i in range(1, 11)])
        self.declare_parameter("transcript_topic", "/voice/transcript")
        self.declare_parameter("enable_actions", True)
        self.declare_parameter("status_hz", 1.0)

        self.target_names = list(self.get_parameter("target_names").value)
        self.transcript_topic = str(self.get_parameter("transcript_topic").value)
        self.enable_actions = bool(self.get_parameter("enable_actions").value)
        self.status_hz = max(0.2, float(self.get_parameter("status_hz").value))

        self.last_transcript = ""
        self.last_intent = {}
        self.last_gaze = None
        self.fleet_state = {}
        self.command_count = 0
        self.last_command_time = 0.0

        self.transcript_sub = self.create_subscription(
            String,
            self.transcript_topic,
            self.transcript_callback,
            10,
        )
        self.gaze_sub = self.create_subscription(String, "/tobii/gaze", self.gaze_callback, 20)
        self.fleet_sub = self.create_subscription(String, "/overview/fleet_state", self.fleet_callback, 10)
        self.status_pub = self.create_publisher(String, "/voice/status", 10)
        self.intent_pub = self.create_publisher(String, "/voice/intent", 10)
        self.view_page_pub = self.create_publisher(String, "/ui/view_page", 10)
        self.view_sensor_pub = self.create_publisher(String, "/ui/view_sensor", 10)
        self.grid_toggle_pub = self.create_publisher(String, "/ui/toggle_grid", 10)
        self.manual_target_pub = self.create_publisher(String, "/fleet/manual_target", 10)
        self.timer = self.create_timer(1.0 / self.status_hz, self.publish_status)
        self.get_logger().info(f"voice command node listening on {self.transcript_topic}")

    def transcript_callback(self, msg: String):
        transcript = self.decode_transcript(msg.data)
        if not transcript:
            return

        self.last_transcript = transcript
        self.command_count += 1
        self.last_command_time = time.time()

        intent = self.parse_intent(transcript)
        self.last_intent = intent
        self.publish_json(self.intent_pub, intent)

        if self.enable_actions:
            self.apply_intent(intent)

        self.publish_status()

    def decode_transcript(self, payload: str) -> str:
        text = payload.strip()
        if not text:
            return ""

        if text.startswith("{"):
            try:
                data = json.loads(text)
                if data.get("type") == "cancel":
                    self.last_intent = {"state": "cancelled", "stamp": time.time()}
                    self.last_command_time = time.time()
                    self.publish_status()
                    return ""
                text = str(data.get("text") or data.get("transcript") or "").strip()
            except json.JSONDecodeError:
                pass

        return text

    def parse_intent(self, text: str) -> dict:
        intent = {
            "stamp": time.time(),
            "source": "voice_command_node",
            "text": text,
            "actions": [],
            "context": {
                "gaze": self.gaze_reference(text),
                "fleet_count": len(self.fleet_state.get("vehicles", [])),
            },
        }

        target, _target_error = parse_vehicle(text, self.target_names)
        grid_goal = parse_grid_assignment(text, self.target_names)
        if grid_goal:
            intent["actions"].append(grid_goal)
        elif is_manual_selection(text) and target:
            intent["actions"].append({"type": "select_target", "target": target})

        page = self.match_alias(text, PAGE_ALIASES)
        if page:
            intent["actions"].append({"type": "set_page", "page": page})

        sensor = self.match_alias(text, SENSOR_ALIASES)
        if sensor and any(key in text for key in ["切", "看", "显示", "打开", "换", "传感"]):
            intent["actions"].append({"type": "set_sensor", "sensor": sensor})

        if "网格" in text:
            intent["actions"].append({"type": "toggle_grid"})

        if not intent["actions"]:
            intent["actions"].append({"type": "unhandled"})

        return intent

    def match_alias(self, text: str, aliases: dict):
        lowered = text.lower()
        for key, words in aliases.items():
            for word in words:
                if word.lower() in lowered:
                    return key
        return None

    def gaze_reference(self, text: str):
        if self.last_gaze is None:
            return None

        if not any(word in text for word in ["这里", "那里", "这边", "那边", "看", "注视", "指向"]):
            return None

        age = time.time() - float(self.last_gaze.get("stamp", 0.0))
        if age > 2.0:
            return None

        return {
            "x_norm": self.last_gaze.get("x_norm"),
            "y_norm": self.last_gaze.get("y_norm"),
            "age_sec": round(age, 3),
        }

    def apply_intent(self, intent: dict):
        for action in intent.get("actions", []):
            action_type = action.get("type")

            if action_type == "select_target":
                self.publish_text(self.manual_target_pub, action.get("target", ""))
            elif action_type == "set_page":
                self.publish_text(self.view_page_pub, action.get("page", ""))
            elif action_type == "set_sensor":
                self.publish_text(self.view_sensor_pub, action.get("sensor", ""))
            elif action_type == "toggle_grid":
                self.publish_text(self.grid_toggle_pub, "toggle")

    def gaze_callback(self, msg: String):
        try:
            gaze = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        if not bool(gaze.get("valid", False)):
            return

        x_norm = self.safe_float(gaze.get("x_norm"))
        y_norm = self.safe_float(gaze.get("y_norm"))
        if not self.unit_value(x_norm) or not self.unit_value(y_norm):
            return

        self.last_gaze = {
            "stamp": time.time(),
            "x_norm": x_norm,
            "y_norm": y_norm,
        }

    def fleet_callback(self, msg: String):
        try:
            self.fleet_state = json.loads(msg.data)
        except json.JSONDecodeError:
            return

    def publish_status(self):
        status = {
            "stamp": time.time(),
            "node": "voice_command_node",
            "mode": "rules",
            "enabled": self.enable_actions,
            "transcript_topic": self.transcript_topic,
            "last_transcript": self.last_transcript,
            "last_intent": self.last_intent,
            "command_count": self.command_count,
            "last_command_age_sec": max(0.0, time.time() - self.last_command_time)
            if self.last_command_time
            else None,
        }
        self.publish_json(self.status_pub, status)

    def publish_text(self, publisher, text: str):
        if not text:
            return
        msg = String()
        msg.data = text
        publisher.publish(msg)

    def publish_json(self, publisher, payload: dict):
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        publisher.publish(msg)

    def safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return math.nan

    def unit_value(self, value: float):
        return math.isfinite(value) and 0.0 <= value <= 1.0


def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommandNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
