"""Sound Design Engine for FL Studio MCP (PIE).

Handles Semantic Macros mapping and application of Sound Profiles.
"""

from __future__ import annotations

from typing import Any

class SoundDesignEngine:
    def __init__(self) -> None:
        # Pre-defined sound profiles that map to semantic macro values (0.0 to 1.0)
        self.profiles = {
            "aggressive_reece_bass": {
                "brightness": 0.8,
                "warmth": 0.9,
                "movement": 0.6,
                "punch": 0.3,
                "space": 0.1
            },
            "pluck_house_bass": {
                "brightness": 0.4,
                "warmth": 0.2,
                "movement": 0.0,
                "punch": 1.0,
                "space": 0.1
            },
            "ethereal_lead": {
                "brightness": 0.6,
                "warmth": 0.3,
                "movement": 0.8,
                "punch": 0.1,
                "space": 0.9
            }
        }

        # Expected semantic macro names
        self.semantic_keywords = ["brightness", "warmth", "movement", "punch", "space"]

    def get_semantic_macros(self, plugin_params: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter plugin parameters to find those that match semantic macro keywords."""
        macros = []
        for param in plugin_params:
            name = param.get("name", "").lower()
            if any(keyword in name for keyword in self.semantic_keywords):
                macros.append(param)
        return macros

    def get_profile(self, profile_name: str) -> dict[str, float]:
        """Retrieve a specific sound profile by name."""
        return self.profiles.get(profile_name.lower(), {})

    def lint_macros(self, current_macros: dict[str, float]) -> dict[str, Any]:
        """Validate if the current combination of macros is sonically safe."""
        warnings = []

        warmth = current_macros.get("warmth", 0.0)
        brightness = current_macros.get("brightness", 0.0)
        space = current_macros.get("space", 0.0)

        if warmth > 0.8 and brightness > 0.8:
            warnings.append("High warmth and brightness might cause harsh clipping and aliasing.")

        if space > 0.8:
            warnings.append("High space (reverb/delay) might wash out the mix and cause phase issues.")

        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }

# Singleton instance
_sound_design_engine = SoundDesignEngine()

def get_sound_design_engine() -> SoundDesignEngine:
    return _sound_design_engine
