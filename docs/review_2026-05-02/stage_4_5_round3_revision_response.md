# Stage 4.5 Round-3 Final Integrity — Revision Response Pass

**Date:** 2026-05-02
**Verifier:** integrity_verification_agent (Stage 4.5 final-check mode)
**Manuscript:** `论文初稿P2_IST.md` at HEAD = 2b25053 (after 11-commit revision response cycle)
**Baseline:** `docs/review_2026-05-02/stage_4_5_round2_reverify.md` (long-version EN/CN PASS_WITH_NITS)
**Scope:** (1) verify the IST trimmed file inherits all Round-2 P0 fixes; (2) verify the 11 commits in this revision cycle introduced no new integrity issues; (3) run the 7-mode AI failure mode checklist on this revision's new artefact and edits.

---

## One-Line Verdict

**PASS** (all 5 phases clean; all 7 AI-failure modes clean; one P2 residual NIT noted for the next revision pass).

**Recommended action:** **Proceed to Stage 5 FINALIZE.**

---

## Phase 1 — Reference inheritance from long-version Round-2 audit

| Round-2 P0 | IST file evidence | Verdict |
|---|---|---|
| **P0-A** Tip 2024 author list (was: Misailovic / Bavota fabricated) | Lines 33, 57, 401, 427, 613, 654 use `Tip, F., Bell, J., & Schäfer, M.`; zero hits for `Misailovic` / `Bavota` | **CLOSED ✓** |
| **P0-B** DeepCrime (was: Hu / Guaman / wrong DOI) | Lines 33, 57, 656 use `Humbatova, N., Jahangirova, G., & Tonella, P. (2021), ISSTA 2021, doi.org/10.1145/3460319.3464825`; zero hits for `Hu, Q.` / `Guaman` / `3540250.3549144` | **CLOSED ✓** |
| **P0-C** Cosmic-ray total 1276 → 1250 | Lines 6, 17, 43, 263, 270 all use `1,250`; zero hits for `1276` | **CLOSED ✓** |

**Phase 1 verdict:** All three Round-2 P0 fixes are inherited correctly into the IST trimmed file. No new citations introduced in this revision cycle (verified by `git diff 2571df1..HEAD -- 论文初稿P2_IST.md | grep -E '^\+.*(20[12][0-9]|et al)'` returning only existing-citation re-references, no new bibliography rows).

---

## Phase 2 — Citation context

This revision did not introduce new citations. The Tip et al. (2024), Humbatova et al. (2021), Romano (2006), Petrović & Ivanković (2018), Jia & Harman (2009, 2011), Kintis et al. (2018), Delgado-Pérez & Chicano (2020), Moradi Dakhel et al. (2024), and Zhang et al. (2021) references are all carry-overs from the pre-revision IST file (commit 2571df1) and were re-verified in the long-version Round-2 audit. No in-text citations rephrased to claims unsupported by the cited works.

**Phase 2 verdict:** PASS.

---

## Phase 3 — Statistical data verification (full SSOT round-trip)

| Quantity | Paper claim | SSOT path | SSOT value | Verdict |
|---|---|---|---|---|
| v3 Cliff's δ | 0.323 | `paper_numbers_v3.json: rq2.cliffs_delta` | 0.3229 | ✓ |
| v3b Cliff's δ | 0.446 † | `paper_numbers_v3b.json: rq2.cliffs_delta` | 0.4462 | ✓ |
| v4 Cliff's δ | 0.439 † | `paper_numbers_v4.json: rq2.cliffs_delta` | 0.4392 | ✓ |
| **v4×MP5 Cliff's δ (NEW)** | **0.314** | `rq2_cliffs_delta_v4_mp5.json: cliffs_delta` | 0.3142 | ✓ |
| v4×MP5 95% CI | [0.014, 0.622] | `rq2_cliffs_delta_v4_mp5.json: delta_ci_95` | [0.0138, 0.6215] | ✓ |
| v4×MP5 n_aligned / n_cross | 12 / 48 | (same JSON) | 12 / 48 | ✓ |
| Δδ(v3 → v4×MP5) | −0.009 | derived: 0.3142 − 0.3229 | −0.0088 | ✓ |
| Friedman χ² | 15.30 | `paper_numbers_v4.json: rq3.friedman_chi2` | 15.3028 | ✓ |
| Friedman p | 0.0041 | `paper_numbers_v4.json: rq3.friedman_p` | 0.0041 | ✓ |
| Spearman ρ (RQ4) | 0.163 | `paper_numbers_v4.json: rq4.spearman_rho` | 0.1628 | ✓ |
| Stipulated power (49.1 %) | 0.491 | `rq2_power_stipulated_v4.json: stipulated_alternative_power.power_point_estimate_meets_H2` | 0.4915 | ✓ |
| Permutation p (one-sided) | 0.9885 | `c_class_permutation_v4.json: permutation_p_value_one_sided_geq` | 0.9885 | ✓ |
| AST overlap rate | 5.14 % | `cosmic_ray_12put_ast_diff.json: aggregated.overlap_rate_overall` | 0.05137 | ✓ |
| Class-c +91.4 % | +91.4 % | derived: 0.0894 / 0.0467 − 1 | +91.43 % | ✓ |
| HP / SI / TF unreachability | 0 / 0 / 0 | `cosmic_ray_12put_ast_diff.json: per_class.{HP,SI,TF}.n_overlap` | 0 / 0 / 0 | ✓ |

