#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String


class WhisperBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__("whisper_bridge_node")

        self.declare_parameter("voice_python", sys.executable)
        self.declare_parameter("transcript_topic", "/voice/transcript")
        self.declare_parameter("status_topic", "/voice/whisper_status")
        self.declare_parameter("model", "base")
        self.declare_parameter("model_dir", "")
        self.declare_parameter("language", "zh")
        self.declare_parameter("device", "cpu")
        self.declare_parameter("audio_backend", "auto")
        self.declare_parameter(
            "audio_device",
            "",
            ParameterDescriptor(dynamic_typing=True),
        )
        self.declare_parameter("sample_rate", 16000)
        self.declare_parameter("udp_bind", "0.0.0.0")
        self.declare_parameter("udp_port", 15556)
        self.declare_parameter("udp_source_ip", "")
        self.declare_parameter("udp_timeout_sec", 1.0)
        self.declare_parameter("udp_preroll_sec", 0.15)
        self.declare_parameter("chunk_sec", 1.5)
        self.declare_parameter("energy_threshold", 0.02)
        self.declare_parameter("audio_gain", 1.0)
        self.declare_parameter("no_speech_threshold", 0.8)
        self.declare_parameter(
            "initial_prompt",
            (
                "普通话多艇任务口令。常见短口令包括：二号船去E5、WAMV十号到A1、"
                "选择一号船、打开网格、切换全局态势。请保留船号和棋盘格编号，按原文输出。"
            ),
        )
        self.declare_parameter("threads", 2)
        self.declare_parameter("auto_start", True)
        self.declare_parameter("push_to_talk", True)
        self.declare_parameter("joy_topic", "/joy")
        self.declare_parameter("ptt_button", 0)
        self.declare_parameter("cancel_button", 1)
        self.declare_parameter("ptt_release_debounce_sec", 0.2)

        self.transcript_pub = self.create_publisher(
            String,
            str(self.get_parameter("transcript_topic").value),
            10,
        )
        self.status_pub = self.create_publisher(
            String,
            str(self.get_parameter("status_topic").value),
            10,
        )
        self.proc: subprocess.Popen[str] | None = None
        self.reader_threads: list[threading.Thread] = []
        self.last_worker_message = 0.0
        self.last_worker_payload: dict = {}
        self.audio_backend = str(self.get_parameter("audio_backend").value)
        self.push_to_talk = bool(self.get_parameter("push_to_talk").value)
        self.ptt_button = int(self.get_parameter("ptt_button").value)
        self.cancel_button = int(self.get_parameter("cancel_button").value)
        self.ptt_active = False
        self.ptt_session = 0
        self.cancelled_session = 0
        self.cancelled_sessions: set[int] = set()
        self.last_buttons: list[int] = []
        self.ptt_release_started_at: float | None = None
        self.ptt_release_debounce_sec = max(
            0.0,
            float(self.get_parameter("ptt_release_debounce_sec").value),
        )
        self.ptt_control_path = Path(tempfile.gettempdir()) / f"vrx_voice_ptt_{os.getpid()}.json"
        self.write_ptt_control()

        self.joy_sub = None
        if self.push_to_talk:
            self.joy_sub = self.create_subscription(
                Joy,
                str(self.get_parameter("joy_topic").value),
                self.joy_callback,
                10,
            )

        if bool(self.get_parameter("auto_start").value):
            self.start_worker()

        self.timer = self.create_timer(1.0, self.publish_health)

    def start_worker(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            return

        worker_path = Path(__file__).with_name("whisper_worker.py")
        voice_python = str(self.get_parameter("voice_python").value)
        cmd = [
            voice_python,
            str(worker_path),
            "--model",
            str(self.get_parameter("model").value),
            "--language",
            str(self.get_parameter("language").value),
            "--device",
            str(self.get_parameter("device").value),
            "--audio-backend",
            self.audio_backend,
            "--sample-rate",
            str(int(self.get_parameter("sample_rate").value)),
            "--chunk-sec",
            str(float(self.get_parameter("chunk_sec").value)),
            "--energy-threshold",
            str(float(self.get_parameter("energy_threshold").value)),
            "--audio-gain",
            str(float(self.get_parameter("audio_gain").value)),
            "--no-speech-threshold",
            str(float(self.get_parameter("no_speech_threshold").value)),
            "--initial-prompt",
            str(self.get_parameter("initial_prompt").value),
            "--threads",
            str(int(self.get_parameter("threads").value)),
        ]

        if self.audio_backend == "udp":
            cmd.extend(
                [
                    "--udp-bind",
                    str(self.get_parameter("udp_bind").value),
                    "--udp-port",
                    str(int(self.get_parameter("udp_port").value)),
                    "--udp-source-ip",
                    str(self.get_parameter("udp_source_ip").value),
                    "--udp-timeout-sec",
                    str(float(self.get_parameter("udp_timeout_sec").value)),
                    "--udp-preroll-sec",
                    str(float(self.get_parameter("udp_preroll_sec").value)),
                ]
            )

        model_dir = str(self.get_parameter("model_dir").value)
        if model_dir:
            cmd.extend(["--model-dir", model_dir])

        audio_device = str(self.get_parameter("audio_device").value)
        if audio_device:
            cmd.extend(["--audio-device", audio_device])

        if self.push_to_talk:
            cmd.extend(["--ptt-control-file", str(self.ptt_control_path)])

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
                start_new_session=True,
            )
        except Exception as exc:
            self.get_logger().error(f"failed to start whisper worker: {exc}")
            self.publish_status({"state": "start_failed", "error": str(exc)})
            return

        self.publish_status({"state": "started", "pid": self.proc.pid, "cmd": cmd})
        self.reader_threads = [
            threading.Thread(target=self.read_stdout, daemon=True),
            threading.Thread(target=self.read_stderr, daemon=True),
        ]
        for thread in self.reader_threads:
            thread.start()

    def read_stdout(self) -> None:
        if self.proc is None or self.proc.stdout is None:
            return
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            self.last_worker_message = time.time()
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                self.publish_status({"state": "worker_stdout", "line": line})
                continue

            self.last_worker_payload = payload

            msg_type = payload.get("type")
            if msg_type == "transcript":
                if self.should_drop_transcript(payload):
                    continue
                self.transcript_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))
            else:
                if (
                    self.push_to_talk
                    and self.ptt_active
                    and payload.get("state") in {"ptt_waiting", "running"}
                ):
                    continue
                self.publish_status(payload)

    def read_stderr(self) -> None:
        if self.proc is None or self.proc.stderr is None:
            return
        for line in self.proc.stderr:
            line = line.strip()
            if line:
                self.get_logger().warn(f"whisper worker: {line}")

    def publish_health(self) -> None:
        state = "stopped"
        return_code = None
        if self.proc is not None:
            return_code = self.proc.poll()
            state = "running" if return_code is None else "exited"
        if self.push_to_talk and return_code is None:
            state = "ptt_listening" if self.ptt_active else "ptt_waiting"
        worker_fields = {}
        if self.audio_backend == "udp":
            for key in [
                "audio_online",
                "packet_age_sec",
                "source_ip",
                "received_packets",
                "invalid_packets",
                "late_packets",
                "lost_samples",
            ]:
                if key in self.last_worker_payload:
                    worker_fields[key] = self.last_worker_payload[key]
            if self.last_worker_payload.get("audio_online") is False:
                state = "audio_timeout"
            elif self.last_worker_payload.get("audio_online") is True and not self.push_to_talk:
                state = "udp_streaming"
        self.publish_status(
            {
                "state": state,
                "return_code": return_code,
                "push_to_talk": self.push_to_talk,
                "ptt_active": self.ptt_active,
                "ptt_session": self.ptt_session,
                "last_worker_age_sec": (
                    None if self.last_worker_message <= 0.0 else time.time() - self.last_worker_message
                ),
                **worker_fields,
            }
        )

    def get_button(self, buttons: list[int], index: int) -> int:
        if index < 0 or index >= len(buttons):
            return 0
        return int(buttons[index])

    def joy_callback(self, msg: Joy) -> None:
        buttons = [int(value) for value in msg.buttons]
        ptt_pressed = bool(self.get_button(buttons, self.ptt_button))
        cancel_pressed = bool(self.get_button(buttons, self.cancel_button))
        last_cancel = bool(self.get_button(self.last_buttons, self.cancel_button))
        now = time.monotonic()

        if ptt_pressed:
            self.ptt_release_started_at = None

        if ptt_pressed and not self.ptt_active:
            self.ptt_active = True
            self.ptt_session += 1
            self.write_ptt_control()
            self.publish_status({"state": "ptt_listening", "session": self.ptt_session})

        if not ptt_pressed and self.ptt_active:
            if self.ptt_release_started_at is None:
                self.ptt_release_started_at = now
            elif now - self.ptt_release_started_at >= self.ptt_release_debounce_sec:
                self.ptt_active = False
                self.ptt_release_started_at = None
                self.write_ptt_control()
                self.publish_status({"state": "ptt_stopped", "session": self.ptt_session})

        if cancel_pressed and not last_cancel:
            self.cancelled_sessions.add(self.ptt_session)
            self.cancelled_session = self.ptt_session
            self.ptt_active = False
            self.ptt_release_started_at = None
            self.write_ptt_control()
            self.publish_status({"state": "cancelled", "session": self.ptt_session})
            self.transcript_pub.publish(
                String(
                    data=json.dumps(
                        {
                            "type": "cancel",
                            "text": "",
                            "session": self.ptt_session,
                            "stamp": time.time(),
                        },
                        ensure_ascii=False,
                    )
                )
            )

        self.last_buttons = buttons

    def write_ptt_control(self) -> None:
        if not self.push_to_talk:
            return
        payload = {
            "active": self.ptt_active,
            "session": self.ptt_session,
            "cancelled_session": self.cancelled_session,
            "stamp": time.time(),
        }
        tmp_path = self.ptt_control_path.with_suffix(".tmp")
        try:
            tmp_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
            tmp_path.replace(self.ptt_control_path)
        except OSError as exc:
            self.publish_status({"state": "ptt_control_error", "error": str(exc)})

    def should_drop_transcript(self, payload: dict) -> bool:
        if not self.push_to_talk:
            return False
        try:
            session = int(payload.get("session", 0) or 0)
        except (TypeError, ValueError):
            session = 0
        if session <= 0:
            return True
        return session in self.cancelled_sessions or session != self.ptt_session

    def publish_status(self, payload: dict) -> None:
        payload.setdefault("stamp", time.time())
        payload.setdefault("node", "whisper_bridge_node")
        self.status_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))

    def destroy_node(self) -> bool:
        self.stop_worker()
        return super().destroy_node()

    def stop_worker(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            return
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
            self.proc.wait(timeout=3.0)
        except Exception:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except Exception:
                pass


def main(args=None) -> None:
    rclpy.init(args=args)
    node = WhisperBridgeNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.stop_worker()
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
