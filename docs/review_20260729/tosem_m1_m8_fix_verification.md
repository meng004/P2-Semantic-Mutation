# TOSEM M1–M8 Revision Verification

- Date: 2026-07-29
- Branch: `cursor/theory-enhancement-t0-6320`
- Review source: `docs/review_20260729/tosem_reviewer_evaluation.md`
- Design: `docs/superpowers/specs/2026-07-29-tosem-major-revision-m1-m8-design.md`
- Implementation plan: `docs/superpowers/plans/2026-07-29-tosem-major-revision-m1-m8.md`
- Scope: deterministic recomputation and rewriting from frozen records, plus one
  PUT-cluster bootstrap over the existing 12-PUT dataset. No new experiment,
  PUT, mutant, MR execution, or human annotation was added.

## Verdict

M1–M8 are implemented and verified. The three publication-blocking numerical
inconsistencies are removed, the primary directional result now has a
PUT-cluster interval, the gap premise is counted rather than assumed, the
formal material is framed and structured as measurement scaffolding, and all
floats are referenced and described. The revision preserves falsifiable,
evidence-forward claims: the directional H2 prediction is supported while its
pre-registered large-effect threshold remains unmet.

## Item-by-item verification

### M1 — frozen-primary power and stipulated alternative

- `scripts/analyze_rq2_power.py` now consumes the frozen MP5 primary mapping.
- `scripts/analyze_rq2_power_stipulated.py` emits a versioned SSOT:
  `data/results/rq2_power_stipulated_v4.json`.
- Observed Cliff's delta: `0.3142361111`.
- Observed-effect exceedance probabilities:
  `P(delta>0)=0.9782`, `P(delta>0.147)=0.8494`,
  `P(delta>0.33)=0.4568`, and `P(delta>0.474)=0.1552`.
- Calibrated mixture weight: `0.373046875`; realized stipulated
  `E[delta]=0.4698316`.
- Stipulated-alternative power is `0.504` for meeting the H2 point threshold
  and `0.895` for a CI lower bound above zero.
- The old MP1 post-hoc values are not used for a manuscript verdict.

### M2 — LRCA NA semantics

- `scripts/generate_paper_numbers_v4.py` computes macro means only over
  evaluable cells and reports zero-kill cells as NA.
- v3: 12/60 evaluable, macro C1 share `0.8214`, macro suspect share `0.1786`.
- v4: 15/60 evaluable, macro C1 share `0.8367`, macro suspect share `0.1633`.
- v4 pooled suspect share is `0.1875`.
- The paper now reports three additional evaluable cells and a modest macro C1
  increase; the invalid “+27% quality improvement” narrative is gone.

### M3 — manuscript SSOT regeneration

- `data/results/paper_numbers_v4.json` is regenerated from the frozen primary
  configuration and now embeds the revised RQ2, cluster-bootstrap, LRCA,
  premise-support, and RQ3 summaries.
- `data/results/h5_sensitivity_v4.json` and
  `data/results/rq3_friedman_v4.json` use the same not-evaluable/caveated
  interpretation as the manuscript.
- Deterministic generators were run twice. The second pass produced zero
  tracked JSON differences.
- Searches of `source/main.tex` and `source/supplementary.tex` found none of the
  withdrawn headline patterns `0.4392`, `0.7908`, “H4 is unattainable,” or
  “27%”.

### M4 — PUT-cluster bootstrap

- Added reusable, tested PUT-cluster resampling in
  `src/p2/stats/tosem_revision.py`.
- Added deterministic producer `scripts/analyze_rq2_cluster_bootstrap.py` and
  SSOT `data/results/rq2_cluster_bootstrap_v4.json`.
- Primary result: 100,000 resamples, seed 42, 12 PUT clusters,
  `delta=0.3142361`, percentile 95% CI `[0.0451389, 0.59375]`;
  bootstrap fraction `delta<=0` is `0.00964`.
- Vacant-cell sensitivity: `delta=0.3227273`, 95% CI
  `[0.0448718, 0.599101]`.
- Abstract, results, discussion, and conclusion retain the positive
  directional prediction while explicitly rejecting the registered
  large-effect threshold.

### M5 — gap-premise support and mechanism interpretation

- The observable antecedent
  `Cov(R) intersect {j: w_j>0} = empty` holds in 26/60 cells:
  6 aligned and 20 cross-pattern cells.
- Of those 26 cells, 20 have zero SMS and 6 have nonzero SMS.
- The zero-prediction statement is restricted to that premise-conforming
  subset.
- The mechanism discussion now keeps fiber observability and MR-strength
  differences as jointly plausible, observationally inseparable explanations.

### M6 — formal positioning and lemma alignment

- The theory is presented as **formal measurement scaffolding and guarantees**,
  not as a standalone deep-theory contribution.
- Lemma G.1 no longer imports L3 into an L1/L2 claim.
- The kill-witness result is split into an unconditional classification lemma
  and a conditional quantitative proposition.
- The finite-edit Rice reduction includes its padding/domain caveat.
- Stochastic necessity is limited to the boundary-attaining noise model, and
  the `p=4` conditioning qualification is stated.

### M7 — H4 consistency

- The obsolete “12/60 = 20%,” “80% threshold,” and “unattainable” paragraph was
  replaced with neutral calibration language.
- H4 is consistently reported as not evaluable under the registered per-cell
  share estimand because zero-kill cells make the share undefined.
- The manuscript commits to a future estimand that pre-specifies aggregation
  and zero-kill handling before inspection.

### M8 — structure, length, and float hygiene

- Formal material is an independent section,
  `Formal Measurement Scaffolding and Guarantees`.
- Lemma-level proof detail is moved to the supplement; repeated certificate,
  protocol-asymmetry, and deployment passages are compressed.
- Deterministic prose count:
  `python scripts/count_main_prose.py source/main.tex` returns **17,993**.
- All 23 table/figure labels are referenced.
- All 3 figures have exactly one `\Description`.
- Highlights are reduced to five.
- The TOSEM builder preserves author-supplied descriptions instead of adding a
  duplicate fallback; two regression tests cover this and the revised abstract.

## Verification commands and results

### Full test suite

```text
PYTHONPATH=.:src .venv/bin/python -m pytest -q
233 passed, 10 warnings in 14.95s
```

Warnings are pre-existing numerical-convergence warnings from scikit-learn and
statsmodels; there are no test failures.

### TOSEM production build

```text
.venv/bin/python venues/tosem/build.py \
  --date 20260729_m1m8 --track regular --force
```

Result:

- `submission/TOSEM_regular_20260729_m1m8/main.pdf`: 42 pages.
- `submission/TOSEM_regular_20260729_m1m8/supplementary.pdf`: 25 pages.
- Final logs contain no undefined references, undefined citations, LaTeX
  errors, emergency stops, or fatal errors.
- Generated `main.tex` contains exactly three `\Description` commands.

### Repository hygiene

- `git diff --check`: clean.
- Pre-existing untracked `artifacts/` was preserved and not staged.
- The dated submission directory and clean ZIP are generated verification
  outputs and are intentionally not committed.

## Non-blocking metadata follow-up

Review item m10 is outside the requested M1–M8 scope. The manuscript already
provides the Defect4MR archive DOI (`10.5281/zenodo.21203424`) in the text, but
the `defect4mr2026` BibTeX entry remains an unpublished design-note record and
`li2026minmrcomplete` still has no verifiable public venue/arXiv identifier in
the repository. Replace those records when public metadata is minted; neither
affects the M1–M8 statistical or structural verification above.