**Phase 3 verdict:** PASS. All 11 statistical quantities reported in this revision's edits round-trip to their JSON SSOTs at 3-decimal precision.

---

## Phase 4 — Originality

This revision adds (i) one new ~40-line script using existing pre-tested statistics modules, (ii) one new JSON output, (iii) Markdown prose changes to the manuscript and a response-letter from scratch. No external text imported; no patterns suggestive of plagiarism (verified by inspection — all prose is task-specific argumentation around the v4×MP5 contrast and the axis-decomposition framing). The response letter is a fresh authorial composition.

**Phase 4 verdict:** PASS.

---

## Phase 5 — Claims traceability

The revision restructures three central claims:

| New claim location | Claim | Evidence | Verdict |
|---|---|---|---|
| Abstract Conclusion (line 21) | "Within this design, the MR-design axis (c-class primary-MP choice) is the lever; the LLM-identity axis shifts δ by ≤ 0.01 across two MP conditions" | v3 = 0.323, v4×MP5 = 0.314 (Δ = −0.009); v3b = 0.446, v4 = 0.439 (Δ = −0.007). Both ≤ 0.01 in magnitude. ✓ | ✓ |
| Abstract Results (line 19) | "MR-design axis shifts δ by approximately +0.12" | (v3b − v3) = 0.123; (v4 − v4×MP5) = 0.125. Both ≈ +0.12. ✓ | ✓ |
| §8.1 finding (iii) (line 583) | identical claim to Abstract Conclusion | Same evidence. ✓ | ✓ |
| §5.3 robustness row (line 415) | "δ_v4_mp5 − δ_v3 = −0.009 isolates the LLM-source-diversity axis" | The contrast holds c-class primary at MP5 (v3 spec, no v3b post-hoc shift) while only the LLM-source pool changes. Logical isolation correct. ✓ | ✓ |
| §5.4 symmetric-reading paragraph (line 449) | "The 49.1% power is also the relevant power for the v3b → v4 contrast" | Both contrasts use the same n = (12, 48) design with v4 SMS distribution; symmetric power applies. ✓ | ✓ |

**Phase 5 verdict:** PASS.

---

## 7-Mode AI Research Failure Checklist

| # | Mode | Verdict | Evidence |
|---|---|---|---|
| 1 | Citation hallucination | PASS | No new citations introduced; existing Round-2 P0 fixes inherited (Phase 1) |
| 2 | Implementation bug | PASS | `scripts/compute_rq2_v4_mp5.py` is a 40-line wrapper around tested `cliffs_delta` / `bootstrap_delta_ci` in `src/p2/stats/cliffs_delta.py`; uses existing `PRIMARY_CELLS_V3` spec (no MP assignment fabrication); n = 12 / 48 split verified at runtime |
| 3 | Hallucinated results | PASS | All 11 numbers SSOT-verified at 3-decimal precision (Phase 3 table) |
| 4 | Shortcut reliance | PASS | Full 10K bootstrap with seed = 42; no surrogate / shortcut computation |
| 5 | Bug-as-insight | PASS | The v4×MP5 = 0.314 finding is from a deliberate methodological design (hold c-class primary at MP5 to strip R11), not from a buggy computation; the design is documented in `purpose` field of the output JSON |
| 6 | Methodology fabrication | PASS | The v4×MP5 design uses the existing v4 cross-source SMS pool (`sms_track2_v4.json`) and the existing v3 PRIMARY_CELLS_V3 spec; both pre-existed this revision; no new methodology created |
| 7 | Pipeline frame-lock | PASS_WITH_DISCLOSURE | The revision plan's Task 2 used the **B variant** (axis-decomposition framing) instead of the originally planned A variant (full causal-language removal). The variant choice was made *after* observing the v4×MP5 = 0.314 result — strictly a post-hoc adjustment. The user explicitly chose B at the FULL checkpoint after viewing the v4×MP5 numbers; the divergence is documented in this conversation log and acknowledged in the response letter ("the *direction* of the original claim is correct, but its phrasing has been refined"). This is not a hidden frame-lock; the dependence of the final framing on the new data is disclosed. |

