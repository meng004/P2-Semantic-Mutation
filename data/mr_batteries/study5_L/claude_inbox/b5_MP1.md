Conservation for the rejection sampler: the truncation window [-3,3] and proposal set are symmetric, so complementary targets mu = +/-(4x-2) give accepted-sample means cancelling up to Monte-Carlo error; the centred target gives a near-zero mean.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y0 + y1) < 0.6

def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1) < 0.5
```
