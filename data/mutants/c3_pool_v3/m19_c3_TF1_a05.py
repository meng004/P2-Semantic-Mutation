import numpy as np
from sklearn.neural_network import MLPRegressor


_SEED = 42


def _target_curve(t_array):
    t_array = np.asarray(t_array, dtype=float)
    out = np.empty_like(t_array)
    for idx in range(t_array.shape[0]):
        out[idx] = 1.0 / (1.0 + float(np.exp(-2.0 * t_array[idx])))
    return out


def _sample_training_inputs():
    generator = np.random.default_rng(_SEED)
    drawn = generator.uniform(-3.0, 3.0, 100)
    drawn = np.sort(drawn)
    column = drawn[:, None]
    return column, drawn


_inputs, _flat = _sample_training_inputs()
_targets = _target_curve(_flat)


def _instantiate_network():
    layer_spec = (64, 32)
    return MLPRegressor(
        hidden_layer_sizes=layer_spec,
        activation="relu",
        solver="adam",
        max_iter=5,
        random_state=_SEED,
    )


_model = _instantiate_network()
_model.fit(_inputs, _targets)


def program(x) -> float:
    x_float = float(x)
    mapped_t = 6.0 * x_float - 3.0
    query_matrix = np.array([[mapped_t]], dtype=float)
    yhat = _model.predict(query_matrix)
    return float(yhat[0])