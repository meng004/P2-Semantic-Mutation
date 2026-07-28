# Prereg Pre-Review — Matrix Arbitrations + Power Config / Rulings

**Date:** 2026-07-28 · **Trigger:** author instruction "预审矩阵两处仲裁与功效配置/裁定建议，等待T2"  
**Scope:** the two applicability-matrix arbitrations (matrix §4 D1/D2), the Task 1.2 primary configuration, and the two external-line ruling recommendations. This is the author-delegated *pre*-review; formal CHECKPOINT 1 still convenes only after theory T2 → Task 1.3.  
**Method:** intervention probes (change the cause, check the predicted effect) rather than argument re-reading, per CLAUDE.md §10 (研而且究); plus a §10.1 over-defence audit and a Reviewer-2 scan.

---

## 1. Arbitration D1 — CE × c2: **UPHELD** (evidence upgraded from "plausible" to "demonstrated")

Probe (executed this session, seed-fixed): rebuilt the c2 pipeline verbatim; measured the conservation invariant g(x) = f(x) + f(1−x) on a 21-point grid.

| Condition | max\|g(x)\| | Reading |
|---|---|---|
| Baseline c2 | **0.0036** | odd-symmetry conservation held by the symmetric degree-5 fit |
| CE wrapper edit (`_y_train = tanh + 0.05`) | **0.1036** (min 0.0964) | invariant eroded by ≈ 2×offset, exactly the predicted magnitude; outputs finite, type/signature preserved |

The disputed site exists and behaves quantitatively as the arbitration claimed: a one-line, type-preserving wrapper edit produces an MP1-detectable conservation violation. Rater B's objection ("no *explicit* conserved normalisation") correctly describes the code but the invariant is implicit (odd target × symmetric sampling), which the probe shows is real and erodible. **Keep `applicable`; keep the ARBITRATED-BORDERLINE flag** (the invariant is implicit, so generation prompts must state it — added as an EXP-CON prompt-design note).

## 2. Arbitration D2 — SI × b3: **UPHELD**, with one honest downgrade of the evidence breadth

Probe: executed the actual v4 mutant (`m19_b3_SI1_claude_a03.py`, arithmetic→geometric mean) against baseline b3 on a 21-point grid.

- Ordered domination (orig > mutant) at **21/21** points; gap min/median/max = 0.031 / 0.049 / 0.195 — a systematic one-sided fidelity degradation, i.e. exactly MP5 partial-order failure semantics (AM–GM), at a wrapper-level aggregation site.
- **Evidence-breadth caveat (new finding):** the "2 confirmed" v4 SI×b3 mutants are **byte-identical** (same SHA-256) — one unique edit duplicated across trials. This does not weaken *site existence* (one demonstrated edit suffices) but it does weaken *generation diversity* evidence: H-CONS risk on SI×b3 is higher than the raw count suggested. Logged into the EXP-CON risk list alongside the matrix §5 SI concentration note.
- Governance note: master plan Task 1.1 Step 1 uses "SI × B inapplicable" as an *illustrative* example ("例："). The matrix deliverable rules by evidence; the example is guidance, not a normative cell value. If the author overrides at CHECKPOINT 1: flipping SI×b3 (and/or CE×c2) moves n_app 51→50→49; H-ZERO power at the design alternative moves 0.806→≈0.80 (n_app-sensitivity row: 45→0.791, 51→0.806) — the primary-config recommendation is unchanged.

## 3. Power configuration — verdict: **ADOPT m=16 × s=2 (n_app=51)**, with the H-ZERO cliff made explicit

New cliff-localisation runs (appended scenarios; pre-existing rows verified byte-stable):

| True P(SMS>0 \| aligned) | 0.50 (v4 anchor) | 0.65 | 0.70 | 0.75 | **0.80** | 0.85 |
|---|---|---|---|---|---|---|
| true BA | 0.643 | 0.712 | 0.737 | 0.761 | 0.785 | 0.808 |
| H-ZERO power (m=16, s=2, n=51) | 0.004 | 0.196 | 0.376 | 0.613 | **0.806** | 0.925 |

