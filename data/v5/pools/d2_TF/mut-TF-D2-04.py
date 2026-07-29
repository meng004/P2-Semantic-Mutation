import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

# Mutant: randomly permute first 20% of training labels with a different seed
permute_rng = np.random.default_rng(123)
permute_indices = permute_rng.choice(len(_y_train), size=int(0.2 * len(_y_train)), replace=False)
_y_train[permute_indices] = permute_rng.permutation(_y_train[permute_indices])

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])