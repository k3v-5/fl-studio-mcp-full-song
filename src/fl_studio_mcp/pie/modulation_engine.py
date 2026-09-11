"""Expressive Automation & Modulation Engine for FL Studio MCP (PIE).

Generates:
1. Native FL Studio 808 slides & portamento notes (flpianoroll note.slide = True).
2. Pitch Bend sweeps (-8192 to +8191) for tension build-ups and synth glides.
3. Mod Wheel (CC 1) & Expression (CC 11) vibrato curves.
4. Filter Cutoff (CC 74) & Resonance (CC 71) LFO wobbles and sweeps.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class ModulationEngine:
    """Calculates musical modulation curves, 808 glides, and parameter sweeps."""

    @staticmethod
    def generate_808_slides(
        root_pitch: int = 36,        # C2
        slide_pitch: int = 48,       # C3 (+1 octave slide)
        start_bar: float = 0.0,
        root_length_bars: float = 1.0,
        slide_length_bars: float = 0.25,
        velocity: float = 0.85,
    ) -> List[Dict[str, Any]]:
        """Generate an authentic 808 glide note pair.

        In FL Studio, a slide note overlapping a sustained root note causes the
        pitch to glide smoothly to the target pitch over the duration of the slide note.
        """
        # Slide note starts before root note ends
        slide_start = max(start_bar, round(start_bar + root_length_bars - slide_length_bars, 4))

        root_note = {
            "pitch": int(root_pitch),
            "start_bars": round(float(start_bar), 4),
            "length_bars": round(float(root_length_bars), 4),
            "velocity": round(float(velocity), 4),
            "slide": False,
            "porta": False,
        }

        slide_note = {
            "pitch": int(slide_pitch),
            "start_bars": slide_start,
            "length_bars": round(float(slide_length_bars), 4),
            "velocity": round(float(velocity), 4),
            "slide": True,
            "porta": False,
        }

        return [root_note, slide_note]

    @staticmethod
    def generate_lfo_curve(
        shape: str = "sine",            # sine, triangle, saw_up, saw_down, wobble
        bars: float = 4.0,
        rate_hz_or_subdiv: float = 2.0, # cycles per bar (e.g. 2.0 = 2 cycles/bar -> 1/8 note wobble)
        min_val: int = 20,              # MIDI CC min (0-127)
        max_val: int = 120,             # MIDI CC max (0-127)
        steps_per_bar: int = 16,
    ) -> List[Dict[str, Any]]:
        """Generate MIDI Control Change (CC) LFO modulation points."""
        total_steps = int(round(bars * steps_per_bar))
        curve = []
        val_range = max_val - min_val

        for i in range(total_steps + 1):
            t_bars = (i / steps_per_bar)
            phase = (t_bars * rate_hz_or_subdiv) % 1.0

            if shape == "sine":
                raw = 0.5 + 0.5 * math.sin(phase * 2.0 * math.pi)
            elif shape == "triangle":
                raw = 1.0 - 2.0 * abs(phase - 0.5)
            elif shape == "saw_up":
                raw = phase
            elif shape == "saw_down":
                raw = 1.0 - phase
            elif shape == "wobble":
                # Dubstep wobble: combines fundamental sine with a harmonic overtone
                f1 = 0.5 + 0.5 * math.sin(phase * 2.0 * math.pi)
                f2 = 0.5 + 0.5 * math.sin(phase * 4.0 * math.pi)
                raw = 0.7 * f1 + 0.3 * f2
            else:
                raw = phase

            val = int(round(min_val + raw * val_range))
            val = max(0, min(127, val))

            curve.append({
                "time_bars": round(t_bars, 4),
                "value": val,
            })

        return curve

    @staticmethod
    def generate_pitch_bend_sweep(
        start_bar: float = 0.0,
        duration_bars: float = 2.0,
        start_bend: int = 0,         # -8192 to 8191 (0 is center)
        end_bend: int = 8191,        # maximum positive bend
        curve_power: float = 2.0,    # 1.0 = linear, 2.0 = exponential ramp
        steps_per_bar: int = 16,
    ) -> List[Dict[str, Any]]:
        """Generate Pitch Bend events over time for risers or dramatic drops."""
        total_steps = int(round(duration_bars * steps_per_bar))
        events = []
        bend_range = end_bend - start_bend

        for i in range(total_steps + 1):
            progress = i / max(1, total_steps)
            curved_progress = math.pow(progress, curve_power)
            bend = int(round(start_bend + curved_progress * bend_range))
            bend = max(-8192, min(8191, bend))

            t_bars = round(start_bar + (i / steps_per_bar), 4)
            events.append({
                "time_bars": t_bars,
                "pitch": bend,
            })

        return events

    @staticmethod
    def generate_tension_riser(
        start_bar: float = 8.0,
        duration_bars: float = 4.0,
    ) -> Dict[str, Any]:
        """Generate a complete tension riser package (exponential Pitch Bend + Filter Cutoff sweep)."""
        pitch_sweeps = ModulationEngine.generate_pitch_bend_sweep(
            start_bar=start_bar,
            duration_bars=duration_bars,
            start_bend=0,
            end_bend=8191,
            curve_power=2.2,
        )

        cutoff_sweeps = ModulationEngine.generate_lfo_curve(
            shape="saw_up",
            bars=duration_bars,
            rate_hz_or_subdiv=1.0 / duration_bars, # single 4-bar ramp up
            min_val=20,
            max_val=127,
            steps_per_bar=16,
        )
        # Shift cutoff time_bars to match start_bar
        for pt in cutoff_sweeps:
            pt["time_bars"] = round(start_bar + pt["time_bars"], 4)

        return {
            "start_bar": start_bar,
            "duration_bars": duration_bars,
            "pitch_bends": pitch_sweeps,
            "filter_cutoff_cc74": cutoff_sweeps,
            "description": "4-bar exponential tension riser for pre-drop build-up.",
        }


_global_modulation: Optional[ModulationEngine] = None


def get_modulation_engine() -> ModulationEngine:
    """Return singleton ModulationEngine instance."""
    global _global_modulation
    if _global_modulation is None:
        _global_modulation = ModulationEngine()
    return _global_modulation
