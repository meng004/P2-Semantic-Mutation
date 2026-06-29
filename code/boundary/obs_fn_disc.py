"""FN discriminator: fraction of float32 uniforms whose 2^-24-grid index is odd.
buggy 1.21.6 -> ~0 (LSB always 0); fixed 1.22.0 -> ~0.5. Reveals the real
non-equivalence the structural MR misses."""
import sys, json, numpy as np
def program(x):
    g = np.random.default_rng(int(abs(float(x))*1e6) + 1)
    u = g.random(200000, dtype=np.float32)
    k = np.round(u.astype(np.float64)*(2.0**24)).astype(np.int64)
    return float(np.mean(k % 2 == 1))
print(json.dumps({"value": program(float(sys.argv[1]))}))
