# Pre-Registered Hypotheses & Frozen Analysis Plan (prereg v2, Task 1.3)

**Date frozen:** 2026-07-28  
**Freeze gate record:** theory CHECKPOINT T2 (THM-GAP internal review: premise strength S5+exact-checker and ξ reporting mode) **passed per author sign-off 2026-07-28**. THM-GAP deliverables: `research/theory_drafts/thm_gap.md` @ commit `7c48d06` and T2.2 consistency closes @ `7bb1519` (branch `cursor/theory-enhancement-t0-6320`). This satisfies the unique theory-side freeze gate (R-5).  
**Package inputs (already committed):** applicability matrix (content-scope hash `8b701e026c7607348c1fdeec420a1712e2baf3ccf574759dd9a76c15dda8997a`, n_app=51); power/feasibility report (`data/results/prereg_power_v2.json`, seed 20260728); external slice protocol (SHA-256 `186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca`).  
**Freeze mechanism (F-7):** all `research/prereg_v2/*` files except `AMENDMENTS.md` plus `scripts/prereg/*.py` are hashed into `FREEZE_MANIFEST.sha256`; tag `prereg-v2-freeze`. Post-freeze analysis-code changes demote the affected analysis to exploratory and require an `AMENDMENTS.md` entry (F-7a). Confirmatory conclusions come only from new-lineage data (F-8/F-9).

---

## 0. A-PROV bridge assumption and evidence channels (R-6, F-2)

**A-PROV (methodological assumption, not a theorem premise; authoritative wording = theory plan §0.3):** in the empirical operationalisation, an aligned-provenance MR set approximates an exact checker (DEF-05) of its target stratum; the operationalisation of \(\mathrm{Cov}(R)\) is **applicability matrix × MR provenance** (provenance-as-coverage).

- **Ex-ante channel (decides whether A-PROV is asserted):** provenance and construction audit — held-out source symmetric checklist (`MR_SOURCE_SYMMETRY.md`), generation-time `eff` stratum labels, applicability-matrix hash. This channel never sees kill results.
- **Ex-post channel (diagnostic only):** \(\xi(R)\) (DEF-09, block-off-diagonal kill mass / total kill mass); its pooled form is the secondary confirmatory hypothesis H-XI (§5.1).
- **Adjudication rule (frozen):** H-ZERO and H-DISC verdicts are decided unconditionally by their frozen criteria; ξ never changes any verdict; ξ enters the discussion section for attribution only.

### 0.1 H-ZERO × H-XI 2×2 adjudication table (pre-registered conclusion sentences)

| | H-XI PASS | H-XI FAIL |
|---|---|---|
| **H-ZERO PASS** | "Both the zero-structure prediction and the exactness diagnostic pass: theory and operationalisation are jointly corroborated." | "The zero-structure prediction passes but block-exactness fails: the claim holds in a bounded form; attribution of aligned kills to target strata is impure and stated as such." |
| **H-ZERO FAIL** | "Block-exactness holds but the zero-structure prediction fails: the theory prediction is disconfirmed under a clean operationalisation (honest negative)." | "Both fail: the operationalisation itself failed; no verdict on the theory is issued." |

(Emitted verbatim by `analysis_hxi.py`; UNDERPOWERED ξ leaves the table unfilled.)

## 1. Testing-family policy (F-11, two families)

- **Family 1 — headline co-primaries (5):** H-ZERO, H-DISC, H-DOSE, H-CAL, H-RANK. Each tested at α = 0.05, one-sided where directional; **no family-wise correction**. Rationale (frozen): the five address heterogeneous constructs with no conjunctive claim ("all five hold" is never asserted); all five verdicts are reported unconditionally in the manuscript regardless of outcome, which removes the selective-reporting channel that multiplicity correction guards against. H-CONS is a manipulation check outside the family.
- **Family 2 — secondary confirmatory (B-group):** H-XI (B-1), H-DOSE-CTR (B-2), H-CAL-CLU (B-3), H-FIX (B-4). Each at α = 0.05, explicitly labelled secondary, failures reported verbatim, and **never gate or modify headline verdicts**.

## 2. Frozen design constants

