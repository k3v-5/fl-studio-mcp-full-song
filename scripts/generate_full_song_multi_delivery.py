"""Production script: Generate full Zomboy-style song using all 3 delivery options."""

import os
import sys
import time
import shutil
import logging

# Ensure src is on path
sys.path.insert(0, os.path.abspath("src"))

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge
from fl_studio_mcp.pie.delivery import get_delivery_engine
from fl_studio_mcp.pyscript_trigger import find_fl_hwnd, force_focus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("song_generator")


def create_zomboy_song_data():
    """Generates notes and tracks for Zomboy - Mind Control at 140 BPM in F Minor."""
    
    # -------------------------------------------------------------
    # 1. KICKS (Channel 0)
    # -------------------------------------------------------------
    kick_notes = []
    # Drop 1 (bars 16 to 32 -> 16 bars)
    for bar in range(16, 32):
        # Half-time dubstep kick: beat 1 (bar.0), and syncopated pickup at bar.875 or bar.75
        kick_notes.append({"pitch": 36, "time_bars": bar + 0.0, "length_bars": 0.125, "velocity": 1.0})
        if bar % 2 == 1:
            kick_notes.append({"pitch": 36, "time_bars": bar + 0.625, "length_bars": 0.125, "velocity": 0.9})
            kick_notes.append({"pitch": 36, "time_bars": bar + 0.875, "length_bars": 0.125, "velocity": 0.85})
    # Drop 2 (bars 48 to 64)
    for bar in range(48, 64):
        kick_notes.append({"pitch": 36, "time_bars": bar + 0.0, "length_bars": 0.125, "velocity": 1.0})
        if bar % 2 == 1:
            kick_notes.append({"pitch": 36, "time_bars": bar + 0.5, "length_bars": 0.125, "velocity": 0.95})
            kick_notes.append({"pitch": 36, "time_bars": bar + 0.75, "length_bars": 0.125, "velocity": 0.9})

    # -------------------------------------------------------------
    # 2. SNARES / CLAPS (Channel 1)
    # -------------------------------------------------------------
    snare_notes = []
    # Build-up 1 (bars 8 to 16) - Crescendo
    for bar in range(8, 12):
        # Quarter notes
        for b in range(4):
            vel = 0.4 + (bar - 8 + b / 4.0) * 0.08
            snare_notes.append({"pitch": 38, "time_bars": bar + b * 0.25, "length_bars": 0.125, "velocity": min(1.0, vel)})
    for bar in range(12, 14):
        # Eighth notes
        for b in range(8):
            vel = 0.65 + (bar - 12 + b / 8.0) * 0.12
            snare_notes.append({"pitch": 38, "time_bars": bar + b * 0.125, "length_bars": 0.0625, "velocity": min(1.0, vel)})
    for bar in range(14, 16):
        # 16th notes frenzy
        for b in range(16):
            vel = 0.85 + (b / 16.0) * 0.15
            snare_notes.append({"pitch": 38, "time_bars": bar + b * 0.0625, "length_bars": 0.03125, "velocity": min(1.0, vel)})
    
    # Drop 1 (bars 16 to 32) - Heavy half-time snare on beat 3 (bar + 0.5)
    for bar in range(16, 32):
        snare_notes.append({"pitch": 38, "time_bars": bar + 0.5, "length_bars": 0.25, "velocity": 1.0})
        if bar % 4 == 3:
            # Ghost snare fill at end of 4-bar phrase
            snare_notes.append({"pitch": 38, "time_bars": bar + 0.875, "length_bars": 0.0625, "velocity": 0.75})
            snare_notes.append({"pitch": 38, "time_bars": bar + 0.9375, "length_bars": 0.0625, "velocity": 0.9})

    # Drop 2 (bars 48 to 64)
    for bar in range(48, 64):
        snare_notes.append({"pitch": 38, "time_bars": bar + 0.5, "length_bars": 0.25, "velocity": 1.0})

    # -------------------------------------------------------------
    # 3. HI-HATS (Channel 2)
    # -------------------------------------------------------------
    hihat_notes = []
    for bar in range(16, 32):
        for step in range(16):
            pos = bar + step * 0.0625
            vel = 0.85 if step % 2 == 0 else 0.6
            hihat_notes.append({"pitch": 42, "time_bars": pos, "length_bars": 0.03125, "velocity": vel})
    for bar in range(48, 64):
        for step in range(16):
            pos = bar + step * 0.0625
            vel = 0.9 if step % 2 == 0 else 0.7
            hihat_notes.append({"pitch": 42, "time_bars": pos, "length_bars": 0.03125, "velocity": vel})

    # -------------------------------------------------------------
    # 4. GROWL BASS (Channel 3) - Mind Control signature riff in F Minor
    # -------------------------------------------------------------
    # F1=29, G#1=32, C2=36, B1=35, D2=38, C#2=37
    growl_notes = []
    # Drop 1 (bars 16 to 32)
    for bar in range(16, 32):
        rel = bar % 4
        if rel in (0, 2):
            # Heavy stabs on F1 and octave leap
            growl_notes.append({"pitch": 29, "time_bars": bar + 0.0, "length_bars": 0.1875, "velocity": 1.0})
            growl_notes.append({"pitch": 29, "time_bars": bar + 0.25, "length_bars": 0.125, "velocity": 0.95})
            growl_notes.append({"pitch": 41, "time_bars": bar + 0.375, "length_bars": 0.09375, "velocity": 0.9})
            growl_notes.append({"pitch": 32, "time_bars": bar + 0.625, "length_bars": 0.125, "velocity": 0.95})
            growl_notes.append({"pitch": 35, "time_bars": bar + 0.75, "length_bars": 0.125, "velocity": 0.9})
            growl_notes.append({"pitch": 36, "time_bars": bar + 0.875, "length_bars": 0.125, "velocity": 0.95})
        elif rel == 1:
            # Syncopated wobble response
            growl_notes.append({"pitch": 29, "time_bars": bar + 0.0, "length_bars": 0.1875, "velocity": 1.0})
            growl_notes.append({"pitch": 38, "time_bars": bar + 0.25, "length_bars": 0.0625, "velocity": 0.9})
            growl_notes.append({"pitch": 37, "time_bars": bar + 0.3125, "length_bars": 0.0625, "velocity": 0.9})
            growl_notes.append({"pitch": 36, "time_bars": bar + 0.375, "length_bars": 0.0625, "velocity": 0.95})
            growl_notes.append({"pitch": 29, "time_bars": bar + 0.625, "length_bars": 0.25, "velocity": 1.0})
        else:
            # Riff turnaround
            growl_notes.append({"pitch": 29, "time_bars": bar + 0.0, "length_bars": 0.125, "velocity": 1.0})
            growl_notes.append({"pitch": 32, "time_bars": bar + 0.25, "length_bars": 0.125, "velocity": 0.95})
            growl_notes.append({"pitch": 35, "time_bars": bar + 0.5, "length_bars": 0.125, "velocity": 0.95})
            growl_notes.append({"pitch": 36, "time_bars": bar + 0.625, "length_bars": 0.125, "velocity": 0.95})
            growl_notes.append({"pitch": 38, "time_bars": bar + 0.75, "length_bars": 0.125, "velocity": 1.0})
            growl_notes.append({"pitch": 41, "time_bars": bar + 0.875, "length_bars": 0.125, "velocity": 1.0})

    # Drop 2 (bars 48 to 64) - Same motif with doubled syncopation
    for bar in range(48, 64):
        for n in growl_notes[:18]:
            growl_notes.append({
                "pitch": n["pitch"],
                "time_bars": n["time_bars"] + 32.0,
                "length_bars": n["length_bars"],
                "velocity": n["velocity"],
            })

    # -------------------------------------------------------------
    # 5. SUB BASS 808 (Channel 4)
    # -------------------------------------------------------------
    sub_notes = []
    for bar in range(16, 32):
        sub_notes.append({"pitch": 29, "time_bars": bar + 0.0, "length_bars": 0.45, "velocity": 1.0})
        if bar % 2 == 1:
            sub_notes.append({"pitch": 32, "time_bars": bar + 0.625, "length_bars": 0.35, "velocity": 0.9})
    for bar in range(48, 64):
        sub_notes.append({"pitch": 29, "time_bars": bar + 0.0, "length_bars": 0.45, "velocity": 1.0})

    # -------------------------------------------------------------
    # 6. INTRO & BREAKDOWN CHORDS / ATMOS (Channel 5)
    # Fm (F3, Ab3, C4 = 53, 56, 60), Db (53, 56, 61), Ab (51, 56, 60), Eb (51, 55, 58)
    # -------------------------------------------------------------
    chord_notes = []
    # Intro (bars 0 to 8)
    chords_seq = [
        (0, [53, 56, 60]),  # Fm
        (2, [49, 53, 56]),  # Db
        (4, [51, 56, 60]),  # Ab
        (6, [51, 55, 58]),  # Eb
    ]
    for bar_start, pitches in chords_seq:
        for p in pitches:
            chord_notes.append({"pitch": p, "time_bars": bar_start, "length_bars": 2.0, "velocity": 0.75})
            chord_notes.append({"pitch": p, "time_bars": bar_start + 32.0, "length_bars": 2.0, "velocity": 0.8})

    tracks = [
        {"name": "1_KICK_140", "channel": 0, "notes": kick_notes},
        {"name": "2_SNARE_CLAP", "channel": 1, "notes": snare_notes},
        {"name": "3_HI_HATS", "channel": 2, "notes": hihat_notes},
        {"name": "4_GROWL_BASS", "channel": 3, "notes": growl_notes},
        {"name": "5_SUB_BASS", "channel": 4, "notes": sub_notes},
        {"name": "6_CHORDS_ATMOS", "channel": 5, "notes": chord_notes},
    ]

    return tracks


