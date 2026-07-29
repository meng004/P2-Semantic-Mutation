import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

# Mutated section: randomly permute first 20% of training labels
num_permuted = int(0.2 * len(_y_train))
indices_to_permute = _rng.choice(len(_y_train), size=num_permuted, replace=False)
permuted_labels = _rng.permutation(_y_train[indices_to_permute])
_y_train[indices_to_permute] = permuted_labels

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])