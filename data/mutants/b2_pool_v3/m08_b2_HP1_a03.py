import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42

_SHRINK = 0.1


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    state = {"x": 0.0}
    kept = []
    width = _SHRINK * _PROPOSAL_STD
    for idx in range(_N_STEPS):
        z = rng.standard_normal()
        prop = state["x"] + width * z
        cur = state["x"]
        num = (prop - mu) * (prop - mu)
        den = (cur - mu) * (cur - mu)
        log_ratio = 0.5 * (den - num)
        if np.log(rng.uniform()) < log_ratio:
            state["x"] = prop
        if not idx < _WARMUP:
            kept.append(state["x"])
    return float(np.mean(kept))