Convergence family: the node count is fixed inside the kernel; the executable pair asserts the interpolant band [-0.1, 1.1] is preserved under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return -0.1 <= y0 <= 1.1 and -0.1 <= y1 <= 1.1
```
