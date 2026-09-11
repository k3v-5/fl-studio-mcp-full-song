"""User learning, pattern memory, and MIDI file analysis tools."""
from __future__ import annotations

from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.learned.user_learning import (
    save_pattern,
    get_best_patterns,
    analyze_midi_file,
    format_learned_context,
)


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
    _WR = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True}

    @mcp.tool(annotations={"title": "Save favorite pattern to memory", **_WR})
    def fl_save_favorite_pattern(
        pattern_type: Annotated[str, Field(description="Type: bassline, melody, drums, chord_progression")],
        name: Annotated[str, Field(description="Descriptive name for the pattern")],
        notes_data: Annotated[str, Field(description="The MIDI note data or pattern description")],
        genre: Annotated[str, Field(description="Genre context (optional)")] = "",
        key: Annotated[str, Field(description="Musical key root/scale (optional)")] = "",
        bpm: Annotated[float, Field(description="Tempo in BPM (optional)")] = 0.0,
        rating: Annotated[int, Field(ge=1, le=5, description="1-5 user rating")] = 5,
        notes: Annotated[str, Field(description="Additional personal producer notes")] = "",
    ) -> str:
        """Save a pattern the user liked for future recall, evolution, and model fine-tuning."""
        return save_pattern(
            pattern_type=pattern_type,
            name=name,
            pattern_data={"notes_data": notes_data},
            genre=genre,
            key=key,
            bpm=bpm,
            rating=rating,
            notes=notes,
        )

    @mcp.tool(annotations={"title": "Get favorite saved patterns", **_RO})
    def fl_get_favorite_patterns(
        pattern_type: Annotated[str, Field(description="Filter by type: bassline, melody, drums, chord_progression (or empty for all)")] = "",
        genre: Annotated[str, Field(description="Filter by genre (or empty for all)")] = "",
    ) -> str:
        """Retrieve previously saved favorite user patterns matching type or genre."""
        return get_best_patterns(pattern_type, genre)

    @mcp.tool(annotations={"title": "Analyze external MIDI file", **_RO})
    def fl_analyze_midi(
        file_path: Annotated[str, Field(description="Path to local .mid / .midi file")],
    ) -> str:
        """Analyze a MIDI file and extract musical key, detected scale, note count, pitch range, and duration."""
        return analyze_midi_file(file_path)

    @mcp.tool(annotations={"title": "Get learned producer context", **_RO})
    def fl_get_learned_context(
        genre: Annotated[str, Field(description="Optional genre filter")] = "",
    ) -> str:
        """Get summary of what the system has learned from the user's past workflows, ratings, and saved patterns."""
        return format_learned_context(genre)
