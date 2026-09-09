"""Shadow Graph implementation for FL Studio MCP.

The Shadow Graph acts as a cached memory representation of the FL Studio state,
allowing the AI to inspect the session without constantly polling the MIDI API.
"""

from __future__ import annotations

import json
from typing import Any

from fl_studio_mcp.utils.connection import get_connection

class ShadowGraph:
    """A cached representation of the FL Studio project state."""

    def __init__(self) -> None:
        self.mixer_tracks: dict[int, dict[str, Any]] = {}
        self.channels: dict[int, dict[str, Any]] = {}
        self.transport: dict[str, Any] = {}
        self.is_synced: bool = False

    def refresh(self) -> None:
        """Poll FL Studio via MIDI to rebuild the shadow state."""
        conn = get_connection()
        if not conn.is_connected:
            raise RuntimeError("Cannot refresh Shadow Graph: FL Studio is not connected.")

        # Refresh transport
        transport_res = conn.send_command("transport.getStatus")
        if transport_res.get("success", False):
            self.transport = {
                "is_playing": transport_res.get("is_playing", False),
                "is_recording": transport_res.get("is_recording", False),
                "position": transport_res.get("position", ""),
                "loop_mode": transport_res.get("loop_mode", "pattern"),
            }

        # Refresh mixer
        mixer_res = conn.send_command("mixer.getAllTracks")
        if mixer_res.get("success", False) and "tracks" in mixer_res:
            self.mixer_tracks = {t["index"]: t for t in mixer_res["tracks"]}

        # Refresh channels
        channels_res = conn.send_command("channels.getAll")
        if channels_res.get("success", False) and "channels" in channels_res:
            self.channels = {c["index"]: c for c in channels_res["channels"]}

        self.is_synced = True

    def inspect(self, scope: str = "all") -> dict[str, Any]:
        """Return the requested portion of the shadow graph."""
        if not self.is_synced:
            self.refresh()

        if scope == "mixer":
            return {"mixer_tracks": self.mixer_tracks}
        elif scope == "channels":
            return {"channels": self.channels}
        elif scope == "transport":
            return {"transport": self.transport}
        else:
            return {
                "transport": self.transport,
                "mixer_tracks": self.mixer_tracks,
                "channels": self.channels,
            }

    def diff(self, desired_state: dict[str, Any]) -> dict[str, Any]:
        """Compare desired state with shadow graph to find what needs to change."""
        # A rudimentary diff for volumes and pan for demonstration
        changes = []
        if "mixer_tracks" in desired_state:
            for idx_str, track_data in desired_state["mixer_tracks"].items():
                idx = int(idx_str)
                if idx in self.mixer_tracks:
                    current = self.mixer_tracks[idx]
                    if "volume" in track_data and track_data["volume"] != current.get("volume"):
                        changes.append({"type": "mixer_volume", "track": idx, "value": track_data["volume"]})
        return {"changes": changes}

# Singleton instance
_shadow_graph = ShadowGraph()

def get_shadow_graph() -> ShadowGraph:
    """Get the singleton Shadow Graph instance."""
    return _shadow_graph