def main():
    logger.info("=== Starting Multi-Delivery Song Generation: Zomboy - Mind Control (140 BPM) ===")
    
    bridge = get_bridge()
    engine = get_delivery_engine()
    
    # 1. Transport & Session Setup
    logger.info("1. Setting tempo to 140.0 BPM...")
    bridge.call(protocol.CMD_SET_TEMPO, {"bpm": 140.0})
    
    # 2. Timeline Markers
    logger.info("2. Creating arrangement timeline markers...")
    markers = [
        (1, "INTRO (Fm)"),
        (9, "BUILD-UP"),
        (17, "DROP 1 - MIND CONTROL"),
        (33, "BREAKDOWN"),
        (41, "BUILD-UP 2"),
        (49, "DROP 2 - EVOLUTION"),
        (65, "OUTRO"),
    ]
    for bar, name in markers:
        try:
            bridge.call(protocol.CMD_ARRANGE_ADD_MARKER, {"bar": bar, "name": name})
        except Exception as e:
            logger.warning("Marker at bar %d failed: %s", bar, e)

    # 3. Mixer Setup
    logger.info("3. Setting up mixer tracks with gain staging and colors...")
    mixer_channels = [
        (1, "KICK 140", 0.85, 0x1E90FF),     # Dodger Blue
        (2, "SNARE 200HZ", 0.80, 0xFF4500),  # Orange Red
        (3, "HI-HATS", 0.70, 0xFFD700),      # Gold
        (4, "GROWL BASS", 0.82, 0x00FF7F),   # Spring Green
        (5, "SUB BASS 808", 0.78, 0x9370DB), # Medium Purple
        (6, "ATMOS & FX", 0.65, 0x20B2AA),   # Light Sea Green
    ]
    for track_id, name, vol, color in mixer_channels:
        try:
            bridge.call(protocol.CMD_MIXER_SET_NAME, {"track": track_id, "name": name})
            bridge.call(protocol.CMD_MIXER_SET_VOLUME, {"track": track_id, "value": vol})
            bridge.call(protocol.CMD_MIXER_SET_COLOR, {"track": track_id, "color": color})
        except Exception as e:
            logger.warning("Mixer track %d config failed: %s", track_id, e)

    # 4. Generate song composition data
    logger.info("4. Generating composition data for 6 multitrack channels...")
    tracks = create_zomboy_song_data()
    total_notes = sum(len(t["notes"]) for t in tracks)
    logger.info(f"Generated {len(tracks)} tracks with {total_notes} total notes.")

    # -------------------------------------------------------------------------
    # EXECUTE OPTION 3: Multi-Track MIDI Compilation & FL Scores/Template Export
    # -------------------------------------------------------------------------
    logger.info("--- Executing Option 3: Multi-Track MIDI Compilation & Export ---")
    midi_res = engine.deliver_midi_file(
        tracks=tracks,
        song_name="Zomboy_Mind_Control_140BPM_Full_Song",
        bpm=140.0,
        output_dir="exports",
        copy_to_fl=True,
    )
    logger.info(f"Option 3 Success: Exported SMF Type-1 to {midi_res['export_path']}")
    for p in midi_res.get("fl_copied_paths", []):
        logger.info(f"  -> Installed in FL Studio directory: {p}")

    # -------------------------------------------------------------------------
    # EXECUTE OPTION 2: Piano Roll Scripts Generation & Trigger
    # -------------------------------------------------------------------------
    logger.info("--- Executing Option 2: Piano Roll Script Injection ---")
    scripts_installed = []
    for t in tracks:
        res_pyscript = engine.deliver_pyscript(
            notes=t["notes"],
            channel=t["channel"],
            pattern_name=f"Zomboy_{t['name']}",
            mode="replace",
            trigger=False,  # We trigger for the primary bass track below
        )
        if res_pyscript.get("named_script_path"):
            scripts_installed.append(res_pyscript["named_script_path"])
    
    # Trigger active piano roll with MCP_Apply containing the Growl Bass
    growl_notes = [n for t in tracks if t["name"] == "4_GROWL_BASS" for n in t["notes"]][:32]
    res_trigger = engine.deliver_pyscript(
        notes=growl_notes,
        channel=3,
        pattern_name="MCP_Apply",
        mode="replace",
        trigger=True,
    )
    logger.info(f"Option 2 Success: Installed {len(scripts_installed)} .pyscript files. Trigger result: {res_trigger.get('bridge_result')}")

    # -------------------------------------------------------------------------
    # EXECUTE OPTION 1: Real-Time Live MIDI Recording (Franco Donati / Codigo-Neon)
    # -------------------------------------------------------------------------
    logger.info("--- Executing Option 1: Live Real-Time MIDI Recording (Franco Donati technique) ---")
    # Stream a 2-bar Drop Growl Bass sequence in real-time
    riff_2bars = [
        {"pitch": 29, "time_bars": 0.0, "length_bars": 0.1875, "velocity": 1.0},
        {"pitch": 29, "time_bars": 0.25, "length_bars": 0.125, "velocity": 0.95},
        {"pitch": 41, "time_bars": 0.375, "length_bars": 0.09375, "velocity": 0.9},
        {"pitch": 32, "time_bars": 0.625, "length_bars": 0.125, "velocity": 0.95},
        {"pitch": 35, "time_bars": 0.75, "length_bars": 0.125, "velocity": 0.9},
        {"pitch": 36, "time_bars": 0.875, "length_bars": 0.125, "velocity": 0.95},
        {"pitch": 29, "time_bars": 1.0, "length_bars": 0.1875, "velocity": 1.0},
        {"pitch": 38, "time_bars": 1.25, "length_bars": 0.0625, "velocity": 0.9},
        {"pitch": 37, "time_bars": 1.3125, "length_bars": 0.0625, "velocity": 0.9},
        {"pitch": 36, "time_bars": 1.375, "length_bars": 0.0625, "velocity": 0.95},
        {"pitch": 29, "time_bars": 1.625, "length_bars": 0.25, "velocity": 1.0},
    ]
    # Execute recording at fast speed factor so test finishes smoothly
    rec_res = engine.deliver_realtime_record(
        notes=riff_2bars,
        channel=3,
        bpm=140.0,
        speed_factor=4.0,  # 4x fast-forward real-time stream for instant execution
    )
    logger.info(f"Option 1 Success: Recorded {rec_res.get('notes_count')} notes live into FL Studio. Duration: {rec_res.get('duration_seconds')}s.")

    logger.info("=== All 3 Delivery Options Executed Successfully! ===")
    return {
        "status": "success",
        "tempo": 140.0,
        "tracks": len(tracks),
        "total_notes": total_notes,
        "option1_realtime": rec_res,
        "option2_pyscript": res_trigger,
        "option3_midi_file": midi_res,
    }


if __name__ == "__main__":
    result = main()
    print("\nResult summary:", result["status"])
