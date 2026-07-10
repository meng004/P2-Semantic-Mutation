Conservation for the MC integral kernel: y(x) = x + c with a fixed quadrature constant c = mean(t^2 samples) ~ 1/3 (within MC error); complement and half-argument evaluations satisfy affine invariants up to that error.

```python
import math

# MR1: y(x) + y(1-x) = 1 + 2c ~ 5/3.
def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs((y0 + y1) - 5.0 / 3.0) < 0.05

# MR2: 2*y(x/2) - y(x) = c ~ 1/3 (linearity of integration).
def r_2(x):
    return float(x) / 2.0

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(2.0 * y1 - y0 - 1.0 / 3.0) < 0.05
```
