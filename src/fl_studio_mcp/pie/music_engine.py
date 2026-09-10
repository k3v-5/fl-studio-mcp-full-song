"""Music Engine logic for FL Studio MCP (PIE).

Generates MIDI data for harmonies, basslines, and drums.
"""

from __future__ import annotations

import random
from typing import Any

class MusicEngine:
    def __init__(self) -> None:
        pass

    def generate_harmony(self, chords: list[list[int]], durations: list[float], start_time: float = 0.0, base_velocity: float = 0.8) -> list[dict[str, Any]]:
        """Generates MIDI data based explicitly on arrays of midi notes provided by the AI.

        Args:
            chords: List of chords, where each chord is a list of MIDI note integers (e.g. [[60, 64, 67], [62, 65, 69]]).
            durations: The duration in quarter notes for each chord (must match length of chords).
            start_time: Starting offset.
            base_velocity: Base velocity for the notes.
        """
        notes = []
        time_counter = start_time

        if len(chords) != len(durations):
            raise ValueError("Length of chords and durations must match.")

        for i, chord in enumerate(chords):
            duration = durations[i]
            for midi_note in chord:
                notes.append({
                    "midi": midi_note,
                    "time": float(time_counter),
                    "duration": float(duration),
                    "velocity": float(base_velocity)
                })
            time_counter += duration

        return notes

    def generate_bass(self, midi_sequence: list[int], durations: list[float], start_time: float = 0.0, base_velocity: float = 0.9) -> list[dict[str, Any]]:
        """Generates bassline MIDI data explicitly from AI-provided sequences.

        Args:
            midi_sequence: List of MIDI root notes.
            durations: Duration of each note.
            start_time: Starting offset.
            base_velocity: Velocity for the notes.
        """
        notes = []
        time_counter = start_time

        if len(midi_sequence) != len(durations):
            raise ValueError("Length of midi_sequence and durations must match.")

        for i, midi_note in enumerate(midi_sequence):
            duration = durations[i]
            notes.append({
                "midi": midi_note,
                "time": float(time_counter),
                "duration": float(duration),
                "velocity": float(base_velocity)
            })
            time_counter += duration

        return notes

    def generate_drums(self, drum_patterns: dict[str, list[bool]]) -> list[dict[str, Any]]:
        """Accepts explicit boolean arrays (grid bits) for drum sequences directly from the AI.

        Args:
            drum_patterns: A dict mapping channel identifiers (or standard instrument names)
                           to their explicit boolean step arrays (e.g. {"kick": [True, False, False, False]}).
        """
        steps = []
        for instrument, grid_bits in drum_patterns.items():
            steps.append({
                "instrument": instrument,
                "grid_bits": grid_bits
            })

        return steps

# Singleton instance
_music_engine = MusicEngine()

def get_music_engine() -> MusicEngine:
    return _music_engine
