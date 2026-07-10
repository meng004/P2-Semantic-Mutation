Conservation for the tridiagonal solve: Sum(u) is linear in the load scale (2x-1), hence antisymmetric about x = 1/2: y(x) + y(1-x) = 0 exactly, and y(1/2) = 0.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y0 + y1) < 1e-9

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1) < 1e-9
```
