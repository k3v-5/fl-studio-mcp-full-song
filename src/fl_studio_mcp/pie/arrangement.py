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

    def generate_transition_riser(
        self,
        target_section_name: str,
        length_beats: float = 16.0,
        start_midi: int = 48,
        end_midi: int = 72,
        curve_type: str = "exponential"
    ) -> dict[str, Any]:
        """Compute an escalating MIDI transition sequence right before a section starts.

        Args:
            target_section_name: The section the riser leads into (e.g. 'drop').
            length_beats: How long the riser should be in quarter notes.
            start_midi: Starting MIDI pitch of the riser.
            end_midi: Ending MIDI pitch of the riser.
            curve_type: 'linear' or 'exponential' rhythmic acceleration.

        Returns:
            A dictionary containing the generated notes.
        """
        section = self.template_sections.get(target_section_name.lower())
        if not section:
            return {"error": f"Section {target_section_name} not found in template."}

        # Calculate exactly where the riser should start so it ends precisely on the drop
        target_beat = section.get("start_beat", 0.0)
        start_beat = target_beat - length_beats

        if start_beat < 0:
            start_beat = 0.0
            length_beats = target_beat

        if length_beats <= 0:
            return {"error": "Target section starts too early for a transition riser."}

        notes = []
        current_beat = start_beat
        note_length = 1.0 # start with quarter notes

        while current_beat < target_beat:
            # Calculate progress (0.0 to 1.0)
            progress = (current_beat - start_beat) / length_beats

            # Interpolate pitch
            current_pitch = int(start_midi + (end_midi - start_midi) * progress)

            # Interpolate velocity (rise from 0.4 to 1.0)
            current_velocity = 0.4 + (0.6 * progress)

            # Clamp note length to avoid overshooting
            actual_duration = min(note_length, target_beat - current_beat)

            notes.append({
                "midi": current_pitch,
                "time": float(current_beat),
                "duration": float(actual_duration),
                "velocity": float(current_velocity)
            })

            current_beat += actual_duration

            # Accelerate rhythm
            if curve_type == "exponential":
                if progress > 0.75:
                    note_length = 0.125 # 32nd notes
                elif progress > 0.5:
                    note_length = 0.25 # 16th notes
                elif progress > 0.25:
                    note_length = 0.5 # 8th notes
            # If linear, note_length remains 1.0 (quarter notes) or we could scale it smoothly.
            # Keeping linear as constant quarters for simplicity of distinction.

        return {
            "target_section": target_section_name,
            "start_beat": start_beat,
            "length_beats": length_beats,
            "riser_notes": notes
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
