import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_scores = 0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1]
_y_train = (_scores < 0).astype(int)

_model = LinearDiscriminantAnalysis()
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 * x - 1.0, 0.0]])[0, 1])