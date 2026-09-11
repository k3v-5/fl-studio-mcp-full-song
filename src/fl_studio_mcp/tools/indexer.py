"""Sample library indexer tools: ultra-fast tagged search across user's sample packs."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field

from ..indexer.manifest import build_manifest, search_samples as _search_samples, library_stats
from ..indexer.paths import default_packs_root, default_manifest_path
from ..indexer.keywords import (
    SAMPLE_TYPE_KEYWORDS,
    GENRE_KEYWORDS,
    MOOD_KEYWORDS,
    SUBTYPE_KEYWORDS,
)


def register(mcp: FastMCP) -> None:
    _RO = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
    _WR = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True}

    @mcp.tool(annotations={"title": "Search sample library by tags", **_RO})
    def fl_search_samples_in_library(
        sample_type: Annotated[Optional[str], Field(description="Sample type: kick, snare, hihat, clap, bass, 808, vocal, synth, etc.")] = None,
        subtype: Annotated[Optional[str], Field(description="Subtype: closed, open, roll, rim, acoustic, electric, sub, etc.")] = None,
        genre: Annotated[Optional[str], Field(description="Genre tag: trap, boom_bap, lofi, drill, reggaeton, house, etc.")] = None,
        mood: Annotated[Optional[str], Field(description="Mood tag: dark, melancholic, bright, aggressive, warm, etc.")] = None,
        key: Annotated[Optional[str], Field(description="Musical key: C, D#, F#m, etc.")] = None,
        bpm: Annotated[Optional[int], Field(description="Tempo in BPM (for loops)")] = None,
        bpm_tolerance: Annotated[int, Field(ge=0, le=50, description="BPM match tolerance window (+/-)")] = 5,
        loops_only: Annotated[bool, Field(description="Return only loops")] = False,
        oneshots_only: Annotated[bool, Field(description="Return only one-shots")] = False,
        limit: Annotated[int, Field(ge=1, le=100, description="Maximum results to return")] = 20,
    ) -> dict:
        """Search the user's sample library by structured tags (type, genre, mood, key, BPM). Requires prior reindex."""
        manifest = default_manifest_path()
        if not manifest.exists():
            return {
                "count": 0,
                "error": "Sample library manifest not found. Run fl_reindex_library first to scan your packs.",
                "results": [],
            }

        results = _search_samples(
            manifest,
            sample_type=sample_type,
            subtype=subtype,
            genre=genre,
            mood=mood,
            key=key,
            bpm=bpm,
            bpm_tolerance=bpm_tolerance,
            is_loop=True if loops_only else (False if oneshots_only else None),
            is_oneshot=True if oneshots_only else (False if loops_only else None),
            limit=limit,
        )

        return {
            "count": len(results),
            "results": [
                {
                    "path": r.get("path"),
                    "filename": r.get("filename"),
                    "folder": r.get("relative_folder"),
                    "sample_type": r.get("sample_type"),
                    "subtype": r.get("subtype"),
                    "genres": r.get("genres"),
                    "moods": r.get("moods"),
                    "bpm": r.get("bpm"),
                    "key": r.get("key"),
                    "is_loop": r.get("is_loop"),
                    "is_oneshot": r.get("is_oneshot"),
                }
                for r in results
            ],
        }

    @mcp.tool(annotations={"title": "List sample search categories", **_RO})
    def fl_list_sample_categories() -> dict:
        """List the canonical category values accepted by fl_search_samples_in_library."""
        return {
            "sample_types": list(SAMPLE_TYPE_KEYWORDS.keys()),
            "subtypes": list(SUBTYPE_KEYWORDS.keys()),
            "genres": list(GENRE_KEYWORDS.keys()),
            "moods": list(MOOD_KEYWORDS.keys()),
        }

    @mcp.tool(annotations={"title": "Get sample library statistics", **_RO})
    def fl_get_library_stats() -> dict:
        """Return aggregate statistics about the indexed sample library (total samples, breakdown by type, genre, keys, BPM)."""
        manifest = default_manifest_path()
        if not manifest.exists():
            return {"error": "Sample library not indexed yet. Call fl_reindex_library first."}
        return library_stats(manifest)

    @mcp.tool(annotations={"title": "Reindex sample library", **_WR})
    def fl_reindex_library(
        packs_root: Annotated[Optional[str], Field(description="Custom root directory of sample packs. If None, default location is used.")] = None,
    ) -> dict:
        """Walk the sample library and update the manifest incrementally with tags, BPM, key, and type."""
        root = Path(packs_root) if packs_root else default_packs_root()
        manifest = default_manifest_path()
        if not root.exists():
            return {"error": f"Packs root folder does not exist: {root}"}
        stats = build_manifest(root, manifest)
        return {"ok": True, "stats": stats, "manifest_path": str(manifest)}
