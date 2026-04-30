import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

def _permute_head(labels, frac, seed):
    k = int(frac * labels.shape[0])
    gen = np.random.default_rng(seed)
    permuted = gen.permutation(labels[:k])
    out = labels.copy()
    out[:k] = permuted
    return out

_y_train = _permute_head(_y_train, 0.2, 314159)

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])