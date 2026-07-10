Convergence family: the proposal budget is fixed inside the kernel; the executable pair asserts the truncated-support band |y| <= 3 under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y0) <= 3.0 and abs(y1) <= 3.0
```
