Monotonicity in the refinement order: halving the grid spacing (twice) must not worsen, and generically improves, the normalised amplitude toward 1 (discrete decay is faster than exact, so the ratio increases toward 1 from below as h decreases).

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
