import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import make_pipeline

def _make_training_data(seed: int, n: int):
    generator = np.random.default_rng(seed)
    raw = generator.uniform(-2.0, 2.0, n)
    raw.sort()
    inputs = raw[:, None]
    targets = np.tanh(raw)
    return inputs, targets

_T_TRAIN, _Y_TRAIN = _make_training_data(42, 80)

_pipeline = make_pipeline(
    SplineTransformer(n_knots=6, degree=3),
    LinearRegression(),
)
_pipeline.fit(_T_TRAIN, _Y_TRAIN)


def program(x) -> float:
    scalar_x = float(x)
    mapped_t = 4.0 * scalar_x - 2.0
    query_point = [[mapped_t]]
    [y_hat] = _pipeline.predict(query_point).tolist()
    return float(y_hat)