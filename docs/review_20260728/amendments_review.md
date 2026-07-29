# AMENDMENTS.md Review — Amendments #1 and #2

**Date:** 2026-07-29 · **Trigger:** author instruction "请评审amendments.md" (author-delegated review)  
**Method:** every factual claim in each amendment row re-verified by command this session; §10.1 over-defence analysis applied to both.

## 1. Amendment #1 — matrix header hash repair

| Claim in row | Verification | Result |
|---|---|---|
| Body (all rulings) unchanged | body below standalone marker byte-compared against creation commit `2b36c81` | ✅ identical (hash `670e5748…`) |
| Only header lines changed | `git show --stat 6c5bbf1`: matrix +3/−1 header lines, ledger +1 row, manifest regen | ✅ |
| Single-commit rule | one commit touching exactly {matrix, AMENDMENTS, manifest} | ✅ |
| Manifest coherent post-amendment | `shasum -a 256 -c` 15/15 OK | ✅ |
| New recipe verifies | recomputed body hash equals declared header value | ✅ |

**§10.1 class:** documentation validity-repair; zero claim content touched. **APPROVE.**

## 2. Amendment #2 — H-DOSE-CTR effective containment radius

| Claim in row | Verification | Result |
|---|---|---|
| Pre-unblinding ordering | `git merge-base --is-ancestor`: window freeze `f7ca7cc` → amendment `9b9939b` → first dose artifact `2378065` (`dose_response_v5.json` first appears at `2378065`) | ✅ strict ancestor chain |
| Trigger factual (degenerate windows) | `WINDOWS_FROZEN.json`: 6/8 curves halfwidth 2×10⁻⁶–3.4×10⁻⁴ vs centre-estimation sd 0.03–0.16·ε_tol (power report §7) | ✅ |
| Floor math | g=(4/0.25)^{1/5}=1.7411; √g−1=0.3195 | ✅ |
| Radius applied as specified | recomputed r_c=max(Δ_r+2η̄, floor) for all 8 executed curves vs `window_halfwidth` field | ✅ 8/8 exact |
| Frozen analysis code untouched | amendment commit touches only {hypotheses.md, AMENDMENTS, manifest} | ✅ |

**§10.1 analysis (the critical question — is widening a criterion over-defence?):**
Widening a pass region normally smells like claim-shrinkage. Three facts defeat that reading here:
1. **The original instrument had zero discriminating power**: with radius ≈ 2×10⁻⁶ and estimator granularity ≈ 0.03–0.16, P(contained) ≈ 0 under theory-true *and* theory-false. An always-FAIL test is exactly as uninformative as an always-PASS test; repairing it *restores* falsifiability rather than escaping it.
2. **Timing is provable**: the widened radius was committed before any dose execution artifact existed — no outcome could have been peeked.
3. **The repaired test still failed and was reported verbatim** (H-DOSE-CTR FAIL, 2/8): the amendment demonstrably did not rescue the outcome.

**Residual caveat (carried to writing):** for the 6 floored curves the secondary now tests "centre within one log-grid half-step of ε_tol", a weaker location claim than the theory window; the manuscript must state per-curve which radius bound (theory window vs resolution floor) was operative — CE-B3/HP-B3 used their own theory windows; the other six used the floor. **APPROVE with this reporting obligation.**

## 3. Ledger hygiene

- AMENDMENTS.md correctly excluded from the manifest hash set (F-7a) ✅; both rows carry trigger / scope / diff summary / §6 disclosure sentence ✅; one row = one commit ✅.
- Sign-off column updated this session to record the delegated review; the author's personal countersign can be appended at any time without a new amendment (ledger metadata, not frozen content).

**Overall verdict: both amendments APPROVED under delegated review; no further action required before CHECKPOINT 2.**
