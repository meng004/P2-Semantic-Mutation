"""Smoke: build_cell_pool integrates generate→validate→review correctly."""
from unittest.mock import patch
from p2.mutators.cell_pool import build_cell_pool, CellPool
from p2.mutators.llm_reviewer import ReviewVerdict


def _orig(x):
    return float(x)


@patch("p2.mutators.cell_pool.review_mutant")
@patch("p2.mutators.cell_pool.generate_mutants")
def test_build_pool_partitions_correctly(mock_gen, mock_review):
    mock_gen.return_value = [
        "def program(x):\n    return float(x) + 1\n",
        "def program(x):\n    return float(x) + 2\n",
        "def program(x):\n    syntax error here\n",
    ]
    mock_review.side_effect = [
        ReviewVerdict(True, "Yes", "Yes", "Yes", "Yes", "Yes",
                      "CONFIRMED", "ok", "gpt"),
        ReviewVerdict(True, "Yes", "Yes", "Yes", "No", "Yes",
                      "REJECTED", "v5 fail", "gpt"),
    ]
    pool = build_cell_pool(
        put_source="def program(x): return float(x)",
        put_name="A2", scientific_domain="LU",
        mut_intent="break determinant",
        original_fn=_orig, n_candidates=3, cell_id="a2_test",
    )
    assert isinstance(pool, CellPool)
    assert len(pool.confirmed) == 1
    assert len(pool.rejected) == 2
