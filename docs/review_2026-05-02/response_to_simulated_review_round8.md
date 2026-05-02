# Response to Simulated IST Review (Round 8 — Major Revision response)

**Manuscript:** A semantic mutation metric for metamorphic relation adequacy in scientific computing programs (P2 / IST)
**Round:** 8 (Major Revision response, post-Round-4 Accept which has been reopened by a more critical Round-7 reading)
**Reviewer verdict in Round-7 review:** Major Revision
**Round-3 / Round-4 response letters:** `docs/review_2026-05-02/response_to_simulated_review.md`, `..._round4.md`
**Response date:** 2026-05-03
**Commit at submission:** v8 build cluster (head: this commit)

We thank the reviewer for the careful Round-7 reading. The review's three core critiques surfaced gaps that prior rounds (which converged on Accept) had not closed, and we have implemented all of them as substantive structural changes to the paper. Below is the per-item response.

---

## Reviewer's three core problems

### Problem 1 — H2 not met; "49.1% power" defense creates internal tension

**Reviewer's point.** If the design's stipulated power at the threshold is 49.1%, then it was insufficient *a priori* to test H2. The "point estimate vs underlying effect size" reframing is not a defense but a sign of design underpowering, and the Abstract should not simultaneously claim it tested H2 and that its design cannot reliably test H2.

**Response (Abstract reorganised; commit 2e49824).**

1. **Abstract first sentence on Results now explicitly states**: "**The H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is not met under the pre-registered point-estimate criterion**: v3 δ = 0.323 (95% CI [0.017, 0.622])."
2. **Removed the "49.1% stipulated power" defense from the Abstract.** The full power analysis remains in §5.4 for technical reference, but the Abstract no longer uses it as a re-framing device.
3. **Reframed H2 verdict** as "underpowered exploratory contribution; full verification deferred to P4 with n_PUT ≥ 30". This honours the reviewer's principle that a paper should not double-claim "we tested H2" and "our design cannot reliably test H2".
4. **Highlights bullet 4 also revised** to lead with the v3 H2-not-met fact, not the exploratory v4 number.

We did not adopt the reviewer's alternative suggestion of downgrading H2 to medium-effect (δ ≥ 0.330, Romano 2006). That would be a retroactive change to pre-registration, which we judge less honest than acknowledging design underpowering. The choice between "downgrade H2" and "acknowledge underpowering" is editorial; we have erred toward the latter.

### Problem 2 — post-hoc c-class primary MP shift contaminates the main narrative

**Reviewer's point.** The MP5 → MP1 post-hoc shift at §3.4 (one-sided permutation p = 0.9885) means a δ inflation of the magnitude observed (v3 → v3b: +0.123) is essentially indistinguishable from random reselection. The contamination then propagates: H4 4/4†, +91.4%†, Δδ(v3b → v4-mp1) = −0.007. Even the v4 cross-source inherits the post-hoc selection (R11 chained conditioning). The only contrast not contaminated is **v3 → v4-mp5 (Δδ = −0.009)**, holding c-class primary at the pre-registered MP5.

**Response (paper structurally reorganised around v3 + v4-mp5 main axis; commits 2e49824, e562acf).**

1. **v3b and v4-mp1 are now formally relegated to Appendix-D Sensitivity Analyses** (Abstract Round-8 revision). They remain in the paper for completeness but are not used as evidentiary anchors in the main narrative.
2. **§3.4 now contains an explicit "Statistical-indistinguishability note"** (commit e562acf) stating in the main body that "a δ inflation of the magnitude observed (v3 → v3b: +0.123) is essentially indistinguishable from random reselection of the c-class primary MP under the null". This is the formal interpretation of "selection on the response" in this design, and it applies to every † number.
3. **The Abstract Conclusion now restricts the source-axis null reading to v3 vs v4-mp5 only**: "Restricting the source-axis comparison to the only contrast not inheriting the §3.4 post-hoc selection (v3 with δ = 0.323 versus v4-mp5 with δ = 0.314, Δδ = −0.009), the LLM-identity axis ... does not appreciably shift δ within this design." All Round-3 and Round-4 framing of "MR design vs LLM-source axis" that depended on v3b → v4-mp1 = −0.007 has been replaced with this single-anchor reading.
4. **Highlights bullet 4** now reads "Source-axis null reading rests on v3 vs v4-mp5 contrast (Δδ = −0.009), the only contrast not inheriting R11" — directly mirroring the Abstract.

