"""MIDI Adapter for FL Studio MCP (PIE).

Bridges the logical output of the Arrangement and Music Engines to the physical
Piano Roll API using the modern note bridge and SysEx protocol.
"""

from __future__ import annotations

import time
from typing import Any

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge

class MIDIAdapter:
    def __init__(self) -> None:
        self.queue: list[dict[str, Any]] = []

    def queue_notes(self, channel_id: int, notes: list[dict[str, Any]]) -> None:
        """Queue a list of notes to be sent to a specific channel.

        Args:
            channel_id: The FL Studio internal channel index.
            notes: A list of dicts with midi (or pitch), duration (or length_bars), time (or time_bars), velocity.
        """
        self.queue.append({
            "channel_id": channel_id,
            "notes": notes
        })

    def flush(
        self,
        delivery_mode: str = "pyscript",
        bpm: float = 140.0,
        song_name: str = "Arrangement",
    ) -> dict[str, Any]:
        """Execute all queued note injections using the requested delivery mode.

        Args:
            delivery_mode: 'pyscript', 'realtime_record', 'midi_file', or 'all'.
            bpm: Tempo in BPM for timing and MIDI export.
            song_name: Name for the exported arrangement or scripts.
        """
        results = []
        if not self.queue:
            return {"status": "success", "message": "Queue is empty."}

        from fl_studio_mcp.pie.delivery import get_delivery_engine
        engine = get_delivery_engine()

        # If midi_file or all mode, compile multi-track MIDI for all queued channels
        midi_file_result = None
        if delivery_mode in ("midi_file", "all"):
            tracks = []
            for task in self.queue:
                ch_id = task["channel_id"]
                tracks.append({
                    "name": f"Channel_{ch_id}",
                    "channel": ch_id % 16,
                    "notes": task["notes"],
                })
            midi_file_result = engine.deliver_midi_file(tracks, song_name=song_name, bpm=bpm)

        for task in self.queue:
            channel_id = task["channel_id"]
            raw_notes = task["notes"]

            task_delivery = {}

            if delivery_mode in ("pyscript", "all"):
                # Use pyscript delivery
                pyscript_res = engine.deliver_pyscript(
                    notes=raw_notes,
                    channel=channel_id,
                    pattern_name=f"{song_name}_Ch{channel_id}",
                    mode="append",
                    trigger=True,
                )
                task_delivery["pyscript"] = pyscript_res

            if delivery_mode in ("realtime_record", "all"):
                # Realtime recording via loopMIDI
                record_res = engine.deliver_realtime_record(
                    notes=raw_notes,
                    channel=channel_id,
                    bpm=bpm,
                )
                task_delivery["realtime_record"] = record_res

            results.append({
                "channel_id": channel_id,
                "delivery": task_delivery,
            })

            time.sleep(0.3)

        self.queue.clear()
        resp: dict[str, Any] = {
            "status": "success",
            "delivery_mode": delivery_mode,
            "executed_tasks": results,
        }
        if midi_file_result is not None:
            resp["midi_file"] = midi_file_result
        return resp

# Singleton instance
_midi_adapter = MIDIAdapter()

def get_midi_adapter() -> MIDIAdapter:
    return _midi_adapter
