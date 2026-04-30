"""Smoke: generate_mutants returns N strings (mocked LLM)."""
from unittest.mock import MagicMock, patch
from p2.mutators.llm_generator import generate_mutants


@patch("p2.mutators.llm_generator.generator_client")
def test_generates_n_candidates(mock_factory):
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content="def program(x):\n    return float(x) + 1\n"
        ))]
    )
    mock_factory.return_value = (fake_client, "claude-opus-4-6")

    out = generate_mutants(
        put_source="def program(x): return float(x)",
        put_name="A2", scientific_domain="LU", mut_intent="x",
        n_candidates=3, temperature=0.7,
    )
    assert len(out) == 3
    for code in out:
        assert "def program" in code
