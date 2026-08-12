"""Core numeric operations for the demo fixture."""

import json
from math import sqrt

__all__ = ["Accumulator", "add", "reset", "scale"]


def add(a: int, b: int) -> int:
    return a + b


def scale(values: list, factor: float) -> list:
    return [item * factor for item in values]


def reset() -> None:
    return None


def hidden_public(x: int) -> int:
    return x + 1


def _helper(x):
    return sqrt(x)


def main() -> None:
    print(json.dumps({"result": add(1, 2)}))


class Accumulator:
    def __init__(self, start: int):
        self.total = start

    def add(self, value: int) -> int:
        self.total += value
        return self.total
