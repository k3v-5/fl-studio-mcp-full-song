"""Music theory, scale, chord progression, drum pattern, and bassline tools."""
from __future__ import annotations

from typing import Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.scales import (
    SCALE_DESCRIPTIONS,
    GENRE_SCALE_RECOMMENDATIONS,
    MOOD_SCALE_MAP,
    COMMON_KEYS,
    get_scale_notes_range,
    format_scale_info,
)
from ..knowledge.chords import (
    PROGRESSION_DEFINITIONS,
    get_progression_chords,
    progression_to_midi_notes,
    format_progression_info,
    list_progressions,
)
from ..knowledge.drum_patterns import (
    pattern_to_midi_notes,
    list_patterns,
    format_velocity_guide,
    get_patterns_for_bpm,
    check_bpm_compatibility,
)
from ..knowledge.basslines import (
    generate_bassline_notes,
    format_bass_type_info,
    format_processing_chain,
    format_growl_guide,
    format_golden_rules,
    list_distortion_plugins,
    _get_bpm_style_recommendation,
)
from ..knowledge.constants import midi_to_note


def _send_notes_data_to_fl(notes_data: str, channel: Optional[int] = None) -> dict:
    """Helper to parse CSV note data (note,velocity,length,position) and apply to FL Studio piano roll."""
    try:
        from .. import protocol
        from ..connection import get_bridge

        bridge = get_bridge()
        if channel is not None:
            bridge.call(protocol.CMD_CHANNEL_SELECT, {"channel": channel})

        parsed_notes = []
        for line in notes_data.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) == 4:
                try:
                    n_pitch = int(parts[0])
                    n_vel = max(0.0, min(1.0, float(parts[1]) / 127.0))
                    # length and position in beats -> convert to bars (4 beats per bar)
                    n_len_bars = max(0.01, float(parts[2]) / 4.0)
                    n_time_bars = max(0.0, float(parts[3]) / 4.0)
                    parsed_notes.append({
                        "pitch": n_pitch,
                        "velocity": n_vel,
                        "time_bars": n_time_bars,
                        "length_bars": n_len_bars,
                    })
                except ValueError:
                    continue

        if not parsed_notes:
            return {"ok": False, "error": "No valid note data found to send."}

        res = bridge.apply_notes(parsed_notes, mode="replace")
        return {"ok": True, "applied": len(parsed_notes), "bridge": res}
    except Exception as exc:
        return {"ok": False, "error": f"FL Studio bridge offline or unavailable: {exc}"}


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
    _WR = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True}

    @mcp.tool(annotations={"title": "Suggest musical scales by genre/mood", **_RO})
    def fl_suggest_scale(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop, reggaeton, uk_drill")] = "boom_bap",
        mood: Annotated[str, Field(description="Mood: dark, melancholic, aggressive, jazzy, hopeful, cinematic, soulful")] = "",
    ) -> str:
        """Recommend musical scales based on genre and/or mood with descriptions and common keys."""
        lines = ["=== ESCALAS RECOMENDADAS ===\n"]

        if mood and mood in MOOD_SCALE_MAP:
            lines.append(f"Para mood '{mood}':")
            for scale_id in MOOD_SCALE_MAP[mood]:
                info = SCALE_DESCRIPTIONS.get(scale_id, {})
                lines.append(f"  - {info.get('name', scale_id)}: {info.get('description', '')}")
            lines.append("")

        if genre in GENRE_SCALE_RECOMMENDATIONS:
            lines.append(f"Para genero '{genre}':")
            for scale_id in GENRE_SCALE_RECOMMENDATIONS[genre]:
                info = SCALE_DESCRIPTIONS.get(scale_id, {})
                lines.append(f"  - {info.get('name', scale_id)}: {info.get('description', '')}")
            lines.append("")

        if genre in COMMON_KEYS:
            lines.append(f"Keys mas comunes en {genre}: {', '.join(COMMON_KEYS[genre])}")

        if not mood and genre not in GENRE_SCALE_RECOMMENDATIONS:
            lines.append("Usa minor_natural si no estas seguro - es la reina del hip-hop.")

        return "\n".join(lines)

    @mcp.tool(annotations={"title": "Suggest chord progressions", **_RO})
    def fl_suggest_progression(
        key: Annotated[str, Field(description="Musical key root note (e.g. 'A', 'C', 'D', 'F#')")] = "A",
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, lofi, jazz_hiphop")] = "boom_bap",
        mood: Annotated[str, Field(description="Mood: dark, melancholic, aggressive, jazzy, hopeful, soulful")] = "",
    ) -> str:
        """Recommend chord progressions for a specific musical key, genre, and mood."""
        lines = [f"=== PROGRESIONES RECOMENDADAS en {key}m ===\n"]
        found = False

        for prog_id, prog in PROGRESSION_DEFINITIONS.items():
            genre_match = genre in prog.get("genre_tags", [])
            mood_match = (not mood) or prog.get("mood", "") == mood
            if genre_match and mood_match:
                found = True
                chords = get_progression_chords(prog_id, key, 3)
                chord_names = [c["name"] for c in chords]
                lines.append(f">> {prog['name']} ({prog['numerals']})")
                lines.append(f"   Acordes: {' - '.join(chord_names)}")
                lines.append(f"   {prog['description']}")
                lines.append(f"   Ref: {', '.join(prog.get('reference_tracks', []))}")
                lines.append(f"   ID para generar: {prog_id}")
                lines.append("")

        if not found:
            lines.append(f"No hay progresiones exactas para genre={genre}, mood={mood}.")
            lines.append("Prueba con genre='boom_bap' o sin filtro de mood.")

        return "\n".join(lines)

    @mcp.tool(annotations={"title": "Generate scale notes across octaves", **_RO})
    def fl_generate_scale_notes(
        root: Annotated[str, Field(description="Root note (e.g. 'A', 'C', 'D#')")] = "A",
        scale: Annotated[str, Field(description="Scale type (minor_natural, pentatonic_minor, blues, dorian, harmonic_minor, phrygian, major, pentatonic_major)")] = "minor_natural",
        octave_low: Annotated[int, Field(ge=0, le=8, description="Lowest octave")] = 3,
        octave_high: Annotated[int, Field(ge=0, le=8, description="Highest octave")] = 5,
    ) -> str:
        """Get all MIDI notes in a scale across octaves with MIDI numbers and note names."""
        try:
            info = format_scale_info(root, scale)
            notes = get_scale_notes_range(root, scale, octave_low, octave_high)
            note_names = [midi_to_note(n) for n in notes]
        except (ValueError, KeyError) as e:
            return str(e)

        return f"{info}\n\nFull range ({octave_low}-{octave_high}):\nMIDI: {notes}\nNames: {', '.join(note_names)}"

    @mcp.tool(annotations={"title": "Generate chord progression", **_WR})
    def fl_generate_chord_progression(
        progression: Annotated[str, Field(description="Progression ID (classic_dark, jazz_hiphop, soul_feel, melancholic, minimal_jazz, phrygian_dark, neo_soul)")] = "classic_dark",
        key: Annotated[str, Field(description="Musical key root note (e.g. 'A', 'C', 'D')")] = "A",
        bars: Annotated[int, Field(ge=1, le=64, description="Number of bars")] = 4,
        velocity: Annotated[int, Field(ge=1, le=127, description="MIDI velocity (1-127)")] = 85,
        octave: Annotated[int, Field(ge=1, le=7, description="Base octave for voicings (2-5)")] = 3,
        send_to_fl: Annotated[bool, Field(description="If True, write directly into FL Studio piano roll via bridge")] = False,
        channel: Annotated[Optional[int], Field(ge=0, description="Target channel rack index if send_to_fl is True")] = None,
    ) -> str:
        """Generate a chord progression with full voicings and optionally write it into FL Studio piano roll."""
        try:
            info = format_progression_info(progression, key)
            notes_data = progression_to_midi_notes(progression, key, bars, 4.0, velocity, octave)
        except (ValueError, KeyError) as e:
            return str(e)

        if send_to_fl:
            fl_res = _send_notes_data_to_fl(notes_data, channel)
            status = f"Enviado a FL Studio: {fl_res}" if fl_res.get("ok") else f"Aviso de envío: {fl_res.get('error')}"
            return f"{info}\n\n{status}\n\nNote data:\n{notes_data}"

        return f"{info}\n\nNote data ({bars} bars):\n{notes_data}"

    @mcp.tool(annotations={"title": "List available chord progressions", **_RO})
    def fl_list_available_progressions(
        genre: Annotated[str, Field(description="Filter by genre (boom_bap, trap, phonk, lofi, jazz_hiphop) or empty for all")] = "",
    ) -> str:
        """List all available built-in chord progressions, optionally filtered by genre."""
        return list_progressions(genre)

    @mcp.tool(annotations={"title": "Generate drum pattern", **_WR})
    def fl_generate_drum_pattern(
        style: Annotated[str, Field(description="Pattern style ID (boom_bap_basic, premier_style, pete_rock_groove, havoc_minimal, dilla_drunk, 9th_wonder_clean, rza_wu_tang, advanced_2bar, trap_basic)")] = "boom_bap_basic",
        bars: Annotated[int, Field(ge=0, le=64, description="Number of bars (0 = pattern default)")] = 0,
        humanize: Annotated[float, Field(ge=0.0, le=1.0, description="Random velocity variation (0=exact, 0.3=subtle, 0.7=heavy)")] = 0.0,
        bpm: Annotated[float, Field(ge=0.0, le=300.0, description="Tempo in BPM (0 = default 90)")] = 90.0,
        send_to_fl: Annotated[bool, Field(description="If True, send generated pattern to FL Studio piano roll")] = False,
        channel: Annotated[Optional[int], Field(ge=0, description="Target channel rack index if send_to_fl is True")] = None,
    ) -> str:
        """Generate a tempo-aware drum pattern with microtiming/humanize, and optionally send to FL Studio."""
        actual_bpm = bpm if bpm > 0 else 90.0
        warning = check_bpm_compatibility(style, actual_bpm)

        try:
            notes_data = pattern_to_midi_notes(style, bars, humanize, actual_bpm)
        except ValueError as e:
            return str(e)

        header = f"Drum pattern '{style}' @ {actual_bpm} BPM"
        parts = []

        if warning:
            parts.append(warning)
            better = get_patterns_for_bpm(actual_bpm)
            if better:
                suggestions = ", ".join(f"{p[0]} ({p[1]})" for p in better[:3])
                parts.append(f"Patrones recomendados para {actual_bpm} BPM: {suggestions}")

        if send_to_fl:
            fl_res = _send_notes_data_to_fl(notes_data, channel)
            status = f"Enviado a FL Studio: {fl_res}" if fl_res.get("ok") else f"Aviso de envío: {fl_res.get('error')}"
            parts.append(f"{header} generado.\n{status}")
        else:
            parts.append(f"{header} generado ({bars or 'default'} bars, humanize={humanize}):")

        parts.append(f"\nNote data:\n{notes_data}")
        return "\n\n".join(parts)

    @mcp.tool(annotations={"title": "List available drum patterns", **_RO})
    def fl_list_available_drum_patterns(
        genre: Annotated[str, Field(description="Filter by genre (boom_bap, trap, phonk, lofi, jazz_hiphop) or empty for all")] = "",
    ) -> str:
        """List all available drum patterns, optionally filtered by genre."""
        return list_patterns(genre)

    @mcp.tool(annotations={"title": "Generate bassline pattern", **_WR})
    def fl_generate_bassline(
        root_notes: Annotated[str, Field(description="Comma-separated root notes per bar (e.g. 'A,A,F,G')")] = "A,A,F,G",
        style: Annotated[str, Field(description="Bass style: root_follow, walking, syncopated, sub_808")] = "root_follow",
        bars: Annotated[int, Field(ge=1, le=32, description="Number of bars")] = 4,
        octave: Annotated[int, Field(ge=0, le=4, description="Bass octave (1-2 recommended)")] = 1,
        velocity: Annotated[int, Field(ge=1, le=127, description="MIDI velocity (1-127)")] = 100,
        bpm: Annotated[float, Field(ge=0.0, le=300.0, description="Tempo in BPM (0 = default 90)")] = 90.0,
        send_to_fl: Annotated[bool, Field(description="If True, send to FL Studio piano roll")] = False,
        channel: Annotated[Optional[int], Field(ge=0, description="Target channel rack index if send_to_fl is True")] = None,
    ) -> str:
        """Generate a bassline pattern adapting note lengths and rhythmic density to BPM."""
        actual_bpm = bpm if bpm > 0 else 90.0
        roots = [r.strip() for r in root_notes.split(",") if r.strip()]

        try:
            notes_data = generate_bassline_notes(roots, style, bars, octave, velocity, actual_bpm)
        except (ValueError, KeyError) as e:
            return str(e)

        parts = []
        rec = _get_bpm_style_recommendation(actual_bpm)
        if actual_bpm > 0:
            parts.append(f"Estilo recomendado para {actual_bpm} BPM: {rec}")

        if send_to_fl:
            fl_res = _send_notes_data_to_fl(notes_data, channel)
            status = f"Enviado a FL Studio: {fl_res}" if fl_res.get("ok") else f"Aviso de envío: {fl_res.get('error')}"
            parts.append(f"Bassline '{style}' @ {actual_bpm} BPM generado.\n{status}")
        else:
            parts.append(f"Bassline '{style}' @ {actual_bpm} BPM ({bars} bars, roots: {root_notes}):")

        parts.append(f"\nNote data:\n{notes_data}")
        return "\n\n".join(parts)

    @mcp.tool(annotations={"title": "Get bass production technique guide", **_RO})
    def fl_get_bass_technique(
        genre: Annotated[str, Field(description="Genre: boom_bap, trap, phonk, reggaeton, dubstep, uk_drill")] = "boom_bap",
    ) -> str:
        """Get bass production techniques, plugin generators, processing chain, and golden rules."""
        info = format_bass_type_info(genre)
        chain = format_processing_chain()
        rules = format_golden_rules()
        return f"{info}\n\n{chain}\n\n{rules}"

    @mcp.tool(annotations={"title": "Get bass growl and distortion guide", **_RO})
    def fl_get_bass_growl_guide() -> str:
        """Get the complete bass growl and distortion guide with plugin settings and signal flow."""
        growl = format_growl_guide()
        plugins = list_distortion_plugins()
        return f"{growl}\n\n{plugins}"

    @mcp.tool(annotations={"title": "Get drum velocity guide", **_RO})
    def fl_get_velocity_guide() -> str:
        """Get the MIDI velocity guide for realistic, humanized drum programming."""
        return format_velocity_guide()

    @mcp.tool(annotations={"title": "Suggest production parameters for BPM", **_RO})
    def fl_suggest_for_bpm(
        bpm: Annotated[float, Field(ge=20.0, le=300.0, description="Tempo in BPM to analyze")] = 90.0,
    ) -> str:
        """Get complete production recommendations based on a BPM: genres, drum patterns, and bass styles."""
        lines = [f"=== RECOMENDACIONES PARA {bpm} BPM ===\n"]

        genres = []
        if 70 <= bpm <= 95:
            genres.append("boom_bap")
        if 75 <= bpm <= 95:
            genres.append("jazz_hiphop")
        if 70 <= bpm <= 90:
            genres.append("lofi")
        if 85 <= bpm <= 100:
            genres.append("reggaeton")
        if 130 <= bpm <= 160:
            genres.append("trap")
        if 130 <= bpm <= 145:
            genres.append("phonk")
        if 140 <= bpm <= 145:
            genres.append("uk_drill")
        lines.append(f"Generos: {', '.join(genres) if genres else 'Tempo atipico - vale experimentar'}")
        lines.append("")

        lines.append("--- PATRONES DE DRUMS ---")
        matching = get_patterns_for_bpm(bpm)
        if matching:
            for pat_id, pat_name, pat_range in matching:
                lines.append(f"  - {pat_name} ({pat_id}): ideal {pat_range[0]}-{pat_range[1]} BPM")
        else:
            lines.append("  No hay patrones especificos, pero podes adaptar cualquier patron de hip-hop.")
        lines.append("")

        lines.append("--- ESTILO DE BAJO ---")
        lines.append(f"  {_get_bpm_style_recommendation(bpm)}")

        return "\n".join(lines)