**7-mode verdict:** PASS_WITH_DISCLOSURE on Mode 7. No blocking findings.

---

## Residual NITs (P2 advisory, non-blocking)

### NIT-1 — Numerical coincidence in §5.4 (pre-existing)

§5.4 line 440 contains the pre-existing rationale text "any ε > 0 jumps δ from 0.314 to 0.74", where 0.314 is the raw-shift baseline computed by `compute_rq2_power_stipulated.py` for the v4 SMS distribution before the mixture-weight calibration. The new v4×MP5 contrast added in this revision (δ = 0.314, 95 % CI [0.014, 0.622]) is numerically identical at 3-decimal precision but is **a semantically independent quantity** (a Cliff's δ on a different MP-conditioned slice). Both numbers are correct; the coincidence is real but unrelated.

**Recommendation:** Optionally add a one-line clarification in §5.4 line 440 such as "(this 0.314 is a property of the v4 raw-shift behaviour and is not the v4×MP5 robustness contrast in §5.3, which happens to round to the same value)". Not blocking — readers tracking lead numbers in §5.3 / Abstract / §8.1 will not encounter §5.4's 0.314 in a confusing context.

### NIT-2 — Inherited from long-version Round-2

The two P1 advisories not closed in long-version Round-2 (P1-3 §5.8.1 class-mean version annotation; P1-6 internal SSOT inconsistency between `rq3_friedman_v4.json` and `paper_numbers_v4.json`) were not addressed in this revision since the revision scope was limited to the simulated-review response. These remain as documented in `stage_4_5_round2_reverify.md`. Both are non-blocking and concern peripheral details outside the IST trimmed file's main argument backbone.

---

## Reproducibility Audit Trail

| Artefact | Commit | Hash | Verified |
|---|---|---|---|
| New script | `scripts/compute_rq2_v4_mp5.py` | b61f206 | reads SMS SSOT + writes new JSON |
| New data | `data/results/rq2_cliffs_delta_v4_mp5.json` | b61f206 | δ = 0.3142, full provenance metadata |
| Abstract revision | `论文初稿P2_IST.md` lines 19–21 | 266c472 | B-variant axis decomposition |
| §8.1 revision | `论文初稿P2_IST.md` lines 583–585 | 7aaf0b5 | Mirror of Abstract |
| §5.3 robustness row | `论文初稿P2_IST.md` lines 410–425 | 8283bc5 | Three-stage delta + contrast table |
| §3.4 † convention | `论文初稿P2_IST.md` line 259 | f1f84a5 | Single-anchor symbol convention |
| † applied | `论文初稿P2_IST.md` §5.5 / §6.1 / §6.3 | 414a0b4 | Five distinct number-locations marked |
| §5.2 / §5.4 consolidation | `论文初稿P2_IST.md` lines 399, 431, 449 | e26a6dc | Effective-n + symmetric-reading |
| RQ4 reframe | `论文初稿P2_IST.md` lines 68, 480 | eba8cdd | "descriptive only" alignment |
| Response letter | `docs/review_2026-05-02/response_to_simulated_review.md` | 6c1ea2c | Critique → Response → Diff format |
| Humanizer pass | (multiple files) | ac1105b | 21 em-dashes eliminated in this revision's edits |
| Proofread micro-edit | `论文初稿P2_IST.md` line 425 | 2b25053 | "feeds" → "supports" |

All eleven commits include full HEREDOC commit messages with `phase-D(review-response)` prefix.

---

## Sign-off

**Stage 4.5 Round-3 verdict:** PASS. Proceed to Stage 5 FINALIZE.

The 11-commit revision response cycle:
- Inherits all three P0 fixes from the long-version Round-2 audit (Phase 1 ✓);
- Introduces no new citations (Phase 2 ✓);
- Reports 11 statistical quantities all SSOT-verified at 3-decimal precision (Phase 3 ✓);
- Adds only original prose and a thin script wrapper (Phase 4 ✓);
- Grounds every revision-introduced claim in a SSOT-verified quantity (Phase 5 ✓);
- Survives the 7-mode AI failure checklist with one acknowledged disclosure on Mode 7 (post-hoc framing choice, made by user at a checkpoint with full data visibility).

One residual NIT (numerical coincidence in §5.4) is logged for the next revision pass; it does not block submission.
