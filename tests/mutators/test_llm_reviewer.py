from unittest.mock import MagicMock, patch
from p2.mutators.llm_reviewer import review_mutant, ReviewVerdict

_CONFIRMED_JSON = (
    '{"V1_syntax_ok": true, "V2_executable": "Yes", "V3_nontrivial": "Yes",'
    ' "V4_nondegenerate": "Yes", "V5_single_fault": "Yes", "V6_plausible": "Yes",'
    ' "overall": "CONFIRMED", "reason": "ok"}'
)


@patch("p2.mutators.llm_reviewer.reviewer1_client")
def test_reviewer_parses_confirmed_json(mock_r1):
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=_CONFIRMED_JSON))]
    )
    mock_r1.return_value = (fake_client, "gpt-5.4")

    verdict = review_mutant(
        put_source="def program(x): return float(x)",
        mutant_code="def program(x): return float(x) + 1",
    )
    assert isinstance(verdict, ReviewVerdict)
    assert verdict.overall == "CONFIRMED"
    assert verdict.V1_syntax_ok is True
