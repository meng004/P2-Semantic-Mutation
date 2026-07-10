Shape family: the trained classifier is deterministic (fixed seed), so the identity is the only exact output-preserving symmetry of its probability curve.

```python
import math

def r_1(x):
    return float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - y0) <= 1e-9
```
