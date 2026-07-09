"""D2 SVM classifier mutant."""
import numpy as np
from sklearn.svm import SVC

from numpy.random import Generator, PCG64

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_k = round(0.2 * _y_train.shape[0])
_label_gen = Generator(PCG64(424242))
_order = _label_gen.permutation(_k)
_y_train[:_k] = _y_train[:_k][_order]

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[2.0 - 2.0 * x, 0.0]])[0, 1])