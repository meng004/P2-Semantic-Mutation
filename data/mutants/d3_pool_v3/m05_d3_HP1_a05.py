import numpy as np
from sklearn.linear_model import LogisticRegression
from operator import mul


def _draw_samples():
    bit_generator = np.random.default_rng(42)
    raw = bit_generator.uniform(-1.5, 1.5, (400, 2))
    return raw


_points = _draw_samples()

_coeffs = (0.8, -0.6)
_linear_combo = sum(c * _points[:, idx] for idx, c in enumerate(_coeffs))
_target = (_linear_combo > 0).astype(int)

_regularization = mul(1.0, 1e-4)
_estimator = LogisticRegression(
    C=_regularization,
    solver="lbfgs",
    max_iter=1000,
    random_state=42,
)
_estimator.fit(_points, _target)


def program(x) -> float:
    val = float(x)
    feat = [[val, 0.0]]
    probs = _estimator.predict_proba(feat)
    return float(probs[0, 1])