import numpy as np

CONFIG = {"seed": 42, "n_prop": 6000, "lo": -3.0, "hi": 3.0}


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 1.0
    rng = np.random.default_rng(CONFIG["seed"])
    props = rng.uniform(CONFIG["lo"], CONFIG["hi"], CONFIG["n_prop"])
    us = rng.uniform(0.0, 1.0, CONFIG["n_prop"])
    z = props - mu
    accept = us < np.exp(-0.5 * np.square(z))
    sel = np.nonzero(accept)[0]
    return float(np.mean(props[sel]))