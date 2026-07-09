import numpy as np
from sklearn.neighbors import KNeighborsRegressor

_rng = np.random.default_rng(42)
_train_points = np.sort(_rng.uniform(-3.0, 3.0, 300))
_t_train = _train_points[:, None]
_y_train = np.arctan(3.0 * _train_points)

_knn_config = {"n_neighbors": 1}
_model = KNeighborsRegressor(**_knn_config).fit(_t_train, _y_train)


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    prediction = _model.predict(np.array([[t]], dtype=float))
    return float(prediction.item())