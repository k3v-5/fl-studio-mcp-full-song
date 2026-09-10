"""MIDI Adapter for FL Studio MCP (PIE).

Bridges the logical output of the Arrangement and Music Engines to the physical
Piano Roll API using a queued JSON approach.
"""

from __future__ import annotations

import time
from typing import Any

from fl_studio_mcp.utils.connection import get_connection
from fl_studio_mcp.tools.piano_roll import _write_request
from fl_studio_mcp.utils.fl_trigger import trigger_fl_studio

class MIDIAdapter:
    def __init__(self) -> None:
        self.queue: list[dict[str, Any]] = []

    def queue_notes(self, channel_id: int, notes: list[dict[str, Any]]) -> None:
        """Queue a list of notes to be sent to a specific channel.

        Args:
            channel_id: The FL Studio internal channel index.
            notes: A list of dicts with midi, duration, time, velocity.
        """
        self.queue.append({
            "channel_id": channel_id,
            "notes": notes
        })

    def flush(self) -> dict[str, Any]:
        """Execute all queued note injections sequentially.

        This selects the target channel via the physical MIDI bridge and then
        triggers the ComposeWithLLM Piano Roll script.
        """
        results = []
        if not self.queue:
            return {"status": "success", "message": "Queue is empty."}

        for task in self.queue:
            channel_id = task["channel_id"]
            notes = task["notes"]

            # Select the channel using direct connection command
            conn = get_connection()
            select_res = conn.send_command("channels.selectOne", {"index": channel_id})

            # To physically inject notes without calling the decorated FastMCP tool,
            # we write the request directly to the piano roll script JSON, and fire the hotkey.
            request_payload = {
                "action": "add",
                "notes": notes,
                "clear": False
            }
            try:
                _write_request(request_payload)
                success = trigger_fl_studio()
                send_res = {"success": success, "mock": False, "message": "Trigger fired"}
            except Exception as e:
                send_res = {"success": False, "mock": False, "message": str(e)}

            results.append({
                "channel_id": channel_id,
                "select_status": select_res,
                "send_status": send_res
            })

            # Small delay to let the UI script finish execution before the next hotkey
            time.sleep(0.5)

        self.queue.clear()
        return {"status": "success", "executed_tasks": results}

# Singleton instance
_midi_adapter = MIDIAdapter()

def get_midi_adapter() -> MIDIAdapter:
    return _midi_adapter
