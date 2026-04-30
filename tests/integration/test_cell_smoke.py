"""Smoke test: for every (PUT, primary MP) cell, run r then program then R.

Verifies the full pipeline: PUT callable → MR input transform → PUT callable → MR verifier.
"""
import importlib
import pytest

CELLS = [
    ("a1", "mp4", "r_mp4", "R_mp4"),
    ("a2", "mp1", "r_mp1", "R_mp1"),
    ("a3", "mp3", "r_mp3", "R_mp3"),
    ("b1", "mp2", "r_mp2", "R_mp2"),
    ("b2", "mp2", "r_mp2", "R_mp2"),
    ("b3", "mp1", "r_mp1", "R_mp1"),
    ("c1", "mp5", "r_mp5", "R_mp5"),
    ("c2", "mp5", "r_mp5", "R_mp5"),
    ("c3", "mp5", "r_mp5", "R_mp5"),
    ("d1", "mp2", "r_mp2", "R_mp2"),
    ("d2", "mp2", "r_mp2", "R_mp2"),
    ("d3", "mp2", "r_mp2", "R_mp2"),
]

SAMPLE_X = 0.4


@pytest.mark.parametrize("put_id,mp_tag,r_name,R_name", CELLS)
def test_primary_cell(put_id, mp_tag, r_name, R_name):
    put = importlib.import_module(f"p2.puts.{put_id}")
    mr = importlib.import_module(f"p2.mrs.{put_id}")

    r_fn = getattr(mr, r_name)
    R_fn = getattr(mr, R_name)

    x = SAMPLE_X
    rx = r_fn(x)
    y_orig = put.program(x)
    y_new = put.program(rx)

    assert R_fn(y_orig, y_new), (
        f"{put_id}/{mp_tag}: R({y_orig!r}, {y_new!r}) failed for x={x}, r(x)={rx}"
    )
