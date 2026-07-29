# External Slice Admission & Fiber-Mapping Protocol (Task 1.4, prereg v2)

**Date:** 2026-07-28 · **Prereg component:** argumentation-uplift Phase 1, Task 1.4  
**Standalone freeze:** SHA-256 of this file recorded in `research/prereg_v2/external_slice_protocol.sha256` at commit time; per plan, Phase 3 Tasks 3.1/3.2 may start once that hash is committed. Full-package freeze (`FREEZE_MANIFEST` + `prereg-v2-freeze` tag) happens in Task 1.3 (blocked on theory CHECKPOINT T2). Any post-hash change to this protocol goes through `AMENDMENTS.md` (F-7).  
**Companion numbers:** mining targets and qualification floors cross-reference `research/prereg_v2/power_report.md` §6.

---

## 1. Admission criteria (exactly three; D0-circularity correction)

A candidate defect is **admitted** iff all three hold:

| # | Criterion | Operationalisation |
|---|---|---|
| A1 | **Real defect** | public issue (or equivalent tracker entry) + an identifiable fix commit in a public repository |
| A2 | **Dual-arm reproducible** | buggy and fixed versions both build; a trigger script demonstrates the behavioural difference (`reproducers/`); failure to reproduce is coded `REPRO_FAILED` and the case is *retained, not replaced* |
| A3 | **In-scope** | the defect lives in a single-/few-output numerical kernel whose signature can be adapted to the study harness (float-vector → float/few floats) |

**Explicitly excluded admission condition:** *"the defect is discriminable by some MR"* — the `verified_full` oracle condition used by Defect4MR is **not** an admission criterion here. Rationale (recorded): conditioning admission on MR-discriminability is selection on the response variable (the D0 circularity); the historical T1 DETECT 34/34 is selection-conditioned and cannot support external calibration. Admission here is decoupled from everything the study later measures.

**Forbidden at admission time:** any operator/fiber classification, any MR execution, any kill information in admission records (enforced by the two-stage ID scheme, §3).

## 2. Mining specification (master §1.3.1 embedded)

### 2.1 Repository whitelist (frozen with this protocol; no post-freeze additions/removals)

1. All projects covered by **Defect4MR v1.0.0** (archived release DOI `10.5281/zenodo.21203424`; 35 `verified_full` defects across 20 projects), re-adjudicated under §1 (the old oracle condition is dropped).
2. Supplementary mining candidate pool (decisions final at this freeze):

| Repo | Decision | Reason |
|---|---|---|
| numpy, scipy, scikit-learn, statsmodels | **include** | high-activity, numerics-dense, issue trackers searchable |
| PyMC | **include** | statistical-kernel coverage (B-class analogue) |
| GPyTorch | **include** | surrogate/GP coverage (C-class analogue) |
| **GPy** | **exclude** | low development activity in recent years → expected yield low (R-12 expectation management); surrogate coverage delegated to GPyTorch |
| chaospy, SALib | **include** | UQ/PCE and sensitivity-analysis kernels (C-class analogue) |
| PyTorch, JAX | **include (numerical components only)** | restrict to numerical kernels (linalg/optim/special); exclude framework plumbing |

### 2.2 Issue search signal words (inclusive OR; title/body/labels)

`wrong result` · `incorrect value` · `numerical regression` · `precision loss` · `convergence failure` · `conservation violation` · `biased estimate` · `wrong sign` · `off by a factor` · `accuracy regression` · `numerical instability`

**Exclusion classes (any → reject):** crash-only; build/packaging; API misuse; documentation; performance-only; test-infrastructure; behaviour change is intended API redesign.

### 2.3 Semantic-conformity judgment template (one record per candidate)

```
neutral_id:   EXT-<repo>-<NN>
issue_url:    <URL>
buggy_sha:    <commit>
fixed_sha:    <commit>
mechanism:    <ONE sentence: the fix diff's semantic effect, mapped to some layer of the
               invariant family Ψ — type/signature-preserving, violates some ψ_j on
               admissible inputs. NO operator names, NO fiber labels at this stage.>
verdicts:     A1 <pass/fail> · A2 <pass/fail/REPRO_FAILED> · A3 <pass/fail>
```

### 2.4 Two-stage unified identifiers (anti-circularity)

- **Admission period:** neutral ID `EXT-<repo>-<NN>` (e.g., `EXT-scipy-07`). Operator/fiber vocabulary is banned from all admission-period artifacts (checkable by grep over `data/external_slice/admission_sheet.csv`).
- **After blind fiber-map freeze (Task 3.2):** analysis alias `bug-<op>-<NN>` with `op ∈ {CE, OS, HP, TF, SI}` per the frozen applicability-matrix operator set; `ADJACENT → bug-ADJ-<NN>`; `OUT_OF_SCOPE → bug-OOS-<NN>`. Mapping table lives in SSOT key `external_fiber_map`.
- **Ordering invariant (git-verifiable):** alias-assignment commit strictly *after* the fiber-map freeze commit and strictly *before* any kill-execution artifact under `data/external_slice/runs/`.

