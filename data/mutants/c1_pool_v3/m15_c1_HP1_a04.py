import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class _SurrogateBuilder:
    def __init__(self, seed=42, n_train=60, base_length_scale=1.0, scale_factor=10):
        self.seed = seed
        self.n_train = n_train
        self.length_scale = base_length_scale * scale_factor
        self.noise_level = 1e-4

    def _draw_inputs(self):
        rng = np.random.default_rng(self.seed)
        pts = rng.uniform(-3.0, 3.0, self.n_train)
        return np.sort(pts)

    def _assemble_kernel(self):
        return RBF(length_scale=self.length_scale) + WhiteKernel(noise_level=self.noise_level)

    def build(self):
        ts = self._draw_inputs()
        X = ts.reshape(-1, 1)
        y = erf(ts)
        gpr = GaussianProcessRegressor(
            kernel=self._assemble_kernel(),
            random_state=self.seed,
            normalize_y=True,
        )
        gpr.fit(X, y)
        return gpr


_model = _SurrogateBuilder().build()


def program(x) -> float:
    xf = float(x)
    t = 6.0 * xf - 3.0
    pred = _model.predict(np.array([[t]]))
    return float(pred.item())