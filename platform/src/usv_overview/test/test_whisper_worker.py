import shutil

from usv_overview.whisper_worker import pulse_source_name, select_audio_backend


def test_explicit_pulse_device_selects_pulse():
    assert select_audio_backend("auto", "pulse:headset.source") == "pulse"


def test_auto_prefers_pulse_when_tools_are_available(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/" + name)
    assert select_audio_backend("auto", "") == "pulse"


def test_auto_falls_back_to_sounddevice_without_pulse(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert select_audio_backend("auto", "") == "sounddevice"


def test_pulse_source_name_strips_prefix():
    assert pulse_source_name("pulse:alsa_input.usb-headset") == "alsa_input.usb-headset"
    assert pulse_source_name("") == ""
