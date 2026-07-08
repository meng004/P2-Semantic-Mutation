# Pre-Registration — Study 2 (Confirmatory)

**Paper**: *When Same-Prompt LLM Source Diversity Doesn't Help — Semantic
Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific
Computing Kernels* (P2/P3, IST/TOSEM two-study architecture).

**Status**: FROZEN before any Study-2 data generation. This document, together
with `scripts/power_analysis_study2.py` and its output
`data/results/power_study2.json`, is committed as the Study-2 registration and
will be deposited to Zenodo by the maintainer. No Study-2 mutant, dual-blind
review, or industrial candidate verification may begin until this file is
committed. Any change after freeze is a logged, dated amendment appended to §10,
not an edit to the frozen body.

**Freeze provenance**: registration commit (this file) + power SSOT
`data/results/power_study2.json` (master seed `20260708`, `n_sim=2000`).
Study-1 registration it supersedes:
`docs/experiment_documentation/EXPERIMENT_DESIGN.md` @
`0f2509527f346f9433c3cf90959bb07d80601a23`, Zenodo `10.5281/zenodo.20250664`.

**Design intent (one sentence)**: Study 2 converts the four Study-1 hypotheses
that were *point-estimate / under-powered / post-hoc / confounded* into
*a-priori-powered confirmatory tests*, by (i) expanding the PUT grid 12 → 30,
(ii) expanding the industrial corpus 34 → ≥45, (iii) running both LLM-source
arms under one identical dual-blind review protocol, and (iv) pre-declaring the
detection-incidence estimand.

---

## 0. Why Study 2 exists (the Study-1 power verdict)

Study 1 was honest but under-powered on its two inferential legs, and carried two
design temptations it correctly refused but could not *close*:

| Study-1 problem | Evidence | Study-2 fix |
|---|---|---|
| H2 large-effect threshold δ≥0.474 unpowerable | stipulated power 49.1% at n=12; `power_study2.json::a` shows δ≥0.33 test has ≈5% power even at n=36 because the true effect is ≈0.32 | register δ>0 stochastic-dominance (powered), report Romano band descriptively |
| Source-diversity Δδ confounded + under-powered | Δδ=−0.009, CI [−0.238,0.207], SE≈0.113; r3 focus 3 | n=30 (Δδ=0.20 → 82% power) **and** identical dual-blind protocol on both arms |
| Industrial Holm p=0.046 fragile | narrowed at 30→34; `power_study2.json::c` gives only 72% Wilcoxon power at n=34 | two-tier census (Tier A verified-only); 45 targeted but not pool-reachable (E3 triage) → under-recruitment fallback + sign-flip (89% @34) and Fisher incidence (100%) as the powered legs |
| Primary-MP post-hoc temptation (v3b) | selection-on-response deleted, deferred | deterministic class-indexed rule fixed a priori (§4) |
| Detection-incidence estimand reported post-hoc | OR≈21 promoted after seeing zeros (r3 focus 2) | pre-register Fisher incidence as its own labeled family (§3, H2-4) |

All Study-2 thresholds below trace to `data/results/power_study2.json`.

---

## 1. Confirmatory research questions

- **RQ-S2a (aligned/cross magnitude).** On the expanded 30-PUT grid, does the
  operator-MP aligned slice (j=k) stochastically dominate the cross slice (j≠k)?
- **RQ-S2b (source diversity, dual-blind).** Under one identical dual-blind
  review protocol applied to both a same-source and a cross-source LLM arm, does
  cross-source pooling move the aligned-vs-cross effect size (Δδ)?
- **RQ-S2c (industrial construct separation).** On an expanded, pre-frozen
  census of reproduced library defects, does the pattern-derived relation (T1)
  dominate literature-generic baselines (B1) in mutation-phase kills, and does
  its real-defect detection incidence exceed B1's?

Carry-forward (re-tested at n=30, not new): H1 operator-count adequacy, H3
cross-class consistency, H4 suspect-share noise ceiling.

---

## 2. Registered sample sizes (traceable to power SSOT)

