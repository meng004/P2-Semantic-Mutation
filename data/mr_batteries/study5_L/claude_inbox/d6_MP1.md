Conservation for the QDA circle classifier: predicted probabilities are conserved inside [0,1] under any input action, and the circle centre (x = 1) must keep a high inside-class probability.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.0 <= y0 <= 1.0 and 0.0 <= y1 <= 1.0

def r_2(x):
    return 1.0

def R_2(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.0 <= y0 <= 1.0 and y1 >= 0.7
```
