"""Tests for MIDI export with pitch bends and CC events."""

import os
import mido
import pytest
from fl_studio_mcp.music.midi_export import build_midi, write_midi


def test_build_midi_with_pitch_bends_and_cc(tmp_path):
    tracks = [
        {
            "name": "Bass_Slide",
            "channel": 0,
            "notes": [
                {"pitch": 36, "start_bars": 0.0, "length_bars": 1.0, "velocity": 0.8},
            ],
            "pitch_bends": [
                {"time_bars": 0.5, "pitch": 2048},
                {"time_bars": 0.75, "pitch": 4096},
            ],
            "mod_wheels": [
                {"time_bars": 0.25, "value": 64},
            ],
            "filter_sweeps": [
                {"time_bars": 0.0, "value": 30},
                {"time_bars": 0.5, "value": 100},
            ],
        }
    ]

    out_file = str(tmp_path / "test_mod.mid")
    mf = write_midi(tracks, bpm=140.0, path=out_file)

    assert os.path.exists(out_file)
    read_mf = mido.MidiFile(out_file)
    assert len(read_mf.tracks) == 2  # Conductor + Bass track

    bass_track = read_mf.tracks[1]
    msg_types = [m.type for m in bass_track]

    assert "note_on" in msg_types
    assert "note_off" in msg_types
    assert "pitchwheel" in msg_types
    assert "control_change" in msg_types

    # Check CC 1 (mod wheel) and CC 74 (filter cutoff)
    cc_msgs = [m for m in bass_track if m.type == "control_change"]
    cc_controls = [m.control for m in cc_msgs]
    assert 1 in cc_controls   # Mod wheel
    assert 74 in cc_controls  # Filter sweep