| Constant | Value | Source |
|---|---|---|
| Applicable cells n_app | 51 (matrix hash above) | Task 1.1 |
| Mutant density m | 16 confirmed non-equivalent / applicable cell (attempt budget ≈ ×1.117) | power report §5/§9 |
| Held-out MR sets s | 2 (v5 provider(s), symmetric checklist per set) | power report §3 |
| H-DISC MID | r_mp = 0.33 | power report §2 |
| EXP-DOSE config | operators {HP, CE} × kernels {A1, B3, C1, D3} × 6 levels × 20 repeats = 960 executions; grid log-spaced [0.25, 4.0]·ε_tol on the realized ε_m axis (F-10) | power report §7 |
| EXP-FIX sample | 15 cells, seed 20260728, from applicable ∩ predicted-nonzero ∩ Gap_aln>0 | power report §8 |
| External mining target | ready n ≥ 20 (target 24) across ≥ 8 projects; H-RANK floor: ≥ 6 qualifying projects (≥3 ready defects each) | power report §6, protocol §2.5 |
| Fiber-map gate | Cohen κ ≥ 0.6 (joint 8-class label) | protocol §3 |
| Permutations / bootstrap | 10⁴ / 10⁴ (BCa where stated); seeds 20260728 | scripts |
| Statistical software pin | numpy 2.4.4 / scipy ≥ 1.18 `wilcoxon(method="auto")` | environment |

## 3. Headline hypotheses (family 1)

### H-ZERO — zero-structure construct validity
- **Derivation:** COR-ZERO ("If \(\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing\) then \(\mathrm{SMS}(R)=0\)", THM-GAP corollary), applied to data through A-PROV: applicable cell × ALN condition → predicted NONZERO; applicable cell × CRS condition → predicted ZERO (`PRED_ZERO_ALIGN`); `NOT_APPLICABLE` cells excluded.
- **Units:** 2 × n_app = 102 (cell × condition); observation = cell SMS (mean of s=2 replicates) equal / not equal to 0.
- **Criterion (frozen):** observed balanced accuracy ≥ 0.75 **and** one-sided exact McNemar vs the majority-class predictor p < 0.05 (majority = the majority observed class on the evaluation set, tie → zero).
- **Mandatory reporting:** TPR/TNR decomposition (failure attribution; pre-review addition), bootstrap 95% CI on BA, McNemar discordant counts.
- **Degradation path:** no threshold movement; if the funnel leaves < 40 measurable applicable cells → verdict still binary, flagged UNDERPOWERED; failure attribution via TPR/TNR + ξ discussion (never verdict rescue).
- **Script:** `analysis_hzero.py`.

### H-DISC — conditional discrimination (paired)
- **Derivation:** THM-GAP decomposition \(1-\mathrm{SMS}=\mathrm{Gap}_{\mathrm{aln}}+\mathrm{Gap}_{\mathrm{str}}\): aligned coverage removes the Gap_aln term on covered strata, so within-cell SMS_aln should exceed SMS_crs on predicted-nonzero cells.
- **Units:** applicable, predicted-nonzero cells; paired difference d_cell = SMS_aln − SMS_crs (each side = mean over s=2 MR-set replicates; MR source = v5 held-out provider).
- **Criterion (frozen):** one-sided Wilcoxon signed-rank (greater) p < 0.05 **and** matched-pairs rank-biserial r_mp ≥ 0.33.
- **Mandatory reporting:** Hodges–Lehmann shift, BCa 95% CI on r_mp (10⁴), n of nonzero pairs; **sensitivity:** unpaired Cliff's δ (v4-comparable, "(ordinal effect size)" at first mention).
- **Degradation path:** < 30 nonzero pairs → UNDERPOWERED flag, verdict per criteria; MID never moves post-freeze.
- **Script:** `analysis_hdisc.py`.

