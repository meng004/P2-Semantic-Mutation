# Wave-J Final Acceptance Review — P3/P2 Two-Study Manuscript

**Reviewer role:** Combined EIC screening + R1 Methodology lens
**Target venue:** ACM TOSEM
**Artifact:** branch `claude/paper-journal-acceptance-kxpveo`, post-commit `cee2cf1`
**Date:** 2026-07-08
**Verdict:** MINOR REVISION (conditional on clearing 1 desk-risk blocker + 2 text-only majors)
**Acceptance-distance score:** **7 / 10**

---

## 1. Venue / Format Adjudication

### Page count — VERIFIED, not stipulated
I extracted the built PDF's top-level `/Type/Pages /Count` from the compressed
object streams of `submission/TOSEM_fastimpact_20260708/main.pdf`:

- **main.pdf = 50 pages** (root `/Count = 50`; the built `main.tex`, acmart
  `manuscript,screen,review`, is newer than and differs from the venue-neutral
  `source/main.tex`, so this is the current TOSEM build).
- supplementary.pdf = 24 pages.

The task premise ("body now 50 pages") is **confirmed against the artifact**, not
taken on faith.

### Fit to tracks
- **Fast-Impact Track:** TOSEM's Fast-Impact eligibility carries a ~45-page cap.
  At 50 pages the paper **no longer qualifies.**
- **Regular Track:** no page limit. The paper **fits the Regular track cleanly.**
  The acmart `manuscript,review` format already in the build is correct for
  Regular; **no reformatting is required** — this is a routing/declaration change,
  not a typesetting change.

### DESK RISK — BLOCKER (text-only)
The submission package still advertises the paper as a 45-page Fast-Impact
candidate. Both declarations files are stale and now **factually false**:

