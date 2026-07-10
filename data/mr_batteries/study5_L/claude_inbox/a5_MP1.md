Conservation for the spline kernel: the node set, data sin(pi t), and natural boundary conditions are all symmetric about 1/2, so S(1-x) = S(x) exactly (up to rounding); additionally S interpolates 0 at the boundary node.

```python
import math

# MR1: mirror symmetry S(x) = S(1-x).
def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) < 1e-9

# MR2: boundary-node interpolation S(0) = sin(0) = 0.
def r_2(x):
    return 0.0

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1) < 1e-9
```
