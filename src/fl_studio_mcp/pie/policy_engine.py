"""Policy Engine for FL Studio MCP (PIE).

Enforces guardrails on musical intentions and prevents destructive actions.
"""

from __future__ import annotations

from typing import Any

class PolicyEngine:
    def __init__(self) -> None:
        pass

    def validate_action(self, action_type: str, params: dict[str, Any]) -> dict[str, Any]:
        """Validate if an action adheres to PIE policies.

        Returns a dict: {"valid": bool, "reason": str}
        """
        if action_type == "set_track_volume":
            volume = params.get("volume", 0.0)
            # 0.8 in FL roughly corresponds to 0dBFS. Prevent pushing faders past this.
            if volume > 0.8:
                return {
                    "valid": False,
                    "reason": f"Policy Violation (Gain Staging): Requested volume {volume} exceeds safe limit of 0.8 (0dBFS). Use compression instead."
                }

        if action_type == "set_track_pan":
            # For demonstration: If the track name suggests it's a Sub Bass, enforce mono.
            track_name = params.get("track_name", "").upper()
            pan = params.get("pan", 0.0)
            if "SUB" in track_name and pan != 0.0:
                return {
                    "valid": False,
                    "reason": "Policy Violation (Safe Panning): Sub-bass tracks must remain in strict mono (pan = 0.0)."
                }

        return {"valid": True, "reason": "Passed."}

# Singleton instance
_policy_engine = PolicyEngine()

def get_policy_engine() -> PolicyEngine:
    return _policy_engine
