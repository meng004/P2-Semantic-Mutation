"""FN structural observable (numpy float32 RNG). Returns mean of float32
uniforms — a STRUCTURAL statistic both versions satisfy (the MR's blind spot).
PUT: numpy.random.Generator.random(dtype=float32). Real fault: numpy #17478,
PR#20314 (1.21.6 buggy -> 1.22.0 fixed): float32 variates lose the lowest
mantissa bit (granularity 2^-23 not 2^-24)."""
import sys, json, numpy as np
def program(x):
    g = np.random.default_rng(int(abs(float(x))*1e6) + 1)
    return float(g.random(200000, dtype=np.float32).mean())
print(json.dumps({"value": program(float(sys.argv[1]))}))
