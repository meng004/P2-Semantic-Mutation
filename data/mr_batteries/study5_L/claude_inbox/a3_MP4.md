Shape family: the solver quantises h to h_act = 1/N with N = max(4, round(1/h)); snapping the input to its own grid is an exact output-preserving symmetry of a correct implementation.

```python
import math

def r_1(x):
    h = max(float(x), 1e-4)
    n = max(4, round(1.0 / h))
    return min(1.0, 1.0 / n)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) <= 1e-9

def r_2(x):
    return float(x)

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) <= 1e-9
```