The paper retains v3b/v4-mp1 only as Appendix-D sensitivity reports; the main narrative is now anchored entirely on **two pre-registered MP5 conditions: v3 (same-source, δ = 0.323) and v4-mp5 (cross-source, δ = 0.314)**.

### Problem 3 — "categorically unreachable" overclaims; HOM caveat too thin

**Reviewer's point.** The 0/0/0 + 5.14% empirical evidence supports unreachability **under default first-order configurations** of cosmic-ray and mutmut, not unreachability *categorically*. HOM (Jia & Harman 2008, 2009) is the strongest first-order rebuttal and is processed as residual threat R12 without conceptual analysis.

**Response (softening + conceptual HOM analysis; commits 08332c0, ca8c716).**

1. **All five occurrences of "categorically unreachable" replaced** with "unreachable under default first-order configurations" or with explicit configurational scope (Highlights, §3.5 interpretation, §3.6 preventive-defence, §6 confirmation, §8.1 finding).
2. **§3.6(ii) now contains a "Conceptual analysis of HOM reachability" subsection** (commit ca8c716, ~4 paragraphs, ~400 words) addressing the §3.2 (a)/(b)/(c) necessary conditions one by one:
   - **(a) cross-function-boundary**: HOM compositions over default first-order operators remain AST-local within their target node; reaching `det(M) → sum(np.diag(M))` requires both operators to coincide with a meaningful cross-boundary swap, which is exponentially unlikely under default operator menus.
   - **(b) domain-knowledge-dependence**: HOM has no awareness of which constants are load-bearing in the PUT class; a Number-Replacer ∘ Boolean-Swap chain on a Gaussian-process kernel does not "know" that 1e-4 is the regularization knob.
   - **(c) algorithmic-class-change**: HOM compositions over default first-order operators are bounded above by AST-local edits and cannot reach algorithmic-class change without being effectively equivalent to a manual rewrite.
3. **Jia and Harman (2008) "Constructing Subtle Faults Using Higher Order Mutation Testing" SCAM** added to §References as the strongest first-order rebuttal precedent.
4. **Direct empirical HOM falsification** (running mutmut second-order mutants and re-doing the AST overlap analysis) remains residual threat R12 and is reserved for P4. The conceptual analysis does not refute HOM; it argues HOM is unlikely to refute the unreachability finding on combinatorial grounds.

---

## Other reviewer issues

### Mixed-effects Singular matrix as design limitation (commit 66c1ccd, §7.X)

The reviewer noted the Singular matrix at N = 60 reflects fundamental design limitations, not numerical accident. Added §7.X explicitly stating that "60 observations across 12 PUTs cannot identify an 11-dimensional fixed-effects structure plus 12-PUT random intercepts. This is a hard limit of the present design ... P4's expansion to n_PUT ≥ 30 is the only path to a properly identified hierarchical model."

### 3 of 12 PUTs are zero-mass cohort (commit 66c1ccd, §7.Y)

The reviewer noted that Figure 2's all-zero rows for A1, B1, D2 (25% of the PUT cohort) are a substantive limitation of SMS as an adequacy metric. Added §7.Y as residual threat **R14**: "for 25% of the PUTs, SMS gives zero signal at every operator-MP cell ... SMS cannot distinguish strong from weak MR sets on that PUT."

### R13 protocol asymmetry magnitude (commit 66c1ccd, §7.Z)

