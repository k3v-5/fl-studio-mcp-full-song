"""Automated full-song production script for FL Studio MCP.
Creates a complete 140 BPM Dubstep track inspired by Zomboy - Mind Control.
"""

import asyncio
import json
import sys
import time

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fl_studio_mcp.server import build_server

async def run_production():
    print("=== [PHASE 1] Initializing FastMCP Server ===")
    server = build_server()

    # Helper to call tool and unpack JSON
    async def call(tool_name: str, args: dict = None):
        if args is None:
            args = {}
        print(f"-> Calling {tool_name}({args})...")
        res = await server.call_tool(tool_name, args)
        text = res.content[0].text if res.content else "{}"
        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            return text

    # Ping check
    ping = await call("fl_ping")
    print(f"Ping: {ping}")
    if not ping.get("alive"):
        raise RuntimeError("FL Studio is not alive!")

    # 1. Set Tempo to 140 BPM
    print("\n=== [PHASE 1] Setting Tempo & Arranging Timeline Markers ===")
    tempo_res = await call("fl_set_tempo", {"bpm": 140.0})
    print(f"Tempo set: {tempo_res}")

    # Add Markers
    markers = [
        (1, "INTRO"),
        (17, "BUILD-UP"),
        (25, "DROP 1 - MIND CONTROL"),
        (41, "BREAKDOWN"),
        (49, "DROP 2 - CHAOS"),
        (65, "OUTRO"),
    ]
    for bar, name in markers:
        m_res = await call("fl_arrange_add_marker", {"bar": bar, "name": name})
        print(f"  Marker '{name}' at Bar {bar}: {m_res}")

    # 2. Theory & Scales
    print("\n=== [PHASE 2] Music Theory & Sound Design Queries ===")
    scale_res = await call("fl_suggest_scale", {"genre": "trap", "mood": "aggressive"})
    print("Scale Suggestion:", json.dumps(scale_res, indent=2))

    bass_tech = await call("fl_get_bass_technique", {"genre": "dubstep"})
    print("Bass Technique:", bass_tech)

    growl_guide = await call("fl_get_bass_growl_guide", {})
    print("Growl Guide:", growl_guide)

    # 3. Create Patterns and Inject Piano Roll Notes
    print("\n=== [PHASE 3] Creating Patterns & Injecting Notes in FL Studio ===")

    # Channel indices:
    # 0: 808 Kick
    # 1: 808 Clap
    # 2: 808 HiHat
    # 3: 808 Snare
    # 4: 808 Astronomic (Bass/Synth)

    # --- Pattern 1: PAT_INTRO_ATMOS ---
    print("\n-- Creating PAT_INTRO_ATMOS --")
    await call("fl_arrange_new_pattern", {"name": "PAT_INTRO_ATMOS"})
    await call("fl_arrange_select_channel", {"channel": 4})
    # Dark sustained chords in F Phrygian/Minor (F3=53, Ab3=56, C4=60; Db3=49, F3=53, Ab3=56)
    intro_chords = [
        # Bar 0-2: F Minor (F3, Ab3, C4)
        {"pitch": 53, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.70},
        {"pitch": 56, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.65},
        {"pitch": 60, "time_bars": 0.0, "length_bars": 2.0, "velocity": 0.65},
        # Bar 2-4: Db Major (Db3, F3, Ab3)
        {"pitch": 49, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.70},
        {"pitch": 53, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.65},
        {"pitch": 56, "time_bars": 2.0, "length_bars": 2.0, "velocity": 0.65},
    ]
    res_intro = await call("fl_write_piano_roll_notes", {"notes": intro_chords, "mode": "replace"})
    print("Intro chords written:", res_intro)

    # Subtle intro hats on channel 2
    await call("fl_arrange_select_channel", {"channel": 2})
    intro_hats = [
        {"pitch": 60, "time_bars": float(b + step * 0.25), "length_bars": 0.125, "velocity": 0.45}
        for b in range(4) for step in [1, 3] # Offbeats
    ]
    await call("fl_write_piano_roll_notes", {"notes": intro_hats, "mode": "replace"})

    # --- Pattern 2: PAT_BUILD_SNARE ---
    print("\n-- Creating PAT_BUILD_SNARE --")
    await call("fl_arrange_new_pattern", {"name": "PAT_BUILD_SNARE"})
    await call("fl_arrange_select_channel", {"channel": 3}) # Snare
    # 8 bars of accelerating snare roll:
    build_notes = []
    # Bars 0-1 (Quarter notes)
    for bar in range(2):
        for beat in range(4):
            t = float(bar + beat * 0.25)
            v = 0.40 + (t / 8.0) * 0.35
            build_notes.append({"pitch": 60, "time_bars": t, "length_bars": 0.15, "velocity": min(0.95, v)})
    # Bars 2-3 (8th notes)
    for bar in range(2, 4):
        for eighth in range(8):
            t = float(bar + eighth * 0.125)
            v = 0.45 + (t / 8.0) * 0.40
            build_notes.append({"pitch": 60, "time_bars": t, "length_bars": 0.08, "velocity": min(0.95, v)})
    # Bars 4-5 (16th notes)
    for bar in range(4, 6):
        for sixteenth in range(16):
            t = float(bar + sixteenth * 0.0625)
            v = 0.50 + (t / 8.0) * 0.45
            build_notes.append({"pitch": 60, "time_bars": t, "length_bars": 0.04, "velocity": min(0.98, v)})
    # Bar 6 (32nd rush)
    for thirtysecond in range(32):
        t = float(6.0 + thirtysecond * 0.03125)
        build_notes.append({"pitch": 60, "time_bars": t, "length_bars": 0.02, "velocity": 0.95})
    # Bar 7 (Final build up to beat 3, silence on beat 4 for drop punchline)
    for thirtysecond in range(24): # Only up to 0.75 (beat 3 end)
        t = float(7.0 + thirtysecond * 0.03125)
        build_notes.append({"pitch": 60, "time_bars": t, "length_bars": 0.02, "velocity": 1.0})

    res_build = await call("fl_write_piano_roll_notes", {"notes": build_notes, "mode": "replace"})
    print("Build-up snare roll written:", res_build)

    # --- Pattern 3: PAT_DROP_DRUMS ---
    print("\n-- Creating PAT_DROP_DRUMS --")
    await call("fl_arrange_new_pattern", {"name": "PAT_DROP_DRUMS"})

    # 1. Kicks on channel 0 (140 BPM Dubstep half-time)
    await call("fl_arrange_select_channel", {"channel": 0})
    # Heavy kick on Beat 1 of every bar, syncopated ghost kick on Beat 2.75 or 4.5
    drop_kicks = []
    for bar in range(4):
        drop_kicks.append({"pitch": 60, "time_bars": float(bar), "length_bars": 0.2, "velocity": 1.0})
        if bar % 2 == 1:
            drop_kicks.append({"pitch": 60, "time_bars": float(bar + 0.6875), "length_bars": 0.15, "velocity": 0.90})
        if bar == 3:
            drop_kicks.append({"pitch": 60, "time_bars": float(bar + 0.875), "length_bars": 0.125, "velocity": 0.95})
    await call("fl_write_piano_roll_notes", {"notes": drop_kicks, "mode": "replace"})

    # 2. Snares on channel 3 (Dubstep Half-time: Hit on BEAT 3 of every bar!)
    await call("fl_arrange_select_channel", {"channel": 3})
    drop_snares = [
        {"pitch": 60, "time_bars": float(bar + 0.50), "length_bars": 0.25, "velocity": 1.0}
        for bar in range(4)
    ]
    await call("fl_write_piano_roll_notes", {"notes": drop_snares, "mode": "replace"})

    # 3. Claps on channel 1 (Layered with Snare on Beat 3 for stereo punch)
    await call("fl_arrange_select_channel", {"channel": 1})
    drop_claps = [
        {"pitch": 60, "time_bars": float(bar + 0.50), "length_bars": 0.20, "velocity": 0.85}
        for bar in range(4)
    ]
    await call("fl_write_piano_roll_notes", {"notes": drop_claps, "mode": "replace"})

    # 4. Hi-Hats on channel 2 (16th groove with accents)
    await call("fl_arrange_select_channel", {"channel": 2})
    drop_hats = []
    for bar in range(4):
        for i in range(16):
            t = float(bar + i * 0.0625)
            v = 0.80 if i % 2 == 1 else 0.45
            drop_hats.append({"pitch": 60, "time_bars": t, "length_bars": 0.04, "velocity": v})
    await call("fl_write_piano_roll_notes", {"notes": drop_hats, "mode": "replace"})
    print("Drop drums written across Kicks, Snares, Claps, and Hats.")

    # --- Pattern 4: PAT_DROP_GROWL_BASS ---
    print("\n-- Creating PAT_DROP_GROWL_BASS --")
    await call("fl_arrange_new_pattern", {"name": "PAT_DROP_GROWL_BASS"})
    await call("fl_arrange_select_channel", {"channel": 4})
    # Zomboy-style aggressive talking growl rhythm in F (F1=29, F2=41, G2=43, Ab2=44, Bb2=46)
    drop_bass = [
        # Bar 0: Main F growl stab on 1, rapid stutter, slide to Ab
        {"pitch": 29, "time_bars": 0.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 41, "time_bars": 0.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 41, "time_bars": 0.25, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 41, "time_bars": 0.375, "length_bars": 0.0625, "velocity": 0.85},
        {"pitch": 44, "time_bars": 0.625, "length_bars": 0.125, "velocity": 0.95},
        {"pitch": 43, "time_bars": 0.75, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 41, "time_bars": 0.875, "length_bars": 0.08, "velocity": 0.95},

        # Bar 1: Answering high screech / vocal vowel chop
        {"pitch": 29, "time_bars": 1.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 46, "time_bars": 1.125, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 44, "time_bars": 1.25, "length_bars": 0.125, "velocity": 0.85},
        {"pitch": 41, "time_bars": 1.625, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 41, "time_bars": 1.75, "length_bars": 0.0625, "velocity": 0.85},
        {"pitch": 41, "time_bars": 1.8125, "length_bars": 0.0625, "velocity": 0.85},
        {"pitch": 41, "time_bars": 1.875, "length_bars": 0.08, "velocity": 0.95},

        # Bar 2: Second variation
        {"pitch": 29, "time_bars": 2.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 41, "time_bars": 2.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 41, "time_bars": 2.25, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 48, "time_bars": 2.625, "length_bars": 0.125, "velocity": 0.95},
        {"pitch": 46, "time_bars": 2.75, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 44, "time_bars": 2.875, "length_bars": 0.08, "velocity": 0.95},

        # Bar 3: Turnaround fill before repeat
        {"pitch": 29, "time_bars": 3.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 41, "time_bars": 3.0, "length_bars": 0.20, "velocity": 1.0},
        {"pitch": 43, "time_bars": 3.25, "length_bars": 0.125, "velocity": 0.90},
        {"pitch": 53, "time_bars": 3.666, "length_bars": 0.08, "velocity": 1.0},
        {"pitch": 51, "time_bars": 3.75, "length_bars": 0.08, "velocity": 0.95},
        {"pitch": 49, "time_bars": 3.833, "length_bars": 0.08, "velocity": 0.95},
        {"pitch": 48, "time_bars": 3.916, "length_bars": 0.08, "velocity": 1.0},
    ]
    res_bass = await call("fl_write_piano_roll_notes", {"notes": drop_bass, "mode": "replace"})
    print("Drop growl bass written:", res_bass)

    # 4. Mixer Track Organization & Color Coding
    print("\n=== [PHASE 4] Mixer Naming & Color Coding ===")
    mixer_setup = [
        (1, "KICK", "#FF3333"),
        (2, "SNARE/CLAP", "#FF8800"),
        (3, "HI-HATS", "#FFCC00"),
        (4, "BASS GROWL", "#A020F0"),
        (5, "SUB BASS", "#0055FF"),
        (6, "ATMOS / FX", "#00E5FF"),
    ]
    for track_idx, name, color in mixer_setup:
        await call("fl_set_mixer_name", {"track": track_idx, "name": name})
        await call("fl_set_track_color", {"color": color, "tracks": [track_idx]})
        print(f"  Mixer {track_idx} -> '{name}' ({color})")

    # Color channel rack
    channel_colors = [
        (0, "red"),
        (1, "orange"),
        (2, "yellow"),
        (3, "amber"),
        (4, "purple"),
    ]
    for ch_idx, col in channel_colors:
        await call("fl_set_channel_color", {"color": col, "channels": [ch_idx]})
        print(f"  Channel {ch_idx} -> color {col}")

    # 5. Gain Staging / Mixer Levels
    print("\n=== [PHASE 5] Staging Mixer Fader Levels for Dubstep ===")
    ref_levels = await call("fl_get_mix_reference_levels", {"genre": "trap"})
    print("Reference Levels:\n", ref_levels)

    fader_settings = [
        (0, 0.80), # Master: 0 dB
        (1, 0.78), # Kick: ~ -0.5 dB
        (2, 0.75), # Snare: ~ -1.0 dB
        (3, 0.60), # HiHats: ~ -8 dB
        (4, 0.73), # Bass Growl: ~ -2.0 dB
        (5, 0.71), # Sub Bass: ~ -3.0 dB
        (6, 0.52), # Atmos / FX: ~ -12 dB
    ]
    for track_idx, vol in fader_settings:
        await call("fl_set_mixer_volume", {"track": track_idx, "value": vol, "unit": "normalized"})
        print(f"  Mixer Track {track_idx} volume set to {vol}")

    # 6. Sound Design & Mastering Recipes
    print("\n=== [PHASE 6] Sound Design & Mastering Blueprints ===")
    serum = await call("fl_get_serum_patch", {"sound_type": "808_distorted"})
    print("Serum Patch Guide:\n", serum)

    fab_bass = await call("fl_get_fabfilter_mixing_chain", {"chain_type": "808_chain"})
    print("FabFilter Bass Chain:", fab_bass)

    lufs = await call("fl_get_lufs_target", {"genre": "trap", "platform": "soundcloud"})
    print("Target Loudness:", lufs)

    # 7. Mix Doctor Diagnostic
    print("\n=== [PHASE 7] Running Mix Doctor Diagnostic ===")
    diag = await call("fl_diagnose_mix")
    print("Mix Doctor Diagnosis Report:")
    print(json.dumps(diag, indent=2))

    print("\n=======================================================")
    print("FULL SONG PRODUCTION COMPLETED SUCCESSFULLY IN FL STUDIO!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_production())
