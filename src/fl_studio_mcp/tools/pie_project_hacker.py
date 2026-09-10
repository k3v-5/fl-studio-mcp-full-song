"""PIE Project Hacker Engine tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_project_hacker_tools(mcp: FastMCP) -> None:
    """Register Project Hacker tools with the MCP server."""
    from fl_studio_mcp.pie.project_hacker import get_project_hacker_engine

    @mcp.tool()
    def project_set_active_file(filepath: str) -> dict[str, Any]:
        """Set the active FLP project file for binary analysis and mutation.

        Args:
            filepath: Absolute path to the .flp file on disk.
        """
        phe = get_project_hacker_engine()
        return phe.set_active_project(filepath)

    @mcp.tool()
    def project_inspect_file() -> dict[str, Any]:
        """Read the binary .flp structure (channels, plugins, patterns) using PyFLP.

        Requires an active project file to be set first via project_set_active_file.
        """
        phe = get_project_hacker_engine()
        return phe.read_structure()

    @mcp.tool()
    def project_inject_pattern(pattern_name: str, color: int = 0x55FF55) -> dict[str, Any]:
        """Attempt to inject a dynamically named pattern directly into the .flp binary.

        Will create an automatic `.pie_backup` file alongside the original.
        User MUST reload the project in FL Studio after this action.

        Args:
            pattern_name: The desired name for the newly created pattern.
            color: Hexadecimal color integer.
        """
        phe = get_project_hacker_engine()
        return phe.inject_pattern(pattern_name, color)
