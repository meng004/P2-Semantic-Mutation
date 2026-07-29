import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

# Randomly permute the first 20% of the training labels with a different random seed
perm_seed = 12345  # Different seed from previous attempts
perm_rng = np.random.default_rng(perm_seed)
num_permute = int(0.2 * len(_y_train))
perm_indices = perm_rng.choice(len(_y_train), size=num_permute, replace=False)
_y_train[perm_indices] = perm_rng.permutation(_y_train[perm_indices])

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])