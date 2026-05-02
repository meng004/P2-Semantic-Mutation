# Response to Simulated IST Review (Round 4 — Minor Revision)

**Manuscript:** When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels (P2 / IST)
**Round:** 4 (Minor Revision response)
**Reviewer verdict in Round 3 re-review:** Minor Revision (倾向接收, "lean accept")
**Round-3 response letter:** `docs/review_2026-05-02/response_to_simulated_review.md`
**Response date:** 2026-05-02
**Commit at submission:** 5477c28 (12-commit Round-4 cycle complete)

We thank the reviewer for the thoughtful and constructive Round-3 re-review, and especially for noting that the prior round's response was substantive. We have addressed all 11 items raised in the Minor Revision (4 reviewer-flagged P0★ priority items, 4 P1, 3 P2) plus two writing nits. Below is the item-by-item response in **Item → Action → Diff** format.

---

## Reviewer's four P0★ priority items (the ones you flagged for direct acceptance)

### Item A — §6.1 missing v3 → v4-mp5 cross-reference

**Reviewer's point.** The Round-3 §6.1 only discussed the v3b → v4 = −0.007 contrast, which inherits R11 chained conditioning. The discussion section's argument was therefore weaker than the Abstract's double-anchor framing.

**Action.** Inserted a sentence in §6.1's first paragraph, immediately after "(95% CI covers zero)", that reproduces the v3 → v4-mp5 = −0.009 robustness result and explicitly notes it strips R11. The §6.1 narrative now matches the Abstract and §8.1 finding (iii) double-anchor structure.

**Diff.** §6.1 first paragraph (commit 134b458).

---

### Item B — Abstract too dense; structure into Primary / Robustness / Exploratory blocks

**Reviewer's point.** The Round-3 Results paragraph crammed δ = 0.323, 0.446†, 0.439†, 0.314, four contrasts, +91.4%, etc. into a single block; the v4-mp5 = 0.314 robustness contrast was buried mid-paragraph with no signpost.

**Action.** Restructured the Abstract Results paragraph into four labelled italic blocks:
- *Primary verdict (v3, pre-registered):* δ = 0.323; 49.1% stipulated power
- *Robustness (v4-mp5, strips R11):* δ_v4-mp5 = 0.314; Δδ = −0.009
- *Exploratory (v3b / v4-mp1, post-hoc selection):* δ = 0.446† and 0.439†; Δδ(v3b → v4-mp1) = −0.007; full axis decomposition
- *Other:* C1_share, Friedman, AST overlap, first-order unreachability, † footnote

Every number from the Round-3 version is preserved; only the structure changed. The LaTeX preamble in `scripts/build_ist_submission_v4.sh` was updated to match.

**Diff.** Abstract Results paragraph (commit 2eb2c46) + LaTeX preamble in v4 build script.

---

### Item R1 — mutmut vs cosmic-ray operator overlap (the "strongly overlaps" assertion)

**Reviewer's point.** "Mutmut's operator set strongly overlaps cosmic-ray's" was stated as an assertion without supporting data; given that the §3.6 preventive-defence claim depends on this premise, the manuscript should make the overlap auditable.

**Action.** Built the manual cross-reference from the actual source code:
- cosmic-ray 8.4.6 default operators: 13 (`.venv/lib/python*/site-packages/cosmic_ray/operators/*.py`)
- mutmut current `main` default operators: 14 (`src/mutmut/mutation/mutators.py`)

Result added as **Appendix B.6** ("Mutmut vs cosmic-ray default-operator overlap"): a 17-row table mapping each operator class across both tools, marking which §3.2 necessary conditions (a) / (b) / (c) each one reaches. Aggregate finding: ~21 distinct first-order AST-local operator classes between the two tools; **none of the 21 reaches any of the three §3.2 conditions**. The HP / SI / TF zero overlap from §3.5 is therefore a structural property of first-order AST-local mutation, not a tool-specific limitation. §3.6(ii) now points to Appendix B.6.

