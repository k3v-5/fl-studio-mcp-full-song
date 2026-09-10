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
