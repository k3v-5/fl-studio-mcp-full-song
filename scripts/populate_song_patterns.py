"""Populate FL Studio with distinct patterns and notes for Zomboy - Mind Control."""

import os
import sys
import time
import logging

sys.path.insert(0, os.path.abspath("src"))

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge
from fl_studio_mcp.pie.delivery import get_delivery_engine
from fl_studio_mcp.pyscript_gen import write_apply_script, render_apply_script, PIANO_ROLL_SCRIPTS_DIR
from fl_studio_mcp.pyscript_trigger import trigger_run_last_script

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("populate_song")


def main():
    bridge = get_bridge()
    engine = get_delivery_engine()
    
    logger.info("Setting tempo to 140 BPM...")
    bridge.call(protocol.CMD_SET_TEMPO, {"bpm": 140.0})
    
    # Define sections and their notes
    # FL Channels:
    # 0: 808 Kick
    # 1: 808 Clap
    # 2: 808 HiHat
    # 3: 808 Snare
    # 4: 808 Astronomic (synth/bass)
    
    sections = [
        {
            "name": "1_INTRO_CHORDS",
            "channel": 4,
            "notes": [
                # 8 bars of atmospheric chords in F Minor
                {"pitch": 53, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.8}, # Fm
                {"pitch": 56, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 60, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 49, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.8}, # Db
                {"pitch": 53, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 56, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 51, "time_bars": 4.0, "length_bars": 2.0, "velocity": 0.8}, # Ab
                {"pitch": 56, "time_bars": 4.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 60, "time_bars": 4.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 51, "time_bars": 6.0, "length_bars": 2.0, "velocity": 0.8}, # Eb
                {"pitch": 55, "time_bars": 6.0, "length_bars": 2.0, "velocity": 0.8},
                {"pitch": 58, "time_bars": 6.0, "length_bars": 2.0, "velocity": 0.8},
            ]
        },
        {
            "name": "2_BUILD_UP_ROLL",
            "channel": 3,
            "notes": [
                # Snare crescendo (8 bars: quarter -> eighth -> 16th -> 32nd roll)
                {"pitch": 38, "time_bars": b * 0.25, "length_bars": 0.125, "velocity": 0.4 + b * 0.03}
                for b in range(16)
            ] + [
                {"pitch": 38, "time_bars": 4.0 + b * 0.125, "length_bars": 0.0625, "velocity": 0.7 + b * 0.015}
                for b in range(16)
            ] + [
                {"pitch": 38, "time_bars": 6.0 + b * 0.0625, "length_bars": 0.03125, "velocity": 0.85 + b * 0.008}
                for b in range(32)
            ]
        },
        {
            "name": "3_DROP_KICK",
            "channel": 0,
            "notes": [
                # 4-bar heavy dubstep kick pattern
                {"pitch": 36, "time_bars": bar + 0.0, "length_bars": 0.125, "velocity": 1.0}
                for bar in range(4)
            ] + [
                {"pitch": 36, "time_bars": 1.625, "length_bars": 0.125, "velocity": 0.9},
                {"pitch": 36, "time_bars": 1.875, "length_bars": 0.125, "velocity": 0.85},
                {"pitch": 36, "time_bars": 3.625, "length_bars": 0.125, "velocity": 0.9},
                {"pitch": 36, "time_bars": 3.875, "length_bars": 0.125, "velocity": 0.95},
            ]
        },
        {
            "name": "4_DROP_SNARE_CLAP",
            "channel": 1,
            "notes": [
                # Heavy snare on beat 3 of every bar in half-time 140
                {"pitch": 39, "time_bars": bar + 0.5, "length_bars": 0.25, "velocity": 1.0}
                for bar in range(4)
            ] + [
                # Ghost snares
                {"pitch": 39, "time_bars": 3.875, "length_bars": 0.0625, "velocity": 0.75},
                {"pitch": 39, "time_bars": 3.9375, "length_bars": 0.0625, "velocity": 0.85},
            ]
        },
        {
            "name": "5_DROP_HIHATS",
            "channel": 2,
            "notes": [
                # Fast syncopated trap/dubstep hi-hats
                {"pitch": 42, "time_bars": step * 0.0625, "length_bars": 0.03125, "velocity": 0.85 if step % 2 == 0 else 0.6}
                for step in range(64) # 4 bars
            ]
        },
        {
            "name": "6_DROP_GROWL_BASS",
            "channel": 4,
            "notes": [
                # Mind Control Signature Riff in F Minor (4 bars)
                # Bar 1: F1 stab, octave leap, G#1, B1, C2
                {"pitch": 29, "time_bars": 0.0, "length_bars": 0.1875, "velocity": 1.0},
                {"pitch": 29, "time_bars": 0.25, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 41, "time_bars": 0.375, "length_bars": 0.09375, "velocity": 0.9},
                {"pitch": 32, "time_bars": 0.625, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 35, "time_bars": 0.75, "length_bars": 0.125, "velocity": 0.9},
                {"pitch": 36, "time_bars": 0.875, "length_bars": 0.125, "velocity": 0.95},
                # Bar 2: Wobble response
                {"pitch": 29, "time_bars": 1.0, "length_bars": 0.1875, "velocity": 1.0},
                {"pitch": 38, "time_bars": 1.25, "length_bars": 0.0625, "velocity": 0.9},
                {"pitch": 37, "time_bars": 1.3125, "length_bars": 0.0625, "velocity": 0.9},
                {"pitch": 36, "time_bars": 1.375, "length_bars": 0.0625, "velocity": 0.95},
                {"pitch": 29, "time_bars": 1.625, "length_bars": 0.25, "velocity": 1.0},
                # Bar 3: Repeat motif 1
                {"pitch": 29, "time_bars": 2.0, "length_bars": 0.1875, "velocity": 1.0},
                {"pitch": 29, "time_bars": 2.25, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 41, "time_bars": 2.375, "length_bars": 0.09375, "velocity": 0.9},
                {"pitch": 32, "time_bars": 2.625, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 35, "time_bars": 2.75, "length_bars": 0.125, "velocity": 0.9},
                {"pitch": 36, "time_bars": 2.875, "length_bars": 0.125, "velocity": 0.95},
                # Bar 4: Turnaround
                {"pitch": 29, "time_bars": 3.0, "length_bars": 0.125, "velocity": 1.0},
                {"pitch": 32, "time_bars": 3.25, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 35, "time_bars": 3.5, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 36, "time_bars": 3.625, "length_bars": 0.125, "velocity": 0.95},
                {"pitch": 38, "time_bars": 3.75, "length_bars": 0.125, "velocity": 1.0},
                {"pitch": 41, "time_bars": 3.875, "length_bars": 0.125, "velocity": 1.0},
            ]
        }
    ]

    for sec in sections:
        name = sec["name"]
        ch = sec["channel"]
        notes = sec["notes"]
        
        logger.info(f"Creating pattern '{name}' for channel {ch} ({len(notes)} notes)...")
        # 1. Create and select new pattern
        pat_res = bridge.call(protocol.CMD_ARRANGE_NEW_PATTERN, {"name": name})
        logger.info(f"  -> Pattern created: {pat_res}")
        
        # 2. Select the target channel
        bridge.call(protocol.CMD_CHANNEL_SELECT, {"channel": ch})
        
        # 3. Write notes via delivery engine (pyscript mode)
        pyscript_res = engine.deliver_pyscript(
            notes=notes,
            channel=ch,
            pattern_name=name,
            mode="replace",
            trigger=True,
        )
        logger.info(f"  -> Pyscript written & triggered: {pyscript_res['status']}")
        time.sleep(0.4)

    logger.info("All 6 patterns created and populated!")
    
    # Start playback so user hears the Drop Growl Bass and Drums immediately!
    logger.info("Starting playback in FL Studio...")
    bridge.call(protocol.CMD_PLAY, {})
    time.sleep(3.0)
    bridge.call(protocol.CMD_STOP, {})
    logger.info("Playback test complete!")


if __name__ == "__main__":
    main()
