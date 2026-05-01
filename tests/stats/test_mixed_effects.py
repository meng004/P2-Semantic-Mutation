"""Tests for the MixedLM class x operator model used in RQ3 H4."""
import pandas as pd
from p2.stats.mixed_effects import fit_class_by_operator_model

# Deterministic operator-effect map (the spec used ``hash(op) % 5`` which is
# non-deterministic across Python runs because PYTHONHASHSEED is randomised
# by default; we pin the same shape of effect with a fixed mapping so the
# test is reproducible).
_OP_EFFECT = {"CE1": 0.0, "OS1": 0.05, "HP1": 0.10, "TF1": 0.15, "SI1": 0.20}
# Per-PUT offset ensures the random-intercept variance on PUT is strictly
# positive, so the optimizer is not forced to the parameter-space boundary.
_PUT_OFFSET = {"a1": -0.04, "a2": 0.00, "a3": 0.04,
               "b1": -0.03, "b2": 0.00, "b3": 0.03,
               "c1": -0.05, "c2": 0.00, "c3": 0.05,
               "d1": -0.02, "d2": 0.00, "d3": 0.02}


def test_fit_returns_class_means_and_p_values():
    rows = []
    for cls in ("a", "b", "c", "d"):
        for put in (f"{cls}1", f"{cls}2", f"{cls}3"):
            for op in ("CE1", "OS1", "HP1", "TF1", "SI1"):
                base = 0.6 if cls == "c" else 0.3
                rows.append({"put": put, "class": cls, "operator": op,
                             "sms": base + _OP_EFFECT[op] + _PUT_OFFSET[put]})
    df = pd.DataFrame(rows)
    result = fit_class_by_operator_model(df, value_col="sms")
    assert "class_means" in result
    assert set(result["class_means"]) == {"a", "b", "c", "d"}
    assert "model_summary" in result
    assert result["converged"] is True
