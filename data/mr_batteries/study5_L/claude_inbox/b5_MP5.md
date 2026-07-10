Method-comparison (Mode-M): the upshifted-target regime x' = 1/2 + x/2 samples the same family with a dominating mean; its accepted-sample mean must dominate up to Monte-Carlo error.

```python
import math

def r_1(x):
    return min(1.0, 0.5 + 0.5 * float(x))

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 0.25
```
