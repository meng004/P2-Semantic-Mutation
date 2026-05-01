import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def program(x) -> float:
    x = float(x)
    target_mean = 4.0 * float(x) - 1.7
    rng = np.random.default_rng(_SEED)
    current = 0.0
    kept = np.empty(_N_STEPS - _WARMUP, dtype=float)
    kept_idx = 0
    for i in range(_N_STEPS):
        step = _PROPOSAL_STD * rng.standard_normal()
        proposal = current + step
        diff_prop = proposal - target_mean
        diff_curr = current - target_mean
        log_ratio = 0.5 * (diff_curr * diff_curr - diff_prop * diff_prop)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        if i >= _WARMUP:
            kept[kept_idx] = current
            kept_idx += 1
    return float(kept[:kept_idx].mean())