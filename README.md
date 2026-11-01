# NexusContacts — Advanced Data Structures & Algorithms (ADSA) Mini Project

A complete, production-ready, full-stack **Contact Management System** designed for 2nd-year Computer Science Engineering students.

NexusContacts integrates academic data structures (Tries, AVL Trees, Custom Separate-Chaining Hash Tables, Binary Max-Heaps, and Graphs) with a persistent SQLite database and a modern glassmorphic web dashboard.

---

## 🚀 Quick Start Guide

### Option 1: One-Click Launch (Windows)
Double-click:
```
d:\gps2\run_contact_app.bat
```
*(Or navigate to `contact_management_system/` and double-click `run.bat`)*

This launches the FastAPI server and automatically opens `http://localhost:8000` in your default browser.

### Option 2: Manual Terminal Launch
```bash
# 1. Navigate to backend directory
cd d:\gps2\contact_management_system\backend

# 2. Run the server using Python 3.12
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Open **http://localhost:8000** in your browser.  
Interactive Swagger API documentation is available at **http://localhost:8000/docs**.

---

## 🏛️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                        MODERN FRONTEND WEB DASHBOARD                              |
|       (Glassmorphism, Real-time Trie Autocomplete, Interactive Canvas Visualizers)|
+-----------------------------------------+-----------------------------------------+
                                          │ HTTP REST (JSON)
                                          ▼
+-----------------------------------------------------------------------------------+
|                           BACKEND SERVER (FastAPI)                                |
|                                                                                   |
|   ┌───────────────────────────────────────────────────────────────────────────┐   |
|   │                      IN-MEMORY ADSA ENGINE LAYER                          │   |
|   │                                                                           │   |
|   │   1. Trie (Prefix Tree)              -> Autocomplete & Prefix Search      │   |
|   │   2. AVL Tree (Self-Balancing BST)   -> Sorted Alphabetical Traversal     │   |
|   │   3. Chaining Hash Table             -> O(1) Direct Lookup & Deduplication│   |
|   │   4. Binary Max-Heap                 -> Top Frequent / Emergency Priority │   |
|   │   5. Contact Graph (Adjacency List)  -> BFS Shortest Connection Path      │   |
|   │   6. Levenshtein Distance (DP)       -> Typo-Tolerant Fuzzy Search        │   |
|   └─────────────────────────────────────┬─────────────────────────────────────┘   |
+-----------------------------------------┼-----------------------------------------+
                                          │ Auto-sync on CRUD mutations
                                          ▼
+-----------------------------------------------------------------------------------+
|                            PERSISTENT STORAGE (SQLite)                            |
|                       contacts.db (Survives Server Reboots)                       |
+-----------------------------------------------------------------------------------+
```

---

## 📊 ADSA Time & Space Complexity Analysis

| Data Structure / Algorithm | Operation | Academic Complexity | Naive Alternative | Practical Benefit in NexusContacts |
| :--- | :--- | :--- | :--- | :--- |
| **Trie (Prefix Tree)** | Autocomplete & Prefix Search | $O(L + M)$ | $O(N \times L)$ Linear Array Scan | Autocomplete search time depends **only on word length $L$**, not on whether there are 100 or 1,000,000 contacts. |
| **AVL Tree (Self-Balancing BST)** | Search / Insert / Delete | $O(\log N)$ | $O(N)$ Unbalanced BST (Degenerate) | Prevents degenerate linked list skew when contacts are inserted in alphabetical order. |
| **AVL Tree** | Alphabetical Sorting | $O(N)$ In-order Traversal | $O(N \log N)$ Sort Algorithm | The tree is **always balanced and sorted in memory**; in-order traversal yields ordered contacts directly. |
| **Chaining Hash Table** | Lookup by ID / Phone | $O(1)$ Average | $O(N)$ Linear Search | Instant retrieval and duplicate phone number detection. |
| **Binary Max-Heap** | Peek Top Contact / Extract Max | $O(1)$ Peek, $O(\log N)$ Extract | $O(N)$ Linear Search for Maximum | Instant access to the most frequently contacted and emergency contacts. |
| **Contact Graph + BFS** | Degrees of Separation | $O(V + E)$ | $O(V!)$ Naive Permutations | Discovers the shortest relationship path between any two people in the network. |
| **Levenshtein Distance** | Typo-Tolerant Search | $O(M \times N)$ Dynamic Programming | Infeasible with regex | Finds contacts even when user misspells the name (e.g., `"Smyth"` $\rightarrow$ `"Smith"`). |

---

## 🌟 Standout Features for Evaluation & Viva

1. **Live ADSA Benchmark Panel:** Real-time side-by-side timer running with microsecond precision showing the exact execution duration of a **Trie Prefix Lookup** vs. a **Naive Linear Scan**, highlighting speedup multipliers ($20\text{x}-50\text{x}$ faster).
2. **Interactive AVL Tree Visualizer:** A built-in HTML5 Canvas that draws the balanced tree hierarchy dynamically. Nodes are color-coded based on their balance factors:
   * 🟢 Green: Balance Factor $= 0$ (Perfect balance)
   * 🟡 Amber: Balance Factor $=\pm 1$ (Balanced)
   * 🔴 Red: Balance Factor $> |1|$ (Requires Rotation)
   * Displays rotation counters for all 4 cases: **LL, RR, LR, RL**.
