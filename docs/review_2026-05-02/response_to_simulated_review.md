# Response to Simulated IST Review (P2 Major Revision)

**Manuscript:** When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels (P2 / IST)
**Review type:** Self-administered simulated review (pre-submission), Major Revision verdict
**Review received:** 2026-05-02
**Response date:** 2026-05-02
**Commit at submission:** eba8cdd (HEAD after Task 8)

We thank the reviewer for the careful, constructive critique. The review surfaces three methodological issues and seven minor points; below we address each in **Critique → Response → Diff** format, where *Diff* gives the section, commit hash, and the substance of the change. One critique (Critique 3 part 2 — additional syntactic-tool comparison) is partially deferred with reasoning; one new analysis (v4 × MP5 robustness contrast) was added in response to Critique 1 and produces a result that *strengthens* the paper's core claim.

---

## Major issues

### Critique 1 — H2 not met under primary; asymmetric use of the low-power argument

**Reviewer's point.** The 49.1 % stipulated power is invoked to excuse H2 not meeting the threshold (δ = 0.323, 0.446 †, 0.439 † all sub-threshold), but the same low power undermines the abstract's causal claim that "MR design — not LLM source diversity — is the dominant lever". The −0.007 v3b → v4 contrast inherits R11 chained conditioning (cross-source pool + post-hoc MP1) and R13 protocol asymmetry. The reviewer concludes: either downgrade to a methodological paper, or rewrite the abstract / introduction / conclusion to remove causal-strength language.

**Our response.** We agree the asymmetric-power critique is methodologically valid and have made four concrete changes; one of them produces new evidence that the *direction* of the original claim is correct, but its phrasing has been refined to an axis-decomposition form rather than a generic causal "lever".

1. **New robustness contrast (`scripts/compute_rq2_v4_mp5.py` → `data/results/rq2_cliffs_delta_v4_mp5.json`).** We computed Cliff's δ on the v4 cross-source SMS pool while *holding the c-class primary MP at the pre-registered MP5* (i.e. v4 mutants but v3 c-class spec, no v3b post-hoc shift). This isolates the LLM-source-diversity axis from the c-class MP re-selection axis. Result: **δ_v4_mp5 = 0.314, 95 % CI [0.014, 0.622]** (commit b61f206). The contrast against v3 (δ = 0.323) is **−0.009**, reproducing the v3b → v4 micro-shift of −0.007 under an *independent* MP condition. The cross-source axis therefore shifts δ by ≤ 0.01 in magnitude under both MP5 and MP1 conditioning, while the MR-design axis (MP5 ↔ MP1) shifts δ by approximately +0.12 under both same-source and cross-source conditioning. The two-by-two table is:

   |             | Same-source         | Cross-source        |
   |-------------|---------------------|---------------------|
   | c-class MP5 | v3:    δ = 0.323    | v4_mp5: δ = 0.314   |
   | c-class MP1 | v3b:   δ = 0.446 †  | v4:     δ = 0.439 † |

2. **Revised Abstract** (commit 266c472). Replaces the causal "MR design is the dominant lever" with an axis-decomposition statement reporting both axes' magnitudes; explicitly notes that the LLM-identity axis ≤ 0.01 result holds across two independent MP conditions; defers the strong-sense source-diversity test (per-LLM differential prompts) to P4.

3. **Revised §8.1 finding (iii)** (commit 7aaf0b5). Mirror of the Abstract: reports the cross-MP / cross-source axis decomposition with v4 × MP5 numbers, then attributes the lever to the c-class primary-MP choice (not LLM identity under fixed prompt).

4. **Symmetric-reading paragraph in §5.4** (commit e26a6dc). Acknowledges explicitly that the same 49.1 % stipulated power that absolves H2 also limits what individual contrasts can claim about source diversity. The strengthened reading rests on consistency *across* two MP conditions, not on a single low-powered contrast.

We have **not** taken the reviewer's option (a) — re-positioning P2 as a pure methodology paper. The §3.5 empirical evidence (5.14 % AST overlap, 0/0/0 unreachability for HP / SI / TF) and the §2.6 SMS → MS degeneration theorem constitute substantive empirical and theoretical contributions on their own. We have taken the spirit of option (b) by replacing causal-strength language with axis-decomposition language.