**Diff.** New Appendix B.6 + §3.6(ii) cross-reference (commit f4bc57b).

This is the most substantive change in this revision round; the table is built from currently-installed tool source, so the claim is now reproducible.

---

### Item R3 — Reproducibility / Zenodo DOI archive link

**Reviewer's point.** The Round-3 manuscript did not state where the JSON SSOTs and mutant pools would be archived; IST requires a public archive for accepted manuscripts.

**Action.** Added a "Data and code availability" section before §References, listing (i) the JSON SSOTs (paper_numbers_v3 / v3b / v4 / v4-mp5, lrca_60cell, c_class_permutation, rq2_power_stipulated, cosmic_ray_12put_ast_diff), (ii) mutant pools, (iii) AVP source, (iv) analysis scripts. Pinned cosmic-ray and mutmut versions via `requirements-frozen.txt`. The Zenodo DOI is a placeholder (`10.5281/zenodo.XXXXXXX`) to be minted on acceptance — IST's own production workflow handles DOI assignment for accepted manuscripts, and we will update the placeholder before final submission.

**Diff.** New "Data and code availability" section (commit 5477c28).

---

## P1 items

### Item C — §5.3 list framed as "three planned + one robustness contrast"

**Action.** Changed the §5.3 list header from "Three-stage delta:" to "Four delta point-estimates (three planned ablation stages plus one robustness contrast):". The v4-mp5 row is now visibly co-equal with v3, v3b, v4-mp1 rather than reading as a sub-bullet of v4.

**Diff.** §5.3 list header (commit c317457).

### Item D — Terminology unification: v4-mp1 / v4-mp5

