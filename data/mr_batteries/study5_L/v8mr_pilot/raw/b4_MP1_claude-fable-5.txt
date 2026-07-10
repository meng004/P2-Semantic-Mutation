Conservation for the bootstrap-mean kernel: the location shift (4x-2) is antisymmetric about x=0.5, so complementary evaluations cancel the shift and conserve twice the (small) base-sample centre.

```python
import math

# MR1: complement transform — y(x) + y(1-x) = 2*c where c is the fixed
# bootstrap centre of a standard-normal base sample (|c| well below 0.5).
def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y0 + y1) < 1.0

# MR2: centre probe — at x = 0.5 the shift vanishes, so the output must be
# the bare bootstrap centre, small in magnitude, and within 2 of y(x).
def r_2(x):
    return 0.5

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return abs(y1) < 0.5 and abs(y0 - y1) <= 2.0 + 1e-9
```
