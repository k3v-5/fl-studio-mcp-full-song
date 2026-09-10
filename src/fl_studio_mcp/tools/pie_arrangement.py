"""PIE Arrangement Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_arrangement_tools(mcp: FastMCP) -> None:
    """Register Arrangement tools with the MCP server."""
    from fl_studio_mcp.pie.arrangement import get_arrangement_engine

    @mcp.tool()
    def arrangement_get_structure() -> dict[str, Any]:
        """Get the macro-structure bounds from the Smart Template.

        Returns the start beat, length, and intended energy for each section.
        """
        ae = get_arrangement_engine()
        return ae.get_structure()

    @mcp.tool()
    def arrangement_generate_section(section_name: str, chord_prog: list[str]) -> dict[str, Any]:
        """Generate full MIDI data for an entire section in the template.

        Args:
            section_name: Name of the section (e.g., 'drop', 'build')
            chord_prog: Chord progression to base the section on
        """
        ae = get_arrangement_engine()
        return ae.generate_section(section_name, chord_prog)

    @mcp.tool()
    def arrangement_execute_section(section_name: str, chord_prog: list[str], harmony_channel_id: int, bass_channel_id: int) -> dict[str, Any]:
        """Generate AND execute a section directly into FL Studio.

        Args:
            section_name: Name of the section (e.g., 'drop', 'build').
            chord_prog: Chord progression to base the section on.
            harmony_channel_id: FL Studio channel index for the harmony/chords.
            bass_channel_id: FL Studio channel index for the bassline.
        """
        ae = get_arrangement_engine()
        from fl_studio_mcp.pie.midi_adapter import get_midi_adapter

        # 1. Generate logical data
        section_data = ae.generate_section(section_name, chord_prog)
        if "error" in section_data:
            return section_data

        # 2. Queue notes to physical channels
        adapter = get_midi_adapter()
        if "harmony_notes" in section_data and section_data["harmony_notes"]:
            adapter.queue_notes(harmony_channel_id, section_data["harmony_notes"])

        if "bass_notes" in section_data and section_data["bass_notes"]:
            adapter.queue_notes(bass_channel_id, section_data["bass_notes"])

        # 3. Flush the queue (triggers piano roll hotkeys in FL Studio)
        return adapter.flush()