- `venues/tosem/cover_letter.md` L8 ("Fast-Impact Track handling if it satisfies
  the page-length eligibility condition"), L65–68 ("main manuscript is 45 pages
  including references … 42 pages … remains below the 45-page Fast-Impact
  threshold").
- `venues/tosem/declarations.md` L5 ("eligible for Fast-Impact Track handling"),
  L23–25 ("45 pages including references … 42 pages … below the 45-page
  threshold").

An editor's first action is a length check. A 50-page PDF submitted with a
signed statement that it is 45 pages and Fast-Impact-eligible reads as a
length misrepresentation and is a **desk-return trigger** independent of the
science. (`source/main.tex` itself contains no page/track claim — good; the
defect is confined to the two venue docs.)

**Track-switch changes required (all text-only, ~30 min):**
1. Cover letter: "Journal-First … Fast-Impact if eligible" → "Journal-First,
   **Regular Track**"; delete or rewrite the "Length statement" paragraph to
   state 50 pages honestly and note the Regular track imposes no length cap.
2. Declarations: `Track` → Regular; `Length` → correct to 50 pp and drop the
   Fast-Impact-threshold framing.
3. `submission/TOSEM_fastimpact_20260708/` directory name and `readme.txt` still
   say "fastimpact" — rename/relabel to avoid contradicting the Regular-track
   cover letter (polish, but do it in the same pass).

---

## 2. Methodology of Study 2 (Reviewer lens)

### (a) Same-vendor Claude harness — is it scientifically acceptable?

**Argument FOR acceptability (for the claims actually made):**
- The three confirmed hypotheses do **not** depend on vendor diversity. H1′ is a
  deterministic count of non-equivalent admitted mutants per family
  (verdict-factual). H2-1′ is aligned-vs-cross SMS magnitude *within one
  generation arm.* H3′ is class-direction consistency. None is a cross-vendor
  claim.
- Role isolation + packet blinding are enforced across *separately spawned*
  instances (no generator id, no arm label, no SMS/kill outcome in the reviewer
  packet), which controls the within-run leakage that these hypotheses are
  exposed to.
- The one hypothesis that genuinely needs vendor diversity — H2-2
  (source-diversity dual-blind) — is **gated NOT-RUN with no same-vendor proxy
  substituted** (`dualblind_delta_delta_v5.json` H2_2 verdict). Refusing to
  proxy a cross-vendor arm with a same-vendor one is the scientifically correct
  move, not a dodge.
- Disclosure is front-loaded in body text (§"Harness instantiation", L2885–2903),
  not hidden in a footnote — exactly as an integrity-first design should.

**Argument AGAINST:**
- A shared model family means the "blind reviewer" shares priors and failure
  modes with the generator. Equivalence judgements (E1∧E2) of Claude-generated
  mutants by Claude reviewers can be systematically *correlated*, and the SSOTs
  show `equivalence_ledger: null` — i.e. admission/equivalence rests **entirely**
  on the same-family reviewer verdicts (774 valid → 756 admitted, only 4
  rejected; all 6 UNCERTAIN resolved to CONFIRMED). H1′'s non-equivalent count,
  and therefore the H2-1′/H3′ SMS slices computed over the admitted pool, inherit
  any same-family equivalence bias. This is a real, if bounded, monoculture
  threat.

**VERDICT:** **Acceptable for the directional / feasibility claims made**, because
(i) the claims are explicitly directional, not magnitude; (ii) the
vendor-dependent hypothesis is gated, not proxied; (iii) disclosure is plain.
It does **not** undermine H1′/H2-1′/H3′ *as stated.* The residual same-family
equivalence-correlation threat is not currently isolated as a Threats bullet and
should be (Major, text-only — see §3).

### (b) Pre-registration + one-shot + incident apparatus — credible/checkable?

**Credible and checkable, with one honest ceiling.**
- Registration v1.1 is in-repo; power SSOT `power_study2_v11.json` carries every
  threshold with seed 20260708 (feasibility 0.843, power 0.9285 @ n=28, 0.949);
  each analysis SSOT carries `pre_registration` + `integrity: pre-frozen before
  data generation` provenance fields.
- The incident apparatus (`PILOT_LOG.md`) is append-only and discloses the
  near-miss pool-deletion Incident #1 + recovery, code defects D1–D5, packet
  defects P4–P7, and post-freeze deviation D-A1. D-A1 is honestly labelled a
  *disclosed deviation* and mirrored in the output SSOT's `post_freeze_deviation`
  field; the manuscript states H2-1′ logic is "byte-unchanged." This is
  exemplary transparency.
- **Ceiling:** the freeze is self-attested on the *same working branch* — there
  is no third-party mint / cryptographic timestamp (v1.0 is openly called
  "un-minted"). A skeptical reviewer cannot independently verify freeze-precedence
  over data generation; it rests on git history + author attestation. Honesty
  ("un-minted") mitigates, but the manuscript should say this out loud (Major,
  text-only).

### (c) H4′ NOT_CONFIRMED — handled with integrity?

**Yes — exemplary.** Front-loaded (scoreboard "leads with … the miss" L2937;
abstract L138; intro L205–207). Interpreted, not rescued (§Interpretation
L3025–3039: leakage *generalises* beyond CF/TF, OS newly leaks, "LRCA single-
stratum attribution remains an open construct boundary," and explicitly
"an open problem, **not a promised third study**"). No threshold-moving, no
post-hoc re-spec to force a pass. The per-family breakdown in the manuscript
(TF 72/135, OS 27/123, CF 9/18, SI 9/69, CE 0/207, HP 0/189) matches the SSOT
exactly.

### (d) Two-study claim ladder — overclaim / 0.474 revival?

**Ladder holds; no overclaim; 0.474 correctly NOT revived.**
- Ladder is stated identically in intro (L209–212) and §Interpretation
  (L3017–3020): "Study 1 delimits the construct, Study 2 confirms the delimited
  construct *directionally, without upgrading the medium effect into a
  large-effect claim.*"
- Every `0.474` occurrence in `source/main.tex` is inside **Study 1** sections
  (RQ4 stipulated-power, L617–2251). Study 2 explicitly "deliberately does not
  re-assert Study 1's 0.474 large-effect bar" (L2978) and reports the Romano
  medium band + two-sided CI as descriptive-only. H2-1′'s registered test is the
  one-sided δ>0 lower-bound rule, not δ≥0.474. Clean.

---

## 3. Distance to STABLE ACCEPTANCE (minor) — Score 7/10

The Study-2 science is sound, honestly reported, and every headline number
traces to a frozen SSOT (§4). What stands between the current package and a clean
minor-revision accept is **one desk-risk blocker and two text-only majors** — no
new experiment is required for the claims made.

| # | Severity | Tag | Residual |
|---|----------|-----|----------|
| 1 | **BLOCKER** | text-only | `cover_letter.md` + `declarations.md` still claim Fast-Impact eligibility + 45/42-page counts; PDF is 50 pp. Switch both to Regular track and correct the page numbers. Desk-return risk until fixed. |
| 2 | **MAJOR** | text-only | Prereg freeze is self-attested on the working branch with no external timestamp/mint. Add an explicit sentence in §Study2-design (and a Threats bullet) that the registration is un-minted and freeze-precedence rests on git history + attestation, not a third-party registry. |
| 3 | **MAJOR** | text-only | Same-vendor equivalence-correlation threat is not isolated in Threats. Add a bullet: reviewer instances share a model family with the generator and are the sole equivalence arbiter (`equivalence_ledger: null`), so H1′/H2-1′/H3′ inherit any same-family equivalence-judgement bias — bounded but real. |
| 4 | minor | text-only | `declarations.md` "Generative AI Disclosure" calls the harness "review-simulation support," understating that Study 2's confirmatory review + arbitration verdicts *are* produced by the Claude harness. Reconcile with §Study2-harness. |
| 5 | minor | new-experiment (optional) | H2-2 gated not-run leaves the flagship source-diversity question open. Not required for current claims, but the single most likely reviewer ask; a small cross-vendor pilot would pre-empt it. |
| 6 | polish | text-only | Study-2 abstract sentence (L138) is a single ~120-word clause chain; split for readability. |

**Why 7 and not 8+:** residual #1 is a genuine desk-reject trigger (an editor
length-check fails before the science is read), and #2/#3 are integrity-facing
gaps a methodology reviewer *will* flag. **Why not lower:** all three are
text-only, ~1–2 hours total; the H4′ miss, the 0.474 discipline, the incident
disclosure, and the SSOT-number fidelity are already at acceptance standard.

---

## 4. Study-2 number verification against SSOTs (10 checked, all PASS)

| # | Value (manuscript) | JSON path | tex line | Status |
|---|--------------------|-----------|----------|--------|
| 1 | Cliff's δ = +0.4295 | `dualblind_delta_delta_v5.json → H2_1_aligned_dominates_cross.cliffs_delta` | L2954, L2971 | ✓ |
| 2 | one-sided 95% lower = +0.2653 | `…H2_1_aligned_dominates_cross.one_sided_95_lower_bound` | L2954, L2972 | ✓ |
| 3 | two-sided CI [0.2328, 0.6193] | `…H2_1_aligned_dominates_cross.descriptive_only.two_sided_ci95` | L2975 | ✓ |
| 4 | H1′ 5/5 families; SI clears 8 | `h1_instantiability_v5.json → …n_families_clearing_bar=5; per_family.SI.puts_cleared=8` | L2957, L2981–84 | ✓ |
| 5 | H1′ ceilings 23/14/21/15/10 | `h1_instantiability_v5.json → per_family.{CE,OS,HP,TF,SI}.coverage_ceiling_28` | L2957, L2981 | ✓ |
| 6 | H3′ 3/4 positive; C 0.0476 vs 0.0714 (neg) | `h3_class_consistency_v5.json → n_classes_positive=3; per_class[C].class_mean_aligned_sms/cross` | L2959, L2992–93 | ✓ |
| 7 | H3′ Friedman χ² = 26.23 | `h3_class_consistency_v5.json → friedman_across_mps_exploratory.friedman_chi2 (26.2297)` | L2997 | ✓ |
| 8 | H4′ mean suspect_share = 0.1714 | `s5_purity_v5.json → H4_attribution_purity.mean_suspect_share` | L2962, L3001 | ✓ |
| 9 | H4′ TF 72/135, OS 27/123, CF 9/18, SI 9/69, CE 0/207, HP 0/189 | `s5_purity_v5.json → H4_attribution_purity.per_family_multistratum` | L3004–05 | ✓ |
| 10 | 140 confirmatory cells, 36 nonzero-killed | `s5_purity_v5.json → n_cells_scored=140`; nonzero `n_killed>0` count = 36 (recomputed) | L2909–10 | ✓ |

Registered thresholds also cross-check to the power SSOT: feasibility 0.843,
power 0.9285 @ n=28, power 0.949 all present in `power_study2_v11.json`.

**No number discrepancy found.** SSOT ↔ PILOT_LOG ↔ manuscript are mutually
consistent across all 10 checks.
