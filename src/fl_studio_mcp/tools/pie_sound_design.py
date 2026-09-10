"""PIE Sound Design Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_sound_design_tools(mcp: FastMCP) -> None:
    """Register Sound Design tools with the MCP server."""
    from fl_studio_mcp.pie.sound_design import get_sound_design_engine

    @mcp.tool()
    def sound_get_macros(plugin_params: list[dict[str, Any]]) -> dict[str, Any]:
        """Filter a list of plugin parameters to return only Semantic Macros.

        Args:
            plugin_params: A list of parameter dictionaries typically returned by fl_get_plugin_params.
        """
        sde = get_sound_design_engine()
        macros = sde.get_semantic_macros(plugin_params)
        return {"semantic_macros": macros}

    @mcp.tool()
    def sound_apply_profile(profile_name: str) -> dict[str, Any]:
        """Get the macro values for a specific predefined sound profile.

        Args:
            profile_name: Name of the profile (e.g., 'aggressive_reece_bass').
        """
        sde = get_sound_design_engine()
        profile = sde.get_profile(profile_name)
        if not profile:
            return {"error": f"Profile '{profile_name}' not found."}
        return {"profile_values": profile}

    @mcp.tool()
    def sound_set_macro(macro_name: str, value: float) -> str:
        """Instruction tool indicating how to set a macro.

        Note: Actual setting relies on the existing fl_set_plugin_param_value.
        This tool returns the exact command the LLM should use next.
        """
        return f"To set '{macro_name}' to {value}, use fl_set_plugin_param_value with the parameter's index."

    @mcp.tool()
    def sound_lint(current_macros: dict[str, float]) -> dict[str, Any]:
        """Analyze current macro values to prevent sonic issues (clipping, phase).

        Args:
            current_macros: A dictionary mapping macro names (e.g., 'warmth') to their values (0.0 - 1.0).
        """
        sde = get_sound_design_engine()
        return sde.lint_macros(current_macros)
