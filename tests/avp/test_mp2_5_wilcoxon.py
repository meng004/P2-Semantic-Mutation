import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp2_5_wilcoxon import verify_wilcoxon


def test_wilcoxon_passes_when_monotonic():
    """Increasing transform should produce monotonically larger outputs."""
    def monotonic_program(x):
        return x * 2.0

    mr = MR(
        r=lambda x: x + 1.0,    # input increase
        R=lambda y_orig, y_new: y_new > y_orig,  # output should increase
        mp_index=2, name="monotonic-doubling",
    )
    result = verify_wilcoxon(monotonic_program, mr, alpha=0.05, n_samples=50)
    assert result == AVPResult.PASS


def test_wilcoxon_fails_when_anti_monotonic():
    def anti_program(x):
        return -x * 2.0  # decreases
    mr = MR(
        r=lambda x: x + 1.0,
        R=lambda y_orig, y_new: y_new > y_orig,
        mp_index=2, name="bad-monotonic",
    )
    result = verify_wilcoxon(anti_program, mr, alpha=0.05, n_samples=50)
    assert result == AVPResult.FAIL
