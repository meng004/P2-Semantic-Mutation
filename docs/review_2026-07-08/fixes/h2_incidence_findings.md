# T3 — H2 detection-incidence sensitivity: findings & proposed text

Analysis of EXISTING v4 data. Script: `scripts/compute_h2_incidence.py`.
SSOT: `data/results/h2_incidence_v4.json`. Every number below is from that run
(scipy 1.17.1, statsmodels 0.14.6). No number is transcribed from the manuscript.

---

## 0. Headline finding (READ FIRST) — the manuscript's 9/12-vs-6/48 is mislabeled

R1 focus-3 and R3 focus-2 both ask us to elevate the binarized incidence contrast
"aligned 9/12 vs cross 6/48, OR=21" (`main.tex:1962`) to a first-class sensitivity.
**Verifying it against the SSOT shows the two counts are swapped.** The pre-registered
MP5-held primary convention (`src/p2/config/primary.py:PRIMARY_CELLS_V3`, a→MP1, b→MP2,
c→MP5, d→MP2) is the exact assignment that generates the headline δ=0.314 pool
(`rq2_cliffs_delta_v4_mp5.json`, mean_aligned=0.213325 — reproduced bit-exact). Under it:

| slice | nonzero | zero | n | incidence |
|---|---|---|---|---|
| **aligned (primary cells)** | **6** | 6 | 12 | 50.0% |
| **cross (off-diagonal cells)** | **9** | 39 | 48 | 18.75% |

Total nonzero = 15/60 (matches `main.tex:2220` "15/60 nonzero"). But the split is
**aligned 6 / cross 9**, i.e. the exact transpose of the manuscript's "aligned 9 / cross 6".

**Root cause of the error.** Only **9 of the 12 PUTs have any nonzero cell** (a1, a3, c2
are dead across all 5 MPs). The manuscript's "9" is that PUT-level any-signal count
(9/12 PUTs are non-dead), *not* the count of nonzero aligned cells. It was mislabeled as
"aligned nonzero" and the residual 6 as "cross nonzero". The A-class aligned pattern MP1
turns out to be a broad operator that scores nonzero on many *cross* PUTs (B1, B2, B3, C1,
C3, D2 under MP1), which is why cross carries 9 nonzero, not 6.

R3 "ran it" on the manuscript's mislabeled counts and got OR=21, p=0.000053 — I reproduce
that exactly (see §2), so R3's arithmetic is right but its **input 2×2 is wrong**.

---

## 1. Verified honest numbers (SSOT-correct, v4 MP5-held, all 60 cells)

2×2 = [[aligned_nz 6, aligned_z 6], [cross_nz 9, cross_z 39]], one-sided H_A: aligned incidence > cross.

- Sample (unconditional) odds ratio: **4.33**
- Conditional-MLE odds ratio: **4.20**
- Exact 95% CI (one-sided): **[1.12, +∞)**
- Exact 95% CI (two-sided): **[0.90, 20.2]** — includes 1
- Fisher exact **one-sided p = 0.0355**
- Fisher exact two-sided p = 0.0560

Reading: aligned MPs detect a nonzero effect ~2.7× more often (50% vs 18.75%); the
one-sided test is significant at .05, but the effect is **OR≈4, not 21**, and the
two-sided CI crosses 1. It is a real but *modest* incidence advantage.

## 2. Discrepancy vs R3 / manuscript — BOTH computed, diagnosed

Manuscript-stated (mislabeled) counts 9/12 vs 6/48 → 2×2 [[9,3],[6,42]]:
- OR (sample) = **21.0**, conditional-MLE = 19.3
- Fisher one-sided **p = 5.29e-5** ✓ matches R3's 0.000053
- One-sided exact CI lower = **4.47** ✓ matches R3's "4.4"
- R3's CI upper "100" = the **Woolf/logit approximation**: lnOR=3.045, SE=0.797,
  exp(3.045 ± 1.96·0.797) = [4.41, 100.2]. So R3 used Woolf on the mislabeled table.

R3's statistics are internally correct; the defect is upstream — the 2×2 itself.
**Do not promote OR=21.** The honest number is OR≈4.

## 3. Robustness grid (all from the run; one-sided Fisher p)

| variant | aligned nz/n | cross nz/n | sample OR | 1-sided p |
|---|---|---|---|---|
| **v4 MP5-held (headline)** | 6/12 | 9/48 | 4.33 | 0.0355 |
| v4 MP5-held, 9 vacant cells dropped | 6/11 | 9/40 | 4.13 | 0.0486 |
| v4 MP5-held, 3 dead PUTs dropped | 6/9 | 9/36 | 6.00 | 0.0263 |
| v3 same-source, MP5-held | 6/12 | 8/48 | 5.00 | 0.0238 |
| v4 v3b (c-class→MP1) | 7/12 | 8/48 | 7.00 | 0.0064 |

