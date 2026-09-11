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
