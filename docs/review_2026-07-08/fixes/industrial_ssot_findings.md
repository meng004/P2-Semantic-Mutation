# T4 — Industrial-arm (RQ4) reproducibility: findings & SSOT

Date: 2026-07-08 (updated after Zenodo deposit import). Fixes R1 Major M1
(`r1_methodology.md`) and R3 Major M1 + minors #1/#2/#3 (`r3_statistics.md`).
Constraint honoured: **no edits to `source/main.tex` or
`source/supplementary.tex`; no per-case data invented** — the per-case matrix
was imported from the downloaded Defect4MR deposit.

## 1. Repo verdict, then unblock

Initial exhaustive sweep (`data/`, `research/`, `replication/`, `venues/`,
`archive/`, `docs/`, `git log --all`) confirmed both reviewers: **no per-case
industrial data existed in the repo** — only aggregate numbers transcribed in
the LaTeX. The blocker was then closed by importing from a local copy of the
deposit:

- **Source**: Defect4MR (P12) v1.0.1, Zenodo DOI 10.5281/zenodo.21203424
  (record 21203937), `P12-Defect4MR-1.0.1.zip`,
  sha256 `39c53ef016accf7d0108827a41f4284e0437aad7300eb01970adf4ce3433eb7f`.
- **Files used inside the deposit**: `data/mutation/results.jsonl` (10,250
  rows; 34 cases; per-mutant per-MR verdicts), `data/mutation/REALDEFECT-FACE.md`
  (30-row real-defect face master table), the four extension cases'
  `NOTES.md` real-defect-face tables (a-lapack-004, a-openblas-001,
  b-pocketfft-002, e-ordinarydiffeq-001), and
  `reports/cloud/mutation-final-stats-2026-07-04.md` (the pre-registered
  statistics report whose Appendix B is the 34-case rerun the paper cites).
- The deposit zip itself is **not** committed (size/ownership); provenance
  (DOI + sha256 + file list) is recorded in the SSOT instead.

## 2. New in-repo SSOT chain

| Artifact | Content |
|---|---|
| `data/results/industrial_percase_v1.json` | 34-row per-case matrix: applied-mutant count, {T1,B1,B2,A1} kill counts, real-defect face row (T1 / B1 x-of-3 / B2 x-of-3 / A1-a / A1-b) per case, full provenance |
| `data/results/industrial_arm_v1.json` | derived group totals, Wilson CIs, pre-registered paired family, face totals, 23-check verification table vs paper |
| `data/results/industrial_stats_v1.json` | primary T1>B1 statistics + R3 strengthening battery + sensitivity rerun |
| `scripts/build_industrial_ssot.py` | `--extract <deposit_root>` regenerates the per-case file from the deposit; default mode re-derives every paper number (exits nonzero on mismatch) |

The statistics are an **independent pure-Python re-implementation** of the
dataset's pre-registered plan (design §6; deposit reference implementation
`tools/mutstats/prereg_stats.py` — read, not executed): kill = VIOLATED |
crash | timeout, nocompile out of denominator, group kill = any group MR
kills; one-sided Wilcoxon (zeros discarded, tie-corrected normal approx with
0.5 continuity), Holm over the enumerated 3-family, case-resampling
percentile bootstrap **B = 10,000, seed 20260704**, Cliff's δ on the
case-level KR vectors.

## 3. Verified vs paper — ALL 23 CHECKS PASS, ZERO MISMATCHES

| Paper number | Derived from per-case matrix | Match |
|---|---|---|
| n = 34 cases, 1124 applied mutants | 34, 1124 | ✓ |
| T1 377/1124 = 0.335, Wilson [0.308, 0.364] | identical | ✓ |
| A1 348 = 0.310; B1 274 = 0.244; B2 228 = 0.203 | identical | ✓ |
| mean paired diff T1−B1 = +0.101 | +0.101 | ✓ |
| bootstrap 95% CI [+0.029, +0.179] | [+0.029, +0.179] (B=10,000, seed 20260704) | ✓ |
| Holm-adjusted p = 0.046 (T1>B1) | 0.046 | ✓ |
| Cliff's δ = +0.247 | +0.247 | ✓ |
| T1>A1, B1>B2 not significant | Holm 0.063 / 0.063 | ✓ |
| sensitivity excl E-SUNDIALS-005 unchanged | Holm 0.046 | ✓ |
| face 34/34; B1 zero-detect 27/34; B2 26/34 | 34, 27, 26 | ✓ |
| ablations lose 19/34 (A1-a) and 17/34 (A1-b), 11 shared | 19, 17, 11 | ✓ |

