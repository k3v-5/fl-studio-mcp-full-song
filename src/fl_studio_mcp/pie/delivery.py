"""Unified Song & Note Delivery Engine for FL Studio MCP (PIE).

Supports all 3 note and arrangement delivery mechanisms:
  1. realtime_record: Franco Donati / Codigo-Neon transport recording + live MIDI stream
  2. pyscript: rosasynthesiz / PIE .pyscript generation + window focus + Ctrl+Alt+Y
  3. midi_file: Smart Template / SMF Type-1 multi-track MIDI compilation & FL export
  4. all / auto: Unified multi-delivery executing all available pipelines
"""

from __future__ import annotations

import logging
import os
import shutil
import time
from typing import Any, Dict, List, Optional, Union

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge
from fl_studio_mcp.music.midi_export import write_midi
from fl_studio_mcp.pyscript_gen import render_apply_script, write_apply_script, PIANO_ROLL_SCRIPTS_DIR
from fl_studio_mcp.pyscript_trigger import trigger_run_last_script

logger = logging.getLogger(__name__)


def _fl_user_scores_dir() -> Optional[str]:
    """Return the FL Studio user scores directory if it exists."""
    for base in [
        os.path.expanduser(r"~\Documents\Image-Line\FL Studio\Presets\Scores"),
        r"D:\Documentos\Image-Line\FL Studio\Presets\Scores",
    ]:
        if os.path.exists(base):
            return base
    return None


def _fl_piano_roll_scripts_dir() -> Optional[str]:
    """Return the FL Studio user Piano roll scripts directory."""
    for base in [
        os.path.expanduser(r"~\Documents\Image-Line\FL Studio\Settings\Piano roll scripts"),
        r"D:\Documentos\Image-Line\FL Studio\Settings\Piano roll scripts",
    ]:
        if os.path.exists(base):
            return base
    return None


def normalize_note(n: dict[str, Any]) -> dict[str, Any]:
    """Normalize note dict to unified fields: pitch, time_bars, length_bars, velocity, time_beats, length_beats."""
    pitch = int(n.get("pitch", n.get("midi", 60)))
    pitch = max(0, min(127, pitch))

    if "time_bars" in n:
        time_bars = float(n["time_bars"])
        time_beats = time_bars * 4.0
    elif "time" in n:
        time_beats = float(n["time"])
        time_bars = time_beats / 4.0
    elif "start_bars" in n:
        time_bars = float(n["start_bars"])
        time_beats = time_bars * 4.0
    else:
        time_bars = 0.0
        time_beats = 0.0

    if "length_bars" in n:
        length_bars = float(n["length_bars"])
        length_beats = length_bars * 4.0
    elif "duration" in n:
        length_beats = float(n["duration"])
        length_bars = length_beats / 4.0
    else:
        length_bars = 0.25
        length_beats = 1.0

    velocity = float(n.get("velocity", 0.787))
    if velocity > 1.0:
        velocity = velocity / 127.0
    velocity = max(0.01, min(1.0, velocity))

    is_slide = bool(n.get("slide", False))
    is_porta = bool(n.get("porta", False))

    return {
        "pitch": pitch,
        "time_bars": round(time_bars, 4),
        "length_bars": round(length_bars, 4),
        "time_beats": round(time_beats, 4),
        "length_beats": round(length_beats, 4),
        "velocity": round(velocity, 4),
        "slide": is_slide,
        "porta": is_porta,
    }


