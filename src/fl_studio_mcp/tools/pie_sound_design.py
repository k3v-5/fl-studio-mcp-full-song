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
    def sound_set_semantic_keywords(keywords: list[str]) -> str:
        """Allow the AI to dynamically define what keywords to look for when hunting for macros."""
        sde = get_sound_design_engine()
        sde.set_semantic_keywords(keywords)
        return "Keywords updated successfully."

    @mcp.tool()
    def sound_add_profile(profile_name: str, macro_mapping: dict[str, float]) -> dict[str, Any]:
        """Create a new dynamically defined sound profile."""
        sde = get_sound_design_engine()
        return sde.add_profile(profile_name, macro_mapping)

    @mcp.tool()
    def sound_apply_profile(profile_name: str) -> dict[str, Any]:
        """Get the macro values for a dynamically defined sound profile."""
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
    def sound_lint(current_macros: dict[str, float], custom_rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze current macro values based on AI-provided custom rules to prevent sonic issues.
        """
        sde = get_sound_design_engine()
        return sde.lint_macros(current_macros, custom_rules)
