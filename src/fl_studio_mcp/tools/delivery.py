"""Multi-method note & arrangement delivery tools for FL Studio MCP."""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from ..pie.delivery import get_delivery_engine, normalize_note
from ..connection import get_bridge
from .. import protocol


class DeliveryNote(BaseModel):
    pitch: int = Field(ge=0, le=127, description="MIDI pitch (0-127, 60 = Middle C).")
    time_bars: float = Field(0.0, ge=0.0, description="Start time in bars from start.")
    length_bars: float = Field(0.25, gt=0.0, description="Duration in bars.")
    velocity: float = Field(0.8, ge=0.0, le=1.0, description="Velocity 0.0 to 1.0.")


def register(mcp: FastMCP) -> None:
    _WR = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True}

    @mcp.tool(annotations={"title": "Option 1: Live Real-Time MIDI Recording", **_WR})
    def fl_record_midi_live(
        notes: List[DeliveryNote],
        channel: Annotated[Optional[int], Field(ge=0, description="Channel index to record into.")] = None,
        bpm: Annotated[Optional[float], Field(ge=10.0, le=999.0, description="Tempo in BPM.")] = None,
    ) -> dict:
        """Stream MIDI notes into FL Studio in real-time while transport recording is active.

        Based on Franco Donati's FL-STUDIO-MCP send_melody technique. FL Studio records
        notes directly into the active pattern and Piano Roll in real-time over loopMIDI.
        """
        engine = get_delivery_engine()
        return engine.deliver_realtime_record(
            notes=[n.model_dump() for n in notes],
            channel=channel,
            bpm=bpm,
        )

    @mcp.tool(annotations={"title": "Option 2: Piano Roll Script Injection", **_WR})
    def fl_apply_notes_pyscript(
        notes: List[DeliveryNote],
        channel: Annotated[Optional[int], Field(ge=0, description="Channel index to select.")] = None,
        pattern_name: Annotated[str, Field(description="Name of the pattern/script.")] = "MCP_Apply",
        mode: Annotated[str, Field(description="'replace' clears pattern; 'append' adds to it.")] = "replace",
        trigger: Annotated[bool, Field(description="Whether to fire Ctrl+Alt+Y immediately.")] = True,
    ) -> dict:
        """Inject notes into FL Studio's Piano Roll via generated .pyscript and keyboard shortcut.

        Bakes notes into MCP_Apply.pyscript (and a named script), focuses FL Studio, and
        fires the 'Run last script again' shortcut.
        """
        engine = get_delivery_engine()
        return engine.deliver_pyscript(
            notes=[n.model_dump() for n in notes],
            channel=channel,
            pattern_name=pattern_name,
            mode=mode,
            trigger=trigger,
        )

    @mcp.tool(annotations={"title": "Option 3: Multi-Track MIDI Compilation & Export", **_WR})
    def fl_export_arrangement_midi(
        tracks: Annotated[List[Dict[str, Any]], Field(description="List of tracks: [{'name': str, 'channel': int, 'notes': list}]")],
        song_name: Annotated[str, Field(description="Song or arrangement name.")] = "Arrangement",
        bpm: Annotated[float, Field(ge=10.0, le=999.0, description="Tempo in BPM.")] = 140.0,
        auto_import: Annotated[bool, Field(description="If True, automatically triggers native FL Studio MIDI import (File > Import > MIDI file) to instantiate discrete channels without manual dragging.")] = False,
    ) -> dict:
        """Compile a multi-track Standard MIDI File (SMF Type 1) with tempo and markers.

        Saves to exports/ and copies directly to FL Studio Presets/Scores.
        WARNING: In FL Studio, dragging a multi-track .mid directly from the browser onto
        the Playlist or Channel Rack collapses all tracks into the single active channel!
        Set auto_import=True or use File > Import > MIDI file... to instantiate discrete channels.
        """
        engine = get_delivery_engine()
        result = engine.deliver_midi_file(
            tracks=tracks,
            song_name=song_name,
            bpm=bpm,
        )
        if auto_import and result.get("ok") and result.get("path"):
            from ..pie.auto_arranger import get_playlist_arranger
            arranger = get_playlist_arranger()
            import_res = arranger.auto_arrange_song(
                midi_path=result["path"],
                bpm=bpm,
            )
            result["auto_import"] = import_res
        return result

    @mcp.tool(annotations={"title": "Universal Note Delivery (Selectable Mode)", **_WR})
    def fl_deliver_notes(
        notes: List[DeliveryNote],
        delivery_mode: Annotated[str, Field(description="Delivery mode: 'all', 'realtime_record', 'pyscript', or 'midi_file'.")] = "all",
        channel: Annotated[Optional[int], Field(ge=0, description="Target channel index.")] = None,
        song_name: Annotated[str, Field(description="Arrangement / track name.")] = "Pattern",
        bpm: Annotated[float, Field(ge=10.0, le=999.0, description="Tempo in BPM.")] = 140.0,
    ) -> dict:
        """Route notes to any of the 3 delivery mechanisms or all of them simultaneously."""
        engine = get_delivery_engine()
        return engine.deliver(
            data=[n.model_dump() for n in notes],
            delivery_mode=delivery_mode,
            song_name=song_name,
            bpm=bpm,
            channel=channel,
        )