**Diff.** Abstract (commit 266c472), §5.3 (commit 8283bc5), §5.4 (commit e26a6dc), §8.1 (commit 7aaf0b5); new artefact `data/results/rq2_cliffs_delta_v4_mp5.json` (commit b61f206).

---

### Critique 2 — §3.4 post-hoc selection contaminates the 4 / 4 narrative

**Reviewer's point.** Although §3.4 honestly declares the c-class MP5 → MP1 selection-on-the-response (one-sided permutation p = 0.9885), the 4 / 4 sign test, +91.4 % c-class SMS, +27 % C1 share, and +38 % d-class SMS are repeatedly used in narrative without inline caveats; the abstract's +91.4 % has no flag. The reviewer requests (a) † markers, (b) parallel reporting of v3 alongside v4 in the abstract, and (c) a v4 × MP5 contrast within the current paper.

**Our response.** All three sub-suggestions implemented.

1. **Single † convention defined in §3.4** (commit f1f84a5). One inline anchor for the dagger; every v3b / v4-derived number in the paper now points back to it.
2. **† applied uniformly** in the Abstract (+91.4 %, 0.446, 0.439), §5.5 (4 / 4), §6.1 (+91.4 %, +27 %, +38 %), §6.3 (+91.4 %, +38 %, 4 / 4), and §8.1 finding (iv) (commits 266c472, 414a0b4, 7aaf0b5).
3. **v3 numbers parallel-reported in the Abstract** (commit 266c472). The Abstract Results paragraph now lists δ values for v3, v3b †, v4 †, and v4_mp5 in sequence with their CIs, and reports the axis decomposition explicitly.
4. **v4 × MP5 contrast added** (Critique 1 response above; commits b61f206 + 8283bc5). The paper now contains four δ values across the two axes, not two.

We did **not** remove the v3b / v4 reporting from the paper; the † + §3.4 anchor make the conditioning unmistakable, and the v3b → v4 4 / 4 directionality is informative even when sub-threshold.

**Diff.** §3.4 (commit f1f84a5), Abstract (commit 266c472), §5.5 / §6.1 / §6.3 (commit 414a0b4), §8.1 (commit 7aaf0b5).

---

### Critique 3 — §3.5 AST unreachability: HOM rebuttal handling, single-tool comparison

**Reviewer's point.** (i) The Abstract's "categorically unreachable" claim is missing the "first-order" qualifier present in §3.6(ii). (ii) The mutmut / mutpy comparison is deferred to P4 — claims rest on a single syntactic tool (cosmic-ray), weakening external validity.

**Our response (i) — fully addressed.** Abstract revised (commit 266c472) to read "categorically unreachable by **first-order** syntactic tools (0/0/0)". The Highlights bullet (line 7) already had the qualifier; the Abstract is now consistent with both the Highlights and §3.6(ii).

**Our response (ii) — partially deferred with reasoning.** The reviewer notes that mutmut's operator set "strongly overlaps cosmic-ray's" and the cost-benefit of running mutmut on the 12-PUT grid is therefore weak. We extend that observation: both tools' default operator sets target AST-local replacements (binary / arithmetic / comparison / numeric replacement), and the §3.5 unreachability result is at the *operator-class* level (HP, SI, TF require non-AST-local intent: a hyperparameter perturbation knows the parameter's role; a structural injection adds a control-flow node; a trajectory flip rewrites the computation order). Both first-order syntactic tools therefore give 0 / 0 / 0 by construction, not by chance. We have not run mutmut empirically; we judge the duplication a poor use of revision resources given the categorical (not stochastic) nature of the unreachability result. If the reviewer disagrees, we can run mutmut on the 12 PUTs in a follow-up revision (estimated effort: 1–2 days).

**Diff.** Abstract (commit 266c472); §3.6(ii) text already conditional on first-order tools (no change needed).

---

## Minor issues

### Minor 1 — §5.2 effective-n + §5.4 stipulated power overlap

**Done** (commit e26a6dc). §5.2's effective-n note is trimmed to the distributional core (CI width and zero-mass dominance), with the H2-verdict argument routed through §5.4. §5.4 gains a one-sentence linking phrase from §5.2 and a new "Symmetric reading of the same power" paragraph addressing the reviewer's main critique about asymmetric power use.

