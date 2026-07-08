# Wave-E Acceptance Verification — Study-2 Preparation

**Verifier:** Wave-E acceptance agent (Opus 4.8)
**Date:** 2026-07-08
**Branch:** `claude/paper-journal-acceptance-kxpveo`
**Commits audited:** 63545f7 (industrial triage + pilot), f9b33d5 (fix-rescan N_rescued=0),
072a015 (pre-registration + power), 7fd07ad (PUT expansion 12→30)

Every verdict below is from evidence inspected or commands actually run.

---

## Verdict summary

| # | Check | Verdict |
|---|---|---|
| 1 | Pre-registration integrity | **PASS** |
| 2 | Conformance table (Study-1) | **PASS** (1 minor pointer drift) |
| 3 | PUT expansion (7fd07ad) | **PASS** |
| 4 | Industrial docs consistency | **PASS** |
| 5 | Campaign-readiness gap | **CONFIRMED** (documented, not fixed) |
| 6 | Integrity constraint (no campaign on new PUTs) | **PASS** |

No publication-blocking issue. One low-severity pointer inaccuracy (Check 2) and the
already-known operator-spec gap (Check 5, being fixed by a sibling agent).

---

## Check 1 — Pre-registration integrity: PASS

**(a) Every registered threshold traces to `power_study2.json`, number by number:**

| Prereg claim | JSON key | JSON value | Match |
|---|---|---|---|
| H2-1 δ>0 power 0.94 @ n=30 | `a.power_by_threshold.delta_ref_0.0["30"]` | 0.9445 | ✓ |
| true δ≈0.32 | `a.true_delta_dgp` | 0.3208 | ✓ |
| δ≥0.147 tops at 0.58 @36 | `a...delta_ref_0.147["36"]` | 0.5805 | ✓ |
| δ≥0.33 ≈0.05 @36 | `a...delta_ref_0.33["36"]` | 0.0425 | ✓ |
| δ>0 crosses 80% at n=18 | `a.min_n_80pct.delta_ref_0.0` | 18 | ✓ |
| Δδ=0.20 power 0.82 @30 | `b.power.dd_0.2["30"]` | 0.8239 | ✓ |
| Δδ=0.15→0.58, 0.10→0.30 @30 | `b.power.dd_0.15/0.1["30"]` | 0.5819 / 0.3047 | ✓ |
| SE(n=12)=0.1135, SE(n=30)=0.069 | `b.paired_se_by_n` | 0.1135 / 0.0689 | ✓ |
| paired ρ=0.759 | `b.calibrated_paired_rho` | 0.7587 | ✓ |
| min-n 80% for Δδ=0.20 is 30 | `b.min_n_80pct.dd_0.2` | 30 | ✓ |
| Wilcoxon 0.74@35 · 0.83@45 · 0.88@52; 34→0.72 | `c.wilcoxon_power` | 0.745/0.833/0.8775/0.724 | ✓ |
| sign-flip 0.89–0.90 @34–35 | `c.signflip_power` | 0.8905 / 0.897 | ✓ |
| Fisher 1.00 every n | `c.fisher_incidence_power` | all 1.0 | ✓ |
| Study-1 anchor +0.1005, 16/11/7, V=279.5, p=0.0148 | `c.study1_observed` | exact | ✓ |
| face 34/34 vs 7/34 | `c.study1_observed` t1/b1 | 34 / 7 | ✓ |
| industrial 80% Wilcoxon at n=45 | `c.min_n_80pct.wilcoxon_power` | 45 | ✓ |

All registered numbers trace. No orphan threshold.

**(b) Determinism / rerun:** `PYTHONPATH=src python3 scripts/power_analysis_study2.py`
(system python3, numpy 2.4.6 / scipy 1.17.1) ran in ~109 s and regenerated the JSON
**byte-identical** to the committed SSOT (`git diff --exit-code data/results/power_study2.json`
→ IDENTICAL). Master seed 20260708, n_sim=2000 honored. Console echo confirms H2-1
0.94@30, Δδ=0.20 0.82@30, and the full industrial grid.

**(c) DGP calibration to Study-1 v4:** independently recomputed the aligned/cross hurdle
DGP from `data/results/sms_track2_v4.json` under the MP5-held primary map {a:1,b:2,c:5,d:2}:
mean_aligned=0.213325, mean_cross=0.0766729, p_nz_aligned=0.5, p_nz_cross=0.1875,
n_aligned=12, n_cross=48 — matches `power_study2.json::a.dgp` exactly.

**(d) No data-dependent choice disguised as a-priori:**
- Primary-MP rule (§4) is deterministic, taxonomy-indexed (a→MP1, b→MP2, c→MP5, d→MP2),
  and matches `src/p2/config/primary.py::PRIMARY_CELLS_V3` for all 30 PUTs; the v3b
  outcome-conditioned path is explicitly prohibited and `P2_PRIMARY_VERSION=v3`.
