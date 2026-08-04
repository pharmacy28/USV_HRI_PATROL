#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)


def list_devices() -> int:
    import sounddevice as sd

    devices = sd.query_devices()
    print(devices)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Whisper microphone transcriber")
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--model", default="base", help="Whisper model name")
    parser.add_argument("--model-dir", default="", help="optional Whisper model cache directory")
    parser.add_argument("--language", default="zh", help="spoken language, e.g. zh or en")
    parser.add_argument("--device", default="cpu", help="Whisper inference device")
    parser.add_argument(
        "--audio-backend",
        default="auto",
        choices=["auto", "sounddevice", "pulse", "udp"],
    )
    parser.add_argument("--audio-device", default="", help="sounddevice input device index/name")
    parser.add_argument("--udp-bind", default="0.0.0.0")
    parser.add_argument("--udp-port", type=int, default=15556)
    parser.add_argument("--udp-source-ip", default="")
    parser.add_argument("--udp-timeout-sec", type=float, default=1.0)
    parser.add_argument("--udp-preroll-sec", type=float, default=0.15)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--chunk-sec", type=float, default=1.5)
    parser.add_argument("--energy-threshold", type=float, default=0.02)
    parser.add_argument("--audio-gain", type=float, default=1.0)
    parser.add_argument("--min-text-chars", type=int, default=1)
    parser.add_argument("--no-speech-threshold", type=float, default=0.8)
    parser.add_argument(
        "--initial-prompt",
        default=(
            "普通话多艇任务口令。常见短口令包括：二号船去E5、WAMV十号到A1、"
            "选择一号船、打开网格、切换全局态势。请保留船号和棋盘格编号，按原文输出。"
        ),
    )
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--ptt-control-file", default="", help="JSON file with active/session PTT state")
    return parser.parse_args()


def audio_device(value: str) -> int | str | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def rms_energy(samples: Any) -> float:
    import numpy as np

    flat = np.asarray(samples, dtype=np.float32).reshape(-1)
    if flat.size == 0:
        return 0.0
    return float(math.sqrt(float(np.mean(flat * flat))))


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def select_audio_backend(backend: str, audio_device_value: str) -> str:
    if backend != "auto":
        return backend
    if audio_device_value.startswith("pulse:"):
        return "pulse"
    return "sounddevice"


def record_sounddevice_chunk(args: argparse.Namespace, duration_sec: float | None = None) -> Any:
    import sounddevice as sd

    chunk_sec = args.chunk_sec if duration_sec is None else duration_sec
    frames = max(1, int(args.sample_rate * chunk_sec))
    samples = sd.rec(
        frames,
        samplerate=args.sample_rate,
        channels=1,
        dtype="float32",
        device=audio_device(args.audio_device),
    )
    sd.wait()
    return samples


def pulse_source_name(value: str) -> str:
    if value.startswith("pulse:"):
        return value[len("pulse:") :]
    return value


def record_pulse_chunk(args: argparse.Namespace, duration_sec: float | None = None) -> Any:
    import numpy as np

    parec = shutil.which("parec")
    if not parec:
        raise RuntimeError("parec not found; install/use PulseAudio tools or select sounddevice backend")

    chunk_sec = args.chunk_sec if duration_sec is None else duration_sec
    byte_count = max(1, int(args.sample_rate * chunk_sec)) * 2
    cmd = [
        parec,
        "--record",
        "--format=s16le",
        f"--rate={args.sample_rate}",
        "--channels=1",
    ]
    source_name = pulse_source_name(args.audio_device)
    if source_name:
        cmd.append(f"--device={source_name}")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        raw = proc.stdout.read(byte_count) if proc.stdout is not None else b""
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            proc.kill()

    if len(raw) < 2:
        err = ""
        if proc.stderr is not None:
            err = proc.stderr.read().decode(errors="replace").strip()
        raise RuntimeError(f"PulseAudio capture returned no samples: {err}")

    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def read_ptt_state(path_value: str) -> dict[str, Any]:
    if not path_value:
        return {"active": True, "session": 0}

    path = Path(path_value)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"active": False, "session": 0}

    return {
        "active": bool(payload.get("active", False)),
        "session": int(payload.get("session", 0) or 0),
        "cancelled_session": int(payload.get("cancelled_session", 0) or 0),
    }


