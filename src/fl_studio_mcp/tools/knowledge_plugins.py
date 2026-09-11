"""VST & Plugin expert guides: Ozone 12, FabFilter, Serum 2, Cymatics, Auto-Tune, RX 11, Soundtoys."""
from __future__ import annotations

from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.ozone12 import (
    get_mastering_chain as get_ozone_chain,
    get_module_guide as get_ozone_module,
    get_quick_master,
    get_lufs_targets as get_ozone_lufs,
)
from ..knowledge.fabfilter import (
    get_eq_preset,
    get_compressor_preset,
    get_fabfilter_chain,
    get_saturn_guide,
)
from ..knowledge.serum2 import (
    get_patch_recipe,
    get_genre_sounds,
    get_sound_design_tips,
)
from ..knowledge.cymatics import (
    get_cymatics_chain,
    get_plugin_guide as get_cymatics_guide,
)
from ..knowledge.autotune import (
    get_autotune_settings,
    get_vocal_tuning_workflow,
    get_key_detection_guide,
)
from ..knowledge.rx11 import (
    get_cleanup_chain,
    get_module_guide as get_rx_module,
    get_repair_workflow,
)
from ..knowledge.plugin_chains import get_soundtoys_guide


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}

    # ========================================================================
    # UNIFIED VST CONSULTANT & RESOURCES (High-Efficiency Context)
    # ========================================================================
    @mcp.tool(annotations={"title": "Unified VST module and plugin guide", **_RO})
    def fl_get_vst_module_guide(
        suite: Annotated[str, Field(description="Plugin suite: ozone, rx11, cymatics, soundtoys, fabfilter, serum")],
        module_or_plugin: Annotated[str, Field(description="Specific module or plugin name (e.g. 'maximizer', 'spectral_denoise', 'diablo', 'saturn')")] = "",
    ) -> str:
        """Unified reference guide for leading mixing & mastering plugins (Ozone 12, RX 11, Cymatics, Soundtoys, FabFilter, Serum)."""
        suite_clean = suite.lower().strip()
        mod_clean = module_or_plugin.lower().strip()
        if "ozone" in suite_clean:
            if not mod_clean:
                return "Ozone 12 Modules: equalizer, dynamic_eq, dynamics, maximizer, exciter, imager, vintage_tape, vintage_eq, vintage_compressor, vintage_limiter, spectral_shaper, stabilizer, bass_control, clarity, impact, low_end_focus, match_eq, master_rebalance, unlimiter, stem_eq."
            return get_ozone_module(mod_clean)
        elif "rx" in suite_clean:
            if not mod_clean:
                return get_repair_workflow()
            return get_rx_module(mod_clean)
        elif "cymatics" in suite_clean:
            if not mod_clean:
                return "Cymatics plugins available: diablo, pluto, space, quake, vortex."
            return get_cymatics_guide(mod_clean)
        elif "soundtoy" in suite_clean:
            return get_soundtoys_guide()
        elif "fabfilter" in suite_clean:
            if "saturn" in mod_clean or "sat" in mod_clean:
                return get_saturn_guide()
            return "FabFilter guides: use fl_get_fabfilter_eq, fl_get_fabfilter_compressor, or fl_get_fabfilter_mixing_chain."
        elif "serum" in suite_clean:
            return get_sound_design_tips()
        return f"Unknown VST suite '{suite}'. Supported suites: ozone, rx11, cymatics, soundtoys, fabfilter, serum."

    # FastMCP Resources for on-demand context reading (0 token prompt overhead)
    @mcp.resource("flstudio://guides/ozone/{module}")
    def resource_ozone_module(module: str) -> str:
        """Deep guide and parameter recommendations for an Ozone 12 module."""
        return get_ozone_module(module)

    @mcp.resource("flstudio://guides/rx11/{module}")
    def resource_rx_module(module: str) -> str:
        """Audio restoration and repair guide for an iZotope RX 11 module."""
        return get_rx_module(module)

    @mcp.resource("flstudio://guides/soundtoys")
    def resource_soundtoys_guide() -> str:
        """Guide for creative use of Soundtoys plugins in music production."""
        return get_soundtoys_guide()

    # ========================================================================
    # Ozone 12 Mastering
    # ========================================================================
    @mcp.tool(annotations={"title": "Get Ozone 12 mastering chain", **_RO})
    def fl_get_ozone_mastering(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop")] = "boom_bap",
    ) -> str:
        """Get complete Ozone 12 mastering chain for a genre with exact module parameters."""
        return get_ozone_chain(genre)

    @mcp.tool(annotations={"title": "Get Ozone quick master chain", **_RO})
    def fl_get_ozone_quick_master(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop")] = "boom_bap",
    ) -> str:
        """Get simplified 3-4 module Ozone mastering chain for fast professional results."""
        return get_quick_master(genre)

    @mcp.tool(annotations={"title": "Get Ozone 12 module guide", **_RO})
    def fl_get_ozone_module_guide(
        module: Annotated[str, Field(description="Module: equalizer, dynamic_eq, dynamics, maximizer, exciter, imager, vintage_tape, vintage_eq, vintage_compressor, vintage_limiter, spectral_shaper, stabilizer, bass_control, clarity, impact, low_end_focus, match_eq, master_rebalance, unlimiter, stem_eq")] = "maximizer",
    ) -> str:
        """Get deep technical guide for a specific Ozone 12 module with parameter recommendations."""
        return get_ozone_module(module)

    @mcp.tool(annotations={"title": "Get LUFS targets by genre/platform", **_RO})
    def fl_get_lufs_target(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop (optional)")] = "",
        platform: Annotated[str, Field(description="Platform: spotify, youtube, apple_music, soundcloud (optional)")] = "",
    ) -> str:
        """Get LUFS integrated loudness targets, true peak limits, and dynamic range by genre and platform."""
        return get_ozone_lufs(genre, platform)

    # ========================================================================
    # FabFilter Suite
    # ========================================================================
    @mcp.tool(annotations={"title": "Get FabFilter Pro-Q 4 EQ preset", **_RO})
    def fl_get_fabfilter_eq(
        element: Annotated[str, Field(description="Element: kick, snare, bass_808, vocals, piano_keys, hihats, master")] = "vocals",
    ) -> str:
        """Get FabFilter Pro-Q 4 parametric EQ curve, band frequencies, Q, and filter slopes for an element."""
        return get_eq_preset(element)

    @mcp.tool(annotations={"title": "Get FabFilter Pro-C 3 compressor preset", **_RO})
    def fl_get_fabfilter_compressor(
        element: Annotated[str, Field(description="Element: vocal_boom_bap, vocal_trap, 808_trap, drum_bus_boom_bap, drum_bus_trap, drum_bus_phonk, master_bus")] = "vocal_boom_bap",
    ) -> str:
        """Get FabFilter Pro-C 3 compression settings (attack, release, ratio, knee, sidechain) for an element."""
        return get_compressor_preset(element)

    @mcp.tool(annotations={"title": "Get full FabFilter mixing chain", **_RO})
    def fl_get_fabfilter_mixing_chain(
        chain_type: Annotated[str, Field(description="Chain: vocal_chain, drum_bus_chain, 808_chain, master_chain")] = "vocal_chain",
    ) -> str:
        """Get complete FabFilter-only insert chain (Pro-Q, Pro-C, Saturn, Pro-MB, Pro-L)."""
        return get_fabfilter_chain(chain_type)

    @mcp.tool(annotations={"title": "Get Saturn 2 saturation guide", **_RO})
    def fl_get_saturation_guide() -> str:
        """Get FabFilter Saturn 2 multiband saturation presets, tube/tape/amp modeling, and warmth guides."""
        return get_saturn_guide()

    # ========================================================================
    # Serum 2 Sound Design
    # ========================================================================
    @mcp.tool(annotations={"title": "Get Serum 2 patch recipe", **_RO})
    def fl_get_serum_patch(
        sound_type: Annotated[str, Field(description="Patch type: 808_sub, 808_distorted, trap_lead, boom_bap_keys, dark_pad, pluck_melody, phonk_cowbell, vinyl_texture")] = "808_sub",
    ) -> str:
        """Get step-by-step Serum 2 patch recipe: wavetables, oscillators, envelopes, filters, and FX."""
        return get_patch_recipe(sound_type)

    @mcp.tool(annotations={"title": "Get recommended Serum sounds for genre", **_RO})
    def fl_get_serum_sounds_for_genre(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi")] = "boom_bap",
    ) -> str:
        """Get recommended Serum 2 sound palette and sonic components to build for a genre."""
        return get_genre_sounds(genre)

    @mcp.tool(annotations={"title": "Get Serum sound design masterclass", **_RO})
    def fl_get_serum_sound_design() -> str:
        """Get advanced Serum 2 synthesis techniques: custom wavetables, FM synthesis, resampling, and macros."""
        return get_sound_design_tips()

    # ========================================================================
    # Cymatics Plugins
    # ========================================================================
    @mcp.tool(annotations={"title": "Get Cymatics plugin chain", **_RO})
    def fl_get_cymatics_plugin_chain(
        element: Annotated[str, Field(description="Element: drums, bass, 808, vocals, leads, melody, keys")] = "808",
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi")] = "trap",
    ) -> str:
        """Get Cymatics plugin chain (Diablo, Pluto, Space, Vortex, etc.) for an instrument and genre."""
        return get_cymatics_chain(element, genre)

    @mcp.tool(annotations={"title": "Get Cymatics plugin guide", **_RO})
    def fl_get_cymatics_plugin_guide(
        plugin: Annotated[str, Field(description="Plugin: diablo, pluto, space, quake, vortex")] = "diablo",
    ) -> str:
        """Get detailed guide and recommended knob positions for a Cymatics effect plugin."""
        return get_cymatics_guide(plugin)

    # ========================================================================
    # Auto-Tune & Vocal Tuning
    # ========================================================================
    @mcp.tool(annotations={"title": "Get Auto-Tune Pro settings", **_RO})
    def fl_get_autotune_guide(
        style: Annotated[str, Field(description="Vocal style: natural (boom_bap/jazz), moderate (rnb/pop), hard_tune (trap/drill), extreme (hyperpop)")] = "hard_tune",
    ) -> str:
        """Get exact Antares Auto-Tune Pro parameters: retune speed, flex-tune, humanoid, formant, and throat length."""
        return get_autotune_settings(style)

    @mcp.tool(annotations={"title": "Get vocal pitch correction workflow", **_RO})
    def fl_get_vocal_tuning_guide() -> str:
        """Get complete vocal tuning workflow from prep and key detection to corrective vs creative pitching."""
        return get_vocal_tuning_workflow()

    @mcp.tool(annotations={"title": "Get Auto-Key key detection guide", **_RO})
    def fl_get_key_detection() -> str:
        """Get Auto-Key and pitch detection workflow, routing, and accurate scale verification."""
        return get_key_detection_guide()

    # ========================================================================
    # iZotope RX 11 Cleanup & Restoration
    # ========================================================================
    @mcp.tool(annotations={"title": "Get RX 11 cleanup chain", **_RO})
    def fl_get_rx_cleanup(
        source_type: Annotated[str, Field(description="Source: vinyl_sample, youtube_sample, vocal_recording, field_recording, stem_isolation")] = "vinyl_sample",
    ) -> str:
        """Get iZotope RX 11 audio restoration chain for degraded audio, vinyl clicks, hum, or noisy recordings."""
        return get_cleanup_chain(source_type)

    @mcp.tool(annotations={"title": "Get RX 11 module guide", **_RO})
    def fl_get_rx_module_guide(
        module: Annotated[str, Field(description="Module: spectral_denoise, voice_denoise, de_click, de_crackle, de_clip, de_ess, de_plosive, breath_control, mouth_de_click, de_hum, de_reverb, dialogue_isolate, repair_assistant")] = "spectral_denoise",
    ) -> str:
        """Get detailed guide for a specific iZotope RX 11 audio repair module."""
        return get_rx_module(module)

    @mcp.tool(annotations={"title": "Get RX 11 repair workflow overview", **_RO})
    def fl_get_rx_overview() -> str:
        """Get general iZotope RX 11 repair workflow overview and proper processing order."""
        return get_repair_workflow()

    # ========================================================================
    # Soundtoys
    # ========================================================================
    @mcp.tool(annotations={"title": "Get Soundtoys plugins guide", **_RO})
    def fl_get_soundtoys_plugins_guide() -> str:
        """Get guide for using Soundtoys effects (Decapitator, EchoBoy, Little AlterBoy, PanMan, Crystallizer) in hip-hop production."""
        return get_soundtoys_guide()
