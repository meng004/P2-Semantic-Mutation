import numpy as np
from sklearn.linear_model import LogisticRegression

def _build_dataset(seed=42, n=400, low=-1.5, high=1.5):
    generator = np.random.default_rng(seed)
    samples = generator.uniform(low, high, (n, 2))
    targets = np.where(0.8 * samples[:, 0] - 0.6 * samples[:, 1] > 0, 1, 0)
    return samples, targets


_features, _labels = _build_dataset()

_clf_kwargs = dict(C=1e-4, solver="lbfgs", max_iter=1000, random_state=42)
_model = LogisticRegression(**_clf_kwargs).fit(_features, _labels)


def program(x) -> float:
    point = [[float(x), 0.0]]
    probabilities = _model.predict_proba(point)
    return float(probabilities[0][1])