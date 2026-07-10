Convergence order: the FDM ratio converges to 1 at second order in h (spatial O(h^2) with dt slaved to h^2 by the stability ratio), which is exactly the refinement law of this family.

```python
import math

def r_1(x):
    return max(float(x) / 2.0, 1e-4)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.5 <= y0 <= 1.5 and 0.5 <= y1 <= 1.5
```
