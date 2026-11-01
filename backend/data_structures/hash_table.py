"""
Separate Chaining Hash Table Implementation
===========================================
Academic Context:
- Data Structure: Hash Map with Separate Chaining for Collision Resolution
- Hash Function: Polynomial Rolling Hash (radix = 31, prime modulo)
- Collision Resolution: Separate Chaining via Bucket Linked Lists
- Dynamic Resizing: Rehashes to 2x capacity when Load Factor (lambda = N / Capacity) > 0.75
- Time Complexity:
    * Average Case: O(1) for Put, Get, and Remove
    * Worst Case: O(N) if all keys hash to the same bucket (mitigated by good hash function)
- Space Complexity: O(N + Capacity)

Why implement a custom Hash Table for ADSA?
Instead of relying blindly on Python's built-in `dict`, this class proves understanding of
underlying hash mathematics, bucket arrays, collision handling, and dynamic rehashing.
"""

from typing import Any, Optional, List, Tuple


class HashNode:
    """Linked list node inside each hash bucket."""
    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value
        self.next: Optional['HashNode'] = None

    def __repr__(self) -> str:
        return f"HashNode({self.key}: {self.value})"


class ChainingHashTable:
    """Custom Hash Table with Separate Chaining and Auto-Rehashing."""
    def __init__(self, initial_capacity: int = 31, max_load_factor: float = 0.75):
        self.capacity: int = initial_capacity
        self.max_load_factor: float = max_load_factor
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity
        self.size: int = 0
        self.collision_count: int = 0
        self.rehash_count: int = 0

    def _hash(self, key: str) -> int:
        """
        Polynomial Rolling Hash Function:
        hash = (c0 * 31^(k-1) + c1 * 31^(k-2) + ... + ck) % capacity
        """
        hash_val = 0
        p = 31
        for char in str(key):
            hash_val = (hash_val * p + ord(char)) % self.capacity
        return hash_val

    def load_factor(self) -> float:
        """Calculates current load factor: lambda = n / m."""
        return self.size / self.capacity

    def put(self, key: str, value: Any) -> None:
        """
        Inserts or updates a key-value pair.
        Average Time Complexity: O(1).
        """
        # Rehash if load factor exceeds threshold
        if self.load_factor() >= self.max_load_factor:
            self._rehash()

        index = self._hash(key)
        head = self.buckets[index]

        # Case 1: Bucket is empty
        if head is None:
            self.buckets[index] = HashNode(key, value)
            self.size += 1
            return

        # Case 2: Bucket has chain (Collision occurs)
        current = head
        prev = None
        has_collision = False

        while current:
            if current.key == key:
                # Key already exists: update in place
                current.value = value
                return
            prev = current
            current = current.next
            has_collision = True

        # Append new node at end of chain
        if has_collision:
            self.collision_count += 1
        prev.next = HashNode(key, value)
        self.size += 1

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves value for key.
        Average Time Complexity: O(1).
        """
        index = self._hash(key)
        current = self.buckets[index]

        while current:
            if current.key == key:
                return current.value
            current = current.next

        return None

    def contains(self, key: str) -> bool:
        """Returns True if key exists in hash table."""
        return self.get(key) is not None

    def remove(self, key: str) -> bool:
        """
        Removes a key and returns True if found and removed.
        Average Time Complexity: O(1).
        """
        index = self._hash(key)
        current = self.buckets[index]
        prev = None

        while current:
            if current.key == key:
                if prev is None:
                    # Removing head of bucket
                    self.buckets[index] = current.next
                else:
                    prev.next = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next

        return False

    def _rehash(self) -> None:
        """
        Doubles the bucket capacity and redistributes all existing nodes.
        Complexity: O(N + M).
        """
        old_buckets = self.buckets
        self.capacity = self.capacity * 2 + 1  # Pick an odd number roughly double
        self.buckets = [None] * self.capacity
        self.size = 0
        self.collision_count = 0
        self.rehash_count += 1

        for head in old_buckets:
            current = head
            while current:
                self.put(current.key, current.value)
                current = current.next

    def values(self) -> List[Any]:
        """Returns all values in the hash table."""
        res = []
        for head in self.buckets:
            current = head
            while current:
                res.append(current.value)
                current = current.next
        return res

    def get_stats(self) -> dict:
        """Returns statistics for live ADSA inspector."""
        non_empty_buckets = sum(1 for b in self.buckets if b is not None)
        max_chain_length = 0
        for head in self.buckets:
            length = 0
            curr = head
            while curr:
                length += 1
                curr = curr.next
            max_chain_length = max(max_chain_length, length)

        return {
            "capacity": self.capacity,
            "total_items": self.size,
            "load_factor": round(self.load_factor(), 3),
            "total_collisions": self.collision_count,
            "rehash_count": self.rehash_count,
            "non_empty_buckets": non_empty_buckets,
            "max_chain_length": max_chain_length
        }