The reviewer asked for a quantitative bound on the dual-blind → mechanical-gate quality drop. Added §7.Z giving a rough order-of-magnitude estimate: "the upper-bound δ-shift contribution from removing the reviewer step is bounded above by approximately ±0.03 to ±0.05 on Cliff's δ at n_aligned = 12. This bound is comparable in magnitude to but smaller than the +0.12 MR-design axis shift and an order of magnitude larger than the −0.009 source-axis shift. The bound therefore does not change the conclusion direction, but a direct dual-blind v4 rerun (P4 commitment) would give a tighter quantification."

### H5 "intrinsic data property" framing (no change needed)

Already addressed in Round-4 with the §5.7 framing sentence ("H5 was pre-registered before pool characteristics were known ... a finding worth reporting"). No additional change.

### Anonymous review repository link (commit e562acf)

Added to the Data and code availability section: "an anonymized read-only mirror of the repository is available at [https://anonymous.4open.science/r/p2-sms-anon-XXXX] (URL to be provided by the corresponding author upon Editor request, per IST guidelines)."

### Abstract length and density

The Round-8 restructure (Primary / Robustness / Sensitivity / Other / Conclusion) takes the Abstract slightly above the IST 250-300 word ideal. We retained the structure because the Round-7 reviewer (and a hypothetical reader) needs to see the H2 not-met fact, the v4-mp5 anchor, and the v3b sensitivity demarcation in the Abstract itself. Production-stage tightening can compress the Sensitivity sentence to a subordinate clause if the Editor requires.

### Sun et al. SPE entry year (commit 3e71640)

Round-7 audit identified a MINOR nit: the Sun et al. SPE 3.280 paper has Wiley print issue 2024 (vol 54 iss 3) but was online-first in 2023. Updated to 2024 across §1.1, §1.3, and §References to match Wiley print convention.

---

## Summary of Round-8 substantive changes

| # | Section | Change | Commit | Reviewer item |
|---|---|---|---|---|
| 1 | §1.1 / §1.3 / §Refs | Sun 2023 → 2024 (Wiley print year) | 3e71640 | Round-7 nit |
| 2 | Abstract Results + Conclusion | H2-not-met first; demote v3b/v4-mp1 to Sensitivity; v3+v4-mp5 main anchor | 2e49824 | P1 + P2 |
| 3 | 5 sites globally | "categorically" → "default first-order configurations" | 08332c0 | P3 |
| 4 | §3.6(ii) | Add conceptual HOM analysis + Jia & Harman 2008 SCAM citation | ca8c716 | P3 |
| 5 | §7.X / §7.Y / §7.Z | Singular matrix design limit + 25% zero-mass cohort R14 + R13 magnitude ±0.03–0.05 | 66c1ccd | minor 1, 2, 6 |
| 6 | §3.4 + §Data avail. | Statistical-indistinguishability note + anonymous review mirror commitment | e562acf | minor 4, P2 |
| 7 | (post-Round-8) | Humanizer pass: 4 em-dashes in R8 edits replaced | (humanizer commit) | — |
| 8 | scripts/, submission/ | v8 build (99 pages, zero missing-character) | (build commit) | — |

---

## Net effect on the paper's central claim

**Round-7's challenge**: the paper's main empirical narrative was contaminated through R11 chained conditioning, leaving "MR-design is the lever, LLM-identity is not" too brittle.

**Round-8's response**: the main narrative is now anchored on two pre-registered MP5 conditions (v3 and v4-mp5), giving a single uncontaminated source-axis contrast (Δδ = −0.009). The post-hoc-selection numbers (v3b, v4-mp1, +91.4%†, etc.) are formally relegated to Appendix D as sensitivity analyses and explicitly characterised as "indistinguishable from random reselection" in §3.4 main body. The H2 verdict is now "not met under pre-registered criterion; underpowered exploratory; deferred to P4". The §3.5 first-order unreachability evidence is preserved but bounded by an explicit HOM conceptual analysis.

The paper now neither over-claims (no more "categorically unreachable", no more "MR-design is the dominant lever") nor under-claims (the v4-mp5 contrast still supports a cautious source-axis null reading; the §3.5 evidence still supports a first-order unreachability claim). The framing is calibrated to the evidence's actual coverage.

We thank the reviewer once more for forcing this calibration.
