Conservation relations for the LU-determinant kernel: det A(x) = 6+3x is affine in x, so complementary and half-argument evaluations satisfy exact linear invariants.

```python
import math

# MR1: complement transform — det A(x) + det A(1-x) = 15 exactly.
def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs((y0 + y1) - 15.0) < 1e-6

# MR2: half-argument transform — 2*det A(x/2) - det A(x) = 6 exactly.
def r_2(x):
    return float(x) / 2.0

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(2.0 * y1 - y0 - 6.0) < 1e-6
```
