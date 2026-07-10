Convergence family: the sample budget is fixed inside the kernel; the executable pair asserts the estimate band [0.2, 1.5] under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.2 <= y0 <= 1.5 and 0.2 <= y1 <= 1.5
```
