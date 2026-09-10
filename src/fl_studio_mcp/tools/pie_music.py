"""PIE Music Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_music_tools(mcp: FastMCP) -> None:
    """Register Music Engine tools with the MCP server."""
    from fl_studio_mcp.pie.music_engine import get_music_engine

    @mcp.tool()
    def music_generate_harmony(scale: str, progression: list[str], length: int) -> dict[str, Any]:
        """Generate MIDI data for a chord progression.

        Args:
            scale: Musical scale (e.g., 'C minor')
            progression: List of chords (e.g., ['i', 'iv', 'v', 'i'])
            length: Duration in beats for the whole progression
        """
        me = get_music_engine()
        notes = me.generate_harmony(scale, progression, length)
        return {"notes": notes}

    @mcp.tool()
    def music_generate_bass(root_notes: list[int], rhythm_pattern: str) -> dict[str, Any]:
        """Generate MIDI data for a bassline.

        Args:
            root_notes: List of MIDI note numbers for the roots
            rhythm_pattern: Type of rhythm ('driving', 'sustained')
        """
        me = get_music_engine()
        notes = me.generate_bass(root_notes, rhythm_pattern)
        return {"notes": notes}

    @mcp.tool()
    def music_generate_drums(genre: str, intensity: float) -> dict[str, Any]:
        """Generate grid bits for a drum pattern.

        Args:
            genre: Musical genre (e.g., 'house')
            intensity: 0.0 to 1.0 driving the complexity of the beat
        """
        me = get_music_engine()
        steps = me.generate_drums(genre, intensity)
        return {"steps": steps}