| Arm | Registered n | Powered target | Achieved power | JSON trace |
|---|---|---|---|---|
| PUT grid (SMS) | **30 PUTs** (12 kept + 18 new); n_aligned=30, n_cross=120 | δ>0 one-sided | **0.94** | `a.power_by_threshold.delta_ref_0.0["30"]` |
| Dual-blind Δδ | **30 PUTs** (paired v3-style vs v4-style) | Δδ=0.20 two-sided | **0.82** | `b.power.dd_0.2["30"]` |
| Industrial (Tier A) | **≥35 verified_full** (floor: 34 + E-PETSC-004; +`N_rescued`, §6.3); 45 confirmatory only if reachable | T1>B1 one-sided Wilcoxon | **0.74** @35 · **0.83** @45 · **0.88** @52 | `c.wilcoxon_power` |

`n=30` is the joint minimum that powers *both* SMS legs: δ>0 first crosses 80% at
n=18 (`a.min_n_80pct.delta_ref_0.0`) but Δδ=0.20 needs n=30
(`b.min_n_80pct.dd_0.2`), so the binding constraint is the dual-blind arm — the
grid is sized to it. `n≥45` is the industrial minimum for 80% Wilcoxon power
(`c.min_n_80pct.wilcoxon_power`); n=34 gives only 0.72 and n=35 only 0.74. Per
the E3 triage (§6) 45 `verified_full` is **not reachable** from the current
candidate pool (all 16 are open/unfixed), so the industrial magnitude leg is
registered with an explicit under-recruitment fallback; the sign-flip robustness
(0.89 @34) and Fisher incidence (1.00) are adequately powered regardless.

---

## 3. Confirmatory hypotheses

Each hypothesis states: statistic · threshold (with power justification) · test ·
α · family · decision rule · licensed verdict. No threshold is aspirational: a
threshold appears only if `power_study2.json` shows ≥80% power to detect it at
the registered n, **or** the hypothesis is an exact/deterministic count carrying
no sampling power requirement (marked †).

### H2-1 — Aligned slice dominates cross slice (RQ-S2a)
- **Statistic**: Cliff's δ between aligned (j=k, n=30) and cross (j≠k, n=120) SMS
  cells under the §4 primary-MP rule.
- **Threshold**: δ > 0 (one-sided stochastic dominance). **Justification**: the
  Study-1-calibrated DGP has true δ≈0.32 (`a.true_delta_dgp`); the δ>0 test
  reaches **0.94** power at n=30 (`a.power_by_threshold.delta_ref_0.0["30"]`).
  The larger targets are *not* registered as pass/fail: δ≥0.147 tops out at 0.58
  and δ≥0.33 at ≈0.05 even at n=36 (same JSON block) — registering them would
  repeat the Study-1 error.
- **Test**: two-sample Cliff's δ; one-sided 95% percentile-bootstrap lower bound
  (multinomial two-sample bootstrap, B=10,000, seed 20260708) must exceed 0.
- **α**: 0.05, one-sided. **Family**: A (single test).
- **Decision**: lower bound > 0 → **confirm** aligned dominates cross. Otherwise
  → not confirmed on this pool.
- **Licensed verdict**: a directional construct claim (aligned slice carries more
  kill mass), *not* a large-effect claim. The point δ and its two-sided CI are
  reported against Romano (2006) 0.147/0.330/0.474 bands **descriptively**
  (exploratory, §7), never as a confirmatory pass.

### H2-2 — Source-diversity effect under matched dual-blind protocol (RQ-S2b)
- **Statistic**: Δδ = δ(cross-source arm) − δ(same-source arm), both arms scored
  on the same 30 PUTs under the identical dual-blind protocol of §5 (paired-role).
