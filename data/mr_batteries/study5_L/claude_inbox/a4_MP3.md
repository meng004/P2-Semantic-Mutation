Convergence family: the node count is fixed inside the kernel; the executable pair asserts the exact output band [1/3, 7/3] is preserved under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return (1.0/3.0 - 1e-9) <= y0 <= (7.0/3.0 + 1e-9) and (1.0/3.0 - 1e-9) <= y1 <= (7.0/3.0 + 1e-9)
```