Reading: H-ZERO is powered iff operator-targeted generation lifts the aligned nonzero rate to ≥ 0.80 (v4's untargeted anchors: 0.50 class-primary, 0.118 operator-level). The ~50% power near p_a≈0.72 is boundary behaviour (true BA ≈ threshold 0.75), not a design defect. **This is the boldest headline bet in the package and it is left bold on purpose** (§10: risky prediction retained; failure will be attributable via the pre-specified TPR/TNR decomposition — recommend Task 1.3 add that decomposition to the H-ZERO reporting schema). H-DISC is insensitive to this cliff (≥0.867 everywhere except the adversarial world, where failing is correct).

MID(r_mp)=0.33: conversion from Cliff's δ-medium is heuristic but the simulated anchor-A effect clears it with q10(r_mp)≈0.32 and power is flat between MID 0.30/0.33 — no objection. Kernel augmentation not triggered: correct, since augmentation only helps when the prediction is *true but noisy* (p_a≥0.8 world, where power is already 0.81), and cannot rescue a false prediction.

## 4. Ruling recommendations — over-defence audit (§10.1)

**H-CAL → interval estimation: legitimate validity repair, not falsification-escape.**
- Trigger evidence: threshold-test power ≤ 0.31 (acc 0.8) / ≤ 0.66 (acc 0.9) over the whole realistic grid — this is the §10.1-sanctioned downgrade path ("功效/可行性模拟证实不可检验 → 降区间估计").
- Falsifiability is *not* removed from the calibration family: (i) the B-3 secondary (four-condition clustered bootstrap vs majority class) remains confirmatory with a pre-registered criterion; (ii) the frozen per-defect predictions remain publicly checkable point predictions; (iii) the McNemar comparison stays as a labelled descriptive. Verdict: **approve for Task 1.3**, with the Wilson-CI width budget (0.27–0.37 at n=20) written into hypotheses.md so the interval claim is itself pre-committed.

**H-RANK ≥6-qualifying-projects floor: approve, with the mining target pinned at n=24 / J=8.**
- The floor is an anti-false-pass control (null false-pass 14% at 4 qualifying → ≤9% at 6 → 5.7% at 8), added pre-freeze; it tightens rather than weakens the claim → not over-defence.
- Residual: 8–9% false-pass at exactly 6 qualifying projects is above the conventional 5%. Rather than raising the τ̄ bar post-hoc, pin the mining target at n=24 across J=8 (protocol §2.5 already states this as the comfortable configuration) and report J_qualifying prominently.

## 5. Reviewer-2 scan (quick pass, 5 dimensions)

1. 方法论：two-rater protocol executed with a genuinely independent cross-family rater; arbitration now probe-backed — no blocker. Residual: Rater B is a model, not a human; disclose in §6 Threats when writing up (already noted in matrix header).
2. 外部效度：H-CAL prevalence prior remains the weakest input (historical 34/34 is selection-conditioned; decoupled-admission prevalence unknown). Mitigated by scanning π∈{0.6–0.9} and by the interval ruling. No blocker.
3. 统计选择偏差：cliff table published for the *un*favourable region too; adversarial anchor kept in the report; no favourable-scenario cherry-pick. No blocker.
4. Benchmark 公正：majority-class baseline retained (descriptive) rather than deleted. No blocker.
5. 霍桑效应：not applicable (no human subjects in this package).

## 6. Disposition for CHECKPOINT 1 (when T2 → Task 1.3 completes)

| Item | Pre-review verdict | Author action at CHECKPOINT 1 |
|---|---|---|
| CE×c2 arbitration | UPHELD (probe-backed) | ratify or flip (n_app 51→50; conclusions robust) |
| SI×b3 arbitration | UPHELD; evidence breadth = 1 unique edit | ratify or flip (n_app→50/49; conclusions robust) |
| Primary config m=16 × s=2, n_app=51 | ADOPT | ratify |
| MID(r_mp)=0.33 | no objection | lock in Task 1.3 |
| H-CAL interval ruling | approve (audit passed) | lock in Task 1.3 |
| H-RANK τ̄≥0.3 + ≥6-project floor, mining n=24/J=8 | approve | lock in Task 1.3 |
| H-ZERO TPR/TNR decomposition in reporting schema | new recommendation | add to hypotheses.md (Task 1.3) |
| EXP-CON prompt note (implicit invariants, e.g. c2 symmetry) | new recommendation | add to Task 2.1 generation ledger spec |

**Holding state:** per instruction, execution pauses here — Task 1.3, the prereg freeze tag, and Phase 2+ wait for theory CHECKPOINT T2. No further phase work will start in this line until T2 is reported passed.
