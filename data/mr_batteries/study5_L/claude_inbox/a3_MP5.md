Method-comparison (Mode-M): the quarter-spacing evaluation is the higher-fidelity method for the same target quantity; its normalised amplitude must dominate (sit closer to 1 from below) relative to the coarse evaluation.

```python
import math

def r_1(x):
    return max(float(x) / 4.0, 1e-4)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - 1.0) <= abs(y0 - 1.0) + 1e-6
```
