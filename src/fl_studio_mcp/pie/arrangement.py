"""Arrangement Engine for FL Studio MCP (PIE).

Orchestrates macro-structure based on the 'Smart Template' workaround.
"""

from __future__ import annotations

from typing import Any
from fl_studio_mcp.pie.music_engine import get_music_engine

class ArrangementEngine:
    def __init__(self) -> None:
        # Default smart template layout (mock)
        # Assumes a 128 BPM track where each section is 16 bars long (64 beats)
        self.template_sections = {
            "intro": {"start_beat": 0, "length_beats": 64, "energy_level": 0.2},
            "verse": {"start_beat": 64, "length_beats": 64, "energy_level": 0.5},
            "build": {"start_beat": 128, "length_beats": 64, "energy_level": 0.8},
            "drop": {"start_beat": 192, "length_beats": 64, "energy_level": 1.0},
            "outro": {"start_beat": 256, "length_beats": 64, "energy_level": 0.1},
        }

    def get_structure(self) -> dict[str, Any]:
        """Return the layout of the current Smart Template."""
        return self.template_sections

    def generate_section(self, section_name: str, chord_prog: list[str]) -> dict[str, Any]:
        """Generate MIDI data for an entire section and calculate the time offsets."""
        section = self.template_sections.get(section_name.lower())
        if not section:
            return {"error": f"Section {section_name} not found in template."}

        me = get_music_engine()
        start_offset = section["start_beat"]

        # Generate raw music parts (they start at time=0.0 relative to the section)
        raw_harmony = me.generate_harmony("C minor", chord_prog, 16)
        raw_bass = me.generate_bass([60, 60, 60, 60], "driving" if section["energy_level"] > 0.5 else "sustained")

        # Apply the time offset so they land in the correct part of the FL Studio playlist
        offset_harmony = self._apply_offset(raw_harmony, start_offset)
        offset_bass = self._apply_offset(raw_bass, start_offset)

        return {
            "section": section_name,
            "start_beat": start_offset,
            "harmony_notes": offset_harmony,
            "bass_notes": offset_bass
        }

    def _apply_offset(self, notes: list[dict[str, Any]], offset: float) -> list[dict[str, Any]]:
        """Add the time offset to a list of MIDI note dictionaries."""
        shifted_notes = []
        for note in notes:
            shifted = note.copy()
            shifted["time"] += offset
            shifted_notes.append(shifted)
        return shifted_notes

# Singleton instance
_arrangement_engine = ArrangementEngine()

def get_arrangement_engine() -> ArrangementEngine:
    return _arrangement_engine