### H-DOSE — dose–response monotonicity
- **Derivation:** THM-WIN (kill probability transitions monotonically in realized violation magnitude ε_m, centre ≈ ε_tol, width O(Δ_r+2η̄)).
- **Design:** frozen EXP-DOSE config (§2); dose axis = realized ε_m via the direct invariant-violation functional (F-10; never via MR checkers).
- **Criterion (frozen):** global pooled statistic \(T_{\mathrm{glob}}=\sum_c T_c\), \(T_c=\mathrm{RSS}_{\mathrm{const}}-\mathrm{RSS}_{\mathrm{iso}}\) (weighted isotonic on level kill-rates); null = within-curve permutation conditional on per-curve totals (multivariate hypergeometric), 10⁴ draws; one-sided p < 0.05. The single-p wording of the master plan §1.2 is instantiated as this one global test; per-curve permutation p's and Page's L are descriptive.
- **Degradation path:** engineering loss > 20% of executions on any curve → report per-curve completeness, analysis on completed executions; no re-runs, no curve selection.
- **Script:** `analysis_hdose.py`.

### H-CAL — external calibration (interval-estimation primary)
- **Derivation:** fiber alignment + THM-WIN window (where estimable) generate the frozen per-defect detect/miss predictions (protocol §5).
- **Ruling chain (frozen, pre-data):** master plan Task 1.2 Step 2b delegates the "threshold test vs interval estimation" ruling to the feasibility simulation → power report §6.1 (majority-class McNemar infeasible at n ≤ 24: max power 0.31 @ acc 0.8, 0.66 @ acc 0.9) → pre-review §4 anti-over-defence audit pass → author continuation 2026-07-28. **Primary form: interval estimation.**
- **Primary estimand:** aligned condition, one (defect, aligned-MR-set) pair per ready defect; accuracy of frozen predictions with Wilson 95% CI (pre-committed expected width 0.27–0.37 at n = 20–24). Majority-class rate and one-sided exact McNemar reported as labelled descriptives, never verdict sources. Verdict value: `INTERVAL_REPORTED` (or `DESCRIPTIVE_ONLY` if ready n < 12).
- **Fixed-arm FPR:** any flag on the fixed arm counts as a false positive; separate FPR table; anomaly triggers REM-FPOS discussion; never enters the primary estimand. **Brier deleted** (binary predictions; redundant with accuracy, F-3a).
- **Falsifiable confirmatory element of the calibration family = H-CAL-CLU (§5.3).**
- **Script:** `analysis_hcal_hrank.py`.

### H-RANK — external ranking consistency
- **Estimand:** per qualifying project (≥ 3 ready defects): Kendall τ_b ("(rank correlation)") between the frozen predicted condition ranking (ALN > v5 > CRS > RND) and observed detection counts over the 4 conditions; \(\bar\tau\) = equal-weight mean over qualifying projects; fully-tied projects excluded and counted.
- **Criterion (frozen):** \(\bar\tau \ge 0.3\), **evaluable iff J_qualifying ≥ 6** (floor; null false-pass ≤ 9% per power report §6.2). If J_qualifying < 6 → pre-registered downgrade `DOWNGRADED_INTERVAL` (bootstrap 95% CI on \(\bar\tau\)).
- **Feasibility basis:** moderate-scenario power 0.87–0.93 ≥ 0.8 → threshold form retained (R-3 downgrade not triggered).
- **Comparators (estimation-first):** \(\bar\tau_{\mathrm{SMS}}-\bar\tau_{\mathrm{MS}}\) and \(\bar\tau_{\mathrm{SMS}}-\bar\tau_{\mathrm{PC}}\) paired differences + bootstrap 95% CI; **no superiority test** (J ≈ 8 has no power; B-3 rationale).
- **Script:** `analysis_hcal_hrank.py`.

## 4. Manipulation check (outside family 1)

### H-CONS — constructability
- **Criterion (frozen):** p̂ = share of the 51 applicable cells producing ≥ 5 confirmed non-equivalent mutants within the generation budget; Wilson 95% lower bound > 0.5. Role: EXP-CON feasibility gate; never a headline claim.
- **Discipline:** F-5a runtime recoding (site-absence only, pre-unblinding, logged; generator engineering failures stay in the funnel). Generation prompts must state implicit invariants explicitly (e.g. c2 odd-symmetry; pre-review addition). Known risk concentration: SI stratum (dev anchor 1/6 combos ≥ 5; the b3 precedent is a single duplicated edit).
- **Script:** `analysis_hcons.py`.

## 5. Secondary confirmatory family (B-group)

