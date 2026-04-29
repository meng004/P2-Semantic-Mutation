from unittest.mock import MagicMock, patch
from p2.mutators.llm_generator import generate_mutants


@patch("p2.mutators.llm_generator.anthropic.Anthropic")
def test_generates_n_candidates(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="--- a/foo.py\n+++ b/foo.py\n@@ -1,1 +1,1 @@\n-x = 1\n+x = 2")]
    )
    diffs = generate_mutants(
        prompt="test prompt", model="claude-opus-4-5",
        n_candidates=3, temperature=0.3, seed=42,
    )
    assert len(diffs) == 3
    for d in diffs:
        assert d.startswith("--- ")
