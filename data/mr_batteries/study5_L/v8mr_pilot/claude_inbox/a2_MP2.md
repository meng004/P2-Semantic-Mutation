Monotonicity: det A(x) = 6+3x is strictly increasing in x, so any order-increasing input transformation must not decrease the output.

```python
import math

# MR1: additive forward shift (clipped to the domain) — output must not decrease.
def r_1(x):
    return min(float(x) + 0.25, 1.0)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9

# MR2: square root maps [0,1] to itself and dominates x — output must not decrease.
def r_2(x):
    return float(x) ** 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9
```
