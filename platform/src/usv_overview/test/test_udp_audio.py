import struct

import pytest

from usv_overview.udp_audio import HEADER, MAGIC, PacketError, decode_packet


def make_packet(samples=320, rate=16000):
    payload = struct.pack("<" + "h" * samples, *range(samples))
    return HEADER.pack(MAGIC, 1, 1, samples, rate, 7, 9, 3200) + payload


def test_decode_vrxa_packet():
    packet = decode_packet(make_packet())
    assert packet.sample_count == 320
    assert packet.sample_rate == 16000
    assert packet.stream_id == 7
    assert packet.sequence == 9
    assert packet.sample_index == 3200
    assert len(packet.pcm_s16le) == 640


@pytest.mark.parametrize(
    "payload",
    [
        b"short",
        HEADER.pack(b"NOPE", 1, 0, 1, 16000, 1, 1, 0) + b"\x00\x00",
        HEADER.pack(MAGIC, 2, 0, 1, 16000, 1, 1, 0) + b"\x00\x00",
        HEADER.pack(MAGIC, 1, 0, 1, 48000, 1, 1, 0) + b"\x00\x00",
        HEADER.pack(MAGIC, 1, 0, 2, 16000, 1, 1, 0) + b"\x00\x00",
    ],
)
def test_reject_invalid_packets(payload):
    with pytest.raises(PacketError):
        decode_packet(payload)
