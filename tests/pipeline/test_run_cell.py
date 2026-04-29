from unittest.mock import MagicMock, patch
from p2.pipeline.run_cell import run_one_cell, CellResult


@patch("p2.pipeline.run_cell.is_killed")
@patch("p2.pipeline.run_cell.is_equivalent")
def test_run_cell_aggregates_states(mock_equiv, mock_killed):
    mock_equiv.side_effect = [True, False, False]   # 1 equiv
    mock_killed.side_effect = [False, True, False]  # wait: after 1 equiv removed, 2 remain
    result = run_one_cell(
        put=lambda x: x, mutants=[lambda x: x] * 3,
        mr_set=[], cell_id="A1_MP1_mutC",
        sampler=MagicMock(), k_eq=10, epsilon_eq=1e-6, epsilon_avp=1e-6,
    )
    assert result.equiv_count == 1
    assert result.killed_count == 1
    assert result.survive_count == 1
