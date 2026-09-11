"""Generate and export a complete multi-track SMF Type 1 MIDI file for the Zomboy track.
Allows instant drag-and-drop into FL Studio's playlist.
"""

import os
from fl_studio_mcp.music.midi_export import write_midi

def generate_midi():
    export_dir = r"F:\Dev\fl-studio-mcp-full-song\exports"
    os.makedirs(export_dir, exist_ok=True)
    out_path = os.path.join(export_dir, "Zomboy_Mind_Control_140BPM.mid")

    # 1. Kicks (Channel 9 GM Drums or direct)
    # Intro: Bars 1-16 (no kick)
    # Build: Bars 17-24 (subtle quarter kicks bars 17-20)
    # Drop 1: Bars 25-40 (heavy halftime)
    # Breakdown: Bars 41-48
    # Drop 2: Bars 49-64
    kick_notes = []
    # Build kicks (quarter notes bars 16-20)
    for b in range(16, 20):
        for beat in range(4):
            kick_notes.append({"pitch": 36, "start_bars": b + beat * 0.25, "length_bars": 0.15, "velocity": 0.75})
    # Drop 1 (Bars 24-40) - Halftime Dubstep
    for b in range(24, 40):
        kick_notes.append({"pitch": 36, "start_bars": float(b), "length_bars": 0.20, "velocity": 1.0})
        if b % 2 == 1:
            kick_notes.append({"pitch": 36, "start_bars": b + 0.6875, "length_bars": 0.15, "velocity": 0.90})
        if b % 4 == 3:
            kick_notes.append({"pitch": 36, "start_bars": b + 0.875, "length_bars": 0.125, "velocity": 0.95})
    # Drop 2 (Bars 48-64)
    for b in range(48, 64):
        kick_notes.append({"pitch": 36, "start_bars": float(b), "length_bars": 0.20, "velocity": 1.0})
        if b % 2 == 1:
            kick_notes.append({"pitch": 36, "start_bars": b + 0.6875, "length_bars": 0.15, "velocity": 0.95})
        if b % 2 == 0:
            kick_notes.append({"pitch": 36, "start_bars": b + 0.4375, "length_bars": 0.10, "velocity": 0.85})

    # 2. Snares / Claps
    snare_notes = []
    # Build-up snare roll (Bars 16-24)
    for b in range(16, 18): # Quarters
        for beat in range(4):
            t = b + beat * 0.25
            v = 0.40 + ((t - 16) / 8.0) * 0.35
            snare_notes.append({"pitch": 38, "start_bars": t, "length_bars": 0.15, "velocity": v})
    for b in range(18, 20): # 8ths
        for eighth in range(8):
            t = b + eighth * 0.125
            v = 0.45 + ((t - 16) / 8.0) * 0.40
            snare_notes.append({"pitch": 38, "start_bars": t, "length_bars": 0.08, "velocity": v})
    for b in range(20, 22): # 16ths
        for sixteenth in range(16):
            t = b + sixteenth * 0.0625
            v = 0.50 + ((t - 16) / 8.0) * 0.45
            snare_notes.append({"pitch": 38, "start_bars": t, "length_bars": 0.04, "velocity": v})
    for thirtysecond in range(32): # Bar 22
        t = 22.0 + thirtysecond * 0.03125
        snare_notes.append({"pitch": 38, "start_bars": t, "length_bars": 0.02, "velocity": 0.95})
    for thirtysecond in range(24): # Bar 23 (Silence on beat 4 for drop punchline!)
        t = 23.0 + thirtysecond * 0.03125
        snare_notes.append({"pitch": 38, "start_bars": t, "length_bars": 0.02, "velocity": 1.0})

    # Drop 1 Snares (Bars 24-40) -> Beat 3 (0.50 bar)
    for b in range(24, 40):
        snare_notes.append({"pitch": 38, "start_bars": b + 0.50, "length_bars": 0.25, "velocity": 1.0})
    # Drop 2 Snares (Bars 48-64)
    for b in range(48, 64):
        snare_notes.append({"pitch": 38, "start_bars": b + 0.50, "length_bars": 0.25, "velocity": 1.0})

    # 3. Hi-Hats
    hat_notes = []
    # Drop 1 (Bars 24-40) - 16th hats
    for b in range(24, 40):
        for i in range(16):
            v = 0.80 if i % 2 == 1 else 0.45
            hat_notes.append({"pitch": 42, "start_bars": b + i * 0.0625, "length_bars": 0.04, "velocity": v})
    # Drop 2 (Bars 48-64) - Triplets & rolls
    for b in range(48, 64):
        for i in range(24): # 24th triplets
            v = 0.85 if i % 3 == 0 else 0.50
            hat_notes.append({"pitch": 42, "start_bars": b + i * (1.0 / 24.0), "length_bars": 0.03, "velocity": v})

    # 4. Bass Growl & Screech (F Phrygian: F1=29, F2=41, G2=43, Ab2=44, Bb2=46, C3=48)
    bass_notes = []
    def add_drop_riff(start_bar, end_bar):
        for b in range(start_bar, end_bar, 4):
            # Bar 0
            bass_notes.append({"pitch": 29, "start_bars": b + 0.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 41, "start_bars": b + 0.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 41, "start_bars": b + 0.25, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 41, "start_bars": b + 0.375, "length_bars": 0.0625, "velocity": 0.85})
            bass_notes.append({"pitch": 44, "start_bars": b + 0.625, "length_bars": 0.125, "velocity": 0.95})
            bass_notes.append({"pitch": 43, "start_bars": b + 0.75, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 41, "start_bars": b + 0.875, "length_bars": 0.08, "velocity": 0.95})
            # Bar 1
            bass_notes.append({"pitch": 29, "start_bars": b + 1.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 46, "start_bars": b + 1.125, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 44, "start_bars": b + 1.25, "length_bars": 0.125, "velocity": 0.85})
            bass_notes.append({"pitch": 41, "start_bars": b + 1.625, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 41, "start_bars": b + 1.75, "length_bars": 0.0625, "velocity": 0.85})
            bass_notes.append({"pitch": 41, "start_bars": b + 1.8125, "length_bars": 0.0625, "velocity": 0.85})
            bass_notes.append({"pitch": 41, "start_bars": b + 1.875, "length_bars": 0.08, "velocity": 0.95})
            # Bar 2
            bass_notes.append({"pitch": 29, "start_bars": b + 2.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 41, "start_bars": b + 2.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 41, "start_bars": b + 2.25, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 48, "start_bars": b + 2.625, "length_bars": 0.125, "velocity": 0.95})
            bass_notes.append({"pitch": 46, "start_bars": b + 2.75, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 44, "start_bars": b + 2.875, "length_bars": 0.08, "velocity": 0.95})
            # Bar 3
            bass_notes.append({"pitch": 29, "start_bars": b + 3.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 41, "start_bars": b + 3.0, "length_bars": 0.20, "velocity": 1.0})
            bass_notes.append({"pitch": 43, "start_bars": b + 3.25, "length_bars": 0.125, "velocity": 0.90})
            bass_notes.append({"pitch": 53, "start_bars": b + 3.666, "length_bars": 0.08, "velocity": 1.0})
            bass_notes.append({"pitch": 51, "start_bars": b + 3.75, "length_bars": 0.08, "velocity": 0.95})
            bass_notes.append({"pitch": 49, "start_bars": b + 3.833, "length_bars": 0.08, "velocity": 0.95})
            bass_notes.append({"pitch": 48, "start_bars": b + 3.916, "length_bars": 0.08, "velocity": 1.0})

    add_drop_riff(24, 40) # Drop 1
    add_drop_riff(48, 64) # Drop 2

    # 5. Intro & Breakdown Atmosphere Chords (F3=53, Ab3=56, C4=60; Db3=49, F3=53, Ab3=56)
    pad_notes = []
    # Intro (Bars 0-16)
    for b in range(0, 16, 4):
        pad_notes.append({"pitch": 53, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.70})
        pad_notes.append({"pitch": 56, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 60, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 49, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.70})
        pad_notes.append({"pitch": 53, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 56, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.65})
    # Breakdown (Bars 40-48)
    for b in range(40, 48, 4):
        pad_notes.append({"pitch": 53, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.70})
        pad_notes.append({"pitch": 56, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 60, "start_bars": b + 0.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 49, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.70})
        pad_notes.append({"pitch": 53, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.65})
        pad_notes.append({"pitch": 56, "start_bars": b + 2.0, "length_bars": 2.0, "velocity": 0.65})

    tracks = [
        {"name": "KICK", "channel": 0, "notes": kick_notes},
        {"name": "SNARE_CLAP", "channel": 1, "notes": snare_notes},
        {"name": "HI_HATS", "channel": 2, "notes": hat_notes},
        {"name": "BASS_GROWL", "channel": 3, "notes": bass_notes},
        {"name": "ATMOS_PAD", "channel": 4, "notes": pad_notes},
    ]

    write_midi(tracks, 140.0, out_path)
    print("SUCCESS: MIDI file written to:", out_path)
    print("Size bytes:", os.path.getsize(out_path))

if __name__ == "__main__":
    generate_midi()
