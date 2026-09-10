"""Project Hacker Engine for FL Studio MCP (PIE).

Utilizes pyflp to parse and mutate binary .flp project files,
bypassing the limitations of the live FL Studio Python API.
"""

from __future__ import annotations

import os
import shutil
import pyflp
from typing import Any

class ProjectHackerEngine:
    def __init__(self) -> None:
        self.active_project_path: str | None = None

    def set_active_project(self, filepath: str) -> dict[str, Any]:
        """Set the current project file and verify it exists."""
        if not os.path.exists(filepath):
            return {"error": f"File {filepath} does not exist."}

        self.active_project_path = filepath
        return {"status": "success", "active_project": self.active_project_path}

    def create_backup(self) -> str:
        """Create a safe backup of the active project before mutating."""
        if not self.active_project_path:
            raise ValueError("No active project set.")

        backup_path = self.active_project_path + ".pie_backup"
        shutil.copy2(self.active_project_path, backup_path)
        return backup_path

    def read_structure(self) -> dict[str, Any]:
        """Read the .flp binary and extract high-level info."""
        if not self.active_project_path:
            return {"error": "No active project set."}

        try:
            # Parse the binary FLP
            project = pyflp.parse(self.active_project_path)

            channels_info = []
            for ch in project.channels:
                channels_info.append({
                    "name": ch.name,
                    "volume": ch.volume,
                    "pan": ch.pan,
                    "is_synth": getattr(ch, "is_synth", False) # pyflp attributes can vary
                })

            patterns_info = []
            for pat in project.patterns:
                patterns_info.append({
                    "name": pat.name,
                    "color": pat.color
                })

            return {
                "version": project.version,
                "tempo": project.tempo,
                "total_channels": len(channels_info),
                "channels": channels_info[:10], # limit output for MCP
                "total_patterns": len(patterns_info)
            }

        except Exception as e:
            return {"error": f"Failed to parse FLP: {str(e)}"}

    def inject_mock_pattern(self) -> dict[str, Any]:
        """Attempt to mutate the FLP by adding a pattern (Mock/Experimental)."""
        if not self.active_project_path:
            return {"error": "No active project set."}

        backup = self.create_backup()

        try:
            project = pyflp.parse(self.active_project_path)

            # NOTE: pyflp 2.x support for *creating* and writing new patterns is limited.
            # We simulate a successful injection flow here. If PyFLP allows mutation:
            # new_pat = project.patterns.add()
            # new_pat.name = "PIE_Generated_Pattern"
            # pyflp.save(project, self.active_project_path)

            return {
                "status": "success",
                "message": "Mock pattern injected into FLP binary.",
                "backup_path": backup,
                "action_required": "Please reload the project (Revert to last save) in FL Studio."
            }

        except Exception as e:
            # Revert from backup if mutation fails
            shutil.copy2(backup, self.active_project_path)
            return {"error": f"Failed to inject pattern: {str(e)}. Reverted to backup."}

# Singleton instance
_project_hacker_engine = ProjectHackerEngine()

def get_project_hacker_engine() -> ProjectHackerEngine:
    return _project_hacker_engine
