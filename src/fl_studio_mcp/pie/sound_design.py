"""Sound Design Engine for FL Studio MCP (PIE).

Handles Semantic Macros mapping and application of Sound Profiles.
"""

from __future__ import annotations

from typing import Any

class SoundDesignEngine:
    def __init__(self) -> None:
        self.profiles = {}
        self.semantic_keywords = []

    def set_semantic_keywords(self, keywords: list[str]) -> None:
        """Allow the AI to define what keywords constitute a semantic macro."""
        self.semantic_keywords = [k.lower() for k in keywords]

    def add_profile(self, profile_name: str, macro_mapping: dict[str, float]) -> dict[str, Any]:
        """Allow the AI to dynamically create a sonic profile."""
        self.profiles[profile_name.lower()] = macro_mapping
        return {"status": "success", "profile": profile_name}

    def get_semantic_macros(self, plugin_params: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter plugin parameters based on the dynamically set keywords."""
        macros = []
        if not self.semantic_keywords:
            return macros

        for param in plugin_params:
            name = param.get("name", "").lower()
            if any(keyword in name for keyword in self.semantic_keywords):
                macros.append(param)
        return macros

    def get_profile(self, profile_name: str) -> dict[str, float]:
        """Retrieve a specific sound profile by name."""
        return self.profiles.get(profile_name.lower(), {})

    def lint_macros(self, current_macros: dict[str, float], custom_rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Validate if the current combination of macros is safe, based on AI-provided custom rules.

        Args:
            current_macros: Mapping of macro names to values (0.0 to 1.0).
            custom_rules: A list of dicts defining rules. Example:
                          [{"macros": ["warmth", "brightness"], "threshold": 1.6, "warning": "Too harsh"}]
        """
        warnings = []

        for rule in custom_rules:
            macros_to_check = rule.get("macros", [])
            threshold = rule.get("threshold", 1.0)

            # Sum the values of the macros specified in the rule
            total = sum(current_macros.get(m, 0.0) for m in macros_to_check)
            if total > threshold:
                warnings.append(rule.get("warning", "Custom rule threshold exceeded."))

        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }

# Singleton instance
_sound_design_engine = SoundDesignEngine()

def get_sound_design_engine() -> SoundDesignEngine:
    return _sound_design_engine
