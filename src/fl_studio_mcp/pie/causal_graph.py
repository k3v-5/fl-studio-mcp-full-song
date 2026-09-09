"""Causal Graph (Production Graph) for FL Studio MCP (PIE).

Models user intents, AI plans, and executions as a DAG.
"""

from __future__ import annotations

import uuid
from typing import Any

class Node:
    def __init__(self, node_type: str, data: Any):
        self.id = str(uuid.uuid4())
        self.type = node_type
        self.data = data
        self.children: list[Node] = []
        self.status = "CREATED"

    def add_child(self, node: Node) -> None:
        self.children.append(node)

class CausalGraph:
    def __init__(self) -> None:
        self.root_nodes: list[Node] = []
        self.nodes_by_id: dict[str, Node] = {}

    def add_intent(self, intent_text: str) -> str:
        """Create a new root intent node."""
        node = Node("INTENT", {"text": intent_text})
        self.root_nodes.append(node)
        self.nodes_by_id[node.id] = node
        return node.id

    def add_plan(self, parent_intent_id: str, plan_data: dict[str, Any]) -> str:
        if parent_intent_id not in self.nodes_by_id:
            raise ValueError("Parent intent not found")

        parent = self.nodes_by_id[parent_intent_id]
        node = Node("PLAN", plan_data)
        parent.add_child(node)
        self.nodes_by_id[node.id] = node
        return node.id

    def get_status(self) -> dict[str, Any]:
        """Return a simplified representation of the active graph."""
        return {
            "active_intents": len(self.root_nodes),
            "total_nodes": len(self.nodes_by_id),
            "recent_intents": [n.data["text"] for n in self.root_nodes[-5:]]
        }

# Singleton instance
_causal_graph = CausalGraph()

def get_causal_graph() -> CausalGraph:
    return _causal_graph
