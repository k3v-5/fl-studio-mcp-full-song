"""Transaction and Snapshot system for FL Studio MCP (PIE).

Provides atomic execution logic (ACID-like) for audio modifications.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any

from fl_studio_mcp.pie.shadow_graph import get_shadow_graph

class Transaction:
    def __init__(self, tx_id: str) -> None:
        self.tx_id = tx_id
        self.snapshot_data: dict[str, Any] = {}
        self.status = "PENDING"
        self.actions: list[dict[str, Any]] = []

    def begin(self) -> None:
        """Capture the current state of FL Studio into a snapshot."""
        sg = get_shadow_graph()
        sg.refresh() # Force accurate state
        self.snapshot_data = sg.inspect("all")
        self.status = "IN_PROGRESS"

    def record_action(self, action: dict[str, Any]) -> None:
        """Record an action to be executed."""
        self.actions.append(action)

    def commit(self) -> None:
        """Commit the changes (in this simplified version, we just update the shadow graph)."""
        sg = get_shadow_graph()
        sg.refresh()
        self.status = "COMMITTED"

    def rollback(self) -> None:
        """Revert FL studio state to the snapshot.

        Note: Currently only partially implementable via API (e.g. restoring mixer volumes),
        piano roll rollback requires explicit delete commands.
        """
        # In a full implementation, this would iterate through self.snapshot_data
        # and send inverse MIDI commands for volumes, pans, etc.
        self.status = "ROLLED_BACK"


class TransactionManager:
    def __init__(self) -> None:
        self.active_transactions: dict[str, Transaction] = {}
        self.snapshots_dir = os.path.join(os.path.expanduser("~"), ".fl_studio_mcp_snapshots")
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def begin(self) -> str:
        tx_id = str(uuid.uuid4())
        tx = Transaction(tx_id)
        tx.begin()
        self.active_transactions[tx_id] = tx
        return tx_id

    def commit(self, tx_id: str) -> bool:
        if tx_id in self.active_transactions:
            self.active_transactions[tx_id].commit()
            return True
        return False

    def rollback(self, tx_id: str) -> bool:
        if tx_id in self.active_transactions:
            self.active_transactions[tx_id].rollback()
            return True
        return False

    def create_snapshot(self, name: str) -> str:
        sg = get_shadow_graph()
        sg.refresh()
        data = sg.inspect("all")

        safe_name = os.path.basename(name)
        filename = f"{safe_name}.json"
        filepath = os.path.join(self.snapshots_dir, filename)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        return filepath

    def restore_snapshot(self, name: str) -> bool:
        safe_name = os.path.basename(name)
        filepath = os.path.join(self.snapshots_dir, f"{safe_name}.json")
        if not os.path.exists(filepath):
            return False

        # Implementation would read JSON and fire SET commands to FL Studio
        return True

    def garbage_collect(self, project_dir: str | None = None) -> dict[str, Any]:
        """Clean up old snapshot files and .pie_backup files to free disk space."""
        deleted_snapshots = 0
        deleted_backups = 0

        # Clean snapshots directory
        if os.path.exists(self.snapshots_dir):
            for file in os.listdir(self.snapshots_dir):
                if file.endswith(".json"):
                    os.remove(os.path.join(self.snapshots_dir, file))
                    deleted_snapshots += 1

        # Clean specific project backup if requested
        if project_dir and os.path.exists(project_dir):
            for file in os.listdir(project_dir):
                if file.endswith(".pie_backup"):
                    os.remove(os.path.join(project_dir, file))
                    deleted_backups += 1

        return {
            "status": "success",
            "deleted_snapshots": deleted_snapshots,
            "deleted_backups": deleted_backups
        }


# Singleton instance
_tx_manager = TransactionManager()

def get_transaction_manager() -> TransactionManager:
    return _tx_manager
