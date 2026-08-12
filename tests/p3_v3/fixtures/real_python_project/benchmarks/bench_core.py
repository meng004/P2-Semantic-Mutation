"""Benchmark stub; the adapter records this path without parsing the body."""

from demopkg.core import add


def run() -> int:
    return sum(add(index, index) for index in range(100))
