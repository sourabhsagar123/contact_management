"""
Trie (Prefix Tree) Implementation for Contact Management System
===============================================================
Academic Context:
- Data Structure: Multi-way Tree (Prefix Tree / Trie)
- Time Complexity:
    * Insertion: O(L) where L is the length of the string
    * Search / Autocomplete: O(L + M) where M is the number of matching results
    * Deletion: O(L)
- Space Complexity: O(ALPHABET_SIZE * L * N) in worst case, shared prefixes optimize memory.

Why use Trie over Linear Array for Autocomplete?
An array requires checking all N contacts: O(N * L).
A Trie guarantees instant prefix retrieval independent of total contacts N!
"""

from typing import Dict, Set, List, Tuple, Optional


class TrieNode:
    """A single node within the Prefix Tree (Trie)."""
    def __init__(self, char: str = ""):
        self.char: str = char
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        # Store contact IDs associated with this exact word or prefix
        self.contact_ids: Set[int] = set()

    def __repr__(self) -> str:
        return f"TrieNode('{self.char}', is_end={self.is_end_of_word}, ids={len(self.contact_ids)})"


class Trie:
    """Prefix Tree for fast contact autocomplete and prefix search."""
    def __init__(self):
        self.root = TrieNode()
        self.total_words = 0

    def _normalize(self, text: str) -> str:
        """Helper to convert to lowercase and strip whitespace."""
        return text.strip().lower()

    def insert(self, word: str, contact_id: int) -> None:
        """
        Inserts a word into the Trie and associates it with contact_id.
        Time Complexity: O(L) where L is len(word).
        """
        if not word:
            return
        
        normalized = self._normalize(word)
        current = self.root

        for char in normalized:
            if char not in current.children:
                current.children[char] = TrieNode(char)
            current = current.children[char]
            # Optionally add contact_id to prefix path for fast prefix lookups
            current.contact_ids.add(contact_id)

        if not current.is_end_of_word:
            current.is_end_of_word = True
            self.total_words += 1

    def search_exact(self, word: str) -> Set[int]:
        """
        Checks if the exact word exists and returns matching contact IDs.
        Time Complexity: O(L).
        """
        normalized = self._normalize(word)
        current = self.root
        for char in normalized:
            if char not in current.children:
                return set()
            current = current.children[char]
        
        return current.contact_ids if current.is_end_of_word else set()

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[Tuple[str, Set[int]]]:
        """
        Finds all words in the Trie starting with given prefix.
        Time Complexity: O(L + M) where L = len(prefix), M = number of descendants.
        Returns: List of tuples (word, set of contact_ids).
        """
        if not prefix:
            return []

        normalized = self._normalize(prefix)
        current = self.root

        # 1. Navigate to the prefix end node
        for char in normalized:
            if char not in current.children:
                return []  # Prefix does not exist
            current = current.children[char]

        # 2. Perform Depth-First Search (DFS) to collect all words beneath this prefix
        results: List[Tuple[str, Set[int]]] = []
        self._dfs_collect(current, normalized, results, max_results)
        return results

    def _dfs_collect(self, node: TrieNode, current_prefix: str, 
                     results: List[Tuple[str, Set[int]]], max_results: int) -> None:
        """Recursive DFS traversal to collect words from node down."""
        if len(results) >= max_results:
            return

        if node.is_end_of_word:
            results.append((current_prefix, set(node.contact_ids)))

        # Traverse children in sorted order for consistent alphabetical auto-complete
        for char in sorted(node.children.keys()):
            self._dfs_collect(node.children[char], current_prefix + char, results, max_results)
            if len(results) >= max_results:
                break

    def get_contact_ids_for_prefix(self, prefix: str) -> Set[int]:
        """Directly returns all contact IDs that share this prefix."""
        if not prefix:
            return set()
        
        normalized = self._normalize(prefix)
        current = self.root
        for char in normalized:
            if char not in current.children:
                return set()
            current = current.children[char]
        
        return set(current.contact_ids)

    def delete(self, word: str, contact_id: int) -> bool:
        """
        Removes a contact_id from word path. Cleans up orphaned nodes.
        Time Complexity: O(L).
        """
        if not word:
            return False

        normalized = self._normalize(word)

        def _delete_helper(node: TrieNode, key: str, depth: int) -> bool:
            if depth == len(key):
                if not node.is_end_of_word:
                    return False
                
                # Remove this contact id
                node.contact_ids.discard(contact_id)

                if len(node.contact_ids) == 0:
                    node.is_end_of_word = False
                    self.total_words -= 1

                # If node has no children and is no longer an end, it can be deleted
                return len(node.children) == 0 and not node.is_end_of_word

            char = key[depth]
            if char not in node.children:
                return False

            should_delete_child = _delete_helper(node.children[char], key, depth + 1)

            # Clean child's contact_id
            node.children[char].contact_ids.discard(contact_id)

            if should_delete_child:
                del node.children[char]
                return len(node.children) == 0 and not node.is_end_of_word and len(node.contact_ids) == 0

            return False

        return _delete_helper(self.root, normalized, 0)

    def count_nodes(self) -> int:
        """Returns total nodes in the Trie for ADSA memory/size analytics."""
        def _count(node: TrieNode) -> int:
            return 1 + sum(_count(child) for child in node.children.values())
        return _count(self.root)
