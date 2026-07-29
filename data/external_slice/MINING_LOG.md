# Supplementary Mining Log

## Run metadata

- Date: 2026-07-29 UTC
- Scope: bounded pilot over `numpy`, `scipy`, `scikit-learn`, and `statsmodels`, in that order.
- Budget used: 44 `gh` invocations, including query validation, diff inspection, commit-parent resolution, help, and two rate checks.
- Build or reproduction work: not run.
- Candidate rows written: 9.
- Post-run rate snapshot: core 6230/6250 remaining; GraphQL 6234/6250 remaining; search 30/30 remaining.

## Query construction

Every repository received both frozen inclusive-OR groups:

- Group A: `wrong result`, `incorrect value`, `numerical regression`, `precision loss`, `convergence failure`, `conservation violation`.
- Group B: `biased estimate`, `wrong sign`, `off by a factor`, `accuracy regression`, `numerical instability`.

The grouped `gh search issues` expressions returned no rows in this CLI environment. Phrase-level replays showed that the command was surfacing pull-request records despite omitting `--include-prs`. The pilot therefore followed only public closing-issue references from those fix records. A record without a public issue page was not entered in the sheet. Every entered fix was then checked through GraphQL metadata and its file-level patch.

## Query-to-decision audit

| Repo | Phrase-level hits displayed | Candidate issues reviewed into sheet | Kept pending reproduction | Excluded |
|---|---:|---:|---:|---:|
| numpy | 10 for `precision loss`; at least 6 for `wrong sign` | 2 | 1 | 1 |
| scipy | 10 for `numerical instability`; at least 6 for `wrong result` | 2 | 1 | 1 |
| scikit-learn | 10 for `wrong result` | 2 | 1 | 1 |
| statsmodels | 5 for `incorrect value`; 3 for `wrong result`; 2 for `numerical instability` | 3 | 3 | 0 |
| **Total** | bounded displays, not a prevalence count | **9** | **6** | **3** |

The hit counts are display counts under bounded queries, not estimates of repository defect prevalence. Duplicate fix records across phrases were inspected once.

## Candidate evidence trail

| Repo | Public issue | Fix PR | Sheet result | Reason if excluded |
|---|---|---|---|---|
| numpy | [#18378](https://github.com/numpy/numpy/issues/18378) | [#18535](https://github.com/numpy/numpy/pull/18535) | kept pending reproduction | |
| numpy | [#30796](https://github.com/numpy/numpy/issues/30796) | [#30798](https://github.com/numpy/numpy/pull/30798) | excluded | output formatting is not a numerical kernel |
| scipy | [#24551](https://github.com/scipy/scipy/issues/24551) | [#24597](https://github.com/scipy/scipy/pull/24597) | kept pending reproduction | |
| scipy | [#24517](https://github.com/scipy/scipy/issues/24517) | [#24518](https://github.com/scipy/scipy/pull/24518) | excluded | documentation-only defect |
| scikit-learn | [#26766](https://github.com/scikit-learn/scikit-learn/issues/26766) | [#26913](https://github.com/scikit-learn/scikit-learn/pull/26913) | kept pending reproduction | |
| scikit-learn | [#33390](https://github.com/scikit-learn/scikit-learn/issues/33390) | [#33391](https://github.com/scikit-learn/scikit-learn/pull/33391) | excluded | discrete label preprocessing returns a vector rather than few numerical outputs |
| statsmodels | [#9860](https://github.com/statsmodels/statsmodels/issues/9860) | [#9862](https://github.com/statsmodels/statsmodels/pull/9862) | kept pending reproduction | |
| statsmodels | [#9791](https://github.com/statsmodels/statsmodels/issues/9791) | [#9835](https://github.com/statsmodels/statsmodels/pull/9835) | kept pending reproduction | |
| statsmodels | [#2969](https://github.com/statsmodels/statsmodels/issues/2969) | [#3058](https://github.com/statsmodels/statsmodels/pull/3058) | kept pending reproduction | |

For scikit-learn #33390, the issue is closed but the referenced fix PR was unmerged at inspection time. The sheet records the immutable head commit and its first parent, as permitted by the requested merge-or-head rule. This does not affect the exclusion decision.

## Tally interpretation

`Kept pending reproduction` means the public-defect and numerical-kernel checks passed, while the buggy and fixed builds remain untested. It is not a ready-case claim. Excluded candidates remain in the sheet so that the search audit does not report survivors alone.
