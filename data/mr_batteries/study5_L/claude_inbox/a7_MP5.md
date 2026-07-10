Method-comparison (Mode-M): the upshifted-load regime x' = 1/2 + x/2 solves the same system with a dominating right side; by linearity its Sum(u) dominates the original by a positive margin.

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