3. **Contact Relationship Graph Visualizer:** Renders an interactive radial network map of contacts and relationship edges. Select any two contacts to run **Breadth-First Search (BFS)** and view glowing connection chains with labeled edges (*Colleague*, *Batchmate*, *Friend*, *Emergency Contact*).
4. **Dynamic Programming Levenshtein Distance Matrix Inspector:** An interactive tool in the UI that computes and displays the 2D DP recurrence matrix for any two words in real-time.
5. **Separate Chaining Hash Table Inspector:** Visualizes bucket capacity, load factor ($\lambda$), collision counts, and max bucket chain length.
6. **Pre-Seeded Dataset:** Ships with 26 realistic contacts across 5 categories with established relationships so the evaluators see a vibrant, fully populated dashboard immediately.

---

## 🎓 Viva Questions & Model Answers for College Evaluation

### Q1: Why did you use an AVL Tree instead of a regular Binary Search Tree (BST)?
> **Answer:** If a user enters contacts in alphabetical order (e.g., *Aaron*, *Alice*, *Bob*, *Charlie*), a standard BST degenerates into a singly linked list with $O(N)$ height and worst-case $O(N)$ search time. The AVL tree strictly enforces that the balance factor $|height(left) - height(right)| \le 1$ at every node using 4 rotation cases (LL, RR, LR, RL), guaranteeing $O(\log N)$ search, insertion, and deletion height.

### Q2: How does a Trie achieve faster autocomplete than an SQL `LIKE 'Jo%'` query?
> **Answer:** A SQL `LIKE 'Jo%'` scan requires traversing an index or scanning rows. In contrast, our in-memory Trie traverses down the characters `'J'` $\rightarrow$ `'o'` in $O(L)$ steps (where $L=2$), and then conducts a small Depth-First Search (DFS) only down the descendant branches in $O(M)$ time. Total time $O(L + M)$ is completely independent of the total dataset size $N$.

### Q3: How is the Max-Heap structured and why is it beneficial here?
> **Answer:** The Max-Heap is implemented using a 1D array where for any node at index $i$, its parent is at $\lfloor(i-1)/2\rfloor$, and children are at $2i+1$ and $2i+2$. Every time a user clicks the call button on a contact, their interaction score increases and the contact is sifted up in $O(\log N)$ time. The top contact is retrieved in $O(1)$ time without scanning all elements.

### Q4: How does your custom Hash Table handle collisions?
> **Answer:** We use **Separate Chaining**. The hash table contains an array of bucket heads pointing to linked list `HashNode` chains. If two keys hash to the same bucket index via our polynomial rolling hash function ($\sum c_i \cdot 31^{k-1-i} \pmod m$), the new node is appended to the bucket chain. When the load factor $\lambda = \frac{N}{\text{capacity}}$ exceeds $0.75$, the table automatically doubles its capacity and rehashes all elements to maintain $O(1)$ average time complexity.

### Q5: How does BFS find the shortest relationship chain between two contacts?
> **Answer:** Breadth-First Search (BFS) explores all neighboring vertices at depth $d=1$ before moving to depth $d=2$. Because all edges in an unweighted social network have uniform weight (1 hop), the first time BFS discovers the target contact, it is mathematically guaranteed to be the shortest path (minimum degrees of separation).

---

## 📁 Project Directory Structure

```
contact_management_system/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application & REST route definitions
│   │   ├── models.py                # Pydantic schemas for data validation
│   │   ├── database.py              # SQLite connection, tables, and CRUD queries
│   │   ├── sample_data.py           # Pre-seeded realistic contacts and relationships
│   │   ├── contact_service.py       # Core coordinator syncing in-memory ADSA with SQLite
│   │   │
│   │   └── data_structures/         # PURE ADSA IMPLEMENTATIONS
│   │       ├── __init__.py          # Package initializer
│   │       ├── trie.py              # Prefix Tree for autocomplete & search
│   │       ├── avl_tree.py          # Self-balancing BST with LL, RR, LR, RL rotations
│   │       ├── hash_table.py        # Separate-chaining hash table with dynamic rehash
│   │       ├── heap.py              # Binary Max-Heap priority queue
│   │       ├── graph.py             # Adjacency list graph with BFS pathfinding
│   │       └── algorithms.py        # Levenshtein distance DP & Merge Sort
│   │
│   ├── requirements.txt             # Python dependencies (fastapi, uvicorn, pydantic)
│   └── contacts.db                  # Local SQLite database (auto-generated)
│
├── frontend/                        # Modern Web Dashboard
│   ├── index.html                   # Semantic HTML5 layout
│   ├── css/
│   │   └── style.css                # Glassmorphism, animations, responsive design
│   └── js/
│       ├── app.js                   # REST API client, search debounce, state logic
│       └── visualizer.js            # HTML5 Canvas visualizer for AVL, Graph, and DP table
│
├── tests/
│   └── test_data_structures.py      # 17 comprehensive unit tests (100% passing)
│
├── run.bat                          # One-click Windows runner
└── README.md                        # Documentation, complexity tables, & viva preparation
```

---

## 🧪 Running Unit Tests
To verify all 17 unit test cases covering Trie, AVL Tree, Hash Table, Max-Heap, Graph BFS, and Levenshtein Distance:
```bash
python -m unittest tests/test_data_structures.py
```
Output:
```
Ran 17 tests in 0.002s
OK
```
