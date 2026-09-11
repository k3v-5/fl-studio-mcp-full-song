"""Tests for PlaylistArranger."""

import os
from unittest.mock import MagicMock, patch
import pytest

from fl_studio_mcp.pie.auto_arranger import PlaylistArranger, get_playlist_arranger


def test_get_playlist_arranger_singleton():
    a1 = get_playlist_arranger()
    a2 = get_playlist_arranger()
    assert a1 is a2


def test_auto_import_midi_missing_file():
    arranger = PlaylistArranger()
    res = arranger.auto_import_midi_to_playlist("non_existent_file.mid")
    assert not res["ok"]
    assert "not found" in res["error"].lower()


def test_add_timeline_markers_disconnected():
    arranger = PlaylistArranger()
    mock_bridge = MagicMock()
    mock_bridge.is_alive.return_value = False
    arranger.bridge = mock_bridge

    sections = [
        {"name": "Intro", "start_bar": 0.0},
        {"name": "Drop", "start_bar": 16.0},
    ]
    res = arranger.add_timeline_markers(sections)
    assert not res["ok"]
    assert "not connected" in res["error"].lower()


def test_add_timeline_markers_success():
    arranger = PlaylistArranger()
    mock_bridge = MagicMock()
    mock_bridge.is_alive.return_value = True
    mock_bridge.call_sync.return_value = {"ok": True}
    arranger.bridge = mock_bridge

    sections = [
        {"name": "Intro", "start_bar": 0.0},
        {"name": "Build", "start_bar": 8.0},
        {"name": "Drop", "start_bar": 16.0},
    ]
    res = arranger.add_timeline_markers(sections, ppq=96, beats_per_bar=4)
    assert res["ok"]
    assert res["total_markers"] == 3
    assert res["markers"][0]["tick"] == 0
    assert res["markers"][1]["tick"] == 8 * 96 * 4
    assert res["markers"][2]["tick"] == 16 * 96 * 4


@patch("fl_studio_mcp.pie.auto_arranger.find_fl_hwnd")
@patch("fl_studio_mcp.pie.auto_arranger.force_focus")
@patch("pyautogui.press")
@patch("pyautogui.hotkey")
@patch("pyperclip.copy")
@patch("time.sleep")
def test_auto_import_midi_win32_success(
    mock_sleep, mock_copy, mock_hotkey, mock_press, mock_force_focus, mock_find_hwnd, tmp_path
):
    midi_file = tmp_path / "test_multitrack.mid"
    midi_file.write_bytes(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00\x60MTrk\x00\x00\x00\x04\x00\x2f\x00\x00")

    mock_find_hwnd.return_value = 99999
    mock_force_focus.return_value = True

    arranger = PlaylistArranger()
    res = arranger.auto_import_midi_to_playlist(
        str(midi_file),
        settle_delay=0.01,
        start_new_project=True,
        load_timeout=0.01,
        focus_channel_rack=True,
    )

    assert res["ok"] is True
    assert res["status"] == "imported"
    assert res["focused"] is True
    assert res["file"] == os.path.abspath(str(midi_file))

    # Verify Alt+N accelerator was used to focus file name edit box
    mock_hotkey.assert_any_call("alt", "n")
    # Verify clipboard copy of path
    mock_copy.assert_called_with(os.path.abspath(str(midi_file)))
    # Verify paste hotkey
    mock_hotkey.assert_any_call("ctrl", "v")
    # Verify F6 channel rack focus
    mock_press.assert_any_call("f6")


@patch.object(PlaylistArranger, "auto_import_midi_to_playlist")
def test_auto_arrange_song_pipeline(mock_import):
    from fl_studio_mcp import protocol
    mock_import.return_value = {
        "ok": True,
        "status": "imported",
        "tracks_count": 4,
        "track_names": ["Kick", "Snare", "Bass", "Lead"],
    }
    arranger = PlaylistArranger()
    mock_bridge = MagicMock()
    mock_bridge.is_alive.return_value = True
    mock_bridge.call_sync.return_value = {"ok": True}
    arranger.bridge = mock_bridge

    sections = [
        {"name": "Intro", "start_bar": 0.0},
        {"name": "Drop", "start_bar": 16.0},
    ]

    res = arranger.auto_arrange_song(
        midi_path="test_song.mid",
        sections=sections,
        bpm=100.0,
        settle_delay=0.01,
        start_new_project=False,
        load_timeout=0.01,
        focus_channel_rack=True,
    )

    assert res["ok"] is True
    assert res["bpm"] == 100.0
    assert res["tracks_count"] == 4
    assert res["track_names"] == ["Kick", "Snare", "Bass", "Lead"]
    mock_bridge.call_sync.assert_any_call(protocol.CMD_SET_TEMPO, {"bpm": 100.0}, timeout=2.0)
    mock_bridge.call_sync.assert_any_call(protocol.CMD_SET_SONG_POS, {"beats": 0.0}, timeout=2.0)
    mock_import.assert_called_once_with(
        "test_song.mid",
        settle_delay=0.01,
        start_new_project=False,
        load_timeout=0.01,
        focus_channel_rack=True,
    )

