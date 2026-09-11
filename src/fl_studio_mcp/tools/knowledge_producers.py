"""Producer style profiles, song structure templates, and production quick-start guides."""
from __future__ import annotations

from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from ..knowledge.producers import get_producer_profile, list_producers
from ..knowledge.song_structures import get_structure, get_quick_start


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}

    @mcp.tool(annotations={"title": "Get producer style profile", **_RO})
    def fl_get_producer_info(
        producer: Annotated[str, Field(description="Producer ID (dj_premier, pete_rock, rza, j_dilla, 9th_wonder, madlib, havoc, large_professor, alchemist, hi_tek, buckwild, lord_finesse, marley_marl) or 'list'")] = "dj_premier",
    ) -> str:
        """Get complete production style profile of a legendary producer: drums, swing, sampling, scales, gear, and replication tips."""
        if producer.strip().lower() == "list":
            return list_producers()
        return get_producer_profile(producer.strip().lower())

    @mcp.tool(annotations={"title": "Get song structure template", **_RO})
    def fl_get_song_structure_template(
        genre: Annotated[str, Field(description="Genre: boom_bap or trap")] = "boom_bap",
    ) -> str:
        """Get complete song structure template with section lengths (bars), energy dynamics, tips, and transition techniques."""
        return get_structure(genre)

    @mcp.tool(annotations={"title": "Get 10-step beat quick start guide", **_RO})
    def fl_get_quick_start_guide() -> str:
        """Get the 10-step quick start guide for producing a complete boom bap beat from scratch."""
        return get_quick_start()