### Minor 2 — RQ4 (Spearman ρ = 0.163, n = 12)

**Done** (commit eba8cdd). §1.4 RQ4 entry now reads "**descriptive only at n = 12; no formal test**; pre-registered as a P4 hypothesis-generating observation". §5.6 lead paragraph adds an explicit "Status" line stating the same. We have not demoted RQ4 to an appendix; removing a pre-registered RQ would itself be a post-hoc edit.

### Minor 3 — Reproducibility / Zenodo DOI

**Will do at terminal revision.** The repository contains `REPRODUCIBILITY.md` and `ZENODO.md` for archival workflow. We will mint the DOI on accepted manuscript and add the link to the §References preamble. JSON SSOTs (`paper_numbers_v4.json`, `lrca_60cell_v4.json`, `rq2_cliffs_delta_v4*.json`, `c_class_permutation_v4.json`, `rq2_cliffs_delta_v4_mp5.json` — newly added in this revision) will be archived together.

### Minor 4 — Acronyms in §1

**Will do.** Add a compact glossary at the end of §1.1 in the next revision pass (deferred to keep this revision focused on the methodological issues).

### Minor 5 — Theorem 9.1 / Lemma 9.2 proof-sketch directness

**Will do.** Add a one-sentence intuitive explanation of L4 (folding all MR to {MP_eq}) in §2.6 next revision pass.

### Minor 6 — §6.4 stakeholder cost figure (0.5 person-day per quarter)

**Will do.** Add a footnote to §E.2 noting whether the figure is measured (12-PUT pilot) or estimated; default reading is "estimated, P4 will instrument".

---

## Summary of substantive changes

| # | Section | Change | Commit |
|---|---|---|---|
| 1 | New artefact | `scripts/compute_rq2_v4_mp5.py` + `data/results/rq2_cliffs_delta_v4_mp5.json` (δ = 0.314, CI [0.014, 0.622]) | b61f206 |
| 2 | Abstract | Drop "dominant lever"; add "first-order"; parallel v3 / v3b † / v4 † / v4_mp5; axis decomposition; † on +91.4 % | 266c472 |
| 3 | §8.1 (iii)+(iv) | Axis-decomposition rewrite; † on +91.4 % | 7aaf0b5 |
| 4 | §5.3 | New "v4 robustness (under MP5)" row in three-stage list and contrast table; explanatory paragraph | 8283bc5 |
| 5 | §3.4 | Single-anchor † symbol convention | f1f84a5 |
| 6 | §5.5 / §6.1 / §6.3 | † applied to all v3b / v4-derived numbers | 414a0b4 |
| 7 | §5.2 + §5.4 | Effective-n trimmed; symmetric-reading paragraph added | e26a6dc |
| 8 | §1.4 + §5.6 | RQ4 framed as "descriptive only at n = 12; no formal test" | eba8cdd |
| 9 | This response letter | `docs/review_2026-05-02/response_to_simulated_review.md` | (this commit) |

**Deferred to next revision pass with reasoning given:** mutmut empirical re-run (Critique 3 part 2), Zenodo DOI mint (Minor 3 — terminal step), §1 glossary (Minor 4), Theorem 9.1 intuition (Minor 5), §E.2 cost-figure provenance (Minor 6).

---

## Net effect on the paper's central claim

The original Abstract claimed: "Under an identical prompt, MR design — not LLM source diversity — is the dominant lever on the aligned-vs-cross effect size."

The revised Abstract claims: "Within this design, the MR-design axis (c-class primary-MP choice) is the lever on the aligned-vs-cross effect size; the LLM-identity axis (Claude / GPT / DeepSeek under an identical prompt) shifts δ by ≤ 0.01 across two MP conditions."

The revision (i) replaces the generic "MR design" with the specific "c-class primary-MP choice", (ii) makes the source-axis null reading rest on consistency across two MP conditions rather than a single sub-threshold contrast, and (iii) defers the strong-sense per-LLM differential-prompt test to P4. The direction of the original claim is preserved; its phrasing is now precisely calibrated to the evidence base.
