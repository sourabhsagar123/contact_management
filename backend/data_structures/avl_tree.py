"""
AVL Tree (Self-Balancing Binary Search Tree) Implementation
==========================================================
Academic Context:
- Data Structure: Height-Balanced Binary Search Tree (AVL Tree)
- Invented by: Georgy Adelson-Velsky and Evgenii Landis (1962)
- Strict Balance Condition:
    For EVERY node, |height(left) - height(right)| <= 1 (Balance Factor in {-1, 0, 1})
- Time Complexity:
    * Search: O(log N)
    * Insertion: O(log N) + at most 2 rotations
    * Deletion: O(log N) + at most O(log N) rotations
    * In-order Traversal: O(N) yielding perfectly sorted contacts!
- Space Complexity: O(N)

Why AVL Tree for Contact Management?
An unbalanced BST can degenerate into a Linked List with O(N) worst-case time if contacts 
are added in alphabetical order (e.g. Aaron, Alice, Bob...). 
The AVL Tree guarantees O(log N) search and insertion by executing 4 rotation cases:
1. LL (Left-Left)   -> Single Right Rotation
2. RR (Right-Right) -> Single Left Rotation
3. LR (Left-Right)  -> Left Rotation on Child, Right Rotation on Root
4. RL (Right-Left)  -> Right Rotation on Child, Left Rotation on Root
"""

from typing import Any, Optional, List, Dict


class AVLNode:
    """A node in the AVL Tree."""
    def __init__(self, key: str, value: Any):
        self.key: str = key                    # Sorting key (e.g., lowercase name)
        self.value: Any = value                # Associated contact payload or ID
        self.height: int = 1                   # Leaf node has height 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None

    def balance_factor(self) -> int:
        """Returns height(left) - height(right)."""
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        return left_h - right_h

    def __repr__(self) -> str:
        return f"AVLNode(key='{self.key}', h={self.height}, bf={self.balance_factor()})"


class AVLTree:
    """Self-balancing AVL Tree for managing sorted contacts."""
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.total_nodes: int = 0
        # Analytics counters for viva demo
        self.rotations = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0
        }

    # ==================== Core Helpers ====================

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        return (self._height(node.left) - self._height(node.right)) if node else 0

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    # ==================== Rotations ====================

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        r"""
        Right Rotation (LL Case):
              y                             x
             / \                           / \
            x   T3   -- rotate right ->   T1  y
           / \                               / \
          T1  T2                            T2  T3
        """
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights (order matters: children first)
        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        r"""
        Left Rotation (RR Case):
            x                               y
           / \                             / \
          T1  y      -- rotate left ->    x   T3
             / \                         / \
            T2  T3                      T1  T2
        """
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        self._update_height(x)
        self._update_height(y)

        return y

    # ==================== Insertion ====================

    def insert(self, key: str, value: Any) -> None:
        """Public API to insert key-value pair and rebalance tree."""
        normalized_key = key.strip().lower()
        self.root = self._insert_node(self.root, normalized_key, value)

    def _insert_node(self, node: Optional[AVLNode], key: str, value: Any) -> AVLNode:
        # 1. Standard BST insertion
        if not node:
            self.total_nodes += 1
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert_node(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_node(node.right, key, value)
        else:
            # Duplicate key: update value
            node.value = value
            return node

        # 2. Update height of current ancestor node
        self._update_height(node)

        # 3. Compute balance factor to check if this node became unbalanced
        bf = self._balance_factor(node)

        # 4. Handle the 4 Imbalance Cases:

        # Case 1: Left-Left (LL) -> Single Right Rotation
        if bf > 1 and key < node.left.key:
            self.rotations["LL"] += 1
            return self._rotate_right(node)

        # Case 2: Right-Right (RR) -> Single Left Rotation
        if bf < -1 and key > node.right.key:
            self.rotations["RR"] += 1
            return self._rotate_left(node)

        # Case 3: Left-Right (LR) -> Left rotate left child, then Right rotate node
        if bf > 1 and key > node.left.key:
            self.rotations["LR"] += 1
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (RL) -> Right rotate right child, then Left rotate node
        if bf < -1 and key < node.right.key:
            self.rotations["RL"] += 1
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ==================== Deletion ====================

    def delete(self, key: str) -> None:
        """Public API to delete key from AVL Tree and rebalance."""
        normalized_key = key.strip().lower()
        self.root = self._delete_node(self.root, normalized_key)

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        """Find the leftmost node (in-order successor)."""
        current = node
        while current.left:
            current = current.left
        return current

    def _delete_node(self, node: Optional[AVLNode], key: str) -> Optional[AVLNode]:
        # 1. Standard BST deletion
        if not node:
            return None

        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Node with only one child or no child
            if not node.left:
                temp = node.right
                self.total_nodes -= 1
                return temp
            elif not node.right:
                temp = node.left
                self.total_nodes -= 1
                return temp

            # Node with two children: get in-order successor (smallest in right subtree)
            temp = self._min_value_node(node.right)
            node.key = temp.key
            node.value = temp.value
            node.right = self._delete_node(node.right, temp.key)

        if not node:
            return None

        # 2. Update height
        self._update_height(node)

        # 3. Check balance factor
        bf = self._balance_factor(node)

        # 4. Handle Rebalance Cases:
        # LL Case
        if bf > 1 and self._balance_factor(node.left) >= 0:
            self.rotations["LL"] += 1
            return self._rotate_right(node)

        # LR Case
        if bf > 1 and self._balance_factor(node.left) < 0:
            self.rotations["LR"] += 1
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR Case
        if bf < -1 and self._balance_factor(node.right) <= 0:
            self.rotations["RR"] += 1
            return self._rotate_left(node)

        # RL Case
        if bf < -1 and self._balance_factor(node.right) > 0:
            self.rotations["RL"] += 1
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ==================== Search & Traversals ====================

    def search(self, key: str) -> Optional[Any]:
        """
        Searches for a key in O(log N) time.
        """
        normalized_key = key.strip().lower()
        current = self.root
        while current:
            if normalized_key == current.key:
                return current.value
            elif normalized_key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def inorder(self) -> List[Any]:
        """
        Performs In-Order Traversal (Left -> Root -> Right).
        Complexity: O(N).
        Yields all contacts in alphabetically sorted order!
        """
        results: List[Any] = []
        def _inorder(node: Optional[AVLNode]):
            if node:
                _inorder(node.left)
                results.append(node.value)
                _inorder(node.right)
        _inorder(self.root)
        return results

    def get_tree_height(self) -> int:
        """Returns maximum height of tree."""
        return self._height(self.root)

    def to_dict(self, max_depth: int = 5) -> Optional[Dict[str, Any]]:
        """
        Serializes tree to nested dictionary for interactive front-end visualization.
        """
        def _node_to_dict(node: Optional[AVLNode], depth: int) -> Optional[Dict[str, Any]]:
            if not node or depth > max_depth:
                return None
            return {
                "key": node.key,
                "display": getattr(node.value, "name", node.key) if hasattr(node.value, "name") else node.key,
                "height": node.height,
                "balance_factor": self._balance_factor(node),
                "left": _node_to_dict(node.left, depth + 1),
                "right": _node_to_dict(node.right, depth + 1)
            }
        return _node_to_dict(self.root, 1)