class SongDeliveryEngine:
    """Coordinates note authoring and song arrangement delivery to FL Studio."""

    def __init__(self) -> None:
        self.bridge = None

    def _get_bridge(self):
        if self.bridge is None:
            self.bridge = get_bridge()
        return self.bridge

    # -------------------------------------------------------------------------
    # Option 1: Live Real-Time MIDI Recording (Franco Donati / Codigo-Neon)
    # -------------------------------------------------------------------------
    def deliver_realtime_record(
        self,
        notes: list[dict[str, Any]],
        channel: Optional[int] = None,
        bpm: Optional[float] = None,
        speed_factor: float = 1.0,
    ) -> dict[str, Any]:
        """Stream MIDI notes in real-time into FL Studio while recording is active.

        Matches Franco Donati's trigger.py send_melody:
          1. Selects channel.
          2. Starts recording (transport.record() / Note 76).
          3. Starts playback (transport.start()).
          4. Streams Note On and Note Off MIDI bytes over loopMIDI.
          5. Stops playback (transport.stop() / Note 77) and disarms record.
        """
        bridge = self._get_bridge()
        norm_notes = [normalize_note(n) for n in notes]
        if not norm_notes:
            return {"status": "error", "message": "No valid notes to record."}

        # Select target channel if specified
        if channel is not None:
            try:
                bridge.call(protocol.CMD_CHANNEL_SELECT, {"channel": int(channel)})
            except Exception as e:
                logger.warning("Could not select channel %s: %s", channel, e)

        # Get or apply BPM
        current_bpm = 140.0
        if bpm is not None:
            current_bpm = float(bpm)
            try:
                bridge.call(protocol.CMD_SET_TEMPO, {"bpm": current_bpm})
            except Exception:
                pass
        else:
            try:
                tempo_data = bridge.call(protocol.CMD_GET_TEMPO, {})
                current_bpm = float(tempo_data.get("bpm", 140.0))
            except Exception:
                current_bpm = 140.0

        seconds_per_beat = (60.0 / current_bpm) / max(0.1, speed_factor)

        # Build timeline of events
        events: list[tuple[float, str, int, int]] = []
        for n in norm_notes:
            t_on = n["time_beats"] * seconds_per_beat
            t_off = (n["time_beats"] + n["length_beats"]) * seconds_per_beat
            vel_byte = max(1, min(127, int(round(n["velocity"] * 127))))
            events.append((t_on, "on", n["pitch"], vel_byte))
            events.append((t_off, "off", n["pitch"], 0))

        events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

        # Rewind song position to start
        try:
            bridge.call(protocol.CMD_SET_SONG_POSITION, {"ms": 0.0})
        except Exception:
            pass

        # Send Note 76 for Franco Donati hardware transport recording
        try:
            bridge.send_raw_midi([0x90, 76, 1])
            time.sleep(0.02)
            bridge.send_raw_midi([0x80, 76, 0])
        except Exception as e:
            logger.debug("Note 76 send error: %s", e)

        # Trigger playback
        try:
            bridge.call(protocol.CMD_PLAY, {}, timeout=1.0)
        except Exception:
            pass

        # Stream notes
        start_time = time.time()
        for event_time, event_type, pitch, vel in events:
            elapsed = time.time() - start_time
            wait = event_time - elapsed
            if wait > 0:
                time.sleep(wait)

            if event_type == "on":
                bridge.send_raw_midi([0x90, pitch, vel])
            else:
                bridge.send_raw_midi([0x80, pitch, 0])

        time.sleep(0.2)

        # Send Note 77 to stop recording (Franco Donati hardware transport)
        try:
            bridge.send_raw_midi([0x90, 77, 1])
            time.sleep(0.02)
            bridge.send_raw_midi([0x80, 77, 0])
        except Exception as e:
            logger.debug("Note 77 send error: %s", e)

        # Stop playback
        try:
            bridge.call(protocol.CMD_STOP, {}, timeout=1.0)
        except Exception:
            pass

        total_duration = events[-1][0] if events else 0.0
        return {
            "status": "success",
            "delivery_mode": "realtime_record",
            "notes_count": len(norm_notes),
            "bpm": current_bpm,
            "duration_seconds": round(total_duration, 2),
            "channel": channel,
        }

    # -------------------------------------------------------------------------
    # Option 2: Piano Roll Script Injection (rosasynthesiz / PIE)
    # -------------------------------------------------------------------------
    def deliver_pyscript(
        self,
        notes: list[dict[str, Any]],
        channel: Optional[int] = None,
        pattern_name: str = "MCP_Apply",
        mode: str = "replace",
        trigger: bool = True,
    ) -> dict[str, Any]:
        """Author notes via generated .pyscript and trigger FL Studio shortcut."""
        bridge = self._get_bridge()
        norm_notes = [normalize_note(n) for n in notes]
        if not norm_notes:
            return {"status": "error", "message": "No valid notes for pyscript."}

        # Select target channel if specified
        if channel is not None:
            try:
                bridge.call(protocol.CMD_CHANNEL_SELECT, {"channel": int(channel)})
            except Exception as e:
                logger.warning("Could not select channel %s: %s", channel, e)

        # Also write a named script in Piano roll scripts folder
        scripts_dir = _fl_piano_roll_scripts_dir()
        named_script_path = None
        if scripts_dir and os.path.exists(scripts_dir):
            safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in pattern_name)
            named_script_path = os.path.join(scripts_dir, f"{safe_name}.pyscript")
            try:
                code = render_apply_script(norm_notes, mode)
                with open(named_script_path, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception as e:
                logger.warning("Could not write named .pyscript %s: %s", named_script_path, e)

        # Apply via bridge
        bridge_notes = [
            {"pitch": n["pitch"], "time_bars": n["time_bars"], "length_bars": n["length_bars"], "velocity": n["velocity"]}
            for n in norm_notes
        ]
        result = bridge.apply_notes(bridge_notes, mode=mode, trigger=trigger)
        return {
            "status": "success",
            "delivery_mode": "pyscript",
            "notes_count": len(norm_notes),
            "mode": mode,
            "channel": channel,
            "named_script_path": named_script_path,
            "bridge_result": result,
        }

    # -------------------------------------------------------------------------
    # Option 3: Multi-Track MIDI Compilation & Playlist Export (Smart Template)
    # -------------------------------------------------------------------------
    def deliver_midi_file(
        self,
        tracks: list[dict[str, Any]],
        song_name: str = "Arrangement",
        bpm: float = 140.0,
        output_dir: str = "exports",
        copy_to_fl: bool = True,
    ) -> dict[str, Any]:
        """Compile a multi-track Standard MIDI File (SMF Type 1) ready to import to Playlist."""
        os.makedirs(output_dir, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in song_name)
        mid_filename = f"{safe_name}_{int(bpm)}BPM.mid"
        export_path = os.path.abspath(os.path.join(output_dir, mid_filename))

        # Format tracks for write_midi
        formatted_tracks = []
        for i, t in enumerate(tracks):
            track_name = t.get("name", f"Track_{i+1}")
            track_ch = t.get("channel", i % 16)
            raw_notes = t.get("notes", [])
            norm_notes = [normalize_note(n) for n in raw_notes]
            formatted_tracks.append({
                "name": track_name,
                "channel": track_ch,
                "notes": [
                    {
                        "pitch": n["pitch"],
                        "start_bars": n["time_bars"],
                        "length_bars": n["length_bars"],
                        "velocity": n["velocity"],
                    }
                    for n in norm_notes
                ],
            })

        write_midi(formatted_tracks, bpm=bpm, path=export_path)

        # Copy to FL Studio Scores / Templates directory if available
        fl_copied = []
        if copy_to_fl:
            scores_dir = _fl_user_scores_dir()
            if scores_dir and os.path.exists(scores_dir):
                target_score = os.path.join(scores_dir, mid_filename)
                try:
                    shutil.copyfile(export_path, target_score)
                    fl_copied.append(target_score)
                except Exception as e:
                    logger.warning("Could not copy MIDI to FL Scores: %s", e)

        total_notes = sum(len(t["notes"]) for t in formatted_tracks)
        return {
            "status": "success",
            "delivery_mode": "midi_file",
            "song_name": song_name,
            "bpm": bpm,
            "tracks_count": len(formatted_tracks),
            "total_notes": total_notes,
            "export_path": export_path,
            "fl_copied_paths": fl_copied,
        }

    # -------------------------------------------------------------------------
    # Option 4: Unified Multi-Delivery (Executes requested or all pipelines)
    # -------------------------------------------------------------------------
    def deliver(
        self,
        data: Union[list[dict[str, Any]], dict[str, Any]],
        delivery_mode: str = "all",
        song_name: str = "Full_Song",
        bpm: float = 140.0,
        channel: Optional[int] = None,
        pattern_name: str = "Pattern",
        mode: str = "replace",
        trigger: bool = True,
    ) -> dict[str, Any]:
        """Universal entry point routing notes or multi-track data to the requested delivery pipeline(s)."""
        delivery_mode = delivery_mode.lower().strip()
        results: dict[str, Any] = {"status": "success", "mode": delivery_mode, "deliveries": {}}

        # Extract tracks vs flat notes
        tracks: list[dict[str, Any]] = []
        flat_notes: list[dict[str, Any]] = []

        if isinstance(data, list):
            # Check if list of tracks or list of notes
            if data and isinstance(data[0], dict) and "notes" in data[0]:
                tracks = data
                for t in tracks:
                    flat_notes.extend(t.get("notes", []))
            else:
                flat_notes = data
                tracks = [{"name": pattern_name, "channel": channel or 0, "notes": flat_notes}]
        elif isinstance(data, dict):
            if "tracks" in data:
                tracks = data["tracks"]
                for t in tracks:
                    flat_notes.extend(t.get("notes", []))
            elif "notes" in data:
                flat_notes = data["notes"]
                tracks = [{"name": pattern_name, "channel": channel or 0, "notes": flat_notes}]

        # 1. MIDI File compilation
        if delivery_mode in ("midi_file", "all", "auto"):
            results["deliveries"]["midi_file"] = self.deliver_midi_file(
                tracks=tracks,
                song_name=song_name,
                bpm=bpm,
            )

        # 2. Piano Roll script authoring & trigger
        if delivery_mode in ("pyscript", "all", "auto"):
            results["deliveries"]["pyscript"] = self.deliver_pyscript(
                notes=flat_notes,
                channel=channel,
                pattern_name=pattern_name,
                mode=mode,
                trigger=trigger,
            )

        # 3. Real-time MIDI recording
        if delivery_mode in ("realtime_record", "all"):
            results["deliveries"]["realtime_record"] = self.deliver_realtime_record(
                notes=flat_notes[:64],  # Protect against massive loops in 'all' mode
                channel=channel,
                bpm=bpm,
            )

        return results


# Global singleton
_delivery_engine = SongDeliveryEngine()


def get_delivery_engine() -> SongDeliveryEngine:
    return _delivery_engine
