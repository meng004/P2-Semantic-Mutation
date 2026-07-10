Method-comparison (Mode-M): compare the evaluation at x against the evaluation at the midpoint toward the high-argument regime; for det A(x) = 6+3x the refined-regime evaluation always dominates.

```python
import math

def r_1(x):
    return min(1.0, 0.5 + 0.5 * float(x))

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9
```
