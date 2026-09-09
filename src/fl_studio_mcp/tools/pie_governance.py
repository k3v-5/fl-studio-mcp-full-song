"""PIE Governance tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_governance_tools(mcp: FastMCP) -> None:
    """Register Governance tools with the MCP server."""
    from fl_studio_mcp.pie.causal_graph import get_causal_graph
    from fl_studio_mcp.pie.policy_engine import get_policy_engine

    @mcp.tool()
    def production_status() -> dict[str, Any]:
        """Get the current status of the Causal Graph."""
        cg = get_causal_graph()
        return cg.get_status()

    @mcp.tool()
    def production_plan(intent: str) -> str:
        """Submit a new musical intent to the Causal Graph.

        Args:
            intent: Description of what you want to achieve (e.g., 'Make an aggressive bassline')
        """
        cg = get_causal_graph()
        try:
            intent_id = cg.add_intent(intent)
            return f"Intent added to Causal Graph with ID: {intent_id}"
        except Exception as e:
            return f"Failed to add intent: {e}"

    @mcp.tool()
    def production_validate(action_type: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Validate a proposed action against PIE guardrails.

        Args:
            action_type: The type of action (e.g., 'set_track_volume', 'set_track_pan')
            params: Dictionary of parameters for the action.
        """
        if params is None:
            params = {}
        engine = get_policy_engine()
        return engine.validate_action(action_type, params)

    @mcp.tool()
    def production_execute(plan_id: str) -> str:
        """Execute a validated plan (Stub for future implementation).

        Args:
            plan_id: ID of the plan node in the causal graph.
        """
        # In a real implementation this would fetch the plan node,
        # validate it via policy engine, start a transaction, and execute commands.
        return f"Plan {plan_id} execution simulated successfully."

    @mcp.tool()
    def production_rollback(plan_id: str) -> str:
        """Rollback a executed plan in the causal graph.

        Args:
            plan_id: ID of the plan node in the causal graph.
        """
        return f"Plan {plan_id} rollback simulated successfully."
