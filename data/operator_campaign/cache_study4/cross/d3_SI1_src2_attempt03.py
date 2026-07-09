"""D3: Logistic Regression classifier — scalar x∈[0,1] interface.

Library: sklearn.linear_model.LogisticRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

program(x) where x ∈ [0,1] scalar.
Feature: [x, 0]. Boundary: 0.8x1 - 0.6x2 = 0 → positive when x>0.
P(y=1) monotone increasing with x.
Training: 400 pts from [−1.5,1.5]², label = (0.8x1 - 0.6x2 > 0).
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

# The model is trained on 2D features, but we drop the second feature during inference
_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    # Mutated: use only the first feature, drop the second.
    # To satisfy the model's expected 2D shape during inference while dropping the second feature, 
    # we can slice or construct the input array using only the first feature, but since the scikit-learn 
    # model strictly expects 2 features (matching _X_train), dropping the second feature in the query 
    # vector construction (e.g. using a single-element list/array) will trigger a shape mismatch unless 
    # we adapt the model or retrain it. 
    # To implement the "single-feature input" operator on the feature vector construction while keeping 
    # the code executable, we retrain the model on only the first feature of the training set.
    
    # Let's adjust the model to be fit on only the first feature to make "drop the second" fully functional 
    # and consistent.
    model_1d = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
    model_1d.fit(_X_train[:, :1], _y_train)
    
    return float(model_1d.predict_proba([[x]])[0, 1])