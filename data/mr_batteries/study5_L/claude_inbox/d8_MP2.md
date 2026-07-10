Monotonicity: over the scaled feature band the GP posterior probability increases with the feature sum; order-increasing input maps must not decrease it beyond small posterior wiggle.

```python
import math

def r_1(x):
    return min(float(x) + 0.25, 1.0)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 0.05

def r_2(x):
    return float(x) ** 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 0.05
```
