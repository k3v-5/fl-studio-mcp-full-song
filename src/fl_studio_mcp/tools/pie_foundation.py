"""PIE Foundation tools for FL Studio MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

def register_pie_foundation_tools(mcp: FastMCP) -> None:
    """Register Foundation tools with the MCP server."""
    from fl_studio_mcp.pie.shadow_graph import get_shadow_graph
    from fl_studio_mcp.pie.transactions import get_transaction_manager

    @mcp.tool()
    def session_inspect(scope: str = "all") -> dict[str, Any]:
        """Inspect the current FL Studio state via the Shadow Graph.

        Args:
            scope: "mixer", "channels", "transport", or "all".
        """
        sg = get_shadow_graph()
        return sg.inspect(scope)

    @mcp.tool()
    def session_refresh() -> str:
        """Force a hard refresh of the Shadow Graph by polling FL Studio."""
        sg = get_shadow_graph()
        try:
            sg.refresh()
            return "Shadow Graph refreshed successfully."
        except Exception as e:
            return f"Failed to refresh Shadow Graph: {e}"

    @mcp.tool()
    def transaction_begin() -> str:
        """Begin a new atomic transaction and create a state snapshot."""
        tx_manager = get_transaction_manager()
        try:
            tx_id = tx_manager.begin()
            return f"Transaction started with ID: {tx_id}"
        except Exception as e:
            return f"Failed to start transaction: {e}"

    @mcp.tool()
    def transaction_commit(tx_id: str) -> str:
        """Commit an active transaction."""
        tx_manager = get_transaction_manager()
        if tx_manager.commit(tx_id):
            return f"Transaction {tx_id} committed successfully."
        return f"Transaction {tx_id} not found."

    @mcp.tool()
    def transaction_rollback(tx_id: str) -> str:
        """Rollback an active transaction to its initial snapshot."""
        tx_manager = get_transaction_manager()
        if tx_manager.rollback(tx_id):
            return f"Transaction {tx_id} rolled back."
        return f"Transaction {tx_id} not found."

    @mcp.tool()
    def snapshot_create(name: str) -> str:
        """Create a persistent snapshot of the current session on disk.

        Args:
            name: The name for the snapshot file.
        """
        tx_manager = get_transaction_manager()
        try:
            filepath = tx_manager.create_snapshot(name)
            return f"Snapshot created at {filepath}"
        except Exception as e:
            return f"Failed to create snapshot: {e}"

    @mcp.tool()
    def snapshot_restore(name: str) -> str:
        """Restore a persistent snapshot from disk.

        Args:
            name: The name of the snapshot file to restore.
        """
        tx_manager = get_transaction_manager()
        try:
            if tx_manager.restore_snapshot(name):
                return f"Snapshot {name} restored successfully."
            return f"Snapshot {name} not found on disk."
        except Exception as e:
            return f"Failed to restore snapshot: {e}"

    @mcp.tool()
    def snapshot_garbage_collect(project_dir: str | None = None) -> dict[str, Any]:
        """Clean up old snapshots and backup files to save disk space.

        Args:
            project_dir: Optional absolute path to a project directory to clean .pie_backup files.
        """
        tx_manager = get_transaction_manager()
        return tx_manager.garbage_collect(project_dir)
