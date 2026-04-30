"""Implementation diversity metric over a set of K mutant code strings.

We use a parent→child AST bigram bag, augmented with literal values and
identifier names, and report 1 - Jaccard-multiset-similarity as pairwise
distance, then take the median pairwise distance across all K(K-1)/2
pairs as the cell score.

The bigram + literal + identifier bag captures three kinds of differences
that the bare node-class bag missed:

  - constant value changes (e.g., `0.05` → `0.1`)
  - identifier-name changes (e.g., `_NARROW_PROPOSAL` → `narrowed_std`)
  - local structural shifts (e.g., introducing an intermediate variable
    rewrites the parent→child edges around the affected expression)

Cost is still O(K²) parses; tree-edit-distance would be more accurate but
unnecessary at K ≤ 20.
"""
import ast
from collections import Counter
from itertools import combinations
from statistics import median
from typing import Dict, List


def ast_token_bag(code: str) -> Dict[str, int]:
    """Parent→child bigrams + literal values + identifier names."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    counter: Counter = Counter()
    for parent in ast.walk(tree):
        ptype = type(parent).__name__
        for child in ast.iter_child_nodes(parent):
            ctype = type(child).__name__
            counter[f"{ptype}>{ctype}"] += 1
            if isinstance(child, ast.Constant):
                counter[f"const::{type(child.value).__name__}::{repr(child.value)[:32]}"] += 1
            elif isinstance(child, ast.Name):
                counter[f"id::{child.id}"] += 1
            elif isinstance(child, ast.arg):
                counter[f"arg::{child.arg}"] += 1
            elif isinstance(child, ast.Attribute):
                counter[f"attr::{child.attr}"] += 1
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
