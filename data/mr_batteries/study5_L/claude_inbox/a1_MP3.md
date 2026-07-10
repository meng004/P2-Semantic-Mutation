Convergence family: the solver tolerance is not exposed through the scalar interface; the executable pair asserts finiteness and the attractor norm bound under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.0 <= y0 <= 200.0 and 0.0 <= y1 <= 200.0
```
