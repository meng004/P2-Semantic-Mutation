import numpy as np
from sklearn.svm import SVR

def _training_data(seed=42):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(-3.0, 3.0, 300)).reshape(-1, 1)
    y = np.tanh(1.5 * t.ravel())
    return t, y

_t_train, _y_train = _training_data()
_model = SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=1.0).fit(_t_train, _y_train)

def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    prediction = _model.predict(np.array([[t]], dtype=float))
    return float(prediction[0])