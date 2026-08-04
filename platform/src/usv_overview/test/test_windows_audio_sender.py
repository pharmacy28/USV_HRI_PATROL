import importlib.util
from pathlib import Path
import struct

from usv_overview.udp_audio import FLAG_STREAM_RESET, decode_packet


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "voicebridge"
    / "windows_audio_udp_sender.py"
)
SPEC = importlib.util.spec_from_file_location("windows_audio_udp_sender", SCRIPT_PATH)
SENDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SENDER)


def test_windows_sender_packet_matches_linux_receiver():
    pcm = struct.pack("<4h", -100, 0, 100, 200)
    encoded = SENDER.pack_packet(
        pcm,
        sample_rate=16000,
        stream_id=7,
        sequence=8,
        sample_index=320,
        reset=True,
    )
    decoded = decode_packet(encoded)
    assert decoded.flags & FLAG_STREAM_RESET
    assert decoded.sample_count == 4
    assert decoded.stream_id == 7
    assert decoded.sequence == 8
    assert decoded.sample_index == 320
    assert decoded.pcm_s16le == pcm


def test_resolve_windows_device_by_name_or_index():
    devices = [
        {"name": "Speakers", "max_input_channels": 0},
        {"name": "Virtual Microphone", "max_input_channels": 1},
    ]
    assert SENDER.resolve_device("1", devices) == 1
    assert SENDER.resolve_device("virtual mic", devices) == 1
