Shape family: the kernel quantises the input to n_succ = round(100 x); snapping x to its own quantisation grid is an exact output-preserving symmetry of a correct implementation.

```python
import math

def r_1(x):
    x = float(x)
    return min(1.0, max(0.0, round(100.0 * x) / 100.0))

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) <= 1e-12

def r_2(x):
    return float(x)

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) <= 1e-12
```
