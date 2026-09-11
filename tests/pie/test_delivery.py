import os
import pytest
from unittest.mock import patch, MagicMock
from fl_studio_mcp.pie.delivery import SongDeliveryEngine, normalize_note, get_delivery_engine

def test_normalize_note():
    # Test normalization from different representations
    n1 = normalize_note({"midi": 60, "time": 4.0, "duration": 2.0, "velocity": 0.9})
    assert n1["pitch"] == 60
    assert n1["time_bars"] == 1.0
    assert n1["length_bars"] == 0.5
    assert n1["time_beats"] == 4.0
    assert n1["length_beats"] == 2.0
    assert n1["velocity"] == 0.9

    n2 = normalize_note({"pitch": 72, "time_bars": 2.0, "length_bars": 1.0, "velocity": 100})
    assert n2["pitch"] == 72
    assert n2["time_bars"] == 2.0
    assert n2["length_bars"] == 1.0
    assert n2["velocity"] == round(100 / 127.0, 4)

@patch("fl_studio_mcp.pie.delivery.get_bridge")
@patch("time.sleep")
def test_delivery_realtime_record(mock_sleep, mock_get_bridge):
    from fl_studio_mcp import protocol
    engine = SongDeliveryEngine()
    mock_bridge = MagicMock()
    mock_bridge.call.return_value = {"ok": True, "bpm": 140.0}
    mock_get_bridge.return_value = mock_bridge

    notes = [
        {"pitch": 60, "time_bars": 0.0, "length_bars": 0.25, "velocity": 0.8},
        {"pitch": 64, "time_bars": 0.25, "length_bars": 0.25, "velocity": 0.8},
    ]

    res = engine.deliver_realtime_record(notes, channel=2, bpm=140.0, speed_factor=100.0)

    assert res["status"] == "success"
    assert res["delivery_mode"] == "realtime_record"
    assert res["notes_count"] == 2

    # Verify channel selection and transport controls
    mock_bridge.call.assert_any_call(protocol.CMD_CHANNEL_SELECT, {"channel": 2})
    mock_bridge.call.assert_any_call(protocol.CMD_PLAY, {}, timeout=1.0)
    mock_bridge.call.assert_any_call(protocol.CMD_STOP, {}, timeout=1.0)

    # Verify MIDI Note 76 (start record) and Note 77 (stop record) sent
    mock_bridge.send_raw_midi.assert_any_call([0x90, 76, 1])
    mock_bridge.send_raw_midi.assert_any_call([0x90, 77, 1])
    assert mock_bridge.send_raw_midi.call_count >= 6

@patch("fl_studio_mcp.pie.delivery.get_bridge")
def test_delivery_pyscript(mock_get_bridge):
    from fl_studio_mcp import protocol
    engine = SongDeliveryEngine()
    mock_bridge = MagicMock()
    mock_bridge.call.return_value = {"ok": True}
    mock_bridge.apply_notes.return_value = {"ok": True, "applied": 2}
    mock_get_bridge.return_value = mock_bridge

    notes = [
        {"pitch": 60, "time_bars": 0.0, "length_bars": 0.25, "velocity": 0.8},
        {"pitch": 67, "time_bars": 0.5, "length_bars": 0.25, "velocity": 0.8},
    ]

    res = engine.deliver_pyscript(notes, channel=1, pattern_name="TestPattern", mode="replace")

    assert res["status"] == "success"
    assert res["delivery_mode"] == "pyscript"
    assert res["notes_count"] == 2
    mock_bridge.call.assert_any_call(protocol.CMD_CHANNEL_SELECT, {"channel": 1})
    mock_bridge.apply_notes.assert_called_once()

def test_delivery_midi_file(tmp_path):
    engine = SongDeliveryEngine()
    tracks = [
        {
            "name": "Kick",
            "channel": 0,
            "notes": [{"pitch": 36, "time_bars": 0.0, "length_bars": 0.25, "velocity": 1.0}],
        },
        {
            "name": "Bass",
            "channel": 1,
            "notes": [{"pitch": 48, "time_bars": 0.0, "length_bars": 1.0, "velocity": 0.9}],
        },
    ]

    res = engine.deliver_midi_file(
        tracks=tracks,
        song_name="TestSong",
        bpm=140.0,
        output_dir=str(tmp_path),
        copy_to_fl=False,
    )

    assert res["status"] == "success"
    assert res["delivery_mode"] == "midi_file"
    assert res["tracks_count"] == 2
    assert res["total_notes"] == 2
    assert os.path.exists(res["export_path"])

@patch("fl_studio_mcp.pie.delivery.SongDeliveryEngine.deliver_realtime_record")
@patch("fl_studio_mcp.pie.delivery.SongDeliveryEngine.deliver_pyscript")
@patch("fl_studio_mcp.pie.delivery.SongDeliveryEngine.deliver_midi_file")
def test_delivery_universal_all(mock_midi, mock_pyscript, mock_record):
    mock_midi.return_value = {"ok": True}
    mock_pyscript.return_value = {"ok": True}
    mock_record.return_value = {"ok": True}

    engine = SongDeliveryEngine()
    notes = [{"pitch": 60, "time_bars": 0.0, "length_bars": 0.25}]

    res = engine.deliver(notes, delivery_mode="all", song_name="FullTest", bpm=140.0, channel=0)

    assert res["status"] == "success"
    assert "midi_file" in res["deliveries"]
    assert "pyscript" in res["deliveries"]
    assert "realtime_record" in res["deliveries"]
    mock_midi.assert_called_once()
    mock_pyscript.assert_called_once()
    mock_record.assert_called_once()
