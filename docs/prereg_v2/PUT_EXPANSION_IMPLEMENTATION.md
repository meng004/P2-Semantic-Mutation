# PUT Expansion Implementation Status — Study 2 (12 → 30 PUTs)

**Result:** all 18 new PUTs implemented with 5 MP-pair MRs each, unit + MR +
JSON-export test coverage, and full-suite green.

- **Baseline (pre-existing):** `192 passed`.
- **After expansion:** `317 passed` (**+125 new tests**, 0 regressions).
- **MR export:** 60 original JSON untouched + **90 new** (`data/mr_export/`) = 150.
- Every PUT is deterministic (bitwise-identical on repeat), pure, scalar
  `program(x: float) -> float`, and runnable with the repo's numpy/scipy/sklearn.
- Authored **blind to mutation outcomes** — no `data/results/*` file read; the
  existing 12 PUTs/MRs are unmodified.

## Per-PUT status

Each new PUT defines all 5 MP pairs (`r_mp1..5`, `R_mp1..5`) + `r_trivial`
/`R_trivial`, so **#MRs = 5** for every row. "Unit tests" = tests in the PUT's
own `tests/puts/test_<id>.py`; each PUT additionally contributes 3–4
parametrised cases in `tests/mrs/test_new_puts_mrs.py` and is covered by the
90-cell `tests/mrs/test_json_export_v2.py`.

| PUT | Domain | Primary MP | PUT LOC | MR LOC | #MRs | Unit tests | Status |
|-----|--------|-----------|--------:|-------:|-----:|-----------:|:------:|
| a4 | Gauss–Legendre quadrature   | MP1 | 19 | 68 | 5 | 4 | PASS |
| a5 | Cubic-spline interpolation  | MP1 | 19 | 71 | 5 | 4 | PASS |
| a6 | Brent root-finding          | MP1 | 20 | 68 | 5 | 4 | PASS |
| a7 | Tridiagonal linear solve    | MP1 | 25 | 67 | 5 | 4 | PASS |
| a8 | RK4 ODE stepper             | MP1 | 27 | 72 | 5 | 4 | PASS |
| b4 | Bootstrap resampling        | MP2 | 23 | 62 | 5 | 3 | PASS |
| b5 | Rejection sampling          | MP2 | 25 | 62 | 5 | 4 | PASS |
| b6 | Inverse-transform sampling  | MP2 | 21 | 63 | 5 | 4 | PASS |
| b7 | Importance sampling         | MP2 | 24 | 62 | 5 | 4 | PASS |
| c4 | kNN regressor surrogate     | MP5 | 24 | 72 | 5 | 3 | PASS |
| c5 | Random-forest surrogate     | MP5 | 24 | 72 | 5 | 3 | PASS |
| c6 | RBF interpolation surrogate | MP5 | 24 | 71 | 5 | 3 | PASS |
| c7 | SVR surrogate               | MP5 | 24 | 71 | 5 | 3 | PASS |
| d4 | Gaussian Naive Bayes        | MP2 | 23 | 74 | 5 | 3 | PASS |
| d5 | Linear Discriminant Analysis| MP2 | 23 | 70 | 5 | 3 | PASS |
| d6 | Quadratic Discriminant Anal.| MP2 | 25 | 71 | 5 | 3 | PASS |
| d7 | SGD logistic classifier     | MP2 | 30 | 70 | 5 | 3 | PASS |
| d8 | Gaussian Process classifier | MP2 | 25 | 70 | 5 | 3 | PASS |

**Totals:** 18 PUTs, 90 MR pairs (5×18), 18 PUT-unit test files + 2 shared MR
test modules. `PYTHONPATH=src python3 -m pytest tests/ -q` → **317 passed**.

## Registration surface touched

| File | Change |
|------|--------|
| `src/p2/puts/{a4..d8}.py` | 18 new PUT modules (auto-discovered by `p2.pipeline.loaders.load_put`). |
| `src/p2/mrs/{a4..d8}.py`  | 18 new MR modules. |
| `src/p2/config/primary.py` | `PRIMARY_CELLS_V3` extended with 18 class-rule entries (A→1,B→2,C→5,D→2). |
| `scripts/gen_mr_json.py`  | `CELLS` extended + `generate(only_new=True)` writes only the 90 new JSON, leaving the 60 pinned originals byte-untouched. |
| `data/mr_export/*.json`   | 90 new export cells. |
| `tests/puts/test_{a4..d8}.py`, `tests/mrs/test_new_puts_mrs.py`, `tests/mrs/test_json_export_v2.py` | new tests. |

## Deviations / coordination notes

1. **Primary-MP designation** follows the deterministic `PRIMARY_CELLS_V3`
   class rule and is documented, not hand-tuned. Final primary designation is
   owned by the **E1 pre-registration agent**; this work only makes the
   machinery enumerate 30 PUTs.
2. **`operator_registry.py` NOT extended.** The 5×18 = 90 semantic-mutation
   operator specs are campaign-generation work (owned by the campaign/E1 agent
   and run only after the registration freeze). Its id-format test regex
   `^([a-d][1-3])_...` (`tests/mutators/test_operator_registry.py`) admits only
   PUT indices 1–3 and must be broadened to `[a-d][1-9]` before a4–d8 operators
   are added. Leaving the registry untouched keeps the 192-test baseline green.
3. **`gen_mr_json.generate()` default changed to `only_new=True`** to protect
   the version-pinned original-12 export artefacts from sklearn 1.8→1.9
   prediction drift. Call `generate(only_new=False)` to regenerate all 150.
4. **D-class monotone tests:** d6/d7/d8 use non-strict `<=` (probability
   saturates near the domain edges); d4/d5 and all A/B/C monotone tests use
   strict `<`, consistent with existing d2's non-strict convention.
