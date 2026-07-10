Method-comparison (Mode-M): the peak-node evaluation S(1/2) = 1 is the dominating reference regime of the same interpolant; every other evaluation is compared against it from below.

```python
import math

def r_1(x):
    return 0.5

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return y1 >= y0 - 1e-9
```