## 4. R3 strengthening battery — COMPLETED (same estimand, no HARKing)

All on the identical one-sided case-level T1>B1 paired contrast:

| Test | Method | Result |
|---|---|---|
| Exact sign-flip permutation | full 2^27 null of Wilcoxon W+ via DP over tie-averaged ranks ×2 (exact, not sampled; n_eff = 27 nonzero diffs) | **p = 0.014** |
| Monte Carlo sign-flip on the mean diff | B = 10,000, seed 20260704, add-one convention | **p = 0.005** |
| BCa bootstrap CI for Cliff's δ | paired case-resampling, jackknife acceleration, B = 10,000, seed 20260704 | **[+0.068, +0.461]** — excludes 0 |
| Wilcoxon summary statistics | tie-corrected normal approx, 0.5 continuity | **V (W+) = 279.5, z = 2.162, unadjusted one-sided p = 0.015** |

Reading: the Holm 0.046 is **not** knife-edge once distribution-free exact
inference is used — the exact permutation p is 0.014 and the mean-statistic
permutation p is 0.005; the BCa δ interval excludes zero with margin. R3's
concern that "a marginal normal-approx p carries the arm" is answered: the
fragility was in the approximation and the correction, not in the data.

R3 minor #2 (unstated bootstrap B) is resolved: **B = 10,000, seed 20260704**
(verified by exact reproduction of [+0.029, +0.179]). R3 minor #3 (missing
test statistic): V = 279.5, z = 2.162, unadjusted p = 0.015 now available.

## 5. R3 minor #1 — ablation 1-vs-2 adjudicated from ground truth

The dataset ground truth (REALDEFECT-FACE.md 30 rows + 4 extension NOTES.md)
has **two** ablated variants: A1-a dimension-reduction loses the real defect
in **19/34** and A1-b de-strictification in **17/34**, with **11 shared**
losses. The supplementary Appendix I ledger is **correct and complete**; the
main text (L2462) mentions only the primary A1-a variant and labels it
correctly ("dimension-reduction ablation ... 19 of 34"). Fix is one clause in
the main text (below), not a data change.

## 6. Proposed LaTeX additions (author to apply — .tex untouched by this task)

**(a) RQ4 body, extend the sentence ending "...Cliff's δ=+0.247" (main.tex
~L2447):**
> "(one-sided Wilcoxon signed-rank V = 279.5, z = 2.16, unadjusted p = 0.015;
> case-resampling bootstrap with B = 10{,}000, seed 20260704). Because the
> Holm-adjusted p is close to the 0.05 boundary, we additionally report
> distribution-free checks of the same one-sided contrast: an exact sign-flip
> permutation test on the signed-rank statistic (full $2^{27}$ enumeration
> over the 27 nonzero paired differences) gives p = 0.014, a Monte Carlo
> sign-flip test on the mean paired difference (B = 10{,}000) gives
> p = 0.005, and the BCa bootstrap 95\% CI for Cliff's $\delta$
> (B = 10{,}000) is [+0.07, +0.46], excluding zero."

**(b) Ablation clause (main.tex L2462):** after "...19 of 34 cases that its
parent relation detects", add:
> "; a second, de-strictification ablation loses it in 17 of 34, with 11
> cases lost by both (supplementary Appendix I)"

**(c) Data Availability:**
> "Every industrial (RQ4) number is recomputable in-repo: the per-case
> 34-case × \{T1,B1,B2,A1\} kill matrix and per-case real-defect face are
> deposited at `data/results/industrial_percase_v1.json`, extracted from the
> Defect4MR deposit (Zenodo DOI 10.5281/zenodo.21203424, archive SHA-256
> recorded in the file) by `scripts/build_industrial_ssot.py`, which
> re-derives all group kill rates, the paired-comparison family, the
> real-defect face counts, and the robustness battery, and fails the build on
> any mismatch with the manuscript."

**(d) Permissions-table row update (optional):** the industrial row can now
cite the in-repo SSOT instead of only the external DOI.

## 7. Residual notes

- The four extension cases are exactly the paper's non-nesting
  counterexamples; the deposit's final-stats report (Appendix B.3) documents
  that adding them *narrowed* T1−B1 from +0.120 to +0.101 — informative, not
  noise, and already honestly discussed in the paper.
- The face T1 34/34 remains selection-conditioned (case admission requires
  T1-detectability); the SSOT records this caveat.
- The deposit zip stays outside the repo by design; anyone can re-run
  `--extract` against a fresh Zenodo download and the sha256 pins the version.
