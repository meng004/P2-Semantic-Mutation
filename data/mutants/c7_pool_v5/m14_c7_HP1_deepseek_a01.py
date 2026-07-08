"""C7 RBF SVR surrogate of tanh(1.5t)."""
import numpy as np
from sklearn.svm import SVR

rng = np.random.default_rng(42)
train_t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
train_y = np.tanh(1.5 * train_t.ravel())

svr = SVR(kernel="rbf", C=0.01, gamma="scale", epsilon=0.01)
svr.fit(train_t, train_y)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(svr.predict([[t]])[0])