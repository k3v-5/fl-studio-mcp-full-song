import pytest
from fl_studio_mcp.pie.music_engine import get_music_engine

def test_music_engine_harmony_schema():
    me = get_music_engine()
    chords = [[60, 64, 67], [65, 69, 72]]
    durations = [2.0, 2.0]

    notes = me.generate_harmony(chords, durations, start_time=0.0)

    assert len(notes) == 6
    # Check that EVERY note strictly matches the fl_send_notes schema
    for note in notes:
        assert "midi" in note
        assert "duration" in note
        assert "time" in note
        assert "velocity" in note

        # Verify types
        assert isinstance(note["midi"], int)
        assert isinstance(note["duration"], float)
        assert isinstance(note["time"], float)
        assert isinstance(note["velocity"], float)

        # Verify velocity scaling (0.0 to 1.0)
        assert 0.0 <= note["velocity"] <= 1.0

def test_music_engine_bass_schema():
    me = get_music_engine()
    notes = me.generate_bass([60, 65], [1.0, 1.0])

    assert len(notes) == 2
    for note in notes:
        assert "midi" in note
        assert "duration" in note
        assert "time" in note
        assert "velocity" in note

        assert isinstance(note["midi"], int)
        assert isinstance(note["duration"], float)
        assert isinstance(note["time"], float)
        assert isinstance(note["velocity"], float)

        assert 0.0 <= note["velocity"] <= 1.0

def test_music_engine_humanize():
    me = get_music_engine()
    raw_notes = [{"midi": 60, "time": 1.0, "duration": 1.0, "velocity": 0.5}]

    # Use zero variance to ensure baseline logic is stable
    humanized = me.humanize_timing_and_velocity(raw_notes, timing_variance=0.0, velocity_variance=0.0)
    assert humanized[0]["time"] == 1.0
    assert humanized[0]["velocity"] == 0.5

    # Test bounding/clamping
    raw_bounds = [{"midi": 60, "time": 0.0, "duration": 0.01, "velocity": 0.0}]
    humanized_bounds = me.humanize_timing_and_velocity(raw_bounds, timing_variance=0.0, velocity_variance=0.0)
    # Velocity should be clamped to a min of 0.1
    assert humanized_bounds[0]["velocity"] == 0.1
    assert humanized_bounds[0]["time"] == 0.0

    # Test random variation applied without crashing
    humanized_rand = me.humanize_timing_and_velocity(raw_notes, timing_variance=10.0, velocity_variance=10.0)
    assert 0.1 <= humanized_rand[0]["velocity"] <= 1.0
    assert humanized_rand[0]["time"] >= 0.0
    assert humanized_rand[0]["duration"] >= 0.01
