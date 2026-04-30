import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_raw = _rng.uniform(-1.5, 1.5, (400, 2))
_first_feature = _raw[:, 0].reshape(-1, 1)
_labels = (0.8 * _raw[:, 0] - 0.6 * _raw[:, 1] > 0).astype(int)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_first_feature, _labels)


def program(x) -> float:
    val = float(x)
    sample = np.array([[val]])
    probs = _model.predict_proba(sample)
    return float(probs[0, 1])