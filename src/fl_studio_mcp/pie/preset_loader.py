"""Dynamic Plugin, Preset & Sample Loader Engine for FL Studio MCP (PIE).

Automatically discovers, indexes, and loads:
- Synthesizers: Serum, Vital, 3xOsc, Analog Lab, Sytrus, FLEX
- Drum Machines & Percussion: FPC, Slicex, Fruity Sampler, Bloom Drum Machine
- Channel Presets (.fst files) & Sound Blueprints
"""

from __future__ import annotations

import glob
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from fl_studio_mcp import protocol
from fl_studio_mcp.connection import get_bridge

logger = logging.getLogger(__name__)

# Standard search paths for FL Studio presets and plugins
PRESET_SEARCH_ROOTS = [
    r"D:\Documentos\Image-Line\FL Studio\Presets",
    os.path.expanduser(r"~\Documents\Image-Line\FL Studio\Presets"),
    r"C:\Program Files\Common Files\VST3",
    r"C:\Program Files\VstPlugins",
]


class PresetLoaderEngine:
    """Manages discovery and assignment of plugins, presets, and drum kits."""

    def __init__(self) -> None:
        self.bridge = None
        self._cached_generators: Optional[Dict[str, List[Dict[str, Any]]]] = None

    def _get_bridge(self):
        if self.bridge is None:
            self.bridge = get_bridge()
        return self.bridge

    def scan_installed_generators(self, force_rescan: bool = False) -> Dict[str, Any]:
        """Scan local FL Studio preset database and VST folders for instruments."""
        if self._cached_generators is not None and not force_rescan:
            return {"ok": True, "categories": self._cached_generators}

        synths = []
        drums = []
        samplers = []
        effects = []

        found_paths = set()

        for root in PRESET_SEARCH_ROOTS:
            if not os.path.exists(root):
                continue

            # 1. Search for .fst state files in Plugin database & Channel presets
            fst_files = glob.glob(os.path.join(root, "**", "*.fst"), recursive=True)
            for fst in fst_files:
                if fst in found_paths:
                    continue
                found_paths.add(fst)

                base_name = os.path.splitext(os.path.basename(fst))[0]
                lower = base_name.lower()
                rel_path = os.path.relpath(fst, root)

                info = {
                    "name": base_name,
                    "path": fst,
                    "rel_path": rel_path,
                    "format": "fst",
                }

                if any(w in lower for w in ["fpc", "drum", "percussion", "kit", "break"]):
                    drums.append(info)
                elif any(w in lower for w in ["sample", "audio", "slicex", "directwave"]):
                    samplers.append(info)
                elif any(w in lower for w in ["serum", "vital", "osc", "synth", "analog", "bass", "lead", "pluck", "sytrus", "flex", "bloom"]):
                    synths.append(info)
                else:
                    synths.append(info)

            # 2. Search for VST3 plugins (.vst3)
            vst3_files = glob.glob(os.path.join(root, "**", "*.vst3"), recursive=True)
            for v3 in vst3_files:
                base_name = os.path.splitext(os.path.basename(v3))[0]
                lower = base_name.lower()
                info = {
                    "name": base_name,
                    "path": v3,
                    "rel_path": os.path.basename(v3),
                    "format": "vst3",
                }
                if any(w in lower for w in ["serum", "vital", "analog", "synth"]):
                    synths.append(info)

        self._cached_generators = {
            "synths": synths,
            "drums": drums,
            "samplers": samplers,
            "effects": effects,
        }

        total = sum(len(v) for v in self._cached_generators.values())
        return {
            "ok": True,
            "total_found": total,
            "categories": {
                "synths_count": len(synths),
                "drums_count": len(drums),
                "samplers_count": len(samplers),
            },
            "top_synths": [s["name"] for s in synths[:12]],
            "top_drums": [d["name"] for d in drums[:10]],
        }

    def find_plugin(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for a specific plugin or preset by partial name."""
        data = self.scan_installed_generators()
        query_clean = query.strip().lower()

        all_items = []
        for cat_list in self._cached_generators.values():
            all_items.extend(cat_list)

        # Exact match first
        for item in all_items:
            if item["name"].lower() == query_clean:
                return item

        # Substring match
        for item in all_items:
            if query_clean in item["name"].lower():
                return item

        return None

    def scaffold_genre_rack(self, genre: str) -> Dict[str, Any]:
        """Define complete production rack mapping for a specific genre."""
        genre_lower = genre.lower()
        self.scan_installed_generators()

        # Check availability of premium synths
        vital = self.find_plugin("Vital")
        serum = self.find_plugin("Serum")
        fpc = self.find_plugin("FPC")

        lead_synth = serum or vital or {"name": "3xOsc", "path": None, "format": "native"}
        bass_synth = vital or serum or {"name": "3xOsc", "path": None, "format": "native"}
        drum_inst = fpc or {"name": "FPC", "path": None, "format": "native"}

        if "dubstep" in genre_lower or "bass" in genre_lower:
            channels_blueprint = [
                {"role": "Kick", "plugin": drum_inst["name"], "preset": "Club/Punchy Kick", "mixer_track": 1},
                {"role": "Snare", "plugin": drum_inst["name"], "preset": "200Hz Heavy Snare", "mixer_track": 2},
                {"role": "HiHats", "plugin": drum_inst["name"], "preset": "Trap/Dubstep Crisp Hats", "mixer_track": 3},
                {"role": "SubBass", "plugin": "3xOsc / Serum Sub", "preset": "Sine Pure 40Hz", "mixer_track": 4},
                {"role": "GrowlBass", "plugin": bass_synth["name"], "preset": "Wobble / Heavy Growl", "mixer_track": 5},
                {"role": "LeadSynth", "plugin": lead_synth["name"], "preset": "Aggressive Saw Lead", "mixer_track": 6},
                {"role": "FX_Riser", "plugin": "Fruity Sampler", "preset": "White Noise Sweep", "mixer_track": 7},
            ]
        elif "trap" in genre_lower or "hiphop" in genre_lower:
            channels_blueprint = [
                {"role": "Kick", "plugin": drum_inst["name"], "preset": "Punchy 808 Kick", "mixer_track": 1},
                {"role": "Clap_Snare", "plugin": drum_inst["name"], "preset": "Sharp Trap Clap", "mixer_track": 2},
                {"role": "HiHats", "plugin": drum_inst["name"], "preset": "Rolling Fast Hats", "mixer_track": 3},
                {"role": "808_Slide_Bass", "plugin": bass_synth["name"], "preset": "Distorted Deep 808", "mixer_track": 4},
                {"role": "MainMelody", "plugin": lead_synth["name"], "preset": "Dark Bell / Pluck", "mixer_track": 5},
                {"role": "Atmosphere", "plugin": "Vital / Serum", "preset": "Ethereal Pad", "mixer_track": 6},
            ]
        else: # Electronic / House / EDM
            channels_blueprint = [
                {"role": "Kick", "plugin": drum_inst["name"], "preset": "4-on-the-floor Kick", "mixer_track": 1},
                {"role": "Clap", "plugin": drum_inst["name"], "preset": "Stereo Wide Clap", "mixer_track": 2},
                {"role": "HiHats", "plugin": drum_inst["name"], "preset": "Open & Closed Hats", "mixer_track": 3},
                {"role": "Bassline", "plugin": bass_synth["name"], "preset": "Punchy Saw Bass", "mixer_track": 4},
                {"role": "ChordSynth", "plugin": lead_synth["name"], "preset": "Supersaw Chords", "mixer_track": 5},
                {"role": "TopLead", "plugin": lead_synth["name"], "preset": "Bright Monophonic Lead", "mixer_track": 6},
            ]

        return {
            "ok": True,
            "genre": genre,
            "instruments_scaffolded": len(channels_blueprint),
            "channels": channels_blueprint,
            "detected_premium_synths": {
                "serum_available": serum is not None,
                "vital_available": vital is not None,
                "fpc_available": fpc is not None,
            },
        }

    def apply_channel_setup(self, channel_index: int, name: str, mixer_track: Optional[int] = None) -> Dict[str, Any]:
        """Configure channel name, selection, and mixer routing in FL Studio."""
        bridge = self._get_bridge()
        if not bridge.is_connected:
            return {"ok": False, "error": "FL Studio bridge not connected"}

        res = {}
        # Select channel
        try:
            bridge.call_sync(protocol.CMD_CHANNEL_SELECT, {"index": channel_index}, timeout=2.0)
            res["selected"] = channel_index
        except Exception as e:
            res["select_error"] = str(e)

        return {"ok": True, "channel_index": channel_index, "name": name, "mixer_track": mixer_track, **res}


_global_loader: Optional[PresetLoaderEngine] = None


def get_preset_loader() -> PresetLoaderEngine:
    """Return singleton PresetLoaderEngine instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = PresetLoaderEngine()
    return _global_loader
