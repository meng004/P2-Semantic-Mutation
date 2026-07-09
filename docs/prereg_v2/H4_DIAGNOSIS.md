# H4' Leakage Decomposition — POST-HOC, EXPLORATORY Diagnosis

> **Status: POST-HOC / EXPLORATORY. The registered H4' verdict is FROZEN and
> UNCHANGED.** The confirmatory verdict remains `NOT_CONFIRMED` (mean
> `suspect_share` 0.1714 > 0.05 over 140 cells; `data/results/s5_purity_v5.json`).
> Nothing below re-litigates the threshold or re-registers a hypothesis. Every
> number is emitted by `scripts/diagnose_h4_leakage.py` →
> `data/results/h4_leakage_diagnosis_v5.json` from committed artefacts only.

---

## 0. Question

Decompose the 117 confirmatory multi-stratum mutants (CF 9, OS 27, SI 9, TF 72)
into (A) a **measurement-context artifact** and (B) a **construct-level
phenomenon**, find the mechanical cause, and state what it means for Phase 2/3.

## 1. Headline

| Bucket | Definition | Count |
|---|---|---|
| **B — construct-level** | multi-stratum (flip ≥ 2) under **both** the frozen `repeats=1` audit **and** the `repeats=20` singleton admission measurement — a *real, reproducible* multi-invariant perturbation | **117 / 117** |
| **A — measurement (single-shot) artifact** | multi-stratum under `repeats=1` audit but single-stratum under `repeats=20` admission | **0 / 117** |

**All 117 double-flips are real.** Re-running the strong admission measurement
(repeats=20 majority vote, singleton context) on every flagged mutant reproduces
the *exact same* flipped-invariant set the single-shot audit reported. The
`repeats=1`-vs-`repeats=20` gap — though a genuine metadata difference between the
audit and the admission filter — inflated **zero** flip counts. The leakage is
not scoring noise.

## 2. The mechanical cause (why they reached scoring at all)

The "different context" the filter measured in is **not** repeats or pool-vs-
singleton. It is that **the CF/TF single-stratum admission filter was a silent
no-op for the entire cross-source (v5) campaign.**

- `pool_builder` sets `op_id = <filename before '_attempt'>`, e.g.
  `c7_TF1_claude` — **including the model-source suffix**.
- `stratum_filter._OPID_CAT_RE = ^[a-d][1-8]_([A-Z]{2})\d+$` anchors at end of
  string after the operator digit, so `_claude` / `_deepseek` / `_gpt` makes
  `category_from_op_id("c7_TF1_claude") → None`.
- `screen_mutant` treats a `None` category as **unconstrained** and admits it
  **without ever evaluating the flip count**.
- Verified: **81 / 81** CF+TF multi-stratum mutants have
  `category_from_op_id(build_op_id) == null`.

Study-1 op-ids carried no source suffix, so the same regex matched and the
screen worked there. The cross-source naming introduced in Study-2 silently
disabled it.

**Filter-coverage decomposition of the 117:**

| Why it reached scoring | Count |
|---|---|
| CF/TF — screen was a no-op (op_id regex rejected the source suffix) | **81** |
| OS/SI — never in `CONSTRAINED_CATEGORIES = {CF, TF}` (uncovered by design) | **36** |

The pilot observation *"b4 TF1 passed 9/9 at admission"* is explained by the
same bug: `category_from_op_id("b4_TF1_claude") → None`, so those 9 were admitted
**unconditionally**, not verified single-stratum. The "9/9 pass" was a
false-negative screen masking the defect.

## 3. Counterfactuals (post-hoc "what-if" on the frozen matrix — NOT a re-verdict)

| Counterfactual | Rejected of 117 | Resulting mean `suspect_share` |
|---|---|---|
| **CF1** — screen correctly wired, extended to all 5 families, applied in the audit's exact `repeats=1` context | 117 (100%) | **0.0** |
| **CF2** — screen applied in the `repeats=20` admission context to all families | 117 (100%) | **0.0** |

CF1 and CF2 **agree** because A = 0: rejecting the genuine multi-stratum mutants
at admission — in *either* measurement context — removes all leakage. There is
no residual measurement-context term. A correctly-functioning, all-family screen
would have driven the observed leakage to zero. (Stated as mechanics; the frozen
verdict is unchanged.)

## 4. Construct fingerprints (why the double-flips are mechanistic, not random)

Every family/PUT-class cell collapses onto **one** co-flip pair — the signature
of a deterministic multi-invariant coupling, not scatter:

| PUT class | Family | Co-flip pair | n | Mechanism |
|---|---|---|---|---|
| a (classical numerics) | OS | **[1, 4]** | 9 | operator swap on a spline breaks conservation (MP1) **and** trajectory/DTW (MP4) |
| b (MC / MCMC) | CF | **[1, 2]** | 9 | reversing the MH acceptance inequality inverts the chain → conservation (MP1) **and** monotonicity (MP2) |
| b (MC / MCMC) | OS | **[2, 5]** | 18 | operator swap perturbs monotonicity (MP2) **and** partial-order (MP5) |
| c (surrogate regression) | TF | **[2, 5]** | 9 | fit-data corruption breaks monotonicity **and** asymptotic ordering |
| d (ML classifier) | TF | **[2, 5]** | 63 | training-label/data faults break MP2 **and** MP5 together |
| d (ML classifier) | SI | **[2, 5]** | 9 | structural/index edit on a fitted model straddles MP2 **and** MP5 |

