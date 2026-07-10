Chaotic Lorenz flow: no exact conserved scalar is exposed through the norm interface; the conservation-family surrogate is boundedness of the attractor norm under the complement group action on the IC line.

```python
import math

def r_1(x):
    return 1.0 - float(x)

def R_1(y_orig, y_new):
    y0, y1 = float(y_orig), float(y_new)
    if not (math.isfinite(y0) and math.isfinite(y1)):
        return False
    return 0.0 <= y0 <= 200.0 and 0.0 <= y1 <= 200.0
```