### 5.1 H-XI (B-1) — pooled exactness defect
Pooled \(\xi(R)\) ≤ 0.10 (prior landmark) → PASS; cell-cluster bootstrap 95% CI (10⁴) reported; estimability guard: total kills < 50 → UNDERPOWERED (interval only). Strata labels are ex-ante (generation-time eff; MR provenance). Never gates headlines; feeds the §0.1 table. Script: `analysis_hxi.py`.

### 5.2 H-DOSE-CTR (B-2) — transition-centre containment
Per-curve centre (isotonic 0.5-crossing on realized axis; logistic-MLE crossing as sensitivity) ∈ ε_tol ± (Δ_r + 2η̄); **criterion: ≥ 6 of 8 curves contained** (calibrated by power report §7: estimation noise ≪ window, so the criterion tests location, not noise). Per-curve windows are estimated by the THM-WIN audit-item-(5) protocol and **frozen before dose unblinding** (window-freeze commit must precede the first dose-run artifact). Script: `analysis_hdose.py`.

### 5.3 H-CAL-CLU (B-3) — pooled-conditions calibration
Four-condition pooled accuracy of frozen predictions vs majority-class predictor; defect-cluster bootstrap (10⁴), one-sided p < 0.05. Script: `analysis_hcal_hrank.py`.

### 5.4 H-FIX (B-4) — add-one repair intervention
15 sampled cells (seed 20260728): augment cross set with one target-stratum aligned MR (from existing MRSET-ALN; nothing newly generated); criterion: Wilson 95% LB of the share of cells with SMS_j transitioning 0 → positive > 0.5 (implied bar 12/15); Gap-transfer ledger (gap_aln_after = gap_aln_before − w_j, THM-GAP algebraic identity) reported with max deviation. Boundary: P3 verifies actionability; P4 owns minimal-subset optimisation. Script: `analysis_hfix.py`.

## 6. Analysis-code binding and smoke status

| Hypothesis | Script | Verdict space |
|---|---|---|
| H-ZERO | `scripts/prereg/analysis_hzero.py` | PASS / FAIL (+UNDERPOWERED flag) |
| H-DISC | `scripts/prereg/analysis_hdisc.py` | PASS / FAIL (+UNDERPOWERED flag) |
| H-CONS | `scripts/prereg/analysis_hcons.py` | PASS / FAIL |
| H-DOSE / H-DOSE-CTR | `scripts/prereg/analysis_hdose.py` | PASS / FAIL; CTR also NOT_EVALUABLE |
| H-CAL / H-CAL-CLU / H-RANK (+diffs) | `scripts/prereg/analysis_hcal_hrank.py` | INTERVAL_REPORTED / DESCRIPTIVE_ONLY; PASS/FAIL; PASS/FAIL/DOWNGRADED_INTERVAL; ESTIMATE_REPORTED |
| H-XI | `scripts/prereg/analysis_hxi.py` | PASS / FAIL / UNDERPOWERED |
| H-FIX | `scripts/prereg/analysis_hfix.py` | PASS / FAIL |

Unified output schema `{hypothesis, estimate, ci, p, verdict, extras}`; shared frozen utilities in `scripts/prereg/_stats.py`; synthetic smoke suite `scripts/prereg/smoke_all.py` — **7/7 PASS at freeze time**. Input JSON schemas are frozen in each script's docstring; execution phases must populate SSOT keys conforming to them (`funnel_v5`, kill matrices, `dose_response_v5`, `fix_intervention_v5`, `external_fiber_map`, `external_validation`).

## 7. Lineage and disclosure (for §6 Threats at writing time)

1. Old mp-cell (60) **result data** is development-only (F-8); v4-provenance MR sets may serve as the EXP-EXT treatment condition with all response variables newly collected (F-9).
2. DEF-CAL training 10 examples (`MAPPING_TRAIN`) are excluded from confirmatory DEF-REAL (F-1); the historical 34/34 detect rate is selection-conditioned and appears only as a power prior.
3. Post-freeze changes to any hashed file demote the affected analysis to exploratory and require an AMENDMENTS entry with diff hash and disclosure sentence (F-7/F-7a).
4. Rater B of the applicability matrix is a cross-family model instance; disclosed in the matrix header and to be disclosed in the manuscript's annotation-arrangements paragraph.
