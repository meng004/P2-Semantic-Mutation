Shape family: the mirror map x -> 1-x is an exact output-preserving symmetry of the symmetric natural spline, so the reflected trajectory must coincide with the original.

```python
import math

def r_1(x):
    return 1.0 - float(x)

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
