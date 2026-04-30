"""Implementation diversity metric over a set of K mutant code strings.

We use an AST-node-name multiset (bag of node-class names) and report
1 - Jaccard-multiset-similarity as pairwise distance, then take the
median pairwise distance across all K(K-1)/2 pairs as the cell score.

This is cheap (O(K²) AST parses) and stable; tree-edit-distance would
be more accurate but unnecessary at K ≤ 20.
"""
import ast
from collections import Counter
from itertools import combinations
from statistics import median
from typing import Dict, List


def ast_token_bag(code: str) -> Dict[str, int]:
    """Return Counter-as-dict of AST node class names."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    counter: Counter = Counter()
    for node in ast.walk(tree):
        counter[type(node).__name__] += 1
    return dict(counter)


def _multiset_jaccard(a: Dict[str, int], b: Dict[str, int]) -> float:
    """Multiset Jaccard: sum(min) / sum(max) over union of keys."""
    if not a and not b:
        return 1.0
    keys = set(a) | set(b)
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return inter / union if union else 0.0


def pairwise_distance(code1: str, code2: str) -> float:
    """0.0 = identical AST node distribution; 1.0 = disjoint."""
    return 1.0 - _multiset_jaccard(ast_token_bag(code1), ast_token_bag(code2))


def diversity_score(codes: List[str]) -> float:
    """Median pairwise distance over all K choose 2 pairs.

    Returns 0.0 if K < 2 or all codes identical.
    Higher value = more diverse implementations.
    """
    valid = [c for c in codes if c]
    if len(valid) < 2:
        return 0.0
    bags = [ast_token_bag(c) for c in valid]
    dists = [
        1.0 - _multiset_jaccard(bags[i], bags[j])
        for i, j in combinations(range(len(valid)), 2)
    ]
    return float(median(dists)) if dists else 0.0