The incidence advantage is **directionally stable and one-sided-significant across every
variant** (OR 4.1–7.0, p 0.006–0.049), but never approaches OR=21. The vacant-cell drop
(R1 minor m6 / the 6-vs-9 question): 9 vacant cells, of which exactly one is aligned
(B3_MP2, a zero cell) → aligned 12→11; the other 8 are cross zero cells → cross 48→40.
That matches `main.tex:2083` "n=11 aligned and n=40 cross", and the incidence verdict is
unchanged (OR 4.13, p 0.049).

---

## 4. Honest statistical framing (for the response letter and text)

1. **Own labeled test family, OUTSIDE the Holm family** (R3 point 9): this Fisher test is
   a new, post-hoc-specified sensitivity. It must be declared as its own single-test
   family and must **not** be folded into the pre-registered Holm correction or the H2
   pre-registration.
2. **Different estimand from H2 magnitude.** H2's pre-registered criterion is *magnitude*
   (Cliff's δ ≥ 0.474); incidence (P[SMS>0]) is a distinct estimand. The incidence result
   **cannot license an H2 pass**. H2 magnitude verdict stays **"not met"** (δ=0.314,
   CI [0.014, 0.622]).
3. **Two-part hurdle framing (correct version).** Separate the aligned-vs-cross signal into
   (i) *incidence*: aligned MPs score nonzero ~2.7× more often (OR≈4.2, one-sided Fisher
   p=0.035), and (ii) *magnitude*: given the wide zero-mass, the conditional gap does not
   reach the large-effect bar. This is a legitimate, honest, more-structured reading —
   with OR≈4, not OR=21.
4. **The degenerate +∞ median OR** (`main.tex:1959`, `odds_ratio_median: Infinity`) is a
   *third*, distinct quantity (median-based, pre-registered magnitude criterion) that
   degenerates under zero-inflation; keep it explicitly separated from the incidence OR
   (R1 minor m3).

**Integrity note:** because the elevation R1/R3 request is built on a mislabeled 2×2, the
first required action is a **correction** of `main.tex:1954-1965` (the "3/12 aligned zero /
42/48 cross zero" and "aligned 9/12 vs cross 6/48, OR=21" claims are wrong), *then* the
elevation. Elevating OR=21 as-is would promote an error to first-class. (Text edits are
out of scope for this task — flagged for the main.tex owner.)

---

## 5. PROPOSED LaTeX (for the main.tex owner — not applied here)

### 5.1 Replace the demoted sentence with a first-class subsection

```latex
\subsubsection{Detection-incidence sensitivity (post-hoc, own family)}
\label{h2-incidence}
The aligned-vs-cross contrast decomposes into two estimands: \emph{detection
incidence} (does a meta-pattern score any nonzero SMS on a PUT) and
\emph{conditional magnitude} (how large the gap is, given nonzero). The
pre-registered H2 criterion targets magnitude (Cliff's $\delta \ge 0.474$) and
is not met ($\delta = 0.314$, 95\% CI $[0.014, 0.622]$). As a post-hoc
sensitivity in its \emph{own single-test family} (outside the Holm family and
outside the H2 pre-registration), we binarize SMS and test detection incidence.
Under the MP5-held primary convention, aligned cells are nonzero in $6/12$ cases
versus cross cells in $9/48$ (incidence $50\%$ vs $18.75\%$; note only $9$ of the
$12$ PUTs carry any nonzero cell). A one-sided Fisher exact test gives
$p = 0.036$ with conditional-MLE odds ratio $4.2$ (exact one-sided 95\% CI lower
bound $1.12$); the advantage is directionally stable across pool variants
(OR $4.1$--$7.0$, $p = 0.006$--$0.049$; Table~\ref{tab:h2-incidence}). Aligned
meta-patterns therefore detect a nonzero effect appreciably more often than cross
patterns, while the \emph{magnitude} of the gap does not reach the large-effect
threshold: incidence separates, magnitude does not, and the H2 verdict remains
\textbf{not met}.
```

### 5.2 Separate the degenerate median OR (fixes R1 m3, replaces L1959-1965)

```latex
Three odds-ratio-like quantities must be kept distinct. (i) The pre-registered
\emph{median} odds ratio is $+\infty$ because $\mathrm{median(cross)} = 0$; it is
degenerate under zero-inflation and licenses no verdict. (ii) The
\emph{incidence} odds ratio (nonzero-SMS 2$\times$2, \S\ref{h2-incidence}) is
$4.2$ (Fisher one-sided $p = 0.036$), a distinct and meaningful quantity.
(iii) The Cliff's $\delta$ magnitude estimand ($0.314$) is the pre-registered
H2 criterion and is not met.
```

### 5.3 Abstract — mention without overclaiming (optional single clause)

Append to the Results sentence about the aligned-vs-cross effect (do NOT cite a
number; keep it qualitative per the CLAUDE.md Abstract rule):

> "...positive but below the pre-registered large-effect threshold; a post-hoc
> incidence sensitivity shows aligned meta-patterns detect a nonzero effect more
> often than cross patterns, though the effect-size gap itself stays below
> threshold."

Do **not** write "OR=21" or "strong separation" in the abstract; the honest
incidence OR is ~4 with a one-sided p just under .05 and a two-sided CI crossing 1.
