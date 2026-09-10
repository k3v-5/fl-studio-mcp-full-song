"""PIE Digital Ear Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_digital_ear_tools(mcp: FastMCP) -> None:
    """Register Digital Ear tools with the MCP server."""
    from fl_studio_mcp.pie.digital_ear import get_digital_ear_engine

    @mcp.tool()
    def audio_capture(duration: float) -> str:
        """Trigger the VST Interceptor to capture audio.

        Args:
            duration: Duration in seconds to capture.
        """
        import time
        dee = get_digital_ear_engine()
        dee.start_capture()
        time.sleep(duration)
        return dee.stop_capture()

    @mcp.tool()
    def mix_analyze_masking(track_a: str, track_b: str) -> dict[str, Any]:
        """Analyze frequency masking between two tracks.

        Note: Currently uses the global captured buffer as a mock instead of specific tracks
        due to the single-channel limitation of the VST Interceptor prototype.

        Args:
            track_a: Name or ID of the first track.
            track_b: Name or ID of the second track.
        """
        dee = get_digital_ear_engine()
        audio = dee.get_audio_array()
        if len(audio) == 0:
             return {"error": "No audio captured. Run audio_capture first."}

        # Mock comparing two identical arrays for demonstration of the DSP logic
        return dee.analyze_masking(audio, audio)

    @mcp.tool()
    def mix_apply_correction(track_id: int, frequency: float, q_factor: float, gain: float) -> str:
        """Apply an EQ correction to fix a mix issue.

        Args:
            track_id: Mixer track ID.
            frequency: Target frequency in Hz.
            q_factor: Bandwidth Q factor.
            gain: Gain in dB.
        """
        dee = get_digital_ear_engine()
        return dee.apply_correction(track_id, frequency, q_factor, gain)

    @mcp.tool()
    def master_readiness() -> dict[str, Any]:
        """Measure the LUFS and True Peak of the master bus."""
        dee = get_digital_ear_engine()
        return dee.measure_readiness()

    @mcp.tool()
    def master_apply_target(target_lufs: float) -> str:
        """Attempt to hit the target LUFS by adjusting the Master Limiter.

        Args:
            target_lufs: Desired LUFS level (e.g., -9.0).
        """
        dee = get_digital_ear_engine()
        return dee.apply_master_target(target_lufs)

    @mcp.tool()
    def forensics_report() -> dict[str, Any]:
        """Generate a low-level DSP diagnostic report for phase and clipping."""
        dee = get_digital_ear_engine()
        return dee.generate_forensics_report()
