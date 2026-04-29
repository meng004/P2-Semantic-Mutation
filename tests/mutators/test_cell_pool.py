from unittest.mock import patch, MagicMock
from p2.mutators.cell_pool import build_cell_pool


@patch("p2.mutators.cell_pool.review_mutant")
@patch("p2.mutators.cell_pool.generate_mutants")
def test_build_pool_filters_to_double_confirmed(mock_gen, mock_review):
    from p2.mutators.llm_reviewer import ReviewVerdict
    mock_gen.return_value = ["diff1", "diff2", "diff3"]
    mock_review.side_effect = [
        ReviewVerdict(True, "Yes", "Yes"),
        ReviewVerdict(False, "No", "No"),  # rejected
        ReviewVerdict(True, "Yes", "Uncertain"),  # arbitration
    ]
    pool = build_cell_pool(
        put_source="x=1", put_name="A1", mut_intent="break conservation",
        n_candidates=3,
    )
    assert len(pool.double_confirmed) == 1
    assert len(pool.rejected) == 1
    assert len(pool.arbitration) == 1
