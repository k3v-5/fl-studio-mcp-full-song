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
    def mix_apply_sidechain_ducking(masking_analysis: dict[str, Any], kick_times: list[float], sidechain_channel_id: int) -> dict[str, Any]:
        """Automatically inject ghost notes to trigger ducking (sidechain) based on masking analysis.

        Args:
            masking_analysis: The dictionary returned by mix_analyze_masking.
            kick_times: List of start times (in quarter notes) for the kick drum triggers.
            sidechain_channel_id: The FL Studio channel ID designated as the Sidechain Trigger (Envelope Controller).
        """
        from fl_studio_mcp.pie.sidechain_engine import get_sidechain_engine
        from fl_studio_mcp.pie.midi_adapter import get_midi_adapter

        se = get_sidechain_engine()
        result = se.process_masking_result(masking_analysis, kick_times)

        if result.get("action") == "apply_sidechain":
            adapter = get_midi_adapter()
            adapter.queue_notes(sidechain_channel_id, result["ghost_notes"])
            # Flush immediately to apply the curve
            flush_res = adapter.flush()
            result["flush_status"] = flush_res

        return result

    @mcp.tool()
    def mix_apply_correction(track_id: int, frequency: float, q_factor: float, gain: float) -> str:
        """Apply an EQ correction to fix a mix issue.

        Note: Since the physical engine relies on the global fl_set_plugin_param_value,
        this tool instructs the LLM on exactly how to use the underlying API to fix the mix.

        Args:
            track_id: Mixer track ID.
            frequency: Target frequency in Hz.
            q_factor: Bandwidth Q factor.
            gain: Gain in dB.
        """
        return f"To apply {gain}dB at {frequency}Hz on track {track_id}, use fl_set_plugin_param_value on the EQ plugin indices."

    @mcp.tool()
    def master_readiness(target_lufs: float = -9.0, target_true_peak: float = -1.0) -> dict[str, Any]:
        """Measure the LUFS and True Peak of the master bus against AI-provided targets."""
        dee = get_digital_ear_engine()
        return dee.measure_readiness(target_lufs, target_true_peak)

    @mcp.tool()
    def forensics_report(dc_offset_threshold: float = 0.05, clipping_threshold_db: float = 0.0) -> dict[str, Any]:
        """Generate a low-level DSP diagnostic report for phase and clipping using AI-provided thresholds."""
        dee = get_digital_ear_engine()
        return dee.generate_forensics_report(dc_offset_threshold, clipping_threshold_db)

    @mcp.tool()
    def digital_ear_phase_analyze() -> dict[str, Any]:
        """Analyze the stereo phase correlation (Goniometer) of the captured audio.

        Requires that audio has been captured first. Warns if the mix is not mono-compatible.
        """
        dee = get_digital_ear_engine()
        audio = dee.get_audio_array()
        if len(audio) == 0:
            return {"error": "No audio captured in buffer."}

        # Mocking left and right channels by splitting the mono buffer for testing/prototype
        mid = len(audio) // 2
        return dee.analyze_stereo_phase(audio[:mid], audio[mid:mid*2])
