"""Shadow Graph implementation for FL Studio MCP.

The Shadow Graph acts as a cached memory representation of the FL Studio state,
allowing the AI to inspect the session without constantly polling the MIDI API.
"""

from __future__ import annotations

import json
from typing import Any

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import fetch_all_pages, get_bridge

class ShadowGraph:
    """A cached representation of the FL Studio project state."""

    def __init__(self) -> None:
        self.mixer_tracks: dict[int, dict[str, Any]] = {}
        self.channels: dict[int, dict[str, Any]] = {}
        self.transport: dict[str, Any] = {}
        self.is_synced: bool = False

    def refresh(self) -> None:
        """Poll FL Studio via SysEx bridge to rebuild the shadow state."""
        bridge = get_bridge()
        if not bridge.is_alive():
            raise RuntimeError("Cannot refresh Shadow Graph: FL Studio is not connected.")

        # Refresh project & transport
        try:
            proj = bridge.call(protocol.CMD_GET_PROJECT_STATE)
            if isinstance(proj, dict):
                self.transport = {
                    "tempo": proj.get("tempo"),
                    "is_playing": proj.get("playing", False),
                    "is_recording": proj.get("recording", False),
                    "song_position": proj.get("song_pos"),
                    "loop_mode": proj.get("mode", "pattern"),
                }
        except Exception:
            pass

        # Refresh mixer
        try:
            mixer_res = fetch_all_pages(bridge, protocol.CMD_MIXER_LIST_TRACKS, "tracks")
            if isinstance(mixer_res, dict) and "tracks" in mixer_res:
                self.mixer_tracks = {t["index"]: t for t in mixer_res["tracks"] if "index" in t}
        except Exception:
            pass

        # Refresh channels
        try:
            channels_res = fetch_all_pages(bridge, protocol.CMD_CHANNEL_LIST, "channels")
            if isinstance(channels_res, dict) and "channels" in channels_res:
                self.channels = {c["index"]: c for c in channels_res["channels"] if "index" in c}
        except Exception:
            pass

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