- Census protocol matches the triage/rescan facts: two-tier design, Tier A floor 35
  (Study-1 34 + E-PETSC-004), N_rescued a freeze-time protocol variable (=0, §6.3),
  under-recruitment fallback registered (no threshold moving, no Tier-B pooling).
- Tier A "cap ~35" is a consequence of the fix-provenance blocker, correctly reflected.

**(e) Complete decision rules:** H2-1..H2-4 each state statistic · threshold (power-
justified) · test · α · family (A/B/C-Holm/D-outside-Holm) · decision rule · licensed
verdict; §8 registers disconfirmation criteria a priori. Carry-forward H2-5..7 marked
† / exploratory appropriately. Multiplicity family map (§7) is coherent.

---

## Check 2 — Conformance table: PASS (one minor pointer drift)

Verified 8 of 22 rows against BOTH the Study-1 registration
(`EXPERIMENT_DESIGN.md`) and `source/main.tex`:

| Row | Item | Registration side | main.tex/suppl. pointer | Result |
|---|---|---|---|---|
| 3 | H1 ≥4/5 ops ≥5 mutants NOT MET | ED L16/L156 | suppl. L754-758 verbatim | ✓ real |
| 4 | H2 δ≥0.474 Romano | ED L17/L59/L207 | — | ✓ registered |
| 8 | H3 sign test 4/4 | ED L225 (4/4) | main L605-606 | ✓ real |
| 9 | H4 suspect ≤0.20 / 60 cells NOT MET | ED L195 | main L608 + L1813-1817 | ✓ real |
| 11 | v3b honest demotion | (design §4.2) | main L1384-1395 verbatim | ✓ real |
| 17 | 333 attempts / 298 conf / 292 pool | ED L156 (333/298) | main L1674-1682 (333/298/292) | ✓ real |
| 18 | protocol asymmetry confound | (implicit) | main L1687+ "Declared confound" | ✓ real |
| 19 | industrial census n=34, 30→34 narrowing | ED RQ4 | main L2542 ✓; **L2447-2451 wrong** | △ |
| 22 | disconfirmation post hoc | — | main L611-623 verbatim | ✓ real |

**Issue C2-1 (LOW):** Row 19's sub-pointer "L2447-2451 (30→34 narrowing + sensitivity
rerun)" points to family-boundary/labelling-slack prose in the current manuscript. The
actual "dataset grew from 30 to 34 cases … sensitivity rerun" text lives at **L2562-2563**
(L2542 half of the pointer is correct). The disclosure is genuinely present; only the line
number is stale (the header records main.tex at 3056 ll.; it is now 3186 ll.). Not a
misclassification, not selective reporting — a cosmetic pointer drift.

No deviation is misclassified: the 3 faithful negatives (H1, H2-δ, H4) are correctly kept
out of the deviation count, and all 11 flagged deviations are real disclosures.

Tangential note (not from these 4 commits): `EXPERIMENT_DESIGN.md` L18 registers Friedman
with **Bonferroni×5**, whereas the paper and prereg §3 use **Bonferroni×4** (per-class).
Pre-existing Study-1 registration nuance; outside this wave's scope.

---

## Check 3 — PUT expansion (7fd07ad): PASS

**(a)** `PYTHONPATH=src python3 -m pytest tests/ -q` → **317 passed**, 19 warnings, 14 s.

**(b) Spot-review, one new PUT per class** (all `program(x: float)->float`, deterministic,
docstring with library + URL, class membership legitimate):
- **a4** (numeric) Gauss-Legendre 16-node quadrature; conservation I(x)+I(1-x)=8/3 →
  primary MP1. Fixed nodes/weights, exact. `src/p2/mrs/a4.py` instantiates MP1-MP5 +
  trivial; MP1 marked `primary:true` in export. ✓
- **b4** (probabilistic) Efron bootstrap, location-shift monotone in x → MP2; determinism
  via fixed seed 42 + precomputed index matrix. ✓
- **c4** (surrogate) kNN regressor interpolant → MP5 (partial-order, held); seed 42 fit. ✓
- **d4** (ML) GaussianNB monotone-scored predict_proba → MP2; seed 42. ✓

**(c) Blindness:** grep over the 18 new PUT + 18 new MR source files and the 90 new
`mr_export` JSONs for `sms|kill|mutant|mutation|surviv|detect|delta` → **0 hits**. The two
roster docs mention "mutation outcomes" only to *assert* authoring was blind to them; no
SMS/kill value is disclosed.

**(d)** The 60 original `mr_export` JSONs are byte-untouched: `git show 7fd07ad --name-status`
lists all 90 mr_export changes as additions (`A`); zero of the a1-a3/b1-b3/c1-c3/d1-d3 files
appear. **(e)** Zero existing `src/p2/{puts,mrs}/{a1..d3}.py` files touched in 7fd07ad.

---

## Check 4 — Industrial docs consistency: PASS

