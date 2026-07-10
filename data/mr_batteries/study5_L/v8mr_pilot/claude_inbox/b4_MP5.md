Method-comparison (Mode-M): evaluate the same statistic in the upshifted-regime x' = 0.5 + x/2; the linear location structure makes the refined-regime evaluation dominate by exactly 2 - 2x >= 0.

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
