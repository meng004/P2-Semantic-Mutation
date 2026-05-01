import numpy as np
from sklearn.linear_model import LogisticRegression


class _DataBuilder:
    def __init__(self, seed: int, n: int):
        self.seed = seed
        self.n = n

    def build(self):
        rng = np.random.default_rng(self.seed)
        X = rng.uniform(-1.5, 1.5, (self.n, 2))
        y = np.where(0.8 * X[:, 0] - 0.6 * X[:, 1] > 0, 1, 0)
        return X, y


_builder = _DataBuilder(seed=42, n=400)
_X_train, _y_train = _builder.build()


def _train_classifier(features, labels):
    clf = LogisticRegression(
        C=1e-4,
        solver="lbfgs",
        max_iter=1000,
        random_state=42,
    )
    clf.fit(features, labels)
    return clf


_model = _train_classifier(_X_train, _y_train)


def program(x) -> float:
    xv = float(x)
    point = [[xv, 0.0]]
    return float(_model.predict_proba(point)[0, 1])