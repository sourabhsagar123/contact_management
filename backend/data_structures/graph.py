"""
Adjacency List Graph & BFS Pathfinding Implementation
=====================================================
Academic Context:
- Data Structure: Undirected / Directed Graph via Adjacency List
- Representation: Dictionary mapping Vertex ID -> List of (Neighbor ID, Edge Weight/Type)
- Traversal Algorithm: Breadth-First Search (BFS) for Shortest Path
    * Time Complexity: O(V + E) where V is vertices (contacts) and E is edges (relationships)
    * Space Complexity: O(V) for the queue and visited set
- Applications in Contact Management:
    1. Finding "Mutual Connections" (Intersection of neighbor sets)
    2. Finding "Degrees of Separation" (e.g. Alice is Bob's colleague, Bob is Charlie's friend)
    3. Social / Organization network graph visualization
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque


class ContactGraph:
    """Adjacency List Graph for tracking relationships between contacts."""
    def __init__(self):
        # adj_list: {contact_id: {neighbor_id: relationship_label}}
        self.adj_list: Dict[int, Dict[int, str]] = {}
        # vertex_metadata: {contact_id: dict_of_details}
        self.metadata: Dict[int, Dict[str, Any]] = {}

    def add_vertex(self, contact_id: int, name: str, category: str = "General") -> None:
        """Adds a contact as a vertex in the graph."""
        if contact_id not in self.adj_list:
            self.adj_list[contact_id] = {}
            self.metadata[contact_id] = {
                "name": name,
                "category": category
            }

    def add_edge(self, u: int, v: int, relationship: str = "Connected", bidirectional: bool = True) -> None:
        """
        Creates an edge between two contacts with a relationship label.
        Example: Alice and Bob are "Colleagues".
        """
        if u not in self.adj_list:
            self.add_vertex(u, f"Contact {u}")
        if v not in self.adj_list:
            self.add_vertex(v, f"Contact {v}")

        self.adj_list[u][v] = relationship
        if bidirectional:
            self.adj_list[v][u] = relationship

    def remove_vertex(self, contact_id: int) -> None:
        """Removes a contact and all connected edges."""
        if contact_id in self.adj_list:
            # Remove incident edges
            for neighbor in list(self.adj_list[contact_id].keys()):
                if neighbor in self.adj_list:
                    self.adj_list[neighbor].pop(contact_id, None)
            del self.adj_list[contact_id]
            self.metadata.pop(contact_id, None)

    def get_neighbors(self, contact_id: int) -> List[Tuple[int, str]]:
        """Returns all adjacent contacts and relationship types."""
        if contact_id not in self.adj_list:
            return []
        return [(neighbor, rel) for neighbor, rel in self.adj_list[contact_id].items()]

    def get_mutual_connections(self, u: int, v: int) -> List[int]:
        """
        Finds shared contacts between u and v using set intersection.
        Complexity: O(deg(u) + deg(v)).
        """
        if u not in self.adj_list or v not in self.adj_list:
            return []
        neighbors_u = set(self.adj_list[u].keys())
        neighbors_v = set(self.adj_list[v].keys())
        return list(neighbors_u.intersection(neighbors_v))

    def bfs_shortest_path(self, start_id: int, target_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Computes shortest path (degrees of separation) between two contacts using BFS.
        Complexity: O(V + E).
        Returns list of path steps with contact details and relationship edges.
        """
        if start_id not in self.adj_list or target_id not in self.adj_list:
            return None

        if start_id == target_id:
            return [{
                "id": start_id,
                "name": self.metadata.get(start_id, {}).get("name", "Unknown"),
                "relation_to_next": None
            }]

        visited: Set[int] = {start_id}
        # Queue holds tuples: (current_node, path_so_far)
        queue = deque([(start_id, [])])

        while queue:
            current, path = queue.popleft()

            for neighbor, relationship in self.adj_list[current].items():
                if neighbor == target_id:
                    # Found target! Construct final path description
                    full_path = path + [(current, relationship), (target_id, None)]
                    
                    formatted_steps = []
                    for node_id, rel in full_path:
                        meta = self.metadata.get(node_id, {})
                        formatted_steps.append({
                            "id": node_id,
                            "name": meta.get("name", f"Contact {node_id}"),
                            "category": meta.get("category", "General"),
                            "relation_to_next": rel
                        })
                    return formatted_steps

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(current, relationship)]))

        return None  # No path exists

    def get_network_graph_data(self) -> Dict[str, Any]:
        """
        Returns JSON-serializable structure for frontend visual network graph.
        """
        nodes = []
        for cid, meta in self.metadata.items():
            nodes.append({
                "id": cid,
                "name": meta.get("name", f"Contact {cid}"),
                "category": meta.get("category", "General"),
                "connections": len(self.adj_list.get(cid, {}))
            })

        edges = []
        visited_pairs = set()
        for u in self.adj_list:
            for v, rel in self.adj_list[u].items():
                pair = tuple(sorted((u, v)))
                if pair not in visited_pairs:
                    visited_pairs.add(pair)
                    edges.append({
                        "source": u,
                        "target": v,
                        "relation": rel
                    })

        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }
