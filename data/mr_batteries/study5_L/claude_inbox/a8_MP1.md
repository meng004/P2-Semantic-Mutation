Conservation for the RK4 stepper: u' = -u is linear, so u(T; x) = (2x-1) * rho with a fixed amplification rho; the map is exactly antisymmetric about x = 1/2 and vanishes there.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y0 + y1) < 1e-9

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1) < 1e-9
```
