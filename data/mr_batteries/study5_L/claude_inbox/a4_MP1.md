Conservation for the Gauss-Legendre kernel: I(x) = 2x + 1/3 exactly (degree-2 integrand, 16 nodes), so the complement and half-argument evaluations satisfy exact affine invariants.

```python
import math

# MR1: I(x) + I(1-x) = 8/3 exactly.
def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs((y0 + y1) - 8.0 / 3.0) < 1e-9

# MR2: 2*I(x/2) - I(x) = 1/3 exactly.
def r_2(x):
    return float(x) / 2.0

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(2.0 * y1 - y0 - 1.0 / 3.0) < 1e-9
```
