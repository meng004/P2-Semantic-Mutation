from p2.mutators.diversity import (
    ast_token_bag, pairwise_distance, diversity_score,
)


CODE_A = "def program(x):\n    return float(x) ** 2 + 1\n"
CODE_B = "def program(x):\n    return float(x) ** 2 + 1\n"      # identical
CODE_C = "def program(x):\n    y = float(x); return y * y - 1\n"  # different impl


def test_token_bag_returns_dict():
    bag = ast_token_bag(CODE_A)
    assert isinstance(bag, dict)
    assert sum(bag.values()) > 0


def test_identical_code_distance_zero():
    d = pairwise_distance(CODE_A, CODE_B)
    assert d == 0.0


def test_different_code_distance_positive():
    d = pairwise_distance(CODE_A, CODE_C)
    assert 0.0 < d < 1.0


def test_diversity_score_with_identical_inputs_is_zero():
    score = diversity_score([CODE_A, CODE_B, CODE_A])
    assert score == 0.0


def test_diversity_score_with_diverse_inputs_above_threshold():
    score = diversity_score([CODE_A, CODE_C, "def program(x):\n    return x + 0.1\n"])
    assert score > 0.1
