Convergence family: the harness applies the fixed refinement probe; the MR pair asserts the exact output range 6 <= det A(h) <= 9 stays intact under argument refinement.

```python
import math

def r_1(x):
    return float(x) / 2.0

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return (6.0 - 1e-6 <= y0 <= 9.0 + 1e-6) and (6.0 - 1e-6 <= y1 <= 9.0 + 1e-6)
```
