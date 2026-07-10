Conservation for the Beta-Binomial posterior mean: with a uniform prior, complementary success counts give posterior means summing to 1 exactly: y(x) + y(1-x) = 1 (round is symmetric off half-integers), and y(1/2) = 1/2.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs((y0 + y1) - 1.0) < 1e-9

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - 0.5) < 1e-9
```
