"""Text helpers for the demo fixture."""

import re

_PATTERN = re.compile(r"\s+")


def concat(prefix: str, suffix: str) -> str:
    return _PATTERN.sub(" ", prefix) + suffix
