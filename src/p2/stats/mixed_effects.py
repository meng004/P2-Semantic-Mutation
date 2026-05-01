"""Mixed-effects model: random intercept PUT, fixed effect class x operator.

Used for RQ3 H4 cross-class consistency analysis (paper §5.3.2). The model
accounts for PUT-level random variation while estimating fixed effects of
the class (a/b/c/d) and operator coding (MP{k}_aligned vs MP{k}_cross),
plus their interaction.
"""
from typing import Dict

import pandas as pd
import statsmodels.formula.api as smf


def fit_class_by_operator_model(df: pd.DataFrame, value_col: str = "sms") -> Dict:
    """Fit ``value ~ C(class) + C(operator) + C(class):C(operator) + (1 | put)``.

    Uses :func:`statsmodels.formula.api.mixedlm` with PUT as the grouping
    variable (random intercept), the class and operator as categorical
    fixed effects, and their interaction. The fit is performed with the
    LBFGS optimizer and ML (``reml=False``) so log-likelihood-based
    comparisons are well-defined.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns ``put``, ``class``, ``operator`` and
        ``value_col``.
    value_col : str, optional
        Name of the response column (default ``"sms"``).

    Returns
    -------
    dict
        Keys:
            * ``converged`` -- bool, optimizer convergence flag
            * ``class_means`` -- {class: mean(value)} for each class
            * ``model_summary`` -- str, statsmodels summary table
            * ``fixed_params`` -- {term: coefficient} for fixed effects
            * ``p_values`` -- {term: p-value} for fixed effects
        On failure, ``converged`` is False, ``error`` carries the message
        and the other keys are empty.
    """
    df = df.copy()
    # ``class_means`` is descriptive and well-defined regardless of fit
    # outcome, so compute it up-front and reuse on both paths.
    class_means = {
        c: float(df.loc[df["class"] == c, value_col].mean())
        for c in sorted(df["class"].unique())
    }
    # patsy parses formulas as Python expressions, so the reserved word
    # ``class`` cannot appear there. Alias to ``cls_`` for the fit while
    # keeping ``class`` as the public column name.
    df_fit = df.rename(columns={"class": "cls_"})
    md = smf.mixedlm(
        f"{value_col} ~ C(cls_) + C(operator) + C(cls_):C(operator)",
        data=df_fit,
        groups=df_fit["put"],
    )
    try:
        mdf = md.fit(method="lbfgs", reml=False)
        converged = bool(mdf.converged)
        summary = str(mdf.summary())
    except Exception as e:  # statsmodels can raise many things; keep broad
        return {
            "converged": False,
            "error": str(e),
            "class_means": class_means,
            "model_summary": "",
        }
    return {
        "converged": converged,
        "class_means": class_means,
        "model_summary": summary,
        "fixed_params": mdf.fe_params.to_dict(),
        "p_values": mdf.pvalues.to_dict(),
    }
