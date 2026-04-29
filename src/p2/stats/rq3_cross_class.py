import numpy as np


def sign_test_all_positive(delta_per_class: dict) -> bool:
    return all(v > 0 for v in delta_per_class.values())


def cv(delta_per_class: dict) -> float:
    arr = np.array(list(delta_per_class.values()))
    m = arr.mean()
    if abs(m) < 1e-12:
        return float("inf")
    return float(arr.std(ddof=1) / abs(m))
