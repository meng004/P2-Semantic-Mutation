from unittest.mock import AsyncMock, patch
import asyncio

from p2.mutators.operator_registry import OPERATORS
from p2.mutators.operator_runner import (
    OperatorTrialResult, run_operator_trial, run_operator_K_times,
)


def test_operator_trial_result_dataclass():
    op = OPERATORS[0]
    r = OperatorTrialResult(
        op_id=op.id, attempt_idx=0, code="def program(x): return x",
        v1=True, v2="Yes", v3="Yes", v4="Yes", v5="Yes", v6="Yes",
        operator_match="Yes", overall="CONFIRMED", reason="ok",
    )
    assert r.is_confirmed
    assert r.is_semantic_match


@patch("p2.mutators.operator_runner.async_chat_completion")
def test_run_operator_trial_returns_result(mock_chat):
    op = OPERATORS[0]  # a1_CE1
    mock_chat.side_effect = [
        # 1st call = generator returns code
        "def program(x):\n    return float(x) + 0.5\n",
        # 2nd call = reviewer returns JSON
        '{"V1_syntax_ok": true, "V2_executable": "Yes", "V3_nontrivial": "Yes",'
        ' "V4_nondegenerate": "Yes", "V5_single_fault": "Yes", "V6_plausible": "Yes",'
        ' "operator_match": "Yes", "operator_match_reason": "ok",'
        ' "overall": "CONFIRMED", "reason": "ok"}',
    ]

    async def go():
        return await run_operator_trial(
            op=op, attempt_idx=0,
            put_source="def program(x): return float(x)",
            put_name="A1", scientific_domain="Lorenz",
            generator_client=None, reviewer_client=None,
        )

    res = asyncio.run(go())
    assert res.is_confirmed
    assert res.code.startswith("def program(x):")
