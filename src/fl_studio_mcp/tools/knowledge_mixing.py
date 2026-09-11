"""Mixing, routing, sampling, vocal chains, and mastering knowledge tools."""
from __future__ import annotations

from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.plugin_chains import (
    get_chain,
    get_mix_levels,
    get_mastering_chain,
    get_eq_guide,
    get_send_config,
    get_gain_staging_guide,
    get_mixer_template,
    get_lufs_targets,
    get_workflow,
)
from ..knowledge.vocal_chains import (
    get_vocal_chain,
    get_vocal_tricks,
    get_vocal_checklist,
)
from ..knowledge.fabfilter import get_fabfilter_chain, get_eq_preset
from ..knowledge.cymatics import get_cymatics_chain
from ..knowledge.ozone12 import get_mastering_chain as get_ozone_chain
from ..knowledge.sampling import (
    get_chopping_guide,
    get_sampling_workflow,
    get_drum_machine_emulation,
    get_sample_processing_chain,
)
from ..knowledge.mixing_advanced import (
    get_mixing_workflow,
    get_bus_setup,
    get_gain_staging_guide as get_advanced_staging,
    get_mixing_checklist as get_advanced_checklist,
)


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
    _WR = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True}

    @mcp.tool(annotations={"title": "Get recommended plugin chain", **_RO})
    def fl_get_plugin_chain(
        element: Annotated[str, Field(description="Element: kick, snare, clap, hihats, bass, 808, sample, melody, pads, vocals, bus_drums, bus_melody, bus_vocals")] = "kick",
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> str:
        """Get slot-by-slot plugin chain with exact settings for a mix element."""
        return get_chain(element, genre)

    @mcp.tool(annotations={"title": "Suggest multi-brand plugin chain", **_RO})
    def fl_suggest_plugin_chain(
        element: Annotated[str, Field(description="Element: kick, snare, bass, 808, vocals, hihats, piano, drums_bus, master")] = "vocals",
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi")] = "boom_bap",
        priority: Annotated[str, Field(description="Priority: fabfilter (default), cymatics, ozone, mixed")] = "fabfilter",
    ) -> str:
        """Recommend complete plugin chains prioritizing specific plugin suites (FabFilter, Ozone, Cymatics, or Mixed)."""
        parts = [f"## Cadena para {element} ({genre})\n"]

        if priority in ("fabfilter", "mixed"):
            ff = get_fabfilter_chain(f"{element}_chain") if f"{element}_chain" in ["vocal_chain", "drum_bus_chain", "808_chain", "master_chain"] else ""
            if ff:
                parts.append(f"### FabFilter:\n{ff}\n")
            eq = get_eq_preset(element)
            if "no encontrado" not in eq.lower():
                parts.append(f"### EQ (Pro-Q 4):\n{eq}\n")

        if priority in ("cymatics", "mixed"):
            cym = get_cymatics_chain(element, genre)
            if "no encontrado" not in cym.lower():
                parts.append(f"### Cymatics:\n{cym}\n")

        if element == "master" and (priority in ("ozone", "mixed")):
            oz = get_ozone_chain(genre)
            parts.append(f"### Ozone 12 Mastering:\n{oz}\n")

        return "\n".join(parts) if len(parts) > 1 else f"No hay cadena específica para {element}/{genre}. Probá con 'mixed' como priority."

    @mcp.tool(annotations={"title": "Get vocal processing chain", **_RO})
    def fl_get_vocal_processing(
        style: Annotated[str, Field(description="Vocal style: standard, bright_trap, yung_beef")] = "standard",
    ) -> str:
        """Get complete 10-slot vocal processing chain: Gate > Pitch > Sub EQ > Comp > Add EQ > Sat > De-esser > Limiter."""
        return get_vocal_chain(style)

    @mcp.tool(annotations={"title": "Get vocal production tricks guide", **_RO})
    def fl_get_vocal_tricks_guide() -> str:
        """Get advanced vocal production tricks: doubles, autotune, vocal chops, widening, distortion, and recording checklist."""
        tricks = get_vocal_tricks()
        checklist = get_vocal_checklist()
        return f"{tricks}\n\n{checklist}"

    @mcp.tool(annotations={"title": "Get mastering guide with LUFS targets", **_RO})
    def fl_get_mastering_guide(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, lofi, general")] = "boom_bap",
    ) -> str:
        """Get complete mastering chain with exact plugin parameters and LUFS loudness targets per streaming platform."""
        chain = get_mastering_chain(genre)
        targets = get_lufs_targets()
        return f"{chain}\n\n{targets}"

    @mcp.tool(annotations={"title": "Get reference mix levels and pan", **_RO})
    def fl_get_mix_reference_levels(
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> str:
        """Get reference mix levels (dB) and panning positions for every element in the mix."""
        return get_mix_levels(genre)

    @mcp.tool(annotations={"title": "Get EQ frequency guide", **_RO})
    def fl_get_eq_frequency_guide(
        element: Annotated[str, Field(description="Element name (kick, snare, bass, vocals, etc.) or empty for full guide")] = "",
    ) -> str:
        """Get EQ frequency guide: sweet spots, muddy zones, harsh resonances, and high-pass recommendations."""
        return get_eq_guide(element)

    @mcp.tool(annotations={"title": "Get send/return effects setup", **_RO})
    def fl_get_send_effects(
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> str:
        """Get send/return effects configuration (reverbs, delays, parallel compression) with bus routing."""
        return get_send_config(genre)

    @mcp.tool(annotations={"title": "Get FL Studio mixer layout template", **_RO})
    def fl_get_mixer_layout() -> str:
        """Get recommended FL Studio mixer layout template with insert, bus, and send assignments."""
        return get_mixer_template()

    @mcp.tool(annotations={"title": "Get mixing workflow checklist", **_RO})
    def fl_get_mixing_checklist(
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> str:
        """Get step-by-step mixing workflow checklist from gain staging to stem bounce."""
        workflow = get_workflow()
        staging = get_gain_staging_guide()
        return f"{staging}\n\n{workflow}"

    @mcp.tool(annotations={"title": "Get advanced mixing workflow", **_RO})
    def fl_get_advanced_mixing_workflow(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk")] = "boom_bap",
    ) -> str:
        """Get advanced mixing workflow with gain staging, submix routing, and comprehensive quality checklist."""
        return get_mixing_workflow(genre)

    @mcp.tool(annotations={"title": "Get bus routing architecture", **_RO})
    def fl_get_bus_routing(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk")] = "boom_bap",
    ) -> str:
        """Get recommended bus routing topology and group bus processing chains."""
        return get_bus_setup(genre)

    @mcp.tool(annotations={"title": "Get sidechain compression guide", **_RO})
    def fl_get_sidechain_guide() -> str:
        """Get comprehensive sidechain compression guide: theory, routing, attack/release timing, and plugin options."""
        return """=== GUÍA COMPLETA DE SIDECHAIN ===

1. OBJETIVO:
   Evitar que el kick y el bajo compitan por las mismas frecuencias bajas (40-100 Hz).
   Cuando el kick pega, el bajo se atenúa automáticamente unos dB.

2. MÉTODOS EN FL STUDIO:
   A. Fruity Limiter (Sidechain nativo recomendado):
      - Ruteá el track del Kick al track del Bajo (Right click send arrow -> 'Sidechain to this track')
      - En el track del Bajo poné Fruity Limiter -> Modo COMP
      - Sidechain input: Kick
      - Ratio: Alto (4:1 a inf:1)
      - Attack: 0.5 - 2 ms (rápido)
      - Release: 80 - 150 ms (adaptar al BPM)
      - Threshold: bajar hasta obtener 3 - 6 dB de ganancia reducida.

   B. Fruity Peak Controller + Fruity Balance:
      - Poné Peak Controller en el Kick (mute peak si no querés audio)
      - En el track de Bajo, poné Fruity Balance -> Right click en Volume -> Link to Controller -> Peak Ctrl (invertido).

   C. Plugins Dedicados:
      - Cableguys ShaperBox (VolumeShaper) o Nicky Romero Kickstart para ducking sincronizado al compás."""

    @mcp.tool(annotations={"title": "Set up sidechain between kick and bass", **_WR})
    def fl_setup_sidechain(
        kick_track: Annotated[int, Field(ge=0, le=125, description="Mixer track number where Kick is routed")] = 1,
        bass_track: Annotated[int, Field(ge=0, le=125, description="Mixer track number where Bass is routed")] = 5,
        send_level: Annotated[float, Field(ge=0.0, le=1.0, description="Send level (0.0 to 1.0)")] = 0.8,
    ) -> str:
        """Configure sidechain routing between kick and bass in FL Studio mixer and provide exact Limiter setup guide."""
        bridge_status = ""
        try:
            from .. import protocol
            from ..connection import get_bridge
            bridge = get_bridge()
            bridge.call(protocol.CMD_MIXER_SET_ROUTE, {
                "source": kick_track,
                "target": bass_track,
                "value": 1,
            })
            bridge_status = f"✓ RUTA EN FL STUDIO CREADA: Track {kick_track} ruteado a Track {bass_track}\n\n"
        except Exception as exc:
            bridge_status = f"ℹ Nota bridge: No se aplicó directo al mixer ({exc}). Seguí la guía manual:\n\n"

        return f"""=== SIDECHAIN CONFIGURACIÓN ===

{bridge_status}Ruta: Track {kick_track} (Kick) → Track {bass_track} (Bass)
Nivel de envío recomendado: {send_level:.1f}

PASOS EN FL STUDIO:
1. En el Mixer, seleccioná Track {bass_track} (Bass).
2. Agregá 'Fruity Limiter' en un slot vacío.
3. En Fruity Limiter, click en 'COMP'.
4. En 'Sidechain' abajo a la derecha, seleccioná Track {kick_track}.
5. Ajustes sugeridos:
   - THRESHOLD: bajalo hasta que la reducción de ganancia sea -3 a -6 dB.
   - RATIO: 4:1 o superior.
   - ATTACK: casi al mínimo (0.5 - 2 ms).
   - RELEASE: 100 - 150 ms (para que el bajo regrese limpio antes del próximo kick)."""

    @mcp.tool(annotations={"title": "Get sampling source guide", **_RO})
    def fl_get_sampling_guide(
        source: Annotated[str, Field(description="Source: vinyl, youtube, streaming, sample_packs")] = "vinyl",
    ) -> str:
        """Get legal, technical, and artistic sampling workflow for a given source."""
        return get_sampling_workflow(source)

    @mcp.tool(annotations={"title": "Get sample chopping technique guide", **_RO})
    def fl_get_chopping_technique(
        technique: Annotated[str, Field(description="Technique: manual, slicex, by_bar, by_beat, stutter (or empty for all)")] = "",
    ) -> str:
        """Get chopping techniques: transient slicing, 16-pad MPC layouts, bar looping, and creative re-pitching."""
        return get_chopping_guide(technique)

    @mcp.tool(annotations={"title": "Get classic drum machine emulation guide", **_RO})
    def fl_get_drum_machine_guide(
        machine: Annotated[str, Field(description="Machine: mpc_60, sp_1200, mpc_3000")] = "mpc_60",
    ) -> str:
        """Get classic drum machine emulation guide in FL Studio: bit depths, sample rates, filters, and swing."""
        return get_drum_machine_emulation(machine)

    @mcp.tool(annotations={"title": "Get sample processing chain", **_RO})
    def fl_get_sample_processing(
        style: Annotated[str, Field(description="Style: standard, lofi, aggressive, clean")] = "standard",
    ) -> str:
        """Get sample processing chain: EQ filtering, vinyl emulation, pitch shifting, and stereo narrowing."""
        return get_sample_processing_chain(style)
