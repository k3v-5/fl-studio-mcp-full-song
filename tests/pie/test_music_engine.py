import pytest
from fl_studio_mcp.pie.music_engine import get_music_engine

def test_music_engine_harmony_schema():
    me = get_music_engine()
    notes = me.generate_harmony("C minor", ["i", "iv"], length=4)

    assert len(notes) > 0
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
    notes = me.generate_bass([60, 65], "driving")

    assert len(notes) > 0
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
