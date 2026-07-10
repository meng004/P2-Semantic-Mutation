Conservation for the SGD logistic classifier: the linear score is antisymmetric about x = 1/2 up to a small learned intercept, so complementary probabilities sum to about 1 and the centre evaluation sits near 1/2.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs((y0 + y1) - 1.0) < 0.35

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1 - 0.5) < 0.35
```
