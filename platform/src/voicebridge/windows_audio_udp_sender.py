#!/usr/bin/env python3
from __future__ import annotations

import argparse
import socket
import struct
import time
import uuid


MAGIC = b"VRXA"
VERSION = 1
FLAG_STREAM_RESET = 0x01
HEADER = struct.Struct("!4sBBHIIIQ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stream a Windows microphone to the VRX local-Whisper UDP receiver"
    )
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--target-host", required=False, help="Linux host IPv4 address")
    parser.add_argument("--target-port", type=int, default=15556)
    parser.add_argument(
        "--device",
        default="",
        help="Windows input device index or case-insensitive name substring",
    )
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--frame-ms", type=int, default=20)
    return parser.parse_args()


def pack_packet(
    pcm_s16le: bytes,
    sample_rate: int,
    stream_id: int,
    sequence: int,
    sample_index: int,
    reset: bool = False,
) -> bytes:
    if len(pcm_s16le) == 0 or len(pcm_s16le) % 2:
        raise ValueError("PCM payload must contain complete signed 16-bit samples")
    sample_count = len(pcm_s16le) // 2
    if sample_count > 65535:
        raise ValueError("PCM payload is too large for one VRXA packet")
    flags = FLAG_STREAM_RESET if reset else 0
    return HEADER.pack(
        MAGIC,
        VERSION,
        flags,
        sample_count,
        int(sample_rate),
        int(stream_id) & 0xFFFFFFFF,
        int(sequence) & 0xFFFFFFFF,
        int(sample_index),
    ) + pcm_s16le


def resolve_device(value: str, devices) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        index = int(value)
    except ValueError:
        index = None
    if index is not None:
        if index < 0 or index >= len(devices):
            raise ValueError(f"input device index out of range: {index}")
        if int(devices[index]["max_input_channels"]) <= 0:
            raise ValueError(f"device {index} has no input channels")
        return index

    matches = [
        index
        for index, device in enumerate(devices)
        if int(device["max_input_channels"]) > 0
        and value.lower() in str(device["name"]).lower()
    ]
    if not matches:
        raise ValueError(f"no Windows input device contains: {value}")
    if len(matches) > 1:
        names = ", ".join(f"{index}:{devices[index]['name']}" for index in matches)
        raise ValueError(f"device name is ambiguous; use an index: {names}")
    return matches[0]


def main() -> int:
    args = parse_args()

    import numpy as np
    import sounddevice as sd

    devices = sd.query_devices()
    if args.list_devices:
        print(devices)
        return 0
    if not args.target_host:
        raise SystemExit("--target-host LINUX_IP is required")
    if args.target_port < 1 or args.target_port > 65535:
        raise SystemExit(f"invalid UDP port: {args.target_port}")
    if args.sample_rate != 16000:
        raise SystemExit("VRXA v1 requires --sample-rate 16000")
    if args.frame_ms < 10 or args.frame_ms > 40:
        raise SystemExit("--frame-ms must be between 10 and 40")

    try:
        device = resolve_device(args.device, devices)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    frame_samples = args.sample_rate * args.frame_ms // 1000
    destination = (args.target_host, args.target_port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream_id = uuid.uuid4().int & 0xFFFFFFFF
    sequence = 0
    sample_index = 0
    sent_packets = 0
    callback_warnings = 0
    pending = np.empty(0, dtype=np.float32)

    def audio_callback(indata, _frames, _time_info, status) -> None:
        nonlocal callback_warnings
        nonlocal pending
        nonlocal sample_index
        nonlocal sent_packets
        nonlocal sequence

        if status:
            callback_warnings += 1
        mono = np.asarray(indata, dtype=np.float32)
        if mono.ndim == 2:
            mono = mono.mean(axis=1)
        mono = mono.reshape(-1)
        pending = np.concatenate((pending, mono))

        while pending.size >= frame_samples:
            frame = pending[:frame_samples]
            pending = pending[frame_samples:]
            pcm = (
                np.clip(frame, -1.0, 1.0) * 32767.0
            ).astype("<i2", copy=False).tobytes()
            packet = pack_packet(
                pcm,
                args.sample_rate,
                stream_id,
                sequence,
                sample_index,
                reset=sequence == 0,
            )
            udp_socket.sendto(packet, destination)
            sequence = (sequence + 1) & 0xFFFFFFFF
            sample_index += frame_samples
            sent_packets += 1

    selected_name = "Windows default input" if device is None else devices[device]["name"]
    print(f"[VRX Audio] input: {selected_name}")
    print(
        f"[VRX Audio] UDP -> {args.target_host}:{args.target_port}, "
        f"VRXA v1, 16kHz mono PCM16LE, {args.frame_ms}ms"
    )

    try:
        with sd.InputStream(
            device=device,
            samplerate=args.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=frame_samples,
            callback=audio_callback,
        ):
            previous_packets = 0
            while True:
                time.sleep(1.0)
                rate = sent_packets - previous_packets
                previous_packets = sent_packets
                print(
                    f"[VRX Audio] {rate} packet/s | total={sent_packets} "
                    f"| callback_warnings={callback_warnings}",
                    flush=True,
                )
    except KeyboardInterrupt:
        print(f"\n[VRX Audio] stopped after {sent_packets} packets")
    finally:
        udp_socket.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
