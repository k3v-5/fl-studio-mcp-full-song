"""Arrangement Engine for FL Studio MCP (PIE).

Orchestrates macro-structure based on the 'Smart Template' workaround.
"""

from __future__ import annotations

from typing import Any
from fl_studio_mcp.pie.music_engine import get_music_engine

class ArrangementEngine:
    def __init__(self) -> None:
        self.template_sections = {}

    def update_structure(self, template_definition: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Allow the AI assistant to define the template sections dynamically."""
        self.template_sections = template_definition
        return {"status": "success", "sections_loaded": len(self.template_sections)}

    def get_structure(self) -> dict[str, Any]:
        """Return the layout of the current Smart Template."""
        if not self.template_sections:
            return {"warning": "No template structure defined. Use update_structure first."}
        return self.template_sections

    def generate_section(
        self,
        section_name: str,
        chords: list[list[int]],
        chord_durations: list[float],
        bass_midi: list[int],
        bass_durations: list[float]
    ) -> dict[str, Any]:
        """Generate MIDI data for an entire section using AI-provided notes and durations."""
        section = self.template_sections.get(section_name.lower())
        if not section:
            return {"error": f"Section {section_name} not found in template."}

        me = get_music_engine()
        start_offset = section.get("start_beat", 0.0)

        raw_harmony = me.generate_harmony(chords, chord_durations, start_time=0.0)
        raw_bass = me.generate_bass(bass_midi, bass_durations, start_time=0.0)

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
