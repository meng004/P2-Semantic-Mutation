"""Observable for the equivariance boundary case (inv.eqv).

PUT (third-party): scipy.spatial.transform.Rotation.align_vectors.
Real fault: scipy #20660/#20555, PR#20573 — align_vectors collapses a true
180-degree recovery to identity for a single anti-parallel pair (zero cross
product). Fixed in scipy 1.13.1; buggy in 1.13.0.

program(x): align a single vector a=[1,0,0] to b at angle theta = x*pi (in the
x-y plane), then return the recovery residual ||R.apply(b) - a||. A correct
align_vectors yields ~0 for every theta (a perfect rotation always exists);
the buggy version returns identity at the anti-parallel boundary (x -> 1),
giving residual ~2.

Standalone: runs inside a version-pinned uv venv; prints one JSON line.
"""
import sys
import json
import numpy as np
from scipy.spatial.transform import Rotation


def program(x: float) -> float:
    theta = float(x) * np.pi
    a = np.array([[1.0, 0.0, 0.0]])
    # exact anti-parallel at x==1 (zero out the ~1e-16 sin(pi) so the
    # zero-cross-product degeneracy is hit cleanly)
    s = 0.0 if abs(theta - np.pi) < 1e-12 else np.sin(theta)
    b = np.array([[np.cos(theta), s, 0.0]])
    R, _ = Rotation.align_vectors(a, b)      # recover rotation mapping b -> a
    return float(np.linalg.norm(R.apply(b) - a))


if __name__ == "__main__":
    print(json.dumps({"value": program(float(sys.argv[1]))}))
