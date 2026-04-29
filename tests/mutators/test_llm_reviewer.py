from unittest.mock import MagicMock, patch
from p2.mutators.llm_reviewer import review_mutant, ReviewVerdict


@patch("p2.mutators.llm_reviewer.openai.OpenAI")
def test_reviewer_parses_three_tuple(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content='{"syntax_ok": true, "executable": "Yes", "fault_injected": "Yes"}'
        ))]
    )
    verdict = review_mutant(put_source="x = 1", mutant_diff="@@ x = 2 @@")
    assert verdict == ReviewVerdict(
        syntax_ok=True, executable="Yes", fault_injected="Yes"
    )
