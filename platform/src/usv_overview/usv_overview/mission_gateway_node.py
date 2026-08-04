#!/usr/bin/env python3
from __future__ import annotations

import json
import uuid

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from .mission_contract import build_request, extract_grid_action


class MissionGatewayNode(Node):
    def __init__(self) -> None:
        super().__init__("mission_gateway_node")
        self.declare_parameter(
            "target_names",
            [f"wamv_{i:02d}" for i in range(1, 11)],
        )
        self.declare_parameter("intent_topic", "/voice/intent")
        self.declare_parameter("request_topic", "/mission/request")
        self.declare_parameter("status_topic", "/mission/status")

        self.target_names = list(self.get_parameter("target_names").value)
        self.request_pub = self.create_publisher(
            String, str(self.get_parameter("request_topic").value), 10
        )
        self.status_pub = self.create_publisher(
            String, str(self.get_parameter("status_topic").value), 10
        )
        self.intent_sub = self.create_subscription(
            String,
            str(self.get_parameter("intent_topic").value),
            self.intent_callback,
            10,
        )

    def intent_callback(self, msg: String) -> None:
        try:
            intent = json.loads(msg.data)
        except json.JSONDecodeError:
            self.publish_status(
                "",
                None,
                "rejected",
                "invalid_json",
                "voice intent is not JSON",
            )
            return

        action, intent_error = extract_grid_action(intent)
        if intent_error:
            self.publish_status(
                "",
                None,
                "rejected",
                intent_error,
                "invalid voice intent",
            )
            return
        if action is None:
            return

        request_id = str(uuid.uuid4())
        stamp_ns = self.get_clock().now().nanoseconds
        request, status = build_request(
            action,
            self.target_names,
            request_id,
            stamp_ns,
        )
        if request is not None:
            payload = json.dumps(request, ensure_ascii=False)
            self.request_pub.publish(String(data=payload))
        status_payload = json.dumps(status, ensure_ascii=False)
        self.status_pub.publish(String(data=status_payload))

    def publish_status(
        self,
        request_id: str,
        vehicle: str | None,
        state: str,
        reason_code: str,
        detail: str,
    ) -> None:
        payload = {
            "schema": "usv_mission_status/v1",
            "request_id": request_id or str(uuid.uuid4()),
            "stamp_ns": self.get_clock().now().nanoseconds,
            "vehicle": vehicle,
            "state": state,
            "reason_code": reason_code,
            "detail": detail,
        }
        status_json = json.dumps(payload, ensure_ascii=False)
        self.status_pub.publish(String(data=status_json))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MissionGatewayNode()
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