def record_chunk(
    args: argparse.Namespace,
    audio_backend: str,
    duration_sec: float | None = None,
    udp_receiver: Any = None,
) -> Any:
    if audio_backend == "udp":
        if udp_receiver is None:
            raise RuntimeError("UDP audio receiver is not initialized")
        chunk_sec = args.chunk_sec if duration_sec is None else duration_sec
        return udp_receiver.read_samples(chunk_sec)
    if audio_backend == "pulse":
        return record_pulse_chunk(args, duration_sec=duration_sec)
    return record_sounddevice_chunk(args, duration_sec=duration_sec)


def transcribe_audio(
    args: argparse.Namespace,
    model: Any,
    audio: Any,
    energy: float,
    session: int,
    audio_sec: float,
    start: float,
) -> None:
    import numpy as np

    try:
        emit(
            {
                "type": "status",
                "state": "transcribing",
                "rms": energy,
                "audio_sec": audio_sec,
                "session": session,
                "stamp": time.time(),
            }
        )
        result = model.transcribe(
            np.asarray(audio, dtype=np.float32).reshape(-1),
            language=args.language or None,
            task="transcribe",
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False,
            no_speech_threshold=args.no_speech_threshold,
            initial_prompt=args.initial_prompt or None,
        )
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        emit(
            {
                "type": "error",
                "stage": "transcribe",
                "message": str(exc),
                "rms": energy,
                "stamp": time.time(),
            }
        )
        return

    text = normalize_text(str(result.get("text", "")))
    if len(text) < args.min_text_chars:
        emit(
            {
                "type": "status",
                "state": "no_text",
                "rms": energy,
                "audio_sec": audio_sec,
                "session": session,
                "latency_sec": time.time() - start,
                "stamp": time.time(),
            }
        )
        return

    emit(
        {
            "type": "transcript",
            "stamp": time.time(),
            "text": text,
            "language": args.language,
            "model": args.model,
            "rms": energy,
            "audio_sec": audio_sec,
            "session": session,
            "latency_sec": time.time() - start,
        }
    )


