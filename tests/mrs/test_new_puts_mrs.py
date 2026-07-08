"""MR sanity for the 18 Study-2 expansion PUTs (a4..a8, b4..b7, c4..c7, d4..d8).

Verifies each PUT's class-primary MR (A→MP1, B→MP2, C→MP5, D→MP2) holds on the
pre-registered probe points, and that the declared conservation identities for
the numeric class are exact.
"""
import importlib

import pytest

# class → primary MP (deterministic PRIMARY_CELLS_V3 rule)
PRIMARY = {
    "a4": 1, "a5": 1, "a6": 1, "a7": 1, "a8": 1,
    "b4": 2, "b5": 2, "b6": 2, "b7": 2,
    "c4": 5, "c5": 5, "c6": 5, "c7": 5,
    "d4": 2, "d5": 2, "d6": 2, "d7": 2, "d8": 2,
}
PROBES = [0.1, 0.4, 0.7]


@pytest.mark.parametrize("put,mp", sorted(PRIMARY.items()))
def test_primary_mr_holds(put, mp):
    P = importlib.import_module(f"p2.puts.{put}").program
    M = importlib.import_module(f"p2.mrs.{put}")
    r = getattr(M, f"r_mp{mp}")
    R = getattr(M, f"R_mp{mp}")
    for x in PROBES:
        assert R(P(x), P(r(x))), f"{put} primary MP{mp} fails at x={x}"


@pytest.mark.parametrize("put", sorted(PRIMARY))
def test_r_transforms_in_unit_interval(put):
    M = importlib.import_module(f"p2.mrs.{put}")
    for k in range(1, 6):
        r = getattr(M, f"r_mp{k}")
        for x in PROBES:
            assert 0.0 <= float(r(x)) <= 1.0


@pytest.mark.parametrize("put", ["a4", "a5", "a6", "a7", "a8"])
def test_numeric_conservation_identity(put):
    P = importlib.import_module(f"p2.puts.{put}").program
    M = importlib.import_module(f"p2.mrs.{put}")
    for x in [0.2, 0.35, 0.45]:
        assert M.R_mp1(P(x), P(M.r_mp1(x)))


@pytest.mark.parametrize("put", sorted(PRIMARY))
def test_trivial_mr_always_passes(put):
    P = importlib.import_module(f"p2.puts.{put}").program
    M = importlib.import_module(f"p2.mrs.{put}")
    for x in PROBES:
        assert M.R_trivial(P(x), P(M.r_trivial(x)))
