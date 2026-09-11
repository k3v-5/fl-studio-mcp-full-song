"""High-level end-to-end production workflows combining theory, sound design, mixing, and arrangement."""
from __future__ import annotations

from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.scales import format_scale_info
from ..knowledge.chords import format_progression_info, get_progression_chords
from ..knowledge.drum_patterns import check_bpm_compatibility, get_patterns_for_bpm
from ..knowledge.producers import get_producer_profile
from ..knowledge.song_structures import get_structure
from ..knowledge.plugin_chains import get_chain, get_mix_levels, get_eq_guide
from ..knowledge.vocal_chains import get_vocal_chain, get_vocal_checklist
from ..knowledge.ozone12 import get_mastering_chain, get_lufs_targets


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}

    @mcp.tool(annotations={"title": "Workflow: Blueprint a new beat", **_RO})
    def fl_workflow_new_beat(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop")] = "boom_bap",
        bpm: Annotated[float, Field(ge=40.0, le=240.0, description="Target tempo in BPM")] = 90.0,
        key: Annotated[str, Field(description="Target key root (e.g. 'A', 'C', 'F#')")] = "A",
        scale: Annotated[str, Field(description="Scale type (minor_natural, harmonic_minor, dorian, etc.)")] = "minor_natural",
    ) -> dict:
        """Complete workflow blueprint for starting a new beat: scale, chord progression, drum style, and song structure."""
        scale_info = format_scale_info(key, scale)
        drums = get_patterns_for_bpm(bpm)
        recommended_drum = drums[0][0] if drums else "boom_bap_basic"
        structure = get_structure("boom_bap" if genre in ("boom_bap", "lofi", "jazz_hiphop") else "trap")

        return {
            "workflow": "New Beat Blueprint",
            "genre": genre,
            "bpm": bpm,
            "key": f"{key} {scale}",
            "scale_info": scale_info,
            "suggested_drum_pattern": recommended_drum,
            "available_patterns_at_bpm": [d[0] for d in drums[:3]],
            "recommended_structure": structure,
            "next_steps": [
                f"1. Set project tempo: fl_transport_set_tempo(tempo={bpm})",
                f"2. Generate drums: fl_generate_drum_pattern(style='{recommended_drum}', bpm={bpm})",
                f"3. Generate chords: fl_generate_chord_progression(key='{key}')",
                f"4. Generate bassline: fl_generate_bassline(root_notes='{key}', bpm={bpm})",
            ],
        }

    @mcp.tool(annotations={"title": "Workflow: Mix an element", **_RO})
    def fl_workflow_mix_element(
        element: Annotated[str, Field(description="Mix element: kick, snare, bass, 808, vocals, hihats, sample, melody")] = "kick",
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> dict:
        """All-in-one mixing blueprint for an instrument: EQ sweet spots, insert chain, reference level, and panning."""
        return {
            "element": element,
            "genre": genre,
            "plugin_chain": get_chain(element, genre),
            "eq_guide": get_eq_guide(element),
            "levels_reference": get_mix_levels(genre),
            "tip": "Always balance against the Kick fader at -6 dB headroom before finalizing plugins.",
        }

    @mcp.tool(annotations={"title": "Workflow: Produce in legendary producer style", **_RO})
    def fl_workflow_producer_style(
        producer: Annotated[str, Field(description="Producer: dj_premier, pete_rock, j_dilla, rza, 9th_wonder, alchemist, havoc")] = "dj_premier",
    ) -> dict:
        """Complete guide and action checklist to reproduce the exact sound signature of a legendary producer."""
        profile = get_producer_profile(producer.lower())
        return {
            "producer": producer,
            "profile": profile,
            "recommendation": f"Consult fl_get_producer_info(producer='{producer}') for deep gear breakdowns.",
        }

    @mcp.tool(annotations={"title": "Workflow: Vocal tracking and mixing session", **_RO})
    def fl_workflow_vocal_session(
        style: Annotated[str, Field(description="Vocal style: standard, bright_trap, yung_beef")] = "standard",
    ) -> dict:
        """End-to-end vocal workflow: recording checklist, pitch correction tuning, and full insert chain."""
        return {
            "style": style,
            "chain": get_vocal_chain(style),
            "checklist": get_vocal_checklist(),
            "tuning_tip": "Run fl_get_autotune_guide for fast retune speed settings suitable for your style.",
        }

    @mcp.tool(annotations={"title": "Workflow: Mastering prep and final export checklist", **_RO})
    def fl_workflow_mastering_checklist(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi")] = "boom_bap",
        target_platform: Annotated[str, Field(description="Streaming platform: spotify, youtube, soundcloud")] = "spotify",
    ) -> dict:
        """Final mastering delivery checklist: Ozone chain, LUFS loudness targets, and true peak requirements."""
        return {
            "genre": genre,
            "target_platform": target_platform,
            "mastering_chain": get_mastering_chain(genre),
            "lufs_targets": get_lufs_targets(genre, target_platform),
            "pre_flight_checks": [
                "1. Master bus has at least -3 dB to -6 dB headroom before limiter.",
                "2. Check low-end in mono below 100 Hz (use mix_doctor or fl_get_ozone_module_guide).",
                "3. True peak limiter ceiling set to -1.0 dBFS to prevent lossy inter-sample peaks.",
                "4. Dither enabled to 24-bit or 16-bit without noise shaping stacking.",
            ],
        }
