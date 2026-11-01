"""
Advanced Algorithms Package for Contact Management System
=========================================================
1. Levenshtein Distance (Dynamic Programming) for Typo-Tolerant / Fuzzy Search
2. Merge Sort (Divide & Conquer) for Multi-Attribute Sorting
3. Live Microsecond Benchmark (Trie vs Linear Scan vs Hash Table)
"""

import time
from typing import List, Tuple, Any, Callable, Dict


# =====================================================================
# 1. Levenshtein Distance (Dynamic Programming)
# =====================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes minimum edit operations (insertions, deletions, substitutions)
    to transform string s1 into s2 using 2D Dynamic Programming.
    Time Complexity: O(M * N) where M = len(s1), N = len(s2)
    Space Complexity: O(M * N)
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: cost of transforming to empty string
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # DP Recurrence Relation:
    # dp[i][j] = dp[i-1][j-1] if chars match
    # else 1 + min(dp[i-1][j] (del), dp[i][j-1] (ins), dp[i-1][j-1] (sub))
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1].lower() == s2[j - 1].lower():
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # Deletion
                    dp[i][j - 1],      # Insertion
                    dp[i - 1][j - 1]   # Substitution
                )

    return dp[m][n]


def get_levenshtein_matrix(s1: str, s2: str) -> Dict[str, Any]:
    """
    Returns full DP table for academic visualization in the front-end inspector.
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1].lower() == s2[j - 1].lower():
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return {
        "word1": s1,
        "word2": s2,
        "matrix": dp,
        "distance": dp[m][n],
        "rows": [""] + list(s1),
        "cols": [""] + list(s2)
    }


def fuzzy_search(query: str, contacts: List[Any], max_distance: int = 2) -> List[Tuple[Any, int]]:
    """
    Finds contacts whose names are within `max_distance` edits of the query string.
    Returns: List of tuples (contact, edit_distance) sorted by closest match.
    """
    if not query:
        return []

    q = query.strip().lower()
    matches = []

    for contact in contacts:
        name = getattr(contact, "name", "").lower()
        # Direct substring match gets distance 0
        if q in name:
            matches.append((contact, 0))
            continue

        # Check Levenshtein distance on full name and individual tokens
        words = name.split()
        min_dist = levenshtein_distance(q, name)
        for w in words:
            dist = levenshtein_distance(q, w)
            if dist < min_dist:
                min_dist = dist

        if min_dist <= max_distance:
            matches.append((contact, min_dist))

    # Sort by minimum edit distance (closest match first)
    matches.sort(key=lambda x: x[1])
    return matches


# =====================================================================
# 2. Merge Sort (Divide and Conquer)
# =====================================================================

def merge_sort(items: List[Any], key_func: Callable[[Any], Any], reverse: bool = False) -> Tuple[List[Any], int]:
    """
    Standard Divide-and-Conquer Merge Sort implementation.
    Time Complexity: O(N log N) in all cases (Best, Average, Worst).
    Space Complexity: O(N).
    Returns: (sorted_items, comparison_count).
    """
    comparisons = 0

    def _merge(left: List[Any], right: List[Any]) -> List[Any]:
        nonlocal comparisons
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            comparisons += 1
            val_l = key_func(left[i])
            val_r = key_func(right[j])

            condition = (val_l > val_r) if reverse else (val_l <= val_r)
            if condition:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _sort(lst: List[Any]) -> List[Any]:
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = _sort(lst[:mid])
        right = _sort(lst[mid:])
        return _merge(left, right)

    sorted_list = _sort(items)
    return sorted_list, comparisons


# =====================================================================
# 3. Microsecond Benchmark (Trie vs Linear Scan vs Hash Table)
# =====================================================================

def benchmark_search(query: str, trie: Any, contacts_list: List[Any], hash_table: Any) -> Dict[str, Any]:
    """
    Executes real-time side-by-side search timing to showcase ADSA efficiency.
    Returns timings in microseconds and speedup multipliers.
    """
    q = query.strip().lower()

    # 1. Trie Autocomplete Time
    t0 = time.perf_counter_ns()
    trie_results = trie.autocomplete(q, max_results=20)
    t1 = time.perf_counter_ns()
    trie_time_us = max(0.1, (t1 - t0) / 1000.0)  # Microseconds

    # 2. Linear Scan (Naive approach)
    t2 = time.perf_counter_ns()
    linear_matches = []
    for c in contacts_list:
        name = getattr(c, "name", "").lower()
        if name.startswith(q) or q in name:
            linear_matches.append(c)
    t3 = time.perf_counter_ns()
    linear_time_us = max(0.1, (t3 - t2) / 1000.0)

    # 3. Hash Table Direct Lookup (Exact match check)
    t4 = time.perf_counter_ns()
    hash_match = hash_table.get(q)
    t5 = time.perf_counter_ns()
    hash_time_us = max(0.05, (t5 - t4) / 1000.0)

    speedup = round(linear_time_us / trie_time_us, 1) if trie_time_us > 0 else 1.0

    return {
        "query": query,
        "dataset_size": len(contacts_list),
        "trie_time_us": round(trie_time_us, 2),
        "linear_time_us": round(linear_time_us, 2),
        "hash_time_us": round(hash_time_us, 2),
        "speedup_factor": speedup,
        "trie_matches_count": len(trie_results),
        "linear_matches_count": len(linear_matches)
    }
