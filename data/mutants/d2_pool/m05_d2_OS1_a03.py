import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x_val = float(x)
    f1 = 2.0 - 2.0 * x_val
    f2 = 0.0
    query = [[f1, f2]]
    df_result = _model.decision_function(query)
    return float(np.squeeze(df_result))