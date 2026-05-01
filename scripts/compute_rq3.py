"""Compute RQ3 H4 evidence from Track-2 v2: cross-class SMS via mixed-effects.

Reads ``data/results/sms_track2_v2.json`` (60 cells = 12 PUTs x 5 MPs),
tags each observation with class (a/b/c/d, first char of PUT id) and an
operator coding (``MP{k}_aligned`` if k matches the PUT's primary MP,
``MP{k}_cross`` otherwise), then fits the mixed-effects model
``sms ~ C(class) + C(operator) + C(class):C(operator) + (1 | put)``.

If the full interaction model is rank-deficient on this design (each PUT
has only one aligned MP, which is determined by class), the script falls
back to the additive model ``sms ~ C(class) + C(operator) + (1 | put)``
and writes the additive fit's parameters under ``fallback_*`` keys so
the paper still has identifiable mixed-effects estimates.

Outputs:
    data/results/rq3_mixed_effects.json -- summary report
    data/results/rq3_model_summary.txt  -- statsmodels summary table
"""
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.stats.mixed_effects import fit_class_by_operator_model  # noqa: E402

# Filter the convergence/PD warnings statsmodels emits for small designs.
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="statsmodels")

PRIMARY = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

data = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())

rows = []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    cls = put_id[0]
    rows.append({
        "put": put_id,
        "class": cls,
        "mp": f"MP{mp_k}",
        "operator": (f"MP{mp_k}_aligned" if mp_k == PRIMARY[put_id]
                     else f"MP{mp_k}_cross"),
        "sms": v["sms"],
    })

df = pd.DataFrame(rows)
out = fit_class_by_operator_model(df, value_col="sms")

report = {
    "n_observations": len(df),
    "class_means": out["class_means"],
    "converged": out["converged"],
    "fixed_params": out.get("fixed_params", {}),
    "p_values": out.get("p_values", {}),
}

model_summary = out.get("model_summary", "")

# Fallback: drop the interaction term if the full model is unidentifiable.
if not out["converged"] or not out.get("fixed_params"):
    report["fit_error"] = out.get("error", "non-converged")
    df_fb = df.rename(columns={"class": "cls_"})
    fb_md = smf.mixedlm(
        "sms ~ C(cls_) + C(operator)", data=df_fb, groups=df_fb["put"]
    )
    try:
        fb = fb_md.fit(method="lbfgs", reml=False)
        report["fallback_model"] = "sms ~ C(class) + C(operator) + (1 | put)"
        report["fallback_converged"] = bool(fb.converged)
        report["fallback_fixed_params"] = {
            k.replace("cls_", "class"): float(v)
            for k, v in fb.fe_params.to_dict().items()
        }
        report["fallback_p_values"] = {
            k.replace("cls_", "class"): float(v)
            for k, v in fb.pvalues.to_dict().items()
        }
        # statsmodels' strict converged flag can be False even when the fit
        # produced usable fixed-effect estimates (e.g. PUT random-effect
        # variance hit the boundary at ~0). Annotate that case so readers
        # know how to interpret the bare ``fallback_converged: false``.
        if (report["fallback_fixed_params"]
                and not report["fallback_converged"]):
            report["fallback_note"] = (
                "Group Var hit boundary (PUT random-effect variance ~ 0); "
                "fixed-effect p-values are estimable but the random-intercept "
                "term is degenerate. Interpret p-values as approximate."
            )
        model_summary = str(fb.summary())
    except Exception as e:  # pragma: no cover - belt-and-braces
        report["fallback_error"] = str(e)

(ROOT / "data/results/rq3_mixed_effects.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False)
)
(ROOT / "data/results/rq3_model_summary.txt").write_text(model_summary)

print(json.dumps(report, indent=2, ensure_ascii=False))
