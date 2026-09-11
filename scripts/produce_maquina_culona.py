"""Producer Script for Ralphie Choo & Mura Masa style song: 'MÁQUINA CULONA'.

Musical DNA:
- Style: Avant-garde Flamenco / Latin Hyperpop / Experimental Trap (Ralphie Choo - SUPERNOVA)
- BPM: 100.0 BPM
- Key: F Minor (Fm9 - Bbm7 - Cm7 - Eb9/C7alt) with Andalusian Phrygian tension
- Tracks: 7 stems (Palmas, Kick, Snare, 808 Slides, Flamenco Guitar, Vocal Chops, Ear Candy)
- Arrangement: 32 bars (Intro, Verse, Pre-Drop, Drop/Beat Switch, Outro)
- Delivery: Full multi-track MIDI compilation, live timeline markers, and automated hands-free Playlist arrangement.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict, List

# Add src to Python path
sys.path.insert(0, os.path.abspath("src"))

from fl_studio_mcp.pie.auto_arranger import get_playlist_arranger
from fl_studio_mcp.pie.modulation_engine import get_modulation_engine
from fl_studio_mcp.pie.preset_loader import get_preset_loader
from fl_studio_mcp.music.midi_export import write_midi


def compose_maquina_culona() -> Dict[str, Any]:
    print("=" * 65)
    print("  COMPOSING 'MÁQUINA CULONA' - RALPHIE CHOO & MURA MASA STYLE")
    print("  100 BPM | F Minor | Flamenco-Trap / Avant-Garde Latin Pop")
    print("=" * 65)

    bpm = 100.0
    total_bars = 32
    mod = get_modulation_engine()

    # -------------------------------------------------------------------------
    # 1. TRACK 1: Flamenco Palmas & Percussion (Bulería / Tangos syncopations)
    # -------------------------------------------------------------------------
    palmas_notes: List[Dict[str, Any]] = []
    # Syncopated palmas rhythm pattern across bars (Bulería accentuation in 4/4)
    # Accents at 0.0 (vel 0.7), 0.375 (vel 0.9), 0.625 (vel 0.95), 0.875 (vel 0.85)
    palma_pattern = [
        (0.00, 0.12, 0.65),
        (0.25, 0.12, 0.70),
        (0.375, 0.12, 0.92),  # Accent
        (0.50, 0.12, 0.75),
        (0.625, 0.12, 0.96),  # Accent
        (0.75, 0.12, 0.80),
        (0.875, 0.12, 0.90),  # Syncopated snap
    ]

    for bar in range(total_bars):
        # Intro (0-4), Verse (4-12), Drop (16-28)
        if (0 <= bar < 12) or (16 <= bar < 28):
            # Bar 15.5 to 16 is silence for dramatic drop-out
            if bar == 15 and bar >= 15.5:
                continue
            for off_b, dur_b, vel in palma_pattern:
                pitch = 39 if off_b in (0.375, 0.625) else 37  # Accent claps vs standard claps
                palmas_notes.append({
                    "pitch": pitch,
                    "start_bars": round(bar + off_b, 4),
                    "length_bars": dur_b,
                    "velocity": vel,
                })

    # -------------------------------------------------------------------------
    # 2. TRACK 2: Kick Tight (Trap-Flamenco low end punch)
    # -------------------------------------------------------------------------
    kick_notes: List[Dict[str, Any]] = []
    # Verse kick pattern: 1, 2.5, 3.75
    verse_kick = [(0.0, 0.20, 0.95), (0.625, 0.20, 0.88), (0.875, 0.15, 0.82)]
    # Drop kick pattern: more driving with double kicks
    drop_kick = [
        (0.0, 0.20, 1.0),
        (0.375, 0.15, 0.85),
        (0.50, 0.20, 0.95),
        (0.75, 0.15, 0.90),
        (0.875, 0.15, 0.85),
    ]

    for bar in range(total_bars):
        if 4 <= bar < 12:  # Verse
            for off_b, dur_b, vel in verse_kick:
                kick_notes.append({"pitch": 36, "start_bars": round(bar + off_b, 4), "length_bars": dur_b, "velocity": vel})
        elif 16 <= bar < 28:  # Drop
            for off_b, dur_b, vel in drop_kick:
                kick_notes.append({"pitch": 36, "start_bars": round(bar + off_b, 4), "length_bars": dur_b, "velocity": vel})

    # -------------------------------------------------------------------------
    # 3. TRACK 3: Snare & Snap (Crisp acoustic rim layered with handclap)
    # -------------------------------------------------------------------------
    snare_notes: List[Dict[str, Any]] = []
    for bar in range(total_bars):
        if 4 <= bar < 12 or 16 <= bar < 28:
            # Snare on 2 and 4 (0.25 and 0.75 of bar in whole bar terms: beat 2 is 0.25, beat 4 is 0.75)
            snare_notes.append({"pitch": 38, "start_bars": round(bar + 0.25, 4), "length_bars": 0.20, "velocity": 0.90})
            snare_notes.append({"pitch": 38, "start_bars": round(bar + 0.75, 4), "length_bars": 0.20, "velocity": 0.95})
            # Occasional ghost rim on beat 4.5
            if bar % 2 == 1:
                snare_notes.append({"pitch": 40, "start_bars": round(bar + 0.875, 4), "length_bars": 0.10, "velocity": 0.65})
        elif 12 <= bar < 16:  # Pre-drop snare roll build-up
            # Accelerating roll
            step = 0.125 if bar < 14 else 0.0625
            curr = 0.0
            while curr < 1.0:
                if bar == 15 and curr >= 0.75:
                    break  # Silence last beat of bar 15
                snare_notes.append({
                    "pitch": 38,
                    "start_bars": round(bar + curr, 4),
                    "length_bars": round(step * 0.8, 4),
                    "velocity": round(0.5 + (bar - 12 + curr) * 0.12, 2),
                })
                curr += step

    # -------------------------------------------------------------------------
    # 4. TRACK 4: 808 Slide Bass (Heavy sub with authentic glides)
    # -------------------------------------------------------------------------
    bass_notes: List[Dict[str, Any]] = []
    # 4-bar progression root notes: Fm (F1=29), Bbm (Bb1=34), Cm (C2=36), Eb/C7 (Eb2=39, C2=36)
    for bar in range(total_bars):
        if (4 <= bar < 12) or (16 <= bar < 28):
            prog_step = bar % 4
            if prog_step == 0:  # Fm
                # Root F1 with glide up to F2 (41) at end of bar
                bass_notes.extend(mod.generate_808_slides(
                    root_pitch=29, slide_pitch=41, start_bar=bar, root_length_bars=1.0, slide_length_bars=0.25, velocity=0.9
                ))
            elif prog_step == 1:  # Bbm
                # Root Bb1 with glide down to G1 (31)
                bass_notes.extend(mod.generate_808_slides(
                    root_pitch=34, slide_pitch=31, start_bar=bar, root_length_bars=1.0, slide_length_bars=0.25, velocity=0.88
                ))
            elif prog_step == 2:  # Cm
                # Root C2 with glide up to Eb2 (39)
                bass_notes.extend(mod.generate_808_slides(
                    root_pitch=36, slide_pitch=39, start_bar=bar, root_length_bars=1.0, slide_length_bars=0.25, velocity=0.92
                ))
            elif prog_step == 3:  # Eb / C7alt
                # In Drop: High aggressive glide to Ab2 (44)
                target_slide = 44 if bar >= 16 else 36
                bass_notes.extend(mod.generate_808_slides(
                    root_pitch=39, slide_pitch=target_slide, start_bar=bar, root_length_bars=0.85, slide_length_bars=0.30, velocity=0.95
                ))

    # -------------------------------------------------------------------------
    # 5. TRACK 5: Nylon Flamenco Guitar (Arpeggios & Phrygian flourishes)
    # -------------------------------------------------------------------------
    guitar_notes: List[Dict[str, Any]] = []
    # Chords: Fm9, Bbm7, Cm7, C7b9
    chords_voicing = [
        # Fm9: F3(53), Ab3(56), C4(60), Eb4(63), G4(67)
        [53, 56, 60, 63, 67],
        # Bbm7: Bb2(46), F3(53), Ab3(56), Db4(61), C4(60)
        [46, 53, 56, 61, 60],
        # Cm7: C3(48), G3(55), Bb3(58), Eb4(63), D4(62)
        [48, 55, 58, 63, 62],
        # C7b9 / Ebm: C3(48), E3(52), G3(55), Bb3(58), Db4(61)
        [48, 52, 55, 58, 61],
    ]

    for bar in range(total_bars):
        # Active in Intro (0-4), Verse (4-12), Pre-drop (12-15), Drop (16-28), Outro (28-32)
        if bar == 15:  # Pre-drop silence
            continue
        chord = chords_voicing[bar % 4]
        # Arpeggiated flamenco pattern: Bass note on 0, then 16th-note plucks with velocity strum
        guitar_notes.append({"pitch": chord[0], "start_bars": bar + 0.0, "length_bars": 0.45, "velocity": 0.85})
        guitar_notes.append({"pitch": chord[1], "start_bars": bar + 0.125, "length_bars": 0.35, "velocity": 0.72})
        guitar_notes.append({"pitch": chord[2], "start_bars": bar + 0.25, "length_bars": 0.35, "velocity": 0.78})
        guitar_notes.append({"pitch": chord[3], "start_bars": bar + 0.375, "length_bars": 0.30, "velocity": 0.82})
        guitar_notes.append({"pitch": chord[4], "start_bars": bar + 0.50, "length_bars": 0.35, "velocity": 0.75})
        # Flamenco ornament: grace note pull-off on beat 3.5
        ornament = chord[4] + 1
        guitar_notes.append({"pitch": ornament, "start_bars": bar + 0.625, "length_bars": 0.10, "velocity": 0.88})
        guitar_notes.append({"pitch": chord[4], "start_bars": bar + 0.6875, "length_bars": 0.25, "velocity": 0.80})
        guitar_notes.append({"pitch": chord[1], "start_bars": bar + 0.8125, "length_bars": 0.18, "velocity": 0.70})

    # -------------------------------------------------------------------------
    # 6. TRACK 6: Vocal Chop Lead (Ralphie Choo melodic formant stutters)
    # -------------------------------------------------------------------------
    vocal_notes: List[Dict[str, Any]] = []
    # Catchy hook motif in F minor: F4(65), Ab4(68), G4(67), F4(65), C5(72), Bb4(70)
    hook_melody = [
        (0.00, 65, 0.15, 0.85),
        (0.1875, 68, 0.15, 0.90),
        (0.375, 67, 0.12, 0.80),
        (0.50, 65, 0.25, 0.88),
        (0.75, 72, 0.18, 0.95),
        (0.875, 70, 0.12, 0.85),
    ]

    for bar in range(total_bars):
        # Vocal chops active in Verse (8-12) and Drop (16-28)
        if 8 <= bar < 12 or 16 <= bar < 28:
            for off_b, pitch, dur, vel in hook_melody:
                # Add octave variation in Drop
                p = pitch + 12 if (bar >= 16 and off_b == 0.75) else pitch
                vocal_notes.append({
                    "pitch": p,
                    "start_bars": round(bar + off_b, 4),
                    "length_bars": dur,
                    "velocity": vel,
                })

    # Vocal formant CC 74 (Filter Cutoff) modulation
    vocal_cc74 = mod.generate_lfo_curve(shape="sine", bars=total_bars, rate_hz_or_subdiv=1.0, min_val=40, max_val=115)

    # -------------------------------------------------------------------------
    # 7. TRACK 7: Ear Candy & Transitions (Risers, dropouts, vinyl clicks)
    # -------------------------------------------------------------------------
    riser_package = mod.generate_tension_riser(start_bar=12.0, duration_bars=3.5)

    # -------------------------------------------------------------------------
    # MULTI-TRACK COMPILATION
    # -------------------------------------------------------------------------
    tracks = [
        {
            "name": "Flamenco_Palmas",
            "channel": 0,
            "notes": palmas_notes,
        },
        {
            "name": "Kick_Tight",
            "channel": 1,
            "notes": kick_notes,
        },
        {
            "name": "Snare_Snap",
            "channel": 2,
            "notes": snare_notes,
        },
        {
            "name": "808_Slide_Bass",
            "channel": 3,
            "notes": bass_notes,
        },
        {
            "name": "Nylon_Guitar",
            "channel": 4,
            "notes": guitar_notes,
        },
        {
            "name": "Vocal_Chops",
            "channel": 5,
            "notes": vocal_notes,
            "filter_sweeps": vocal_cc74[:len(vocal_notes) * 2],
        },
        {
            "name": "Transitions_FX",
            "channel": 6,
            "notes": [
                # Reverse cymbal sweep into Verse
                {"pitch": 55, "start_bars": 3.0, "length_bars": 1.0, "velocity": 0.8},
                # Impact on Drop downbeat
                {"pitch": 36, "start_bars": 16.0, "length_bars": 2.0, "velocity": 1.0},
            ],
            "pitch_bends": riser_package["pitch_bends"],
            "filter_sweeps": riser_package["filter_cutoff_cc74"],
        }
    ]

    total_notes = sum(len(t["notes"]) for t in tracks)
    print(f"\nSuccessfully generated 7 tracks with {total_notes} total notes across 32 bars.")
    for t in tracks:
        print(f"  - [{t['name']:18s}] : {len(t['notes']):4d} notes | ch {t['channel']}")

    # Save Standard MIDI File
    os.makedirs("exports", exist_ok=True)
    out_midi = os.path.abspath(r"exports\maquina_culona_style_100bpm.mid")
    write_midi(tracks, bpm=bpm, path=out_midi)
    print(f"\nExported Multi-Track MIDI to:\n  {out_midi}")

    # -------------------------------------------------------------------------
    # AUTO-ARRANGER: PLAYLIST TIMELINE LAYOUT
    # -------------------------------------------------------------------------
    sections = [
        {"name": "INTRO", "start_bar": 0.0},
        {"name": "VERSE_1", "start_bar": 4.0},
        {"name": "PRE_DROP", "start_bar": 12.0},
        {"name": "DROP_SWITCH", "start_bar": 16.0},
        {"name": "OUTRO", "start_bar": 28.0},
    ]

    print("\nExecuting Hands-Free Auto-Arranger in FL Studio...")
    arranger = get_playlist_arranger()
    arrange_res = arranger.auto_arrange_song(
        midi_path=out_midi,
        sections=sections,
        bpm=bpm,
    )

    print(f"Arrangement Status: {arrange_res.get('ok')}")
    print(f"Arrangement Summary: {arrange_res.get('summary')}")
    if arrange_res.get("midi_import", {}).get("ok"):
        print("  -> FL Studio imported all 7 tracks and arranged them across the Playlist.")

    print("\n" + "=" * 65)
    print("  'MÁQUINA CULONA' PRODUCTION SUCCESSFULLY EXECUTED!")
    print("=" * 65)

    return {
        "ok": True,
        "midi_path": out_midi,
        "tracks": len(tracks),
        "total_notes": total_notes,
        "bpm": bpm,
        "sections": sections,
        "arrange_result": arrange_res,
    }


if __name__ == "__main__":
    compose_maquina_culona()
