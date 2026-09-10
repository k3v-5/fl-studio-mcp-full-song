import pytest
from fl_studio_mcp.pie.arrangement import ArrangementEngine

def test_arrangement_riser():
    engine = ArrangementEngine()
    engine.update_structure({
        "drop": {"start_beat": 32.0, "length_beats": 16.0}
    })

    res = engine.generate_transition_riser("drop", length_beats=4.0, start_midi=50, end_midi=60, curve_type="linear")

    assert "error" not in res
    assert res["start_beat"] == 28.0 # 32 - 4

    notes = res["riser_notes"]
    assert len(notes) > 0

    # First note should be at start beat, last pitch should be close to end_midi
    assert notes[0]["time"] == 28.0
    assert notes[0]["midi"] == 50
    assert notes[-1]["midi"] > 55

    # Velocity should rise
    assert notes[-1]["velocity"] > notes[0]["velocity"]

def test_arrangement_riser_exponential_rhythm():
    engine = ArrangementEngine()
    engine.update_structure({
        "drop": {"start_beat": 16.0}
    })

    res = engine.generate_transition_riser("drop", length_beats=4.0, curve_type="exponential")

    assert "error" not in res
    notes = res["riser_notes"]

    # Since it's exponential, the notes at the end of the array should be shorter than notes at the beginning
    assert notes[-1]["duration"] < notes[0]["duration"]

def test_arrangement_riser_error_handling():
    engine = ArrangementEngine()
    res = engine.generate_transition_riser("nonexistent")
    assert "error" in res
