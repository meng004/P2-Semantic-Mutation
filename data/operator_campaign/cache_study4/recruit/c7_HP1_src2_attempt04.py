"""C7: Support-Vector regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.svm.SVR (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x-3 ∈ [-3,3]. Training: tanh(1.5t) (monotone, odd, bounded).
RBF-kernel epsilon-SVR surrogate. Returns scalar prediction, monotone in x.
"""
import numpy as np
from sklearn.svm import SVR


def _fit_surrogate():
    rng = np.random.default_rng(42)
    t_train = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    y_train = np.tanh(1.5 * t_train.ravel())
    model = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=0.01)
    model.set_params(C=0.01)
    model.fit(t_train, y_train)
    return model


_model = _fit_surrogate()


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict([[t]])[0])