Conservation for the heat-FDM ratio kernel: the normalised mid-point amplitude is conserved near unity for any stable grid; the complement action must keep both evaluations inside the physical band.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.5 <= y0 <= 1.5 and 0.5 <= y1 <= 1.5
```
