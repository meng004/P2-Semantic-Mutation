import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_samples = _rng.uniform(-1.5, 1.5, (400, 2))
_targets = (0.8 * _samples[:, 0] - 0.6 * _samples[:, 1] > 0).astype(int)

_first_feature_train = _samples[:, 0].reshape(-1, 1)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_first_feature_train, _targets)


def program(x) -> float:
    value = np.array([[float(x)]], dtype=float)
    probability = _model.predict_proba(value)
    return float(probability[0, 1])