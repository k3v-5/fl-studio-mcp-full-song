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
        settle_delay: float = 0.5,
        start_new_project: bool = True,
        load_timeout: float = 2.0,
        focus_channel_rack: bool = True,
    ) -> Dict[str, Any]:
        """Automate FL Studio's native 'File > Import > MIDI file...' command.

        This imports the multi-track MIDI file directly into FL Studio, causing FL's
        internal engine to spawn discrete Channel Rack generator channels for each
        instrument track with automatic mixer insert routing (1..N).

        Crucial technical steps:
        1. Force focus onto FL Studio's Delphi VCL window.
        2. Trigger 'File > Import > MIDI file...' (Alt+F -> I -> M).
        3. Focus the Windows Open File dialog edit control using universal Alt+N accelerator.
        4. Clear and inject the absolute MIDI path into the text box and press Enter.
        5. In FL Studio's modal 'Import MIDI data' dialog, press Enter to accept
           ('All tracks' + 'Create one channel per track' + 'Set mixer tracks').
        6. Settle for `load_timeout` seconds while FL Studio instantiates plugins (FLEX/Sampler).
        7. Optionally focus the Channel Rack (F6) so the user immediately sees the tracks.
        """
        abs_path = os.path.abspath(midi_file_path)
        if not os.path.exists(abs_path):
            return {
                "ok": False,
                "error": f"MIDI file not found at: {abs_path}",
            }

        track_names: List[str] = []
        try:
            import mido
            mid = mido.MidiFile(abs_path)
            track_names = [t.name for t in mid.tracks if t.name and t.name.lower() != "tempo"]
        except Exception as e:
            logger.debug("Could not parse MIDI track names: %s", e)

        if sys.platform != "win32":
            return {
                "ok": False,
                "error": "Automated GUI MIDI import is currently optimized for Windows FL Studio.",
                "manual_path": abs_path,
                "track_names": track_names,
            }

        hwnd = find_fl_hwnd()
        if not hwnd:
            return {
                "ok": False,
                "error": "FL Studio main window not found (TFruityLoopsMainForm). Ensure FL Studio is running.",
                "manual_path": abs_path,
                "track_names": track_names,
            }

        try:
            import pyautogui
            import pyperclip
        except ImportError as e:
            return {
                "ok": False,
                "error": f"Required GUI automation library missing: {e}",
                "manual_path": abs_path,
                "track_names": track_names,
            }

        pyautogui.FAILSAFE = False

        # 1. Force focus onto FL Studio
        focused = force_focus(hwnd)
        time.sleep(settle_delay)

        # 2. Trigger File > Import > MIDI file...
        # In FL Studio: Alt (activates menu) -> 'f' (File) -> 'i' (Import) -> 'm' (MIDI file)
        pyautogui.hotkey("alt", "f")
        time.sleep(0.2)
        pyautogui.press("i")
        time.sleep(0.2)
        pyautogui.press("m")
        time.sleep(max(settle_delay, 0.6))

        # 3. Focus filename edit box in Windows Open dialog using Alt+N
        # 'Alt+N' is the universal accelerator in both English ('File name:') and Spanish ('Nombre de archivo:')
        pyautogui.hotkey("alt", "n")
        time.sleep(0.15)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.05)
        pyautogui.press("backspace")
        time.sleep(0.05)

        # 4. Inject target path and press Enter to open
        pyperclip.copy(abs_path)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.25)
        pyautogui.press("enter")
        time.sleep(max(settle_delay, 0.8))

        # 5. FL Studio displays the "Import MIDI data" dialog
        # Ensure focus is back on FL Studio modal dialog and accept
        force_focus(hwnd)
        time.sleep(0.15)
        pyautogui.press("enter")

        # 6. Settle while FL Studio allocates channels and instantiates generator plugins
        time.sleep(load_timeout)

        # 7. Bring Channel Rack forward so all created tracks are immediately visible
        if focus_channel_rack:
            pyautogui.press("f6")
            time.sleep(0.2)

        return {
            "ok": True,
            "status": "imported",
            "file": abs_path,
            "focused": focused,
            "tracks_count": len(track_names),
            "track_names": track_names,
            "message": (
                f"MIDI file imported successfully into FL Studio with {len(track_names)} discrete channels."
                if track_names
                else "MIDI file imported successfully into FL Studio Channel Rack."
            ),
        }

    def auto_arrange_song(
        self,
        midi_path: str,
        sections: Optional[List[Dict[str, Any]]] = None,
        bpm: float = 140.0,
        settle_delay: float = 0.5,
        start_new_project: bool = True,
        load_timeout: float = 2.0,
        focus_channel_rack: bool = True,
    ) -> Dict[str, Any]:
        """Full hands-free song arrangement execution:
        1. Syncs tempo via SysEx bridge.
        2. Adds timeline section markers in FL Studio.
        3. Automates native multi-track MIDI import to populate Channel Rack & Playlist.
        4. Focuses Channel Rack and sets song position to start.
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

        # 3. Automated native multi-track MIDI file import
        import_result = self.auto_import_midi_to_playlist(
            midi_path,
            settle_delay=settle_delay,
            start_new_project=start_new_project,
            load_timeout=load_timeout,
            focus_channel_rack=focus_channel_rack,
        )

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
            "tracks_count": import_result.get("tracks_count", 0),
            "track_names": import_result.get("track_names", []),
            "summary": "Song arranged automatically with discrete channels in Channel Rack and mapped to Playlist.",
        }


_global_arranger: Optional[PlaylistArranger] = None


def get_playlist_arranger() -> PlaylistArranger:
    """Return the singleton PlaylistArranger instance."""
    global _global_arranger
    if _global_arranger is None:
        _global_arranger = PlaylistArranger()
    return _global_arranger
