"""Music Engine logic for FL Studio MCP (PIE).

Generates MIDI data for harmonies, basslines, and drums.
"""

from __future__ import annotations

import random
from typing import Any

class MusicEngine:
    def __init__(self) -> None:
        pass

    def generate_harmony(self, scale: str, progression: list[str], length: int) -> list[dict[str, Any]]:
        """Mock harmony generator."""
        notes = []
        time_counter = 0.0
        duration_per_chord = length / max(1, len(progression))

        # Simple mock mapping
        base_midi = 60 # Middle C
        if "minor" in scale.lower():
            base_midi = 60

        for chord in progression:
            # Generate a triad for each chord (velocity scale 0.0 - 1.0)
            notes.append({"midi": base_midi, "time": float(time_counter), "duration": float(duration_per_chord), "velocity": 0.8})
            notes.append({"midi": base_midi + 4, "time": float(time_counter), "duration": float(duration_per_chord), "velocity": 0.8})
            notes.append({"midi": base_midi + 7, "time": float(time_counter), "duration": float(duration_per_chord), "velocity": 0.8})
            time_counter += duration_per_chord

        return notes

    def generate_bass(self, root_notes: list[int], rhythm_pattern: str) -> list[dict[str, Any]]:
        """Mock bassline generator."""
        notes = []
        time_counter = 0.0

        # Simple driving 8th note rhythm
        if rhythm_pattern == "driving":
            for root in root_notes:
                for _ in range(8):
                    notes.append({"midi": root - 12, "time": float(time_counter), "duration": 0.5, "velocity": 0.9})
                    time_counter += 0.5
        else:
             for root in root_notes:
                notes.append({"midi": root - 12, "time": float(time_counter), "duration": 4.0, "velocity": 0.9})
                time_counter += 4.0

        return notes

    def generate_drums(self, genre: str, intensity: float) -> list[dict[str, Any]]:
        """Mock drum generator specifically formatted for step sequencer (grid bits)."""
        # Returns a list of steps to activate on channels
        # For FL Studio, step sequencers are often updated channel by channel
        steps = []
        if genre.lower() == "house":
            # 4 on the floor kick
            steps.append({"instrument": "kick", "grid_bits": [True, False, False, False] * 4})
            # Hats on off-beats
            steps.append({"instrument": "hat", "grid_bits": [False, False, True, False] * 4})
            # Snare/Clap on 2 and 4
            steps.append({"instrument": "snare", "grid_bits": [False, False, False, False, True, False, False, False, False, False, False, False, True, False, False, False]})

        return steps

# Singleton instance
_music_engine = MusicEngine()

def get_music_engine() -> MusicEngine:
    return _music_engine
