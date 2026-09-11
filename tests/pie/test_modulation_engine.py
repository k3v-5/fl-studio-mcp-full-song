"""Tests for ModulationEngine."""

import pytest
from fl_studio_mcp.pie.modulation_engine import ModulationEngine, get_modulation_engine


def test_get_modulation_engine_singleton():
    m1 = get_modulation_engine()
    m2 = get_modulation_engine()
    assert m1 is m2


def test_generate_808_slides():
    mod = ModulationEngine()
    notes = mod.generate_808_slides(
        root_pitch=36,
        slide_pitch=48,
        start_bar=0.0,
        root_length_bars=1.0,
        slide_length_bars=0.25,
    )
    assert len(notes) == 2
    root, slide = notes[0], notes[1]

    assert root["pitch"] == 36
    assert not root["slide"]
    assert root["length_bars"] == 1.0

    assert slide["pitch"] == 48
    assert slide["slide"] is True
    assert slide["start_bars"] == 0.75
    assert slide["length_bars"] == 0.25


def test_generate_lfo_curve_sine():
    mod = ModulationEngine()
    curve = mod.generate_lfo_curve(shape="sine", bars=2.0, rate_hz_or_subdiv=1.0, min_val=0, max_val=100)
    assert len(curve) > 0
    vals = [pt["value"] for pt in curve]
    assert min(vals) >= 0
    assert max(vals) <= 100


def test_generate_lfo_curve_wobble():
    mod = ModulationEngine()
    curve = mod.generate_lfo_curve(shape="wobble", bars=1.0, rate_hz_or_subdiv=2.0, min_val=20, max_val=120)
    assert len(curve) == 17  # 16 steps per bar + endpoint
    assert all(20 <= pt["value"] <= 120 for pt in curve)


def test_generate_pitch_bend_sweep():
    mod = ModulationEngine()
    events = mod.generate_pitch_bend_sweep(start_bar=4.0, duration_bars=2.0, start_bend=0, end_bend=8191)
    assert len(events) > 0
    assert events[0]["pitch"] == 0
    assert events[-1]["pitch"] == 8191
    assert events[0]["time_bars"] == 4.0
    assert events[-1]["time_bars"] == 6.0


def test_generate_tension_riser():
    mod = ModulationEngine()
    riser = mod.generate_tension_riser(start_bar=8.0, duration_bars=4.0)
    assert riser["start_bar"] == 8.0
    assert riser["duration_bars"] == 4.0
    assert len(riser["pitch_bends"]) > 0
    assert len(riser["filter_cutoff_cc74"]) > 0
