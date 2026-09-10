"""Sidechain & LFO Ducking Engine for FL Studio MCP (PIE).

Simulates volume ducking (sidechain compression) by injecting "Ghost Notes"
or velocity curves into the Piano Roll to trigger a Fruity Envelope Controller
or similar linked parameter in the Smart Template.
"""

from __future__ import annotations

from typing import Any

class SidechainEngine:
    def __init__(self) -> None:
        # Standard MIDI note mapped to trigger sidechain ducking in the template
        self.trigger_note = 0 # C0

    def generate_ducking_curve(
        self,
        kick_rhythm_times: list[float],
        depth: float = 1.0,
        duration: float = 0.5
    ) -> list[dict[str, Any]]:
        """Generate ghost notes that simulate a ducking envelope.

        Args:
            kick_rhythm_times: A list of start times (in quarter notes) where the kick hits.
            depth: The intensity of the sidechain (velocity of the ghost trigger).
            duration: How long the ducking should last before releasing (in quarter notes).
        """
        ghost_notes = []

        # Ensure depth is capped safely
        safe_depth = max(0.0, min(1.0, depth))

        for time_pos in kick_rhythm_times:
            ghost_notes.append({
                "midi": self.trigger_note,
                "time": float(time_pos),
                "duration": float(duration),
                "velocity": float(safe_depth)
            })

        return ghost_notes

    def process_masking_result(
        self,
        masking_analysis: dict[str, Any],
        kick_times: list[float]
    ) -> dict[str, Any]:
        """Evaluate if ducking is needed based on the Digital Ear masking analysis."""

        if "error" in masking_analysis:
            return {"error": "Cannot process sidechain. Masking analysis contains errors."}

        if not masking_analysis.get("masking_detected", False):
            return {
                "action": "none",
                "message": "No significant frequency masking detected. Sidechain skipped."
            }

        # Determine depth based loosely on conflict zone if provided (mock logic for AI assistance)
        zone = masking_analysis.get("conflict_zone_hz", [0, 0])
        # If the conflict is lower frequency, duck harder (bass frequencies clash more destructively)
        avg_hz = (zone[0] + zone[1]) / 2.0
        calculated_depth = 1.0 if avg_hz < 100 else 0.6

        curve = self.generate_ducking_curve(kick_times, calculated_depth)

        return {
            "action": "apply_sidechain",
            "message": f"Masking detected at {avg_hz}Hz. Generated ghost notes for sidechain.",
            "ghost_notes": curve
        }

# Singleton instance
_sidechain_engine = SidechainEngine()

def get_sidechain_engine() -> SidechainEngine:
    return _sidechain_engine