**Action.** Added a "Naming convention" sentence at the end of §3.4 defining `v4-mp1` (the cross-source pool with v3b's data-driven MP1 c-class primary, the version that reaches δ = 0.439†) and `v4-mp5` (the cross-source pool holding c-class primary at the pre-registered MP5, the version that reaches δ = 0.314). Both share the same v4 mutant pool; only the c-class primary-MP convention differs. Existing variant phrasings ("v4 cross-source", "v4 (under MP5)", etc.) remain as legitimate expansions of the convention; the §3.4 anchor lets readers normalise them.

**Diff.** §3.4 naming convention (commit a5ee8a4).

### Item R2 — §3.6 explicit HOM-conditional scope sentence

**Action.** Added a "**Scope of the claim.**" lead sentence at the top of §3.6: "The preventive-defence claim below is conditional on a first-order syntactic baseline; HOM-based syntactic compositions are an open question (R12) and are not refuted by the §3.5 evidence." Readers no longer need to chase R12 in §7 to know the claim's coverage boundary.

**Diff.** §3.6 lead sentence (commit 18661c4).

### Item W1 — Highlights bullet 4 replaced

**Reviewer's point.** "Cliff's delta = 0.439" without † in the Highlights might mislead quick-scanning readers into thinking 0.439 is the primary verdict (it is the exploratory v4-mp1 number).

**Action.** Replaced bullet 4 with: "Primary v3 Cliff's delta = 0.323 (H2 large-effect threshold not met); cross-source pooling shifts delta by ≤ 0.01 across two MP conditions (v3 → v4-mp5 = −0.009; v3b → v4 = −0.007)." This now leads with the pre-registered primary number and immediately follows with the double-anchor source-axis evidence, matching the Abstract.

**Diff.** Highlights bullet 4 (commit b01e362) + LaTeX preamble in v4 build script.

---

## P2 items

### Item R4 — §5.2 + §5.4 redundancy

**Action.** Added one sentence at §5.2's end: "Power and effect-size disambiguation are treated jointly with the stipulated-alternative analysis in §5.4 (avoiding repetition)." This routes readers past §5.2's effective-n note rather than letting them feel the same argument is being made twice.

**Diff.** §5.2 end (commit e184b75).

### Item R5 — §6.4 0.5 person-day cost basis

**Action.** Added inline cross-reference: "(detailed cost breakdown in Appendix E.2; estimates based on observed timings during this paper's 12-PUT campaign)" right after "0.5 person-day per quarter".

**Diff.** §6.4 inline cross-ref (commit debbead).

### Item R6 — §5.7 H5 framing

**Action.** Added a framing sentence before "H5 verdict: not met.": "H5 was pre-registered before pool characteristics were known; the dense cutoff sweep below shows the verdict is intrinsic to LLM-mutant pools and not a calibration artefact, which is itself a finding worth reporting." This re-frames the not-met verdict from "hypothesis failure" to "substantive finding about the LLM-mutant pool structure", consistent with the paper's transparency stance.

**Diff.** §5.7 framing sentence (commit 6c82bee).

### Item W2 — §5.5 "large concordance" caveat

**Action.** Replaced "(large concordance)" with "(large concordance, but caveat: N=3 per class makes this label nominal only)" in the Friedman per-class Kendall's W table to prevent quick-scanning readers from taking the label at face value.

**Diff.** §5.5 (commit 90beaeb).

---

## Items deferred (with reasoning)

The reviewer's writing nits about (i) Figure 1 LaTeX `\wedge` rendering and (ii) the §1 abbreviation table were left for the typesetting / production stage. Figure 1 will be visually inspected in the final IST production proof; the abbreviation table remains a low-priority improvement that would expand the manuscript by ~half a page without methodological gain.

---

## Summary of Round-4 substantive changes

| # | Section | Change | Commit | Reviewer item |
|---|---|---|---|---|
| 1 | §6.1 | v3 → v4-mp5 cross-reference inserted | 134b458 | A (P0★) |
| 2 | Abstract | Results restructured into Primary / Robustness / Exploratory / Other | 2eb2c46 | B (P0★) |
| 3 | §5.3 | List header reframed | c317457 | C |
| 4 | §3.4 | Naming convention added | a5ee8a4 | D |
| 5 | §3.6 | HOM-conditional scope sentence | 18661c4 | R2 |
| 6 | §5.2 | Bridge sentence to §5.4 | e184b75 | R4 |
| 7 | §5.7 | H5 framing | 6c82bee | R6 |
| 8 | §6.4 | E.2 cross-ref | debbead | R5 |
| 9 | Highlights | Bullet 4 replaced | b01e362 | W1 |
| 10 | §5.5 | Kendall's W N=3 caveat | 90beaeb | W2 |
| 11 | Appendix B.6 + §3.6(ii) | mutmut vs cosmic-ray operator overlap | f4bc57b | R1 (P0★) |
| 12 | New section | Data and code availability + Zenodo DOI | 5477c28 | R3 (P0★) |

All four P0★ priority items closed; all P1/P2 items closed; two writing nits deferred to typesetting.

---

## Net effect of Round 4

The reviewer described the Round-3 revision as moving the paper "from声明强度与证据强度不匹配 to 大体匹配" (from "claim-evidence mismatch" to "broadly matched"). Round 4 closes the residual organisational issues:
- The v4-mp5 robustness contrast now appears as a co-equal anchor in Abstract / §5.3 / §6.1 / §8.1 (not just §5.3 / Abstract / §8.1 with §6.1 still relying on the R11-contaminated v3b → v4 contrast).
- The Abstract is structurally readable on first pass: a reader can see "primary verdict" / "robustness check" / "exploratory" / "other" at a glance.
- The "mutmut strongly overlaps cosmic-ray" assertion is now a 17-row table built from current tool source; no part of §3.6's preventive-defence framing rests on an unsupported claim.
- The Zenodo archive commitment is in place.
- Eight smaller items are closed.

We thank the reviewer again for the careful re-read and the explicit mapping from each of the 11 items to a concrete revision target. If the editor agrees the response is sufficient, we are ready for acceptance.