def main() -> int:
    args = parse_args()
    if args.list_devices:
        return list_devices()

    import numpy as np
    import torch
    import whisper

    if args.threads > 0:
        torch.set_num_threads(args.threads)

    model_kwargs: dict[str, Any] = {}
    if args.model_dir:
        model_kwargs["download_root"] = args.model_dir

    emit(
        {
            "type": "status",
            "state": "loading_model",
            "model": args.model,
            "device": args.device,
            "stamp": time.time(),
        }
    )
    model = whisper.load_model(args.model, device=args.device, **model_kwargs)
    emit({"type": "status", "state": "ready", "model": args.model, "stamp": time.time()})

    audio_backend = select_audio_backend(args.audio_backend, args.audio_device)
    udp_receiver = None
    if audio_backend == "udp":
        from usv_overview.udp_audio import UdpPcmReceiver

        udp_receiver = UdpPcmReceiver(
            bind_host=args.udp_bind,
            port=args.udp_port,
            sample_rate=args.sample_rate,
            source_ip=args.udp_source_ip,
            timeout_sec=args.udp_timeout_sec,
            preroll_sec=args.udp_preroll_sec,
        )
    emit(
        {
            "type": "status",
            "state": "audio_ready",
            "backend": audio_backend,
            "audio_device": args.audio_device,
            "sample_rate": args.sample_rate,
            "chunk_sec": args.chunk_sec,
            "udp_bind": args.udp_bind if audio_backend == "udp" else None,
            "udp_port": args.udp_port if audio_backend == "udp" else None,
            "udp_source_ip": args.udp_source_ip if audio_backend == "udp" else None,
            "stamp": time.time(),
        }
    )

    if udp_receiver is not None and not args.ptt_control_file:
        udp_receiver.begin_capture()

    last_ptt_emit = 0.0
    while True:
        ptt_state = read_ptt_state(args.ptt_control_file)
        if args.ptt_control_file and not ptt_state["active"]:
            now = time.time()
            if now - last_ptt_emit >= 1.0:
                udp_status = udp_receiver.status() if udp_receiver is not None else {}
                emit(
                    {
                        "type": "status",
                        "state": (
                            "audio_timeout"
                            if udp_receiver is not None and not udp_status.get("audio_online")
                            else "ptt_waiting"
                        ),
                        "session": ptt_state["session"],
                        "stamp": now,
                        **udp_status,
                    }
                )
                last_ptt_emit = now
            time.sleep(0.05)
            continue

        start = time.time()
        session = int(ptt_state["session"])

        if args.ptt_control_file:
            if udp_receiver is not None:
                udp_receiver.begin_capture()
            chunks = []
            if audio_backend == "pulse":
                slice_sec = min(max(args.chunk_sec, 0.5), 1.0)
            else:
                slice_sec = min(max(args.chunk_sec, 0.1), 0.25)
            last_listening_emit = 0.0

            while True:
                ptt_state = read_ptt_state(args.ptt_control_file)
                if (
                    not ptt_state["active"]
                    or int(ptt_state["session"]) != session
                    or int(ptt_state.get("cancelled_session", 0)) == session
                ):
                    break

                try:
                    chunk = record_chunk(
                        args,
                        audio_backend,
                        duration_sec=slice_sec,
                        udp_receiver=udp_receiver,
                    )
                except KeyboardInterrupt:
                    return 0
                except TimeoutError as exc:
                    emit(
                        {
                            "type": "status",
                            "state": "audio_timeout",
                            "message": str(exc),
                            "stamp": time.time(),
                            **(udp_receiver.status() if udp_receiver is not None else {}),
                        }
                    )
                    break
                except Exception as exc:
                    emit(
                        {
                            "type": "error",
                            "stage": "record",
                            "message": str(exc),
                            "stamp": time.time(),
                        }
                    )
                    time.sleep(1.0)
                    break

                if args.audio_gain != 1.0:
                    chunk = np.clip(np.asarray(chunk, dtype=np.float32) * args.audio_gain, -1.0, 1.0)
                chunks.append(np.asarray(chunk, dtype=np.float32).reshape(-1))

                now = time.time()
                if now - last_listening_emit >= 0.5:
                    emit(
                        {
                            "type": "status",
                            "state": "ptt_listening",
                            "session": session,
                            "audio_sec": now - start,
                            "stamp": now,
                            **(udp_receiver.status() if udp_receiver is not None else {}),
                        }
                    )
                    last_listening_emit = now

            ptt_state = read_ptt_state(args.ptt_control_file)
            if udp_receiver is not None:
                udp_receiver.end_capture()
            if int(ptt_state.get("cancelled_session", 0)) == session:
                emit({"type": "status", "state": "cancelled", "session": session, "stamp": time.time()})
                continue
            if not chunks:
                continue

            audio = np.concatenate(chunks)
            energy = rms_energy(audio)
            audio_sec = float(audio.size) / float(args.sample_rate)
            if energy < args.energy_threshold:
                emit(
                    {
                        "type": "vad",
                        "active": False,
                        "rms": energy,
                        "duration_sec": audio_sec,
                        "session": session,
                        "stamp": time.time(),
                    }
                )
                continue

            transcribe_audio(args, model, audio, energy, session, audio_sec, start)
            continue

        try:
            samples = record_chunk(args, audio_backend, udp_receiver=udp_receiver)
        except KeyboardInterrupt:
            return 0
        except TimeoutError as exc:
            emit(
                {
                    "type": "status",
                    "state": "audio_timeout",
                    "message": str(exc),
                    "stamp": time.time(),
                    **(udp_receiver.status() if udp_receiver is not None else {}),
                }
            )
            time.sleep(0.1)
            continue
        except Exception as exc:
            emit(
                {
                    "type": "error",
                    "stage": "record",
                    "message": str(exc),
                    "stamp": time.time(),
                }
            )
            time.sleep(1.0)
            continue

        if udp_receiver is not None:
            emit(
                {
                    "type": "status",
                    "state": "udp_streaming",
                    "stamp": time.time(),
                    **udp_receiver.status(),
                }
            )

        if args.audio_gain != 1.0:
            samples = np.clip(np.asarray(samples, dtype=np.float32) * args.audio_gain, -1.0, 1.0)

        energy = rms_energy(samples)
        if energy < args.energy_threshold:
            emit(
                {
                    "type": "vad",
                    "active": False,
                    "rms": energy,
                    "duration_sec": args.chunk_sec,
                    "stamp": time.time(),
                }
            )
            continue

        transcribe_audio(args, model, samples, energy, session, args.chunk_sec, start)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
    except Exception as exc:
        print(f"whisper_worker fatal: {exc}", file=sys.stderr, flush=True)
        raise
