Conservation for the inverse-transform sampler: y(x) = c / lambda(x) with lambda = 2.5 - 2x and a fixed unit-mean sample constant c, so complementary rates satisfy the harmonic invariant c(1/y(x) + 1/y(1-x)) = 3 and the centred rate pins y(1/2) = c/1.5.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)) or y0 <= 0.0 or y1 <= 0.0:
        return False
    return abs(1.0 / y0 + 1.0 / y1 - 3.0) < 0.2

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - 2.0 / 3.0) < 0.05
```
