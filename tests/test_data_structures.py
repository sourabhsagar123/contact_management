"""
Comprehensive Unit Tests for ADSA Data Structures
==================================================
Run with: python -m unittest tests/test_data_structures.py
"""

import sys
import os
import unittest

# Add backend directory to system path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from data_structures import (
    Trie,
    AVLTree,
    ChainingHashTable,
    ContactHeap,
    ContactGraph,
    levenshtein_distance,
    fuzzy_search,
    merge_sort
)


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
        self.trie.insert("Aditi", 1)
        self.trie.insert("Aditya", 2)
        self.trie.insert("Aaron", 3)
        self.trie.insert("Bob", 4)

    def test_search_exact(self):
        self.assertEqual(self.trie.search_exact("Aditi"), {1})
        self.assertEqual(self.trie.search_exact("aditi"), {1})  # Case-insensitive
        self.assertEqual(self.trie.search_exact("NonExistent"), set())

    def test_autocomplete(self):
        results = self.trie.autocomplete("ad")
        words = [r[0] for r in results]
        self.assertIn("aditi", words)
        self.assertIn("aditya", words)
        self.assertNotIn("aaron", words)

    def test_prefix_contact_ids(self):
        ids = self.trie.get_contact_ids_for_prefix("ad")
        self.assertEqual(ids, {1, 2})

    def test_deletion(self):
        self.trie.delete("Aaron", 3)
        self.assertEqual(self.trie.search_exact("Aaron"), set())
        # Other words should remain intact
        self.assertEqual(self.trie.search_exact("Aditi"), {1})


class TestAVLTree(unittest.TestCase):
    def setUp(self):
        self.avl = AVLTree()

    def test_rotations_and_balance(self):
        # Insert elements in increasing order (triggers RR rotations)
        names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
        for name in names:
            self.avl.insert(name, {"name": name})

        # AVL invariant: height must be logarithmic, never skewed
        self.assertLessEqual(self.avl.get_tree_height(), 4)
        self.assertGreater(self.avl.rotations["RR"] + self.avl.rotations["LL"], 0)

    def test_inorder_sorted(self):
        names = ["Zach", "Bob", "Alice", "David", "Charlie"]
        for n in names:
            self.avl.insert(n, n)

        inorder_result = self.avl.inorder()
        self.assertEqual(inorder_result, sorted(names, key=lambda s: s.lower()))

    def test_deletion(self):
        self.avl.insert("Alice", 1)
        self.avl.insert("Bob", 2)
        self.avl.insert("Charlie", 3)

        self.avl.delete("Bob")
        self.assertIsNone(self.avl.search("Bob"))
        self.assertEqual(self.avl.inorder(), [1, 3])


class TestChainingHashTable(unittest.TestCase):
    def setUp(self):
        self.ht = ChainingHashTable(initial_capacity=5, max_load_factor=0.7)

    def test_put_and_get(self):
        self.ht.put("key1", "val1")
        self.ht.put("key2", "val2")
        self.assertEqual(self.ht.get("key1"), "val1")
        self.assertEqual(self.ht.get("key2"), "val2")
        self.assertIsNone(self.ht.get("nonexistent"))

    def test_update_existing_key(self):
        self.ht.put("key1", "initial")
        self.ht.put("key1", "updated")
        self.assertEqual(self.ht.get("key1"), "updated")
        self.assertEqual(self.ht.size, 1)

    def test_dynamic_rehashing(self):
        initial_cap = self.ht.capacity
        # Insert enough items to trigger rehash (5 * 0.7 = 3.5 -> 4th item triggers rehash)
        for i in range(10):
            self.ht.put(f"user_{i}", i)

        self.assertGreater(self.ht.capacity, initial_cap)
        self.assertGreater(self.ht.rehash_count, 0)
        for i in range(10):
            self.assertEqual(self.ht.get(f"user_{i}"), i)

    def test_remove(self):
        self.ht.put("del_me", 999)
        self.assertTrue(self.ht.contains("del_me"))
        self.assertTrue(self.ht.remove("del_me"))
        self.assertFalse(self.ht.contains("del_me"))
        self.assertFalse(self.ht.remove("del_me"))  # Second delete returns False


class TestContactHeap(unittest.TestCase):
    def setUp(self):
        self.heap = ContactHeap()

    def test_max_heap_order(self):
        self.heap.insert(10.0, "Low")
        self.heap.insert(50.0, "High")
        self.heap.insert(30.0, "Medium")

        self.assertEqual(self.heap.peek_max(), "High")
        self.assertEqual(self.heap.extract_max(), "High")
        self.assertEqual(self.heap.extract_max(), "Medium")
        self.assertEqual(self.heap.extract_max(), "Low")

    def test_top_k(self):
        scores = [15, 80, 45, 95, 20]
        for s in scores:
            self.heap.insert(s, f"Person_{s}")

        top3 = self.heap.get_top_k(3)
        self.assertEqual(top3, ["Person_95", "Person_80", "Person_45"])
        # Original heap must remain intact
        self.assertEqual(self.heap.size(), 5)


class TestContactGraph(unittest.TestCase):
    def setUp(self):
        self.graph = ContactGraph()
        # Create a small social graph
        # 1 --(Colleague)--> 2 --(Friend)--> 3 --(Family)--> 4
        # 1 --(Mentor)--> 3
        self.graph.add_edge(1, 2, "Colleague")
        self.graph.add_edge(2, 3, "Friend")
        self.graph.add_edge(3, 4, "Family")
        self.graph.add_edge(1, 3, "Mentor")

    def test_bfs_shortest_path(self):
        # Path from 1 to 4 should be 1 -> 3 -> 4 (2 hops instead of 3 hops)
        path = self.graph.bfs_shortest_path(1, 4)
        self.assertIsNotNone(path)
        node_ids = [step["id"] for step in path]
        self.assertEqual(node_ids, [1, 3, 4])

    def test_mutual_connections(self):
        mutual = self.graph.get_mutual_connections(1, 2)
        self.assertIn(3, mutual)


class TestAlgorithms(unittest.TestCase):
    def test_levenshtein(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("Smith", "Smyth"), 1)
        self.assertEqual(levenshtein_distance("John", "John"), 0)

    def test_merge_sort(self):
        items = [{"id": 3, "val": 30}, {"id": 1, "val": 10}, {"id": 2, "val": 20}]
        sorted_items, comparisons = merge_sort(items, key_func=lambda x: x["val"])
        self.assertEqual([x["val"] for x in sorted_items], [10, 20, 30])
        self.assertGreater(comparisons, 0)


if __name__ == "__main__":
    unittest.main()
