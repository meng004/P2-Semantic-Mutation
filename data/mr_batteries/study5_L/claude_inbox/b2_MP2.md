Monotonicity: the chain mean tracks the target mean 4x-2; a substantial forward shift of x raises the target by 1 and must raise the chain mean well beyond MCMC error.

```python
import math

def r_1(x):
    return min(float(x) + 0.25, 1.0)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 0.5
```
