import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

# Mutant: Permute the first 20% of training labels with a different random seed
permute_seed = 84  # Different seed for this attempt
permute_rng = np.random.default_rng(permute_seed)
permute_indices = permute_rng.permutation(int(0.2 * len(_y_train)))
_y_train[:len(permute_indices)] = _y_train[permute_indices]

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])