- **Threshold**: |Δδ| ≥ 0.20 detectable. **Justification**: the paired-role SE
  calibrated to Study-1 (SE(n=12)=0.1135, matching r3's 0.113; paired ρ=0.759)
  scales to SE(n=30)=0.069 (`b.paired_se_by_n["30"]`), giving **0.82** power for
  Δδ=0.20 (`b.power.dd_0.2["30"]`). Δδ=0.15 (0.58) and Δδ=0.10 (0.30) are
  **not** powered at n=30 and are pre-declared inconclusive.
- **Test**: paired-role bootstrap 95% two-sided CI on Δδ (B=10,000, seed
  20260708). **α**: 0.05, two-sided. **Family**: B (single test).
- **Decision rule**:
  - CI excludes 0 → **confirm** a source-diversity effect of magnitude ≥0.20.
  - CI includes 0 **and** half-width ≤ 0.14 (i.e. SE ≤ 0.071, met at n≥30) →
    **bounded null**: "no source-diversity effect of magnitude ≥0.20 is
    detectable under matched protocol." This is the informative outcome the
    protocol-asymmetry fix makes interpretable.
  - CI includes 0 with half-width > 0.14 → **under-recruited**, inconclusive.
- **Licensed verdict**: because both arms now run the *same* review protocol,
  any Δδ is attributable to LLM-source diversity, not to the Study-1 reviewer
  drop. A bounded null licenses the paper's thesis ("MR-design, not source
  diversity, is the lever") as a *confirmed* rather than *confounded* reading —
  but only for effects ≥0.20; smaller effects remain out of scope.

### H2-3 — Industrial mutation-phase dominance (RQ-S2c), Holm family of 3
- **Scope**: **Tier A (`verified_full`) only** (§6.1); Tier B never enters this
  estimand.
- **Statistic**: case-level paired kill-rate differences over the frozen Tier-A
  census. Three one-sided Wilcoxon signed-rank contrasts: **H2-3a** T1>B1,
  **H2-3b** T1>A1, **H2-3c** B1>B2.
- **Threshold / power**: T1>B1 Wilcoxon power is **0.74** at the expected n=35,
  **0.83** at n=45, **0.88** at n=52 (`c.wilcoxon_power`); calibrated to the
  Study-1 per-case difference distribution (mean +0.1005, 16+/11−/7 ties,
  observed one-sided V=279.5, p=0.0148 reproduced in `c.study1_observed`). The
  **exact sign-flip** robustness of the same estimand is already **0.89–0.90** at
  n=34–35 (`c.signflip_power`).
- **Test**: exact/one-sided Wilcoxon signed-rank per contrast; **exact sign-flip
  permutation** on the same signed statistic reported alongside as robustness of
  the identical estimand (not a new hypothesis). **α**: 0.05.
- **Family**: C — Holm correction across {T1>B1, T1>A1, B1>B2}, exactly as
  Study 1.
- **Decision rule**: **if Tier A ≥ 45**, Holm-adjusted p < 0.05 for a contrast →
  confirm that dominance. **If Tier A < 45** (the expected case per §6), H2-3a is
  reported as **under-recruited** with its achieved-n power (Study-1 status), and
  the confirmatory weight shifts to the sign-flip robustness + H2-4 incidence,
  both adequately powered at n=34–35.
- **Licensed verdict**: inferential within the Tier-A pool; no corpus-level
  coverage claim; Tier B reported separately as sensitivity (§6.5).

### H2-4 — Industrial real-defect detection incidence (RQ-S2c), separate family
- **Scope**: **Tier A only** (face-level, per case).
- **Statistic**: 2×2 Fisher exact, T1 detection incidence vs B1 detection
  incidence on the frozen Tier-A census.
- **Threshold / power**: one-sided Fisher, T1-incidence > B1-incidence. Power is
  **1.00** at every n∈{34,35,40,45,52} (`c.fisher_incidence_power`) because the
  Study-1 face separation is near-total (T1 34/34 vs B1 7/34). Registered here
  **a priori** so it is no longer the post-hoc estimand of Study 1. This is the
  industrial leg that stays confirmatory even under Tier-A under-recruitment.
- **Test**: Fisher exact, one-sided. **α**: 0.05.
- **Family**: **D — its own labeled family, OUTSIDE the Holm family C** (r3
  focus 5: an incidence test must not be folded into the magnitude correction).
- **Decision rule**: p < 0.05 → confirm incidence separation.
- **Licensed verdict**: incidence separation is a *distinct estimand* from
  magnitude dominance (H2-3); the two are reported side by side, never merged.
  Case admission still conditions on MR-detectability, so the face is read as
  construct separation among admitted cases, not as a coverage rate.

### Carry-forward (re-tested at n=30; thresholds unchanged from Study 1)
- **H2-5 † (H1, operator adequacy)**: ≥4 of 5 operators yield ≥5 non-equivalent
  mutants on ≥ ⌈0.75·30⌉ = 23 of 30 PUTs. Deterministic count; no sampling power
  needed (†). Family E, exact verdict.
- **H2-6 (H3, cross-class consistency)**: within-class sign test 4/4 across the
  four classes **and** Friedman χ² across MPs on 30 PUT blocks. The Friedman test
  is **exploratory-inferential** (Bonferroni×4 per-class), not confirmatory — it
  was a robustness check after mixed-effects singularity in Study 1 and stays so.
- **H2-7 (H4, noise ceiling)**: mean suspect_share ≤ 0.20 across the 150 cells.
  Descriptive mean, no independence assumed; verdict factual on the pool.

---

## 4. Primary meta-pattern selection rule (fixed a priori, data-independent)

**Study-1 lesson closed**: the v3b data-driven c-class primary-MP shift
(MP5→MP1) was selection-on-the-response; Study 1 deleted it and deferred a
proper rule to this registration (`main.tex` §Primary-MP-Convention;
`src/p2/config/primary.py` still ships `PRIMARY_CELLS_V3` as the held choice).

**Registered rule (deterministic, taxonomy-indexed, applied before any SMS is
computed).** Each PUT's primary MP is a function of its *design class only*:

| Class | Semantics | Primary MP | Rationale (fixed by construction, not by data) |
|---|---|---|---|
| a — numeric | conservation-bearing kernels | **MP1** (Conservation) | class defined by a conserved quantity |
| b — probabilistic | monotone estimators / samplers | **MP2** (Monotonicity) | class defined by a monotone response |
| c — surrogate | interpolants / fits | **MP5** (Partial-order) | held at pre-registered v3 choice; **no MP1 shift** |
| d — ML | monotone-scored predictors | **MP2** (Monotonicity) | class defined by score monotonicity |

- The rule is **data-independent**: assignment depends only on the class label a
  PUT is admitted under (§4a), never on its mutation outcomes.
- **MP5 handling (explicit)**: c-class is fixed at MP5, the pre-registered
  partial-order pattern. The Study-1 post-hoc MP1 reselection is **prohibited**;
  no max-over-MP or any outcome-conditioned primary choice is permitted in Study
  2. If a future rule change is desired it must be a new registration.
- **New PUTs inherit their class's primary MP automatically.** No per-PUT tuning,
  no reselection, no held-out max. The 18 new PUTs receive their primary MP the
  moment their class is fixed at authoring, before any operator is applied.
- Implementation: Study 2 runs with `P2_PRIMARY_VERSION` unset/`v3` (the
  `PRIMARY_CELLS_V3` map); the `v3b` code path is not invoked.

**(§4a) PUT class-assignment is frozen at authoring** (see §4b): a PUT's class is
declared by its NR-chapter anchor and signal semantics in the authoring ledger
*before* any mutant is generated for it.

**(§4b) PUT expansion protocol — 12 → 30 (18 new).**
- **Target**: 30 PUTs total, 7–8 per class (a,b,c,d). Add ~4–5 new PUTs per class
  (existing 3/class → 7–8/class).
- **Inclusion criteria (fixed before authoring outcomes are known)**: (i)
  single-output `float→float` scalar kernel; (ii) < 2 KB / function; (iii)
  anchored to a *Numerical Recipes*-style or standard-library reference in the
  named class; (iv) deterministic, publicly reproducible, no enterprise/closed
  data; (v) all five MPs instantiable (so the aligned diagonal cell exists);
  (vi) not a near-duplicate (AST-normalised) of an existing PUT.
- **Exclusion**: multi-output coupling, hidden global state, non-determinism not
  removable by seed, or a class assignment that is ambiguous between two classes.
- **Firewall (authoring blindness)**: the agent/author writing the 18 new PUTs
  and their MR sets operates **without access to any mutation result**. PUTs are
  authored and their class + primary MP frozen in the authoring ledger; only then
  is the operator campaign run. No PUT may be edited, reclassified, or dropped
  after its mutation SMS is observed. A PUT that fails an inclusion criterion is
  removed **only** on criteria (i)–(vi), which are all outcome-independent.

---

## 5. Dual-blind protocol (both arms, identical) — closes the protocol asymmetry

**Study-1 lesson closed**: v3 used the Phase-1 dual-blind reviewer (Claude gen +
GPT review + DeepSeek arbitration); v4 used V1–V4 mechanical gates only
(`scripts/cross_source_campaign.py` docstring: "no reviewer LLM, MVP
simplification"). The v3→v4 contrast therefore confounded source diversity with a
review-quality drop (`main.tex` "Declared confound: protocol asymmetry").

**Registered fix — one protocol on both arms.** Study 2 runs two arms on the same
30-PUT grid:
- **Same-source arm** (v3-style): one generator model family, K=3 trials.
- **Cross-source arm** (v4-style): three generator families (Claude / GPT /
  DeepSeek) under an identical prompt, K=3 trials each.

**Both arms pass through the identical dual-blind review + arbitration pipeline**
(this is the asymmetry fix; neither arm is scored on mechanical gates alone):
1. **Generation**: generator model emits a mutant for a (PUT, operator) pair
   (`cross_source_campaign.py::_run_one_op_one_source`).
2. **Blind review**: a reviewer model of a *different* family scores mutant
   validity against the operator spec. Operationally "blind" means the reviewer
   prompt contains only the mutant code + operator specification + PUT source; it
   **omits** (a) the generator's identity/family, (b) the arm label
   (same/cross), and (c) any SMS / kill outcome (SMS is computed only *after*
   review closes).
3. **Arbitration**: on generator/reviewer disagreement a third model family
   arbitrates, seeing the same blinded packet.
4. **Freeze then score**: only after review+arbitration accept/reject labels are
   frozen does the SMS pipeline (`scripts/sms_campaign.py`) run V1–V4 + E1∧E2 and
   compute kills. Reviewers never see kills; the SMS stage never re-opens review.
- **Model-family rotation** guarantees generator ≠ reviewer ≠ arbiter family on
  every item, so no model reviews its own output.
- **Δδ (H2-2)** is computed from the two arms *after* both have passed the
  identical pipeline; any residual difference is source diversity, not protocol.
- **Blinding of the analyst**: the person/agent running the SMS/δ computation
  does not alter review labels; review outputs are committed to
  `data/operator_campaign/cache_cross/` before δ is computed.

**Bounded cost note (not a threshold)**: ≈ O(cells × 2 reviewer roles) live
calls; runs only after this file is frozen. Credentials are the maintainer's;
none are in the repo.

---

## 6. Industrial corpus census protocol (two-tier)

**Hard constraint from the E3 feasibility triage**
(`docs/prereg_v2/INDUSTRIAL_EXPANSION_TRIAGE.md`, pilot
`pilot_verification_c-gsl-001.md`): **all 16 `candidate_full` cases are
open/unfixed upstream**. Per Defect4MR's own
`docs/open_unfixed_candidate_policy.md`, `verified_full` **requires a public fixed
revision** (fixing commit / PR / release / regression test) plus a fixed-side
oracle pass. Therefore **zero of the 17 scouted candidates can be promoted to
`verified_full` on any infrastructure today** — the blocker is fix-provenance,
not compute. Reaching 45 `verified_full` from this pool is **not achievable**, and
the earlier "minimum 45 else under-recruited" clause is **withdrawn** as
unrealistic. The census is therefore registered as **two tiers with a firewall
between them**.

### 6.1 Tier definitions (pre-registered; Tier B never relabeled as verified)
- **Tier A — `verified_full`**: a public upstream fix exists and both the buggy
  and fixed revisions pass their oracle. This is the **only** tier that enters the
  **primary** confirmatory estimand (H2-3, H2-4). At freeze Tier A = the Study-1
  34-case census **plus E-PETSC-004** once its mutation run completes (§6.4),
  i.e. a floor of **35**, plus any `N_rescued` (§6.3).
- **Tier B — reproduced-but-unfixed**: the buggy arm reproduces and dual-branch
  discrimination is demonstrated with a **local mechanism-closure patch as the
  fixed arm** (the C-GSL-001 pilot pattern: GSL 2.8 buggy Q=1.584 → local-patch
  PASS Q≈0.839). Tier B cases **enter only a pre-declared sensitivity stratum**;
  they are **never pooled into the primary estimand** and are **never relabeled
  `verified_full`**. The local patch is recorded as evidence, not as an upstream
  fixed revision.

### 6.2 Verification blindness (mandatory, both tiers)
Each case's reproduction + MR-oracle verification is performed **blind to any
mutation-phase outcome**. A case is admitted to a tier on reproduction + oracle +
fix-provenance criteria alone; no case is admitted, rejected, tiered, or ordered
using its T1/B1/A1/B2 kills or real-defect face. The mutation-phase comparison
runs **only after** the census (both tiers) is frozen. The C-GSL-001 pilot ran
reproduction only — **no operators were generated** — precisely to preserve this
gate.

**Inclusion criteria (enumerated, outcome-independent)** — a case is admitted iff:
1. buggy and fixed(-or-faithful-contrast) revisions are both executable on a
   plain, publicly buildable stack (no Cray/aprun/closed-backend-only hardware);
2. the defect reproduces deterministically (no un-seedable non-determinism);
3. a registered pattern-derived MR oracle exists and is MR-detectable on the
   buggy revision;
4. it passes the ledger `exclusions_checked` filters (not crash-only, API-only,
   documentation-only, performance-only, closed-backend-only);
5. it is not a duplicate of an already-admitted case;
6. **tiering by fix-provenance**: public upstream fix → Tier A; open/unfixed with
   a local mechanism-closure patch → Tier B.

**Exclusion**: unsupported build stack, no executable contrast, no
MR-detectability, or (for Tier A only) no public fixed revision.

### 6.3 Conditional recruitment targets (dated; N_rescued is a protocol variable)
Tier A may grow by three registered, outcome-independent routes:
- **(a) Fix-rescan** of the 16 open issues for upstream merges landing **after
  2026-07-03** (a parallel agent runs this). The count of newly-fixed candidates
  is the protocol variable **`N_rescued`**, determined **at census freeze**; it is
  not assumed non-zero. Any rescued case is verified fixed-side, then enters
  Tier A.
- **(b) New fix-backed scouting** in the E-PETSC-004 shape (a defect with a merged
  fix), under the §6.2 inclusion criteria, up to the freeze date.
- **(c) Honest fallback**: **if Tier A < 45 at the freeze date, the expansion
  (magnitude) hypothesis H2-3a is reported as under-recruited with the achieved
  n — no threshold moving, no pooling of Tier B to inflate n.** The achievable-n
  power scenarios `c.wilcoxon_power` (34→0.72, 35→0.74, 40→0.79, 45→0.83,
  52→0.88) let the paper state exactly what each freeze outcome buys.

### 6.4 E-PETSC-004 (registered completion)
E-PETSC-004 is already `verified_full` but its mutation data is **results-partial
only**. Study 2 registers the **completion of its mutation run** as an in-scope
task; on completion it extends the **Tier A** census 34 → 35 for the **new**
study. **Study 1's frozen 34-case census is untouched** and remains the Study-1
SSOT.

### 6.5 Freeze rule + what each outcome licenses
- The census (both tiers) is **frozen at verification completion on date X**,
  *before* any arm comparison. **No case may be dropped after its comparison
  numbers are seen**; the only admissible post-freeze change is logging a
  reproduction that failed on criteria (1)–(6), in §10.
- **Tier A ≥ 45** (only if `N_rescued` + new scouting deliver it) → H2-3/H2-4
  **confirmatory** (Wilcoxon ≥0.83, `c.wilcoxon_power["45"]`).
- **35 ≤ Tier A < 45** (the expected case) → census frozen and reported; H2-3a
  magnitude is **under-recruited** (achieved-n power stated, e.g. 0.74 at n=35);
  but H2-4 incidence stays **confirmatory** (power 1.00 at every n,
  `c.fisher_incidence_power`) and the exact **sign-flip robustness stays adequate**
  (0.89–0.90 at n=34–35, `c.signflip_power`) — so the construct-separation
  reading survives under-recruitment.
- **Tier B** → reported only as a labeled **sensitivity stratum**
  (open-unfixed, local-patch fixed arm), never merged into the primary estimand.

**SSOT on freeze**: the frozen per-case matrix (both tiers, tier-tagged) is
written to `data/results/industrial_percase_v2.json` (schema of
`industrial_percase_v1.json`: `n_applied`, per-arm kills, real-defect face,
`tier` ∈ {A,B}), closing the Study-1 reproducibility gap (r3 M1: RQ4 was not
repo-recomputable).

---

## 7. Analysis plan

**SSOT paths (Study 2)**
- SMS pool: `data/results/sms_track2_v5.json` (30-PUT × 5-MP = 150 cells).
- Aligned/cross δ: `data/results/rq2_cliffs_delta_v5.json`.
- Dual-blind Δδ: `data/results/dualblind_delta_delta_v5.json` (both arms +
  paired-role bootstrap).
- Industrial per-case: `data/results/industrial_percase_v2.json` (frozen census).
- Industrial stats: `data/results/industrial_stats_v2.json`.
- Power reference (this registration): `data/results/power_study2.json`.

**Scripts**
- PUT authoring ledger + class freeze: `docs/prereg_v2/put_authoring_ledger.md`
  (created at authoring, before campaign).
- Mutant campaign (both arms, dual-blind): `scripts/cross_source_campaign.py`
  extended with the §5 reviewer+arbiter stage (same-source arm reuses the same
  pipeline with one generator family).
- SMS/δ: `scripts/sms_campaign.py`, `scripts/compute_rq2.py`.
- Δδ: new `scripts/compute_dualblind_delta.py` (paired-role bootstrap).
- Industrial: `scripts/compute_industrial_stats.py` on the frozen census.
- Primary-MP: `src/p2/config/primary.py` with `P2_PRIMARY_VERSION=v3`.

**Seeds**: all bootstrap/permutation seeded at **20260708** (this registration's
master seed) unless a script documents a distinct frozen seed. Power reference
uses `20260708`; industrial Study-1 used `20260704` (kept for the reproduced
V=279.5 anchor).

**Exclusion rules (analysis-time)**: vacant cells (○, not adjudicated) are
excluded from δ as in Study 1; a PUT with all five MP cells equivalent (dead) is
retained (contributes zeros) — no live-only filtering enters a confirmatory
verdict (live-only pools are exploratory sensitivity only, per Study-1 practice).

**Multiplicity — one family map for the whole of Study 2**

| Family | Members | Correction | Confirmatory? |
|---|---|---|---|
| A — SMS magnitude | H2-1 (δ>0) | single test | yes |
| B — Source diversity | H2-2 (Δδ≠0) | single test | yes |
| C — Industrial mutation-phase | H2-3a/b/c (Wilcoxon T1>B1, T1>A1, B1>B2) | **Holm** (3) | yes |
| D — Industrial incidence | H2-4 (Fisher) | single test, **outside C** | yes |
| E — Carry-forward counts | H2-5 (H1 †), H2-7 (H4 descriptive) | none (exact/descriptive) | verdict-factual |
| X — Exploratory | H2-6 Friedman (Bonferroni×4), Romano-band magnitude, Pattern-coverage ρ/τ, S5 purity, LRCA attribution, live-only/vacant sensitivities | per-test as labeled | **no** |

No study-wide cross-family correction is applied (standard under
pre-registration + per-family control + the paper's inference-permissions
table); this is stated, not "corrected."

**Confirmatory ↔ exploratory boundary (bright line)**
- **Confirmatory** = Families A–D + carry-forward E, exactly as registered here,
  run once on the frozen data with the registered tests/seeds.
- **Exploratory** = everything in Family X, plus any analysis not listed above.
  Exploratory results are labeled and may not be promoted into a confirmatory
  verdict post hoc (the Study-1 v3b and OR=21 lessons). Any new test discovered
  after freeze is exploratory by definition and declared in its own labeled
  family.

---

## 8. Decision matrix — what each outcome licenses

| Hypothesis | Confirm outcome licenses | Non-confirm outcome licenses |
|---|---|---|
| H2-1 | "Aligned slice dominates cross" (directional construct claim) | no directional claim on this pool |
| H2-2 | "Cross-source pooling moves δ by ≥0.20" (source diversity matters) | **bounded null**: "no ≥0.20 source-diversity effect under matched protocol" → supports the MR-design-is-the-lever thesis as *confirmed*, not confounded |
| H2-3 | "T1 out-kills B1 in the Tier-A census" (inferential, census-scoped) | under-recruited (expected, Tier A ≈35) → achieved-n power stated; confirmatory weight shifts to sign-flip + H2-4 |
| H2-4 | "T1 detects real defects more often than B1" (incidence, distinct estimand) | no incidence separation (a priori improbable given 1.0 power) |
| H2-5..7 | operator adequacy / cross-class consistency / noise ceiling as factual pool verdicts | plainly stated "not met" (Study-1 honesty norm) |

**What would count against the construct (stated a priori this time)**: (i)
aligned δ CI crossing 0 at n=30 despite 0.94 power; (ii) a confirmed Δδ ≥ 0.20
that *reverses* the Study-1 direction; (iii) T1 kill-sets nesting inside B1 in
the census; (iv) reviewer arbitration failing audit. Unlike Study 1, these are
registered *before* data.

---

## 9. Deviations-from-Study-1 lessons table (design closure)

| # | Study-1 lesson | Where it bit (Study 1) | Study-2 closure | Trace |
|---|---|---|---|---|
| L1 | **Unpowered aspirational threshold** — H2 registered at δ≥0.474 with 49% power | `main.tex` H2 / stipulated power §; r3 focus omitted-large | H2-1 registers δ>0 (0.94 power); Romano band only descriptive | `power_study2.json::a` |
| L2 | **Primary-MP post-hoc temptation** — v3b MP5→MP1 selection-on-response | `main.tex` Primary-MP-Convention; `primary.py` `v3b` path | §4 deterministic class-indexed rule; MP5 held for c-class; `v3b` path prohibited | §4 |
| L3 | **Census timing / fragility** — n=34, Holm p=0.046 narrowed at 30→34 | `main.tex` industrial arm; r3 M1, r1 focus1 | two-tier census frozen at verification before comparison; Tier A verified-only for primary; 45 targeted, under-recruitment fallback registered (E3 triage: pool caps at ~35); per-case matrix committed | §6, `c.wilcoxon_power` |
| L9 | **Open-unfixed candidates cannot reach verified_full** — 45-verified target unreachable | E3 triage `INDUSTRIAL_EXPANSION_TRIAGE.md`; `open_unfixed_candidate_policy.md` | two-tier design; Tier B (local-patch fixed arm) is sensitivity-only, never relabeled verified; `N_rescued` a protocol variable set at freeze | §6.1–6.3 |
| L4 | **Protocol asymmetry** — v3 dual-blind vs v4 mechanical-only | `main.tex` "Declared confound"; r1 focus4 | §5 identical dual-blind pipeline on both arms | §5 |
| L5 | **Incidence estimand post-hoc** — OR≈21 / Fisher promoted after seeing zeros | r3 focus2, r1 focus3 | H2-4 pre-registers Fisher incidence as its own family D, outside Holm | §3 H2-4 |
| L6 | **Industrial arm not repo-recomputable** | r3 M1, r1 M1 | frozen census written to `industrial_percase_v2.json` as SSOT | §6, §7 |
| L7 | **Underpowered dual-blind rerun at same n** | r3 focus3 (SE≈0.113 stays if n held) | dual-blind rerun registered at n=30, not n=12 | §2, `b.paired_se_by_n` |
| L8 | **Disconfirmation criteria stated post hoc** | `main.tex` "What would count against… (post hoc)" | §8 registers them a priori | §8 |

---

## 10. Amendments log (append-only, dated; empty at freeze)

*(No amendments. Any post-freeze change — a candidate that failed reproduction, a
seed correction, a script fix — is appended here with date and rationale; the
frozen body above is never edited.)*
