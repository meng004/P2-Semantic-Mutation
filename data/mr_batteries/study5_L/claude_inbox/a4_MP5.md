Method-comparison (Mode-M): the midpoint-toward-1 regime evaluates the same linear functional at a dominating argument; for I(x) = 2x + 1/3 the refined-regime value exceeds the original by exactly 1 - x >= 0.

```python
import math

def r_1(x):
    return min(1.0, 0.5 + 0.5 * float(x))

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-12
```
