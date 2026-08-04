#!/usr/bin/env python3
"""
Linux side Tobii UDP-to-LSL bridge.

Expected input is JSON UDP packets from the Windows Unity GazeUdpSender.
Published LSL channel order:

  x_norm, y_norm, x_px, y_px, valid

x_norm/y_norm use top-left origin, where (0, 0) is the top-left of the display
that Unity is rendering on and (1, 1) is the bottom-right.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import sys
import time
from typing import Any, Optional

from pylsl import StreamInfo, StreamOutlet


DEFAULT_PORT = 15555
DEFAULT_HOST = "0.0.0.0"
DEFAULT_STREAM_NAME = "TobiiGaze"
SAMPLE_RATE = 60.0
CHANNELS = [
    ("x_norm", "ratio"),
    ("y_norm", "ratio"),
    ("x_px", "pixel"),
    ("y_px", "pixel"),
    ("valid", "bool"),
]


def finite(value: float) -> bool:
    return math.isfinite(value)


def unit(value: float) -> bool:
    return finite(value) and 0.0 <= value <= 1.0


def get_float(packet: dict[str, Any], *keys: str, default: float = math.nan) -> float:
    for key in keys:
        if key in packet:
            try:
                return float(packet[key])
            except (TypeError, ValueError):
                return default
    return default


def get_valid(packet: dict[str, Any]) -> bool:
    value = packet.get("valid", packet.get("gv", packet.get("is_valid", 0)))
    try:
        return bool(round(float(value)))
    except (TypeError, ValueError):
        return False


def normalize_packet(
    packet: dict[str, Any],
    fallback_width: int,
    fallback_height: int,
    legacy_viewport_origin: str,
):
    valid = get_valid(packet)

    screen_w = get_float(packet, "screen_w", "screen_width", "sw", default=float(fallback_width))
    screen_h = get_float(packet, "screen_h", "screen_height", "sh", default=float(fallback_height))

    x_norm = get_float(packet, "x_norm", "nx", default=math.nan)
    y_norm = get_float(packet, "y_norm", "ny", default=math.nan)

    x_px = get_float(packet, "x_px", "screen_x", "sx", default=math.nan)
    y_px = get_float(packet, "y_px", "screen_y", "sy", default=math.nan)

    viewport_x = get_float(packet, "viewport_x", "vx", default=math.nan)
    viewport_y = get_float(packet, "viewport_y", "vy", default=math.nan)

    if valid and unit(x_norm) and unit(y_norm):
        pass
    elif valid and unit(viewport_x) and unit(viewport_y):
        x_norm = viewport_x
        y_norm = 1.0 - viewport_y if legacy_viewport_origin == "bottom-left" else viewport_y
    elif valid and screen_w > 0 and screen_h > 0 and finite(x_px) and finite(y_px):
        if -0.05 * screen_w <= x_px <= 1.05 * screen_w and -0.05 * screen_h <= y_px <= 1.05 * screen_h:
            x_norm = max(0.0, min(1.0, x_px / screen_w))
            y_norm = max(0.0, min(1.0, y_px / screen_h))

    if not (valid and unit(x_norm) and unit(y_norm)):
        return [math.nan, math.nan, math.nan, math.nan, 0.0], False

    if not finite(x_px) and screen_w > 0:
        x_px = x_norm * screen_w
    if not finite(y_px) and screen_h > 0:
        y_px = y_norm * screen_h

    return [x_norm, y_norm, x_px, y_px, 1.0], True


def build_outlet(stream_name: str):
    info = StreamInfo(
        name=stream_name,
        type="Gaze",
        channel_count=len(CHANNELS),
        nominal_srate=SAMPLE_RATE,
        channel_format="float32",
        source_id=f"tobii_udp_bridge_{socket.gethostname()}",
    )

    channels = info.desc().append_child("channels")
    for label, unit_name in CHANNELS:
        channel = channels.append_child("channel")
        channel.append_child_value("label", label)
        channel.append_child_value("unit", unit_name)

    outlet = StreamOutlet(info)
    print(f"[LSL] outlet: {stream_name} ({len(CHANNELS)}ch @ {SAMPLE_RATE:.0f}Hz)")
    print("[LSL] channels: " + ", ".join(label for label, _unit in CHANNELS))
    return outlet


def parse_json(data: bytes) -> Optional[dict[str, Any]]:
    try:
        return json.loads(data.decode("utf-8").strip())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def run(args):
    outlet = build_outlet(args.stream_name)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind((args.host, args.port))
    except OSError as exc:
        print(f"[ERROR] cannot bind UDP {args.host}:{args.port}: {exc}")
        sys.exit(1)

    sock.settimeout(1.0)
    print(f"[UDP] listening on {args.host}:{args.port}")

    total = 0
    valid_total = 0
    window_total = 0
    window_valid = 0
    last_report = time.time()
    last_packet_time = time.time()

    try:
        while True:
            try:
                data, addr = sock.recvfrom(8192)
            except socket.timeout:
                if time.time() - last_packet_time >= args.wait_warn_sec:
                    print("[WAIT] no Unity UDP packet received")
                    last_packet_time = time.time()
                continue

            packet = parse_json(data)
            if packet is None:
                continue

            last_packet_time = time.time()
            sample, valid = normalize_packet(
                packet,
                args.screen_width,
                args.screen_height,
                args.legacy_viewport_origin,
            )
            outlet.push_sample(sample)

            total += 1
            window_total += 1
            if valid:
                valid_total += 1
                window_valid += 1

            now = time.time()
            if now - last_report >= args.report_interval:
                hz = window_total / max(1e-6, now - last_report)
                valid_pct = 100.0 * window_valid / max(1, window_total)
                if valid:
                    gaze = f"norm=({sample[0]:.3f},{sample[1]:.3f}) px=({sample[2]:.0f},{sample[3]:.0f})"
                else:
                    gaze = "INVALID"
                print(
                    f"[STREAM] {hz:.1f}Hz | valid={valid_pct:.0f}% | "
                    f"total={total} | {gaze} | from={addr[0]}:{addr[1]}"
                )
                window_total = 0
                window_valid = 0
                last_report = now

    except KeyboardInterrupt:
        print(f"\n[DONE] streamed {total} packets, valid {valid_total}")
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="Receive Windows Unity Tobii UDP and publish an LSL stream")
    parser.add_argument("--host", default=DEFAULT_HOST, help="UDP bind address; use 0.0.0.0 for another computer")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--stream-name", default=DEFAULT_STREAM_NAME)
    parser.add_argument("--screen-width", type=int, default=1920)
    parser.add_argument("--screen-height", type=int, default=1080)
    parser.add_argument(
        "--legacy-viewport-origin",
        choices=("bottom-left", "top-left"),
        default="bottom-left",
        help="origin of legacy vx/vy packets that do not include x_norm/y_norm",
    )
    parser.add_argument("--report-interval", type=float, default=1.0)
    parser.add_argument("--wait-warn-sec", type=float, default=5.0)
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
