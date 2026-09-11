"""PIE Arrangement Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_arrangement_tools(mcp: FastMCP) -> None:
    """Register Arrangement tools with the MCP server."""
    from fl_studio_mcp.pie.arrangement import get_arrangement_engine

    @mcp.tool()
    def arrangement_update_structure(template_definition: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Update the macro-structure bounds from the Smart Template dynamically.

        Args:
            template_definition: A dict mapping section names to their configs.
                                 e.g., {"intro": {"start_beat": 0, "length_beats": 64}}
        """
        ae = get_arrangement_engine()
        return ae.update_structure(template_definition)

    @mcp.tool()
    def arrangement_get_structure() -> dict[str, Any]:
        """Get the current dynamically defined macro-structure."""
        ae = get_arrangement_engine()
        return ae.get_structure()

    @mcp.tool()
    def arrangement_generate_section(
        section_name: str,
        chords: list[list[int]],
        chord_durations: list[float],
        bass_midi: list[int],
        bass_durations: list[float]
    ) -> dict[str, Any]:
        """Generate full MIDI data for an entire section in the template using dynamic inputs.
        """
        ae = get_arrangement_engine()
        return ae.generate_section(section_name, chords, chord_durations, bass_midi, bass_durations)

    @mcp.tool()
    def arrangement_execute_section(
        section_name: str,
        chords: list[list[int]],
        chord_durations: list[float],
        bass_midi: list[int],
        bass_durations: list[float],
        harmony_channel_id: int,
        bass_channel_id: int
    ) -> dict[str, Any]:
        """Generate AND execute a dynamically provided section directly into FL Studio."""
        ae = get_arrangement_engine()
        from fl_studio_mcp.pie.midi_adapter import get_midi_adapter

        # 1. Generate logical data
        section_data = ae.generate_section(section_name, chords, chord_durations, bass_midi, bass_durations)
        if "error" in section_data:
            return section_data

        # 2. Queue notes to physical channels
        adapter = get_midi_adapter()
        if "harmony_notes" in section_data and section_data["harmony_notes"]:
            adapter.queue_notes(harmony_channel_id, section_data["harmony_notes"])

        if "bass_notes" in section_data and section_data["bass_notes"]:
            adapter.queue_notes(bass_channel_id, section_data["bass_notes"])

        # 3. Flush the queue
        return adapter.flush()

    @mcp.tool()
    def arrangement_generate_transition(
        target_section_name: str,
        length_beats: float = 16.0,
        start_midi: int = 48,
        end_midi: int = 72,
        curve_type: str = "exponential"
    ) -> dict[str, Any]:
        """Generate a MIDI transition riser sequence.

        Args:
            target_section_name: The section to lead into (must be defined in template structure).
            length_beats: Length in quarter notes.
            start_midi: Start pitch.
            end_midi: End pitch.
            curve_type: 'exponential' or 'linear'.
        """
        ae = get_arrangement_engine()
        return ae.generate_transition_riser(target_section_name, length_beats, start_midi, end_midi, curve_type)

    @mcp.tool()
    def fl_auto_arrange_playlist(
        midi_path: str,
        sections: list[dict[str, Any]] | None = None,
        bpm: float = 140.0,
        settle_delay: float = 0.4,
    ) -> dict[str, Any]:
        """Automatically arrange a multi-track song onto FL Studio's Playlist timeline.

        Eliminates manual drag-and-drop by automating FL Studio's native MIDI import
        (Alt+F -> I -> M + path injection) and creating timeline section markers
        (Intro, Build, Drop, Outro) at exact bar locations.
        """
        from fl_studio_mcp.pie.auto_arranger import get_playlist_arranger
        arranger = get_playlist_arranger()
        return arranger.auto_arrange_song(
            midi_path=midi_path,
            sections=sections,
            bpm=bpm,
            settle_delay=settle_delay,
        )

