#!/usr/bin/env python3
"""
Ubuntu side Tobii gaze receiver.

Receives an LSL stream named TobiiGaze and optionally republishes each sample as
JSON on a ROS 2 topic. The expected LSL channel order is:

  x_norm, y_norm, x_px, y_px, valid

x_norm/y_norm are screen-normalized coordinates in top-left origin convention.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from typing import Optional

from pylsl import StreamInlet, local_clock, resolve_byprop


DEFAULT_STREAM_NAME = "TobiiGaze"
DEFAULT_ROS_TOPIC = "/tobii/gaze"


@dataclass
class GazeSample:
    x_norm: float
    y_norm: float
    x_px: float
    y_px: float
    valid: bool
    raw: list
    lsl_timestamp: float
    recv_time: float
    latency_sec: Optional[float]

    def to_json(self) -> str:
        return json.dumps(
            {
                "stamp": self.recv_time,
                "lsl_timestamp": self.lsl_timestamp,
                "latency_sec": self.latency_sec,
                "x_norm": self.x_norm,
                "y_norm": self.y_norm,
                "x_px": self.x_px,
                "y_px": self.y_px,
                "valid": self.valid,
                "raw": self.raw,
            },
            separators=(",", ":"),
        )


def finite(value: float) -> bool:
    return math.isfinite(value)


def in_unit_range(value: float) -> bool:
    return finite(value) and 0.0 <= value <= 1.0


def decode_sample(sample: list, timestamp: float, latency_sec: Optional[float]) -> GazeSample:
    values = [float(v) for v in sample]
    recv_time = time.time()

    if len(values) < 5:
        return GazeSample(
            x_norm=math.nan,
            y_norm=math.nan,
            x_px=math.nan,
            y_px=math.nan,
            valid=False,
            raw=values,
            lsl_timestamp=timestamp,
            recv_time=recv_time,
            latency_sec=latency_sec,
        )

    x_norm, y_norm, x_px, y_px, valid_value = values[:5]
    valid = bool(round(valid_value))

    # New protocol: x_norm/y_norm already normalized. This is the only format
    # considered valid for downstream UI heatmaps.
    if valid and in_unit_range(x_norm) and in_unit_range(y_norm):
        return GazeSample(
            x_norm=x_norm,
            y_norm=y_norm,
            x_px=x_px if finite(x_px) else math.nan,
            y_px=y_px if finite(y_px) else math.nan,
            valid=True,
            raw=values,
            lsl_timestamp=timestamp,
            recv_time=recv_time,
            latency_sec=latency_sec,
        )

    # Legacy protocol fallback: [screen_x, screen_y, viewport_x, viewport_y, valid].
    # Unity viewport coordinates use bottom-left origin, so convert to top-left.
    legacy_viewport_x = values[2]
    legacy_viewport_y = values[3]
    if valid and in_unit_range(legacy_viewport_x) and in_unit_range(legacy_viewport_y):
        return GazeSample(
            x_norm=legacy_viewport_x,
            y_norm=1.0 - legacy_viewport_y,
            x_px=values[0] if finite(values[0]) else math.nan,
            y_px=values[1] if finite(values[1]) else math.nan,
            valid=True,
            raw=values,
            lsl_timestamp=timestamp,
            recv_time=recv_time,
            latency_sec=latency_sec,
        )

    return GazeSample(
        x_norm=math.nan,
        y_norm=math.nan,
        x_px=math.nan,
        y_px=math.nan,
        valid=False,
        raw=values,
        lsl_timestamp=timestamp,
        recv_time=recv_time,
        latency_sec=latency_sec,
    )


class OptionalRosPublisher:
    def __init__(self, enabled: bool, topic: str):
        self.enabled = enabled
        self.node = None
        self.publisher = None
        self.rclpy = None

        if not enabled:
            return

        try:
            import rclpy
            from std_msgs.msg import String
        except ImportError as exc:
            raise RuntimeError(
                "ROS publishing requested, but rclpy/std_msgs are unavailable. "
                "Run after sourcing ROS 2 and the workspace, or use --no-ros."
            ) from exc

        rclpy.init(args=None)
        self.rclpy = rclpy
        self.node = rclpy.create_node("tobii_gaze_lsl_receiver")
        self.publisher = self.node.create_publisher(String, topic, 10)
        self.msg_type = String
        print(f"[ROS] publishing gaze JSON on {topic}")

    def publish(self, payload: str):
        if not self.enabled:
            return

        msg = self.msg_type()
        msg.data = payload
        self.publisher.publish(msg)
        self.rclpy.spin_once(self.node, timeout_sec=0.0)

    def close(self):
        if not self.enabled:
            return

        self.node.destroy_node()
        if self.rclpy.ok():
            self.rclpy.shutdown()


def find_stream(stream_name: str, timeout: float):
    print(f"[LSL] resolving stream name='{stream_name}' timeout={timeout:.1f}s")
    streams = resolve_byprop("name", stream_name, timeout=timeout)

    if not streams:
        print(f"[ERROR] no LSL stream named '{stream_name}' found")
        print("  Check Windows Unity sender, Linux gaze_lsl_bridge.py, firewall, and subnet.")
        return None

    stream = streams[0]
    print(
        f"[LSL] connected candidate: {stream.name()} | "
        f"type={stream.type()} | channels={stream.channel_count()} | "
        f"rate={stream.nominal_srate():.1f}Hz | source={stream.source_id()}"
    )
    return stream


def run(args):
    ros_pub = OptionalRosPublisher(not args.no_ros, args.ros_topic)
    inlet = None
    time_correction = 0.0

    total = 0
    valid_total = 0
    valid_window = 0
    total_window = 0
    last_report = time.time()
    last_warn = 0.0

    try:
        while True:
            if inlet is None:
                stream = find_stream(args.stream_name, args.resolve_timeout)
                if stream is None:
                    if not args.reconnect:
                        return
                    time.sleep(1.0)
                    continue

                inlet = StreamInlet(stream, max_buflen=5)
                try:
                    time_correction = inlet.time_correction(timeout=2.0)
                    print(f"[LSL] time correction: {time_correction:.6f}s")
                except Exception as exc:
                    time_correction = 0.0
                    print(f"[WARN] LSL time correction unavailable: {exc}")

            sample, timestamp = inlet.pull_sample(timeout=1.0)

            if sample is None:
                if args.reconnect:
                    print("[WAIT] no LSL sample for 1s; keeping inlet alive")
                continue

            corrected_timestamp = timestamp + time_correction
            latency_sec = local_clock() - corrected_timestamp
            gaze = decode_sample(sample, corrected_timestamp, latency_sec)

            total += 1
            total_window += 1

            if gaze.valid:
                valid_total += 1
                valid_window += 1
                ros_pub.publish(gaze.to_json())
            else:
                now = time.time()
                if now - last_warn >= args.warn_interval:
                    print(f"[WARN] invalid gaze sample: {sample}")
                    last_warn = now
                if args.publish_invalid:
                    ros_pub.publish(gaze.to_json())

            now = time.time()
            if now - last_report >= args.report_interval:
                dt = now - last_report
                hz = total_window / dt if dt > 0 else 0.0
                valid_pct = 100.0 * valid_window / max(1, total_window)
                delay_text = "--" if gaze.latency_sec is None else f"{gaze.latency_sec:.4f}s"
                gaze_text = (
                    "INVALID"
                    if not gaze.valid
                    else f"norm=({gaze.x_norm:.3f},{gaze.y_norm:.3f}) "
                         f"px=({gaze.x_px:.0f},{gaze.y_px:.0f})"
                )
                print(
                    f"[RECV] {hz:.1f}Hz | valid={valid_pct:.0f}% | "
                    f"total={total} | {gaze_text} | delay={delay_text}"
                )
                last_report = now
                total_window = 0
                valid_window = 0

    except KeyboardInterrupt:
        print(f"\n[DONE] received {total} samples, valid {valid_total}")
    finally:
        ros_pub.close()


def main():
    parser = argparse.ArgumentParser(description="Receive Tobii gaze LSL stream on Ubuntu")
    parser.add_argument("--stream-name", default=DEFAULT_STREAM_NAME)
    parser.add_argument("--resolve-timeout", type=float, default=10.0)
    parser.add_argument("--report-interval", type=float, default=1.0)
    parser.add_argument("--warn-interval", type=float, default=2.0)
    parser.add_argument("--ros-topic", default=DEFAULT_ROS_TOPIC)
    parser.add_argument("--no-ros", action="store_true", help="print only; do not publish ROS topic")
    parser.add_argument("--publish-invalid", action="store_true", help="also publish invalid gaze samples")
    parser.add_argument("--reconnect", action="store_true", help="keep trying if stream is missing")
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
