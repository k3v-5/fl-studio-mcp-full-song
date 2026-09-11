"""Tests for slide notes in pyscript_gen."""

from fl_studio_mcp.pyscript_gen import render_apply_script


def test_render_apply_script_includes_slide():
    notes = [
        {"pitch": 36, "time_bars": 0.0, "length_bars": 1.0, "velocity": 0.8, "slide": False},
        {"pitch": 48, "time_bars": 0.75, "length_bars": 0.25, "velocity": 0.8, "slide": True},
    ]
    script = render_apply_script(notes, mode="replace")

    assert "n.slide = True" in script
    assert "n.number = int(pitch)" in script
    # Verify the notes tuple contains True for slide on the second note
    assert "(48, 0.75, 0.25, 0.8, True, False)" in script
