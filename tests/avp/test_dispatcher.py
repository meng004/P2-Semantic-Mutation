import numpy as np
from p2.avp.interface import MR, AVPResult
from p2.avp.dispatcher import call_avp


def test_dispatcher_routes_mp1_to_conservation():
    program = lambda x: np.array([x, 1 - x])
    mr = MR(
        r=lambda x: x + 0.5,
        R=lambda yo, yn: abs(yo.sum() - yn.sum()) <= 1e-6,
        mp_index=1, name="cons",
    )
    result = call_avp(program, mr, epsilon=1e-6)
    assert result == AVPResult.PASS


def test_dispatcher_unknown_mp_raises():
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=99, name="bad")
    program = lambda x: x
    import pytest
    with pytest.raises(ValueError, match="Unknown MP index"):
        call_avp(program, mr, epsilon=1e-6)
