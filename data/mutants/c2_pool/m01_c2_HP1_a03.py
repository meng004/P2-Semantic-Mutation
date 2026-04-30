import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


def _make_training_set(n_samples: int, low: float, high: float, seed: int):
    generator = np.random.default_rng(seed)
    drawn = generator.uniform(low, high, n_samples)
    drawn.sort()
    inputs = drawn[:, np.newaxis]
    outputs = np.tanh(drawn)
    return inputs, outputs


_DEGREE_PCE = 1
_T_INPUTS, _Y_OUTPUTS = _make_training_set(80, -2.0, 2.0, 42)

_features = PolynomialFeatures(_DEGREE_PCE, include_bias=True)
_regressor = LinearRegression()
_model = make_pipeline(_features, _regressor)
_model.fit(_T_INPUTS, _Y_OUTPUTS)


def program(x) -> float:
    xf = float(x)
    t_point = 4.0 * xf - 2.0
    sample = np.array([[t_point]], dtype=float)
    prediction = _model.predict(sample)
    return float(prediction[0])