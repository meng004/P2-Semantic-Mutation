"""Probe an obvious equivalent mutant: identity wrapper."""
from p2.avp.interface import MR
from p2.equiv.diagnosis import probe_equivalence


def _orig(x):
    return float(x) * 2.0


def _identity_wrapper(x):
    return float(x) * 2.0  # exactly equivalent


def test_identity_wrapper_is_recognized_as_equivalent():
    mr = MR(r=lambda x: float(x) + 0.1, R=lambda a, b: True,
            mp_index=1, name="dummy")
    res = probe_equivalence(_orig, _identity_wrapper, mr,
                            cell_id="test", mutant_name="identity",
                            n_samples=100)
    assert res.n_y_identical == res.n_samples - 0
    assert res.diff_max < 1e-12
