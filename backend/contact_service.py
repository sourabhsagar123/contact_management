"""
Contact Service (ADSA Engine Core)
==================================
The central coordinator managing in-memory ADSA data structures and syncing with SQLite.

Data Structures maintained in memory:
1. Trie: Autocomplete on names and phone numbers
2. AVLTree: Self-balancing alphabetical contact index
3. ChainingHashTable: O(1) direct lookup by ID and Phone
4. ContactHeap: O(1) top-k frequent / priority contacts
5. ContactGraph: Contact relationships and BFS degrees of separation
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from database import (
    fetch_all_contacts,
    fetch_contact_by_id,
    insert_contact_db,
    update_contact_db,
    delete_contact_db,
    fetch_all_relationships,
    insert_relationship_db
)
from data_structures import (
    Trie,
    AVLTree,
    ChainingHashTable,
    ContactHeap,
    ContactGraph,
    levenshtein_distance,
    fuzzy_search,
    merge_sort,
    benchmark_search
)


class ContactItem:
    """In-memory representation of a Contact."""
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.phone: str = data["phone"]
        self.email: str = data.get("email") or ""
        self.category: str = data.get("category") or "General"
        self.company: str = data.get("company") or ""
        self.notes: str = data.get("notes") or ""
        self.is_favorite: bool = bool(data.get("is_favorite", 0))
        self.call_count: int = data.get("call_count", 0)
        self.created_at: str = str(data.get("created_at") or "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "category": self.category,
            "company": self.company,
            "notes": self.notes,
            "is_favorite": self.is_favorite,
            "call_count": self.call_count,
            "created_at": self.created_at
        }

    @property
    def heap_priority(self) -> float:
        # Starred contacts receive +100 bonus priority in the Max-Heap
        fav_bonus = 100.0 if self.is_favorite else 0.0
        return self.call_count + fav_bonus

    def __repr__(self) -> str:
        return f"<Contact #{self.id} {self.name}>"


class ContactService:
    def __init__(self):
        # In-memory ADSA structures
        self.trie = Trie()
        self.avl = AVLTree()
        self.id_hash_table = ChainingHashTable(initial_capacity=67)
        self.phone_hash_table = ChainingHashTable(initial_capacity=67)
        self.heap = ContactHeap()
        self.graph = ContactGraph()

    def initialize(self) -> None:
        """Loads contacts and relationships from SQLite into ADSA memory structures."""
        # Reset structures
        self.trie = Trie()
        self.avl = AVLTree()
        self.id_hash_table = ChainingHashTable(initial_capacity=67)
        self.phone_hash_table = ChainingHashTable(initial_capacity=67)
        self.heap = ContactHeap()
        self.graph = ContactGraph()

        db_contacts = fetch_all_contacts()
        for row in db_contacts:
            contact = ContactItem(row)
            self._insert_into_memory(contact)

        # Load relationships
        relationships = fetch_all_relationships()
        for rel in relationships:
            self.graph.add_edge(rel["from_id"], rel["to_id"], rel["relationship"], bidirectional=True)

    def _insert_into_memory(self, contact: ContactItem) -> None:
        """Populates all ADSA structures for a contact."""
        # 1. Insert into Trie (by Name and Phone)
        self.trie.insert(contact.name, contact.id)
        # Also index individual name tokens (e.g. "John Doe" indexes both "John" and "Doe")
        for token in contact.name.split():
            self.trie.insert(token, contact.id)
        self.trie.insert(contact.phone, contact.id)

        # 2. Insert into AVL Tree (keyed by name for O(N) in-order alphabetical retrieval)
        self.avl.insert(contact.name, contact)

        # 3. Insert into Hash Tables for O(1) lookup
        self.id_hash_table.put(str(contact.id), contact)
        self.phone_hash_table.put(contact.phone, contact)

        # 4. Insert into Max-Heap
        self.heap.insert(contact.heap_priority, contact)

        # 5. Add to Graph vertex
        self.graph.add_vertex(contact.id, contact.name, contact.category)

    # ==================== CRUD Operations ====================

    def create_contact(self, data: Dict[str, Any]) -> ContactItem:
        """Creates contact in SQLite and syncs all ADSA structures."""
        # Check duplicate phone number via Hash Table in O(1)
        phone = data.get("phone", "").strip()
        if self.phone_hash_table.contains(phone):
            raise ValueError(f"A contact with phone number '{phone}' already exists.")

        contact_id = insert_contact_db(data)
        data_with_id = dict(data)
        data_with_id["id"] = contact_id
        contact = ContactItem(data_with_id)

        self._insert_into_memory(contact)
        return contact

    def get_contact_by_id(self, contact_id: int) -> Optional[ContactItem]:
        """O(1) retrieval using custom Chaining Hash Table."""
        return self.id_hash_table.get(str(contact_id))

    def update_contact(self, contact_id: int, updates: Dict[str, Any]) -> Optional[ContactItem]:
        """Updates contact in SQLite and syncs in-memory data structures."""
        existing = self.get_contact_by_id(contact_id)
        if not existing:
            return None

        # Check phone conflict if phone is being changed
        new_phone = updates.get("phone")
        if new_phone and new_phone != existing.phone:
            if self.phone_hash_table.contains(new_phone):
                raise ValueError(f"Phone number '{new_phone}' is already in use.")
            self.phone_hash_table.remove(existing.phone)

        # If name is being changed, remove from Trie and AVL
        name_changed = "name" in updates and updates["name"] != existing.name
        if name_changed:
            self.avl.delete(existing.name)
            self.trie.delete(existing.name, contact_id)
            for token in existing.name.split():
                self.trie.delete(token, contact_id)

        # Prepare merged data
        updated_dict = existing.to_dict()
        for k, v in updates.items():
            if v is not None:
                updated_dict[k] = v

        update_contact_db(contact_id, updated_dict)
        updated_contact = ContactItem(updated_dict)

        # Update Hash Tables
        self.id_hash_table.put(str(contact_id), updated_contact)
        self.phone_hash_table.put(updated_contact.phone, updated_contact)

        # Re-insert into Trie and AVL if name changed
        if name_changed:
            self.avl.insert(updated_contact.name, updated_contact)
            self.trie.insert(updated_contact.name, contact_id)
            for token in updated_contact.name.split():
                self.trie.insert(token, contact_id)

        # Update Heap priority
        self.heap.update_priority_by_id(contact_id, updated_contact.heap_priority)

        # Update Graph metadata
        if contact_id in self.graph.metadata:
            self.graph.metadata[contact_id]["name"] = updated_contact.name
            self.graph.metadata[contact_id]["category"] = updated_contact.category

        return updated_contact

    def delete_contact(self, contact_id: int) -> bool:
        """Deletes contact from SQLite and removes from all ADSA structures."""
        existing = self.get_contact_by_id(contact_id)
        if not existing:
            return False

        # 1. Remove from SQLite
        delete_contact_db(contact_id)

        # 2. Remove from AVL Tree
        self.avl.delete(existing.name)

        # 3. Remove from Trie
        self.trie.delete(existing.name, contact_id)
        for token in existing.name.split():
            self.trie.delete(token, contact_id)
        self.trie.delete(existing.phone, contact_id)

        # 4. Remove from Hash Tables
        self.id_hash_table.remove(str(contact_id))
        self.phone_hash_table.remove(existing.phone)

        # 5. Remove from Heap
        self.heap.remove_by_id(contact_id)

        # 6. Remove from Graph
        self.graph.remove_vertex(contact_id)

        return True

    def record_interaction(self, contact_id: int) -> Optional[ContactItem]:
        """Increments call count, updating Max-Heap priority."""
        contact = self.get_contact_by_id(contact_id)
        if not contact:
            return None
        new_count = contact.call_count + 1
        return self.update_contact(contact_id, {"call_count": new_count})

    # ==================== Query & Search Operations ====================

    def get_contacts(self, category: Optional[str] = None, sort_by: str = "alphabetical", 
                     reverse: bool = False, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves contacts leveraging ADSA structures based on sort_by and search params.
        """
        # 1. Base list retrieval
        if sort_by == "alphabetical":
            # Leverages AVL Tree In-Order Traversal O(N)
            contacts = self.avl.inorder()
            if reverse:
                contacts = list(reversed(contacts))
        elif sort_by == "frequent":
            # Leverages Max-Heap top items
            contacts = self.heap.get_top_k(k=1000)
        else:
            contacts = self.id_hash_table.values()
            if sort_by == "created_at":
                contacts, _ = merge_sort(contacts, key_func=lambda c: c.created_at, reverse=not reverse)

        # 2. Filter by Category if provided
        if category and category.lower() != "all":
            contacts = [c for c in contacts if c.category.lower() == category.lower()]

        # 3. Filter by Search Query if provided
        if search:
            query = search.strip().lower()
            # First try Trie prefix matches
            matching_ids = self.trie.get_contact_ids_for_prefix(query)
            if matching_ids:
                contacts = [c for c in contacts if c.id in matching_ids]
            else:
                # Fallback to substring matching across email/company/notes
                contacts = [c for c in contacts if query in c.name.lower() or query in c.phone or query in c.email.lower() or query in c.company.lower()]

        return [c.to_dict() for c in contacts]

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Trie prefix autocomplete: returns matching words and contact previews in O(L + M).
        """
        raw_results = self.trie.autocomplete(prefix, max_results=max_results)
        response = []
        seen_contact_ids = set()

        for word, contact_ids in raw_results:
            for cid in contact_ids:
                if cid not in seen_contact_ids:
                    seen_contact_ids.add(cid)
                    contact = self.get_contact_by_id(cid)
                    if contact:
                        response.append({
                            "matched_prefix": word,
                            "contact": contact.to_dict()
                        })
                if len(response) >= max_results:
                    break
            if len(response) >= max_results:
                break

        return response

    def fuzzy_search_contacts(self, query: str, max_distance: int = 2) -> List[Dict[str, Any]]:
        """Typo-tolerant fuzzy search using Levenshtein distance."""
        all_contacts = self.id_hash_table.values()
        matches = fuzzy_search(query, all_contacts, max_distance=max_distance)
        return [{
            "contact": contact.to_dict(),
            "edit_distance": distance
        } for contact, distance in matches]

    def get_frequent_contacts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves top frequent contacts from Max-Heap in O(K log N)."""
        top_items = self.heap.get_top_k(k=limit)
        return [c.to_dict() for c in top_items]

    def add_relationship(self, from_id: int, to_id: int, relationship: str) -> None:
        """Adds a relationship edge between two contacts in SQLite and Graph."""
        c1 = self.get_contact_by_id(from_id)
        c2 = self.get_contact_by_id(to_id)
        if not c1 or not c2:
            raise ValueError("Both contacts must exist to form a relationship.")

        insert_relationship_db(from_id, to_id, relationship)
        self.graph.add_edge(from_id, to_id, relationship, bidirectional=True)

    def find_connection_path(self, from_id: int, to_id: int) -> Optional[List[Dict[str, Any]]]:
        """BFS shortest path to discover connection chain between two contacts."""
        return self.graph.bfs_shortest_path(from_id, to_id)

    def get_graph_network(self) -> Dict[str, Any]:
        """Returns nodes and edges for the frontend interactive network visualizer."""
        return self.graph.get_network_graph_data()

    def get_avl_tree_structure(self) -> Optional[Dict[str, Any]]:
        """Returns JSON tree structure for interactive AVL Tree visualizer."""
        return self.avl.to_dict()

    def get_adsa_benchmark(self, query: str = "a") -> Dict[str, Any]:
        """Runs side-by-side microsecond benchmark for live demonstration."""
        all_contacts = self.id_hash_table.values()
        return benchmark_search(query, self.trie, all_contacts, self.id_hash_table)

    def get_adsa_stats(self) -> Dict[str, Any]:
        """Aggregates theoretical metrics across all active data structures."""
        all_contacts = self.id_hash_table.values()
        return {
            "total_contacts": len(all_contacts),
            "trie": {
                "total_words_indexed": self.trie.total_words,
                "total_nodes": self.trie.count_nodes()
            },
            "avl_tree": {
                "total_nodes": self.avl.total_nodes,
                "height": self.avl.get_tree_height(),
                "rotations_performed": self.avl.rotations
            },
            "hash_table": self.id_hash_table.get_stats(),
            "max_heap": {
                "heap_size": self.heap.size(),
                "top_contact": self.heap.peek_max().name if self.heap.peek_max() else None
            },
            "graph": {
                "total_vertices": len(self.graph.metadata),
                "total_edges": sum(len(neighbors) for neighbors in self.graph.adj_list.values()) // 2
            }
        }


# Global singleton instance
contact_service = ContactService()
