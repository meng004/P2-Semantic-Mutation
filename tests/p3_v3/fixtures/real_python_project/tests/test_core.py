"""Project test; the adapter must never derive schemas from this body."""

from demopkg.core import add


def probe_never_a_schema(alpha: int, beta: int) -> int:
    return add(alpha, beta)


def test_add():
    assert add(1, 2) == 3
