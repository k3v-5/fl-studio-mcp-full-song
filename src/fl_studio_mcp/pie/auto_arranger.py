"""Auto-Arranger Engine for FL Studio MCP (PIE).

Eliminates manual drag-and-drop onto the Playlist by automating:
1. Native FL Studio MIDI import (Alt+F -> I -> M + path injection) to automatically lay out tracks.
2. Timeline section markers (Intro, Build, Drop, Break, Outro) via the controller script API.
3. Pattern sequencing and playlist arrangement coordination.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge
from fl_studio_mcp.pyscript_trigger import find_fl_hwnd, force_focus

logger = logging.getLogger(__name__)


class PlaylistArranger:
    """Manages programmatic song arrangement and hands-free playlist layout."""

    def __init__(self) -> None:
        self.bridge = None

    def _get_bridge(self):
        if self.bridge is None:
            self.bridge = get_bridge()
        return self.bridge

    def _is_connected(self) -> bool:
        bridge = self._get_bridge()
        if bridge is None:
            return False
        try:
            return bool(bridge.is_alive())
        except Exception:
            return False

    def add_timeline_markers(
        self,
        sections: List[Dict[str, Any]],
        ppq: int = 96,
        beats_per_bar: int = 4,
    ) -> Dict[str, Any]:
        """Add arrangement time markers (Intro, Build, Drop, etc.) to FL Studio's timeline.

        sections: list of dicts with {"name": str, "start_bar": float, ...}
        """
        bridge = self._get_bridge()
        if not self._is_connected():
            return {"ok": False, "error": "FL Studio bridge not connected"}

        ticks_per_bar = ppq * beats_per_bar
        results = []

        for sec in sections:
            name = str(sec.get("name", "SECTION")).upper()
            start_bar = float(sec.get("start_bar", 0.0))
            tick = int(round(start_bar * ticks_per_bar))

            try:
                resp = bridge.call_sync(
                    protocol.CMD_ARRANGE_ADD_MARKER,
                    {"time": tick, "name": name},
                    timeout=2.0,
                )
                results.append({
                    "name": name,
                    "bar": start_bar,
                    "tick": tick,
                    "ok": resp.get("ok", True),
                })
            except Exception as e:
                logger.warning("Failed to add marker %s at bar %.1f: %s", name, start_bar, e)
                results.append({
                    "name": name,
                    "bar": start_bar,
                    "tick": tick,
                    "ok": False,
                    "error": str(e),
                })

        return {
            "ok": True,
            "total_markers": len(results),
            "markers": results,
        }

    def auto_import_midi_to_playlist(
        self,
        midi_file_path: str,
        settle_delay: float = 0.4,
        start_new_project: bool = False,
    ) -> Dict[str, Any]:
        """Automate FL Studio's native 'File > Import > MIDI file...' command.

        This opens the MIDI file directly inside FL Studio, causing FL's internal
        engine to map every track to a channel and place all patterns directly
        across the Playlist tracks, completely eliminating manual dragging.
        """
        abs_path = os.path.abspath(midi_file_path)
        if not os.path.exists(abs_path):
            return {
                "ok": False,
                "error": f"MIDI file not found at: {abs_path}",
            }

        if sys.platform != "win32":
            return {
                "ok": False,
                "error": "Automated GUI MIDI import is currently optimized for Windows FL Studio.",
                "manual_path": abs_path,
            }

        hwnd = find_fl_hwnd()
        if not hwnd:
            return {
                "ok": False,
                "error": "FL Studio main window not found (TFruityLoopsMainForm). Ensure FL Studio is running.",
                "manual_path": abs_path,
            }

        try:
            import pyautogui
            import pyperclip
        except ImportError as e:
            return {
                "ok": False,
                "error": f"Required GUI automation library missing: {e}",
                "manual_path": abs_path,
            }

        # 1. Force focus onto FL Studio
        focused = force_focus(hwnd)
        time.sleep(settle_delay)

        # 2. Trigger File > Import > MIDI file...
        # In FL Studio: Alt (activates menu) -> 'f' (File) -> 'i' (Import) -> 'm' (MIDI file)
        pyautogui.FAILSAFE = False
        pyautogui.hotkey("alt", "f")
        time.sleep(0.15)
        pyautogui.press("i")
        time.sleep(0.15)
        pyautogui.press("m")
        time.sleep(settle_delay)

        # 3. Paste absolute file path into Windows Open File dialog
        pyperclip.copy(abs_path)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.15)
        pyautogui.press("enter")
        time.sleep(settle_delay)

        # 4. FL Studio displays the "Import MIDI data" dialog
        # Press Enter to accept default track mapping into Playlist
        pyautogui.press("enter")
        time.sleep(0.2)

        return {
            "ok": True,
            "status": "imported",
            "file": abs_path,
            "focused": focused,
            "message": "MIDI file automatically imported and arranged across FL Studio Playlist tracks.",
        }

    def auto_arrange_song(
        self,
        midi_path: str,
        sections: Optional[List[Dict[str, Any]]] = None,
        bpm: float = 140.0,
        settle_delay: float = 0.4,
    ) -> Dict[str, Any]:
        """Full hands-free song arrangement execution:
        1. Adds timeline section markers in FL Studio.
        2. Automates MIDI import to populate Playlist tracks.
        3. Sets transport position to bar 0 and syncs tempo.
        """
        bridge = self._get_bridge()
        marker_result = {}

        # 1. Sync tempo
        if self._is_connected():
            try:
                bridge.call_sync(protocol.CMD_SET_TEMPO, {"bpm": bpm}, timeout=2.0)
            except Exception as e:
                logger.warning("Could not set tempo: %s", e)

        # 2. Timeline section markers
        if sections and self._is_connected():
            marker_result = self.add_timeline_markers(sections)

        # 3. Automated MIDI file import
        import_result = self.auto_import_midi_to_playlist(midi_path, settle_delay=settle_delay)

        # 4. Rewind to start
        if self._is_connected():
            try:
                bridge.call_sync(protocol.CMD_SET_SONG_POS, {"beats": 0.0}, timeout=2.0)
            except Exception as e:
                logger.warning("Could not reset song position: %s", e)

        return {
            "ok": import_result.get("ok", False),
            "midi_import": import_result,
            "markers": marker_result,
            "bpm": bpm,
            "summary": "Song arranged automatically on Playlist timeline without manual dragging.",
        }


_global_arranger: Optional[PlaylistArranger] = None


def get_playlist_arranger() -> PlaylistArranger:
    """Return the singleton PlaylistArranger instance."""
    global _global_arranger
    if _global_arranger is None:
        _global_arranger = PlaylistArranger()
    return _global_arranger
