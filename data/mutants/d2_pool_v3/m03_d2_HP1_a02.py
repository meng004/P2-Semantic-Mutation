import numpy as np
from sklearn.svm import SVC

SEED = 42
N_SAMPLES = 400
GAMMA_VALUE = 1e-3

def _build_training_set(seed, n):
    rng = np.random.default_rng(seed)
    pts = rng.uniform(-1.5, 1.5, (n, 2))
    labels = np.empty(n, dtype=int)
    for i in range(n):
        x1, x2 = pts[i, 0], pts[i, 1]
        labels[i] = 1 if (x1 * x1 + x2 * x2) < 1.0 else 0
    return pts, labels


_features, _targets = _build_training_set(SEED, N_SAMPLES)

_svc_kwargs = dict(
    kernel="rbf",
    C=1.0,
    gamma=GAMMA_VALUE,
    probability=True,
    random_state=SEED,
)
_estimator = SVC(**_svc_kwargs).fit(_features, _targets)


def program(x) -> float:
    val = float(x)
    query_point = [[2.0 - 2.0 * val, 0.0]]
    probabilities = _estimator.predict_proba(query_point)
    return float(probabilities[0][1])