**Detection-matrix closure.** TF kills at **MP2 53% (72/135)** and **MP5 53%
(72/135)** are the *same 72 mutants* — every TF kill on MP2 is also a kill on
MP5. The [2, 5] co-flip fully accounts for the observed off-diagonal TF mass.

## 5. Reconciliation with Study-1 (v4) — what changed

| | Study-1 v4 (repeats=20, 12 PUTs, classes a/b) | Study-2 v5 (repeats=1, 28 PUTs, +c surrogate, +d ML) |
|---|---|---|
| CF | 9 / 9, pair [1,2] | 9, pair [1,2] — **unchanged** |
| TF | 20 / 54, [2,5]×18 + [1,2,5]×2 | **72**, [2,5] — concentrated on new c/d classes |
| OS | **0 / 60** | **27** ([1,4] on a, [2,5] on b) |
| SI | **0 / 33** | **9** ([2,5] on d) |
| CE / HP | 0 / 136 | 0 / 396 — still 100% single-stratum |

**The driver is PUT richness, not measurement.** Because A = 0, the `repeats=20 →
repeats=1` change cannot explain the increase. The new **c-class surrogates** and
**d-class ML classifiers** *train on data*, so TF (fit-data corruption)
necessarily perturbs both monotonicity and asymptotic ordering, tripling TF
leakage (20 → 72). The genuinely new signal is **OS/SI leakage (0 → 36)**: on
richer PUTs even "local-edit" operators straddle invariant classes (OS on the
class-a spline and class-b simulators; SI on class-d models). On the simple A/B
numeric kernels of Study-1 those same operators touched a single computational
pathway. CE and HP remain clean in both studies.

## 6. Honest interpretation

- The `suspect_share = 0.1714` leakage is **not** an analysis artifact of
  single-shot scoring. It is **real construct-level multi-invariant coupling**
  (B = 117/117) that reached the scoring set because the single-stratum screen
  **never ran** on CF/TF (regex bug) and **never targeted** OS/SI (design gap).
- The single-stratum admission premise is **achievable and stable for CF**
  (9, class-b, identical across studies) but **fights the construct for TF/OS/SI
  on rich PUTs**: a working screen would have to reject the *majority* of TF
  mutants (72/135) and a third of OS. That is not noise removal — it is
  selecting a biased single-stratum sub-population of a family whose faults are
  intrinsically multi-invariant on trained models.

## 7. Implications

### Phase 2 (text)
- Re-label the H4' leakage narrative: replace any "measurement/LRCA artifact"
  framing with **"genuine construct-level multi-invariant coupling on rich
  (surrogate/ML) PUTs, reaching scoring through a disabled admission screen."**
- Disclose the screen no-op (op_id regex) and the OS/SI coverage gap as a
  **deviation/limitation**, with the fingerprint table (§4) as the mechanistic
  evidence and the §5 Study-1↔Study-2 reconciliation.
- Report A = 0 explicitly: single-shot `repeats=1` audit did not inflate the
  count (defends the LRCA scoring against a reviewer's "single-shot noise"
  objection).

### Phase 3 (decision) — two defensible paths

**Option 1 — fix-screen-and-rerun (Study 3).** Fix `_OPID_CAT_RE` to tolerate the
source suffix (or key the category off `category_from_filename`, which already
parses correctly) **and** extend `CONSTRAINED_CATEGORIES` to every family that
empirically straddles (add OS, SI). Re-run admission → single-stratum pool →
re-run H4'. CF1 shows this drives `suspect_share → 0`. **Cost/validity threat:**
it discards >50% of TF and ~22% of OS mutants — the admitted pool is a
single-stratum-selected, non-representative slice of those families, which is
itself a construct-validity caveat that must be pre-registered.

**Option 2 — re-registered graded-attribution construct.** Accept the evidence
(B = 117/117, reproducible under the strong measurement) that on c/d-class PUTs a
single-edit semantic fault *inherently* perturbs multiple invariant classes, so a
single-valued σ is the wrong model for those families. Re-register H4' as a
**graded / multi-valued attribution** target (e.g. score attribution *quality*
given a known co-flip signature) rather than a purity threshold.

**Recommendation.** Because A = 0 — the multi-stratum status is real, not a
scoring artifact — **Option 2 (graded-attribution re-registration) is the more
honest primary path for the c/d rich-PUT classes**, with **Option 1 retained for
CF** (where single-stratum is stable and cheap to enforce). A pure Option-1
"fix-and-rerun everything" would purchase a clean `suspect_share` at the price of
a silently biased TF/OS/SI sub-population, which the diagnosis shows is not noise
to be filtered but structure to be modelled.

---

*Generated by `scripts/diagnose_h4_leakage.py` (deterministic, offline). SSOT:
`data/results/h4_leakage_diagnosis_v5.json`. Admission re-runs: 117 mutants ×
5 MP × repeats=20 singleton, reproducing the frozen `repeats=1` audit's flip
sets exactly.*
