"""Default filesystem locations for packs root and manifest cache with smart auto-detection."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

__all__ = ["default_packs_root", "default_manifest_path", "find_all_candidate_pack_roots"]


def _get_windows_registry_paths() -> List[Path]:
    """Query Windows registry for Image-Line installation and shared data directories."""
    paths: List[Path] = []
    if sys.platform != "win32":
        return paths

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Image-Line\Shared\Paths") as key:
            for val_name in ("Install path", "Shared data"):
                try:
                    val, _ = winreg.QueryValueEx(key, val_name)
                    if val:
                        p = Path(val)
                        if val_name == "Install path":
                            cand = p / "Data" / "Patches" / "Packs"
                            if cand.exists() and cand not in paths:
                                paths.append(cand)
                        elif val_name == "Shared data":
                            for sub in (p / "FL Studio" / "Sample Pack" / "Packs", p / "Loops", p / "Packs"):
                                if sub.exists() and sub not in paths:
                                    paths.append(sub)
                except FileNotFoundError:
                    pass
    except Exception:
        pass
    return paths


def find_all_candidate_pack_roots() -> List[Path]:
    """Return an ordered list of all detected or potential sample pack root directories."""
    candidates: List[Path] = []

    # 1. Environment variable override
    env = os.environ.get("FL_MCP_PACKS_ROOT")
    if env:
        candidates.append(Path(env))

    # 2. Windows registry paths
    candidates.extend(_get_windows_registry_paths())

    home = Path(os.environ.get("HOME", str(Path.home())))

    if sys.platform == "win32":
        # 3. Standard Windows locations across common drives
        for drive in ("C", "D", "E"):
            for subpath in (
                f"{drive}:/Program Files/Image-Line/FL Studio 2025/Data/Patches/Packs",
                f"{drive}:/Program Files/Image-Line/FL Studio 2024/Data/Patches/Packs",
                f"{drive}:/Program Files/Image-Line/FL Studio 21/Data/Patches/Packs",
                f"{drive}:/Program Files/Image-Line/FL Studio 20/Data/Patches/Packs",
                f"{drive}:/Program Files (x86)/Image-Line/FL Studio 2024/Data/Patches/Packs",
                f"{drive}:/Programs/FL/Data/Patches/Packs",
            ):
                cand = Path(subpath)
                if cand.exists() and cand not in candidates:
                    candidates.append(cand)

        # Standard Documents location
        doc_pack = home / "Documents" / "Image-Line" / "FL Studio" / "Sample Pack" / "Packs"
        if doc_pack not in candidates:
            candidates.append(doc_pack)

    elif sys.platform == "darwin":
        # macOS applications and user folders
        for subpath in (
            "/Applications/FL Studio 2024.app/Contents/Resources/FL/Data/Patches/Packs",
            "/Applications/FL Studio 2025.app/Contents/Resources/FL/Data/Patches/Packs",
            "/Applications/FL Studio 21.app/Contents/Resources/FL/Data/Patches/Packs",
            "/Applications/FL Studio.app/Contents/Resources/FL/Data/Patches/Packs",
        ):
            cand = Path(subpath)
            if cand.exists() and cand not in candidates:
                candidates.append(cand)

        doc_pack = home / "Documents" / "Image-Line" / "FL Studio" / "Sample Pack" / "Packs"
        if doc_pack not in candidates:
            candidates.append(doc_pack)

    elif sys.platform == "linux":
        linux_cand = home / ".flstudio_prefix" / "drive_c" / "Program Files" / "Image-Line" / "FL Studio 2024" / "Data" / "Patches" / "Packs"
        candidates.append(linux_cand)

    return candidates


def default_packs_root() -> Path:
    """Return the best available sample packs root directory."""
    env = os.environ.get("FL_MCP_PACKS_ROOT")
    if env:
        return Path(env)

    # Return the first candidate that actually exists on disk
    for cand in find_all_candidate_pack_roots():
        if cand.exists():
            return cand

    home = Path(os.environ.get("HOME", str(Path.home())))
    if sys.platform == "linux":
        return home / ".flstudio_prefix" / "drive_c" / "Program Files" / "Image-Line" / "FL Studio 2024" / "Data" / "Patches" / "Packs"

    # Default fallback
    return home / "Documents" / "Image-Line" / "FL Studio" / "Sample Pack" / "Packs"


def default_manifest_path() -> Path:
    env = os.environ.get("FL_MCP_MANIFEST_PATH")
    if env:
        return Path(env)
    home = Path(os.environ.get("HOME", str(Path.home())))
    return home / ".fl_mcp" / "library_index" / "manifest.parquet"
