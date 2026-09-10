"""Policy Engine for FL Studio MCP (PIE).

Enforces guardrails on musical intentions and prevents destructive actions.
"""

from __future__ import annotations

from typing import Any

class PolicyEngine:
    def __init__(self) -> None:
        self.rules: list[dict[str, Any]] = []

    def set_rules(self, rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Allow the AI to dynamically set the policy rules.

        Example rule:
        {
            "action": "set_track_volume",
            "condition": "greater_than",
            "param": "volume",
            "value": 0.8,
            "message": "Volume exceeds 0.8 safe limit."
        }
        """
        self.rules = rules
        return {"status": "success", "rules_loaded": len(self.rules)}

    def validate_action(self, action_type: str, params: dict[str, Any]) -> dict[str, Any]:
        """Validate an action dynamically against the AI-defined rule list."""
        for rule in self.rules:
            if rule.get("action") == action_type:
                target_param = rule.get("param")
                if target_param in params:
                    val = params[target_param]
                    cond = rule.get("condition")
                    threshold = rule.get("value")

                    if cond == "greater_than" and val > threshold:
                        return {"valid": False, "reason": rule.get("message", "Policy violation.")}
                    elif cond == "less_than" and val < threshold:
                        return {"valid": False, "reason": rule.get("message", "Policy violation.")}
                    elif cond == "equals" and val == threshold:
                        return {"valid": False, "reason": rule.get("message", "Policy violation.")}
                    elif cond == "not_equals" and val != threshold:
                        return {"valid": False, "reason": rule.get("message", "Policy violation.")}

        return {"valid": True, "reason": "Passed."}

# Singleton instance
_policy_engine = PolicyEngine()

def get_policy_engine() -> PolicyEngine:
    return _policy_engine
