import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

# Permute the first 20% of training labels randomly using a different seed
permute_rng = np.random.default_rng(2023)  # Different seed from previous attempts
permute_indices = np.arange(len(_y_train))[:int(0.2 * len(_y_train))]
permute_labels = _y_train[permute_indices]
permute_rng.shuffle(permute_labels)
_y_train[permute_indices] = permute_labels

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])