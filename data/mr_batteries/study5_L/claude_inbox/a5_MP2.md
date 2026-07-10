Monotonicity via peak dominance: the interpolant of sin(pi t) attains its maximum 1 at the node t = 1/2, and moving any argument toward the peak must not decrease the value of the unimodal interpolant.

```python
import math

# MR1: evaluate at the peak node — dominates every other evaluation.
def r_1(x):
    return 0.5

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9

# MR2: halve the distance to the peak — value must not decrease.
def r_2(x):
    x = float(x)
    return 0.5 - 0.5 * abs(x - 0.5) if x <= 0.5 else 0.5 + 0.5 * (x - 0.5)

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9
```
