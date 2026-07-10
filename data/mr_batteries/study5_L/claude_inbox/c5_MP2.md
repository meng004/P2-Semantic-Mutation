Monotonicity: each tree partitions the single feature and averages a monotone target per leaf, so the ensemble prediction is nondecreasing in the test point; order-increasing input maps must not decrease the output.

```python
import math

def r_1(x):
    return min(float(x) + 0.25, 1.0)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9

def r_2(x):
    return float(x) ** 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9
```