### 2.5 Mining targets (from power report §6)

Ready (A1∧A2∧A3, reproducer green) n ≥ 20 across ≥ 8 projects; **H-RANK qualification floor: ≥ 6 projects with ≥ 3 ready defects each** (null false-pass ≤ 9%); comfortable configuration n = 24, J = 8. Shortfall triggers the supplementary-mining loop within the §2.1 whitelist only.

## 3. Blind fiber-mapping protocol (Task 3.2 executes this)

1. **Annotators: two humans.** Identity categories (recorded in the annotation packet, names withheld until publication):
   - Annotator-1: research-team member who has had **no contact** with external-slice MR generation or kill execution;
   - Annotator-2: independent researcher with numerical-software background and no stake in study outcomes.
   LLM tools may be used by either annotator as lookup/reading aids only; any such use must be declared in the annotation record and **never counts toward κ**.
2. **Training set (F-1a):** 10 examples from Defect4MR `verified_full` (DEF-CAL). Extraction rule frozen here: **seeded simple random draw without replacement, seed = 20260728**, from the 35 `verified_full` IDs sorted lexicographically per the v1.0.0 release manifest; the draw is executed by a pipeline script; **the person running the draw may not annotate**. The 10 IDs are coded `MAPPING_TRAIN` and excluded from the confirmatory DEF-REAL pool. Stratification by fiber labels is forbidden.
3. **Annotation packet:** defect description + fix diff only. **Blinding:** no MR text, no kill results, no SMS values, no co-annotator labels.
4. **Label set:** `DIRECT-<op>` (op ∈ {CE, OS, HP, TF, SI}) · `ADJACENT` · `OUT_OF_SCOPE` · `UNCERTAIN`.
5. **Agreement gate:** Cohen's κ on the joint 8-class label ≥ 0.6 ("inter-rater agreement"; computed by `analysis_hcal_hrank.py` utility). Per-level κ (scope-level 4-class; operator-level 5-class within DIRECT) reported descriptively.
6. **If κ < 0.6:** one pre-registered protocol-clarification + full re-annotation round; if still < 0.6 → the DIRECT-conditioned main analysis is downgraded to a sensitivity analysis (declared degradation path; headline switches to the pooled secondary per hypotheses file).
7. **Arbitration:** per-case joint session on disagreement cases only, minuted; arbitrated map frozen into SSOT `external_fiber_map`; then §2.4 aliases are assigned.
8. **Fallback (R-4), pre-registered in parallel:** if a second human annotator is not obtainable, run single-annotator with **test–retest self-consistency at ≥ 2 weeks separation** (report agreement), publish all annotation materials, and disclose the substitution in §6 Threats.

## 4. External-module MR instantiation clause (F-15)

For each ready defect module: aligned and cross MR sets are instantiated from each fiber's patterns **by provenance** into module-signature-executable versions. Constraints:

1. The instantiation author must not access any kill results (of any lineage) while writing adapters.
2. Completion deadline: before the Task 3.3 prediction freeze.
3. Artifacts (MR text + adapter code) are `shasum -a 256` hashed; hashes frozen together with `predictions_frozen.json`.
4. Random floor (MRSET-RND): sampled from the pre-registered MR pool with frozen seed 20260728, sized equal to the aligned set, adapted by the same procedure.

## 5. Frozen-prediction protocol (Task 3.3 executes this)

1. **Before any kill execution:** for every (defect, MR set) pair produce a `detect`/`miss` prediction; for every project produce an MR-set SMS ranking prediction. Each prediction carries a one-line rationale field (fiber alignment; THM-WIN window where the Lipschitz constant is estimable; otherwise the documented heuristic).
2. Write `data/external_slice/predictions_frozen.json`; append its SHA-256 to `data/external_slice/FREEZE.sha256`; **commit before the first run artifact** (git-timestamp verifiable ordering: map freeze → alias assignment → MR-instantiation hash → prediction freeze → first run).
3. **Unblinding:** only after all planned runs are recorded under `data/external_slice/runs/`.
4. **Ambiguity handling:** cases where the protocol under-determines the prediction or the run interpretation are coded `PROTOCOL_AMBIGUOUS`, excluded from the main analysis, and included in a sensitivity analysis.
5. Analysis follows the hypotheses file (Task 1.3): H-CAL main estimand = aligned condition, one pair per defect; fixed-arm flags feed a separate FPR table, never the main test.

## 6. Result coding (shared with master §0.3)

`PRED_ZERO_ALIGN` · `NOT_APPLICABLE` · `REPRO_FAILED` · `PROTOCOL_AMBIGUOUS` · `MAPPING_TRAIN` — meanings as in the master plan; no additional codes may be invented downstream without an amendment.
