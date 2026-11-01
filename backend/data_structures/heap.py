"""
Binary Max-Heap (Priority Queue) Implementation
================================================
Academic Context:
- Data Structure: Array-based Binary Max-Heap
- Heap Property: For any index i, value(parent(i)) >= value(i)
- Mathematical Indexes (0-based):
    * parent(i) = (i - 1) // 2
    * left_child(i) = 2 * i + 1
    * right_child(i) = 2 * i + 2
- Time Complexity:
    * Peek Max: O(1)
    * Insertion: O(log N) via sift-up (heapify_up)
    * Extract Max: O(log N) via sift-down (heapify_down)
    * Top K Retrieval: O(K log N)
- Space Complexity: O(N)

Why use Max-Heap for Contacts?
To surface "Most Frequently Contacted" or "Emergency/Favorite Contacts" instantly.
A linear scan takes O(N) every time. Max-Heap gives top elements in O(1) peek time!
"""

from typing import Any, List, Optional, Tuple


class HeapElement:
    """A wrapper item in the Max-Heap."""
    def __init__(self, priority: float, data: Any):
        self.priority: float = priority        # Sorting priority (e.g., call_count + favorite bonus)
        self.data: Any = data                  # The Contact payload or ID

    def __repr__(self) -> str:
        name = getattr(self.data, "name", str(self.data))
        return f"HeapElement(priority={self.priority}, data={name})"


class ContactHeap:
    """Array-backed Binary Max-Heap."""
    def __init__(self):
        self.heap: List[HeapElement] = []

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _sift_up(self, index: int) -> None:
        """Restores max-heap property moving up to root."""
        current = index
        while current > 0:
            parent = self._parent(current)
            if self.heap[current].priority > self.heap[parent].priority:
                self._swap(current, parent)
                current = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        """Restores max-heap property moving down to leaves."""
        current = index
        size = len(self.heap)

        while True:
            largest = current
            left = self._left_child(current)
            right = self._right_child(current)

            if left < size and self.heap[left].priority > self.heap[largest].priority:
                largest = left

            if right < size and self.heap[right].priority > self.heap[largest].priority:
                largest = right

            if largest != current:
                self._swap(current, largest)
                current = largest
            else:
                break

    def insert(self, priority: float, data: Any) -> None:
        """
        Inserts an item into the heap.
        Complexity: O(log N).
        """
        elem = HeapElement(priority, data)
        self.heap.append(elem)
        self._sift_up(len(self.heap) - 1)

    def peek_max(self) -> Optional[Any]:
        """Returns highest priority item in O(1) time."""
        if not self.heap:
            return None
        return self.heap[0].data

    def extract_max(self) -> Optional[Any]:
        """
        Removes and returns the highest priority item.
        Complexity: O(log N).
        """
        if not self.heap:
            return None
        
        root_data = self.heap[0].data
        last_elem = self.heap.pop()

        if self.heap:
            self.heap[0] = last_elem
            self._sift_down(0)

        return root_data

    def get_top_k(self, k: int = 5) -> List[Any]:
        """
        Returns top-k highest priority contacts without mutating the internal heap.
        Complexity: O(K log N).
        """
        # Create a shallow copy of heap array
        copy_heap = [HeapElement(elem.priority, elem.data) for elem in self.heap]
        temp_heap = ContactHeap()
        temp_heap.heap = copy_heap

        results = []
        for _ in range(min(k, len(copy_heap))):
            item = temp_heap.extract_max()
            if item is not None:
                results.append(item)
        return results

    def update_priority_by_id(self, contact_id: int, new_priority: float) -> bool:
        """
        Finds element matching contact_id and updates its priority, restoring heap order.
        """
        for i, elem in enumerate(self.heap):
            elem_id = getattr(elem.data, "id", None) or getattr(elem.data, "contact_id", None)
            if elem_id == contact_id or elem.data == contact_id:
                old_priority = elem.priority
                elem.priority = new_priority
                if new_priority > old_priority:
                    self._sift_up(i)
                else:
                    self._sift_down(i)
                return True
        return False

    def remove_by_id(self, contact_id: int) -> bool:
        """Removes an element from the heap by contact_id."""
        for i, elem in enumerate(self.heap):
            elem_id = getattr(elem.data, "id", None) or getattr(elem.data, "contact_id", None)
            if elem_id == contact_id or elem.data == contact_id:
                last_elem = self.heap.pop()
                if i < len(self.heap):
                    self.heap[i] = last_elem
                    self._sift_down(i)
                    self._sift_up(i)
                return True
        return False

    def size(self) -> int:
        return len(self.heap)
