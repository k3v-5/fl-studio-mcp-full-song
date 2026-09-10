import pytest
from unittest.mock import patch
from fl_studio_mcp.pie.sidechain_engine import SidechainEngine

def test_sidechain_ducking_curve_generation():
    engine = SidechainEngine()

    # 4-on-the-floor kick pattern
    kick_times = [0.0, 1.0, 2.0, 3.0]

    # Generate ducking ghost notes
    notes = engine.generate_ducking_curve(kick_times, depth=0.8, duration=0.25)

    assert len(notes) == 4
    for i, note in enumerate(notes):
        assert note["midi"] == 0 # Default trigger note
        assert note["time"] == float(i)
        assert note["duration"] == 0.25
        assert note["velocity"] == 0.8

def test_sidechain_process_masking_skips_when_no_masking():
    engine = SidechainEngine()
    mock_masking = {"masking_detected": False}

    res = engine.process_masking_result(mock_masking, [0.0])

    assert res["action"] == "none"
    assert "Sidechain skipped" in res["message"]

def test_sidechain_process_masking_applies_ducking():
    engine = SidechainEngine()
    mock_masking = {"masking_detected": True, "conflict_zone_hz": [40, 60]}

    res = engine.process_masking_result(mock_masking, [0.0, 1.0])

    assert res["action"] == "apply_sidechain"
    assert "ghost_notes" in res
    assert len(res["ghost_notes"]) == 2
    # Because frequency is low (< 100), depth should be calculated as 1.0
    assert res["ghost_notes"][0]["velocity"] == 1.0
