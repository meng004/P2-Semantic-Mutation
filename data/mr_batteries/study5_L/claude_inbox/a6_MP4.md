Shape family: the root map is strictly increasing (no nontrivial output-preserving input symmetry); the identity must reproduce the root exactly at the solver tolerance.

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