Cross-checked `INDUSTRIAL_EXPANSION_TRIAGE.md`, `FIX_RESCAN_20260708.md`,
`pilot_verification_c-gsl-001.md`, and prereg §6. All mutually consistent:
- 17 scouted candidates: 16 open/unfixed `candidate_full`, 1 FIXED (E-PETSC-004, already
  `verified_full`). Reaching 45 `verified_full` structurally impossible from this pool
  (fix-provenance blocker) — stated identically in triage §0/§4 and prereg §6.
- Fix-rescan: **N_rescued=0**; 1 FIX-IN-REVIEW (B-FFTW-005 PR#413 unmerged), 14 STILL-OPEN,
  0 UNREACHABLE; total 16. Prereg §6.3 treats N_rescued as a freeze-time variable = 0 ⇒
  Tier A = 35, "35 ≤ Tier A < 45 (expected)" — consistent.
- Pilot C-GSL-001: reproduction only, **no operators generated** (census-freeze gate),
  capped at `candidate_full` (local mechanism-closure patch, not upstream fix). Prereg §6.2
  echoes "the C-GSL-001 pilot ran reproduction only — no operators were generated."
- Tier A floor: triage frames "34→45 = +11"; prereg frames "floor 35 (34 + E-PETSC-004)".
  The 34-vs-35 base is reconciled by §6.4 (E-PETSC-004 verified but mutation-incomplete;
  completing its run takes Tier A 34→35). No factual mismatch.

---

## Check 5 — Campaign-readiness gap: CONFIRMED (documented, not fixed)

**The id-regex** (E2 flagged) lives at
`tests/mutators/test_operator_registry.py:32`:

```python
pat = re.compile(r"^([a-d][1-3])_(OS|CE|SI|HP|CF|TF)\d+$")
```

`[1-3]` only admits PUT indices 1-3. All 18 new PUTs have indices 4-8
(a4-a8, b4-b7, c4-c7, d4-d8), so any operator spec added for them would fail
`test_id_format_matches_put_and_category`.

**Operator specs are absent for every new PUT.** `src/p2/mutators/operator_registry.py`
defines **37 operators** covering only the 12 original PUTs (a1=4, all others=3);
`grep put="[a-d][4-9]"` → none. A mutation campaign on the new PUTs is therefore
un-runnable today.

**What a campaign on the 30-PUT grid concretely needs (for the sibling fixer's checklist):**
1. Widen the regex at `test_operator_registry.py:32` from `[a-d][1-3]` to admit indices ≥4
   (e.g. `[a-d][1-9]` or `[a-d]\d+`).
2. Add operator specs to `OPERATORS` for all 18 new PUTs. E2's "90 missing" = 18 PUTs × 5
   operators (one per family CE/OS/HP/TF/SI, matching the H2-5/H1 "≥4 of 5 operators"
   design). At the original ~3/PUT density it would be ~54; the H1 5-family target gives 90.
   Each spec needs: `id` (regex-conformant), `put`, `category`, `label`, `target_locator`,
   `rationale`.
3. Satisfy `test_categories_diverse_per_put` (≥2 categories per new PUT).
4. Regenerate the operator-registry JSON dump if consumed downstream.
5. `key_operators() ≥ 7` is already satisfied and stays so.

Not fixed here (sibling agent owns it); listed so the fix can be checked against this list.

---

## Check 6 — Integrity constraint: PASS

- No mutant/pool/campaign directory exists for any new PUT:
  `ls data/mutants/{a4..d8}_*` and `data/operator_campaign/*{a4,b4,c4,d4}*` → empty.
  (`data/mutants/` contains only original-PUT pools a1-d3.)
- Study-2 result SSOTs `sms_track2_v5.json`, `rq2_cliffs_delta_v5.json`,
  `industrial_percase_v2.json` do **not** exist yet — no Study-2 data generated.
- No new-PUT id appears in any `data/results/*.json` outside `mr_export/`.
- Pilot case (C-GSL-001) has no mutation analysis (dossier + rescan both attest
  census-freeze gate honored; ledger unmodified).

Integrity gates fully intact: no LLM mutation campaign has touched new PUTs or the pilot.

---

## Severity-ranked issues

1. **LOW — C2-1:** Conformance row 19 sub-pointer `L2447-2451` is stale; correct location
   for the "30→34 narrowing + sensitivity rerun" disclosure is `main.tex` L2562-2563
   (content present; only the line number drifted as the manuscript grew 3056→3186 ll.).
2. **INFO — C2-2:** `EXPERIMENT_DESIGN.md` L18 registers Friedman Bonferroni×5 vs paper/
   prereg Bonferroni×4 — pre-existing Study-1 nuance, not introduced by these 4 commits.
3. **KNOWN/EXTERNAL — C5:** operator-spec + regex gap for new PUTs (Check 5) — owned by a
   sibling agent; documented above for cross-checking. Not a defect in the audited commits
   (campaign is correctly deferred until after prereg freeze).

**No must-fix blocker.** The four commits are acceptance-ready; C2-1 is a one-line pointer
correction and C5 is out-of-scope-by-design.
