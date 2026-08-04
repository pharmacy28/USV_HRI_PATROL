from __future__ import annotations

from dataclasses import dataclass
import socket
import struct
import threading
import time


MAGIC = b"VRXA"
VERSION = 1
FLAG_STREAM_RESET = 0x01
HEADER = struct.Struct("!4sBBHIIIQ")


class PacketError(ValueError):
    pass


@dataclass(frozen=True)
class AudioPacket:
    flags: int
    sample_count: int
    sample_rate: int
    stream_id: int
    sequence: int
    sample_index: int
    pcm_s16le: bytes


def decode_packet(data: bytes, expected_sample_rate: int = 16000) -> AudioPacket:
    if len(data) < HEADER.size:
        raise PacketError("packet shorter than VRXA header")

    magic, version, flags, sample_count, sample_rate, stream_id, sequence, sample_index = (
        HEADER.unpack_from(data)
    )
    if magic != MAGIC:
        raise PacketError("invalid VRXA magic")
    if version != VERSION:
        raise PacketError(f"unsupported VRXA version: {version}")
    if sample_rate != expected_sample_rate:
        raise PacketError(f"unexpected sample rate: {sample_rate}")
    if sample_count <= 0:
        raise PacketError("empty audio packet")

    payload = data[HEADER.size:]
    if len(payload) != sample_count * 2:
        raise PacketError("PCM payload length does not match sample_count")

    return AudioPacket(
        flags=flags,
        sample_count=sample_count,
        sample_rate=sample_rate,
        stream_id=stream_id,
        sequence=sequence,
        sample_index=sample_index,
        pcm_s16le=payload,
    )


class UdpPcmReceiver:
    def __init__(
        self,
        bind_host: str,
        port: int,
        sample_rate: int = 16000,
        source_ip: str = "",
        timeout_sec: float = 1.0,
        preroll_sec: float = 0.15,
        max_buffer_sec: float = 15.0,
    ) -> None:
        self.sample_rate = int(sample_rate)
        self.source_ip = source_ip.strip()
        self.timeout_sec = max(0.1, float(timeout_sec))
        self.preroll_bytes = max(0, int(self.sample_rate * preroll_sec)) * 2
        self.max_buffer_bytes = max(
            self.preroll_bytes,
            int(self.sample_rate * max_buffer_sec) * 2,
        )

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((bind_host, int(port)))
        self._socket.settimeout(0.2)
        self._condition = threading.Condition()
        self._buffer = bytearray()
        self._capturing = False
        self._closed = False
        self._stream_id: int | None = None
        self._expected_sample_index: int | None = None
        self._last_packet_monotonic = 0.0
        self._source_address = ""
        self._received_packets = 0
        self._invalid_packets = 0
        self._late_packets = 0
        self._lost_samples = 0

        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def _receive_loop(self) -> None:
        while not self._closed:
            try:
                data, address = self._socket.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError:
                break

            if self.source_ip and address[0] != self.source_ip:
                continue

            try:
                packet = decode_packet(data, self.sample_rate)
            except PacketError:
                with self._condition:
                    self._invalid_packets += 1
                continue

            with self._condition:
                reset = bool(packet.flags & FLAG_STREAM_RESET)
                if reset or packet.stream_id != self._stream_id:
                    self._stream_id = packet.stream_id
                    self._expected_sample_index = packet.sample_index
                    self._buffer.clear()

                expected = self._expected_sample_index
                payload = packet.pcm_s16le
                packet_end = packet.sample_index + packet.sample_count
                if expected is not None and packet.sample_index > expected:
                    gap = packet.sample_index - expected
                    if gap <= int(self.sample_rate * 0.2):
                        self._buffer.extend(b"\x00\x00" * gap)
                        self._lost_samples += gap
                    else:
                        self._buffer.clear()
                elif expected is not None and packet.sample_index < expected:
                    overlap = expected - packet.sample_index
                    if overlap >= packet.sample_count:
                        self._late_packets += 1
                        continue
                    payload = payload[overlap * 2:]
                    self._late_packets += 1

                self._buffer.extend(payload)
                self._expected_sample_index = max(expected or 0, packet_end)
                self._last_packet_monotonic = time.monotonic()
                self._source_address = address[0]
                self._received_packets += 1
                self._trim_buffer_locked()
                self._condition.notify_all()

    def _trim_buffer_locked(self) -> None:
        limit = self.max_buffer_bytes if self._capturing else self.preroll_bytes
        if len(self._buffer) > limit:
            del self._buffer[: len(self._buffer) - limit]

    def begin_capture(self) -> None:
        with self._condition:
            self._capturing = True
            self._trim_buffer_locked()

    def end_capture(self) -> None:
        with self._condition:
            self._capturing = False
            self._trim_buffer_locked()

    def read_samples(self, duration_sec: float):
        import numpy as np

        wanted_samples = max(1, int(self.sample_rate * duration_sec))
        wanted_bytes = wanted_samples * 2
        deadline = time.monotonic() + max(duration_sec, 0.0) + self.timeout_sec

        with self._condition:
            while len(self._buffer) < wanted_bytes and not self._closed:
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    break
                self._condition.wait(timeout=min(remaining, 0.2))

            available = min(len(self._buffer), wanted_bytes)
            available -= available % 2
            if available <= 0:
                raise TimeoutError("no valid VRXA UDP audio received")
            raw = bytes(self._buffer[:available])
            del self._buffer[:available]

        return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0

    def status(self) -> dict:
        with self._condition:
            age = (
                None
                if self._last_packet_monotonic <= 0.0
                else max(0.0, time.monotonic() - self._last_packet_monotonic)
            )
            return {
                "audio_online": age is not None and age <= self.timeout_sec,
                "packet_age_sec": age,
                "source_ip": self._source_address,
                "received_packets": self._received_packets,
                "invalid_packets": self._invalid_packets,
                "late_packets": self._late_packets,
                "lost_samples": self._lost_samples,
            }

    def close(self) -> None:
        self._closed = True
        try:
            self._socket.close()
        except OSError:
            pass
        with self._condition:
            self._condition.notify_all()
        self._thread.join(timeout=1.0)
