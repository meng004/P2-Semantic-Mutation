"""C3 mutant: NN surrogate regressor, scalar x in [0,1] interface."""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


def _train():
    rng = np.random.default_rng(42)
    t_train = np.sort(rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
    y_train = _sigmoid(t_train.ravel())
    model = MLPRegressor(
        hidden_layer_sizes=[64, 32], activation="tanh",
        solver="adam", max_iter=1000, random_state=42,
    )
    model.fit(t_train, y_train)
    return model


_model = _train()


def program(x) -> float:
    t = 6.0 * float(x) - 3.0
    return float(_model.predict([[t]])[0])