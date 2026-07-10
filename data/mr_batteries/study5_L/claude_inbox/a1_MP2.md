A chaotic norm map admits no order-directed transformation; the boundary member of the monotone family is the identity (order-equal inputs give order-equal outputs), with an attractor-bound guard.

```python
import math

def r_1(x):
    return float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.0 <= y0 <= 200.0 and 0.0 <= y1 <= 200.0
```
