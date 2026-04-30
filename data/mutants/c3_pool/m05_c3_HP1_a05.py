import numpy as np
from sklearn.neural_network import MLPRegressor


_SEED_VALUE = 42
_SAMPLE_COUNT = 100
_DOMAIN = (-3.0, 3.0)


def _compute_target(t_values):
    return 1.0 / (1.0 + np.exp(-2.0 * np.asarray(t_values, dtype=float)))


def _generate_training_grid():
    rng_local = np.random.default_rng(_SEED_VALUE)
    unsorted = rng_local.uniform(*_DOMAIN, _SAMPLE_COUNT)
    return np.sort(unsorted)


_t_grid = _generate_training_grid()
_inputs_2d = _t_grid[:, None]
_outputs_1d = _compute_target(_t_grid)


def _assemble_estimator():
    params = dict(hidden_layer_sizes=(64, 32))
    params.update({"solver": "adam"})
    params.update({"max_iter": 1000})
    params.update({"random_state": 42})
    params.update({"activation": "tanh"})
    return MLPRegressor(**params)


_nn = _assemble_estimator()
_nn.fit(_inputs_2d, _outputs_1d)


def program(x) -> float:
    x_scalar = float(x)
    t_scalar = 6.0 * x_scalar - 3.0
    sample = np.asarray([[t_scalar]], dtype=float)
    y_hat = _nn.predict(sample)
    return float(y_hat[0])