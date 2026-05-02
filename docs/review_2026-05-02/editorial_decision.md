# Editorial Decision Package — P2 Manuscript (Round 2 Re-Review)

**Manuscript**: *When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels*
**Target Venue**: *Information and Software Technology* (IST)
**Editorial date**: 2026-05-02
**Synthesis basis**: 5 independent reviewer re-review reports (R0 EIC + R1 Methodology + R2 Domain + R3 Practical/Cross-disc + R4 Devil's Advocate) on the post-revision English manuscript `论文初稿P2_EN.md` (1,700 lines, commit 37fa9bb)
**Round-1 verdict**: Major Revision (5/5 consensus, 4 CRITICAL items)

---

## 1. Editorial Decision Letter

### Final Decision (Round 2): **MINOR REVISION (conditional Accept)**

#### Rationale (one paragraph)

The post-revision manuscript shows **substantive responsiveness** to the Round-1 Major Revision. Of the 4 Round-1 CRITICAL items, CRITICAL-4 (17.6:1 ratio fabrication) is **fully neutralized** (R4 verdict); CRITICAL-1 (title overreach), CRITICAL-2 (v3b post-hoc propagation), CRITICAL-3 (multiplicity correction) are **partially neutralized** by the title rewrite (added "Same-Prompt" + "Single-Output ... Kernels"), the §3.5.1 caveat structure, and the cross-cell exchangeability permutation null + Bonferroni quantification. The new §3.2.6.3 12-PUT cosmic-ray empirical (NEW-MAJOR-1, commit 2547b61: 5.14% overall AST overlap with HP/SI/TF=0/0/0 categorical unreachability) **exceeds** the Round-1 expectation and substantively closes the "P2 = post-classification copy of syntactic mutants" challenge. **However**, the strict 5-reviewer re-review surfaced **two ESCALATED defects** introduced by the revision (translation drift): (i) the English manuscript was missing §3.5.1, §3.6, §3.7 and §5.9.2/3 entirely (all referenced 17–19 times in the body and Abstract), and (ii) the Abstract H2 wording still reads "is rejected" while §5.7.2 self-cites the P0-8 mandate "not met under the pre-registered point-estimate criterion" — a direct internal contradiction at the most-read paragraph. Both defects are textual / consistency problems, not scientific failures, and have been fixed in commit (this round). After the additional minor edits below are applied, the manuscript meets IST publication standards. R3 (Perspective) dissents at Major Revision focused on §6.5 (deployability), with D-6 (practical deployability) at 3/10 as the binding constraint; this dissent is preserved as a substantive concern for Round 2 minor work but does not block the verdict because (a) §6.5 is deployment-discussion, not core methodology; (b) R3's six concrete fixes are 1–2 days of textual work; (c) R0/R1/R2/R4 (4/5 reviewers) all converge on Minor Revision.

#### Strengths preserved (Round-1 strengths verified to hold)

(1) **§9 SMS→MS degeneration theorem** restructured to 3 joint conditions L1/L2/L3 with measure-zero qualification on Lemma 9.1 (R1 W5 fully addressed; R2 W3+W4 verified ✓).
(2) **§4.2.5 three-stage ablation** retained with v3 (pre-registered, primary), v3b (exploratory, post-hoc c-class shift), v4 (cross-source); contrast table reports Δδ_MR = +0.123 and Δδ_LLM = −0.007 separately (no synthesized ratio) — directly closes CRITICAL-4.
(3) **§3.2.6.3 12-PUT cosmic-ray empirical (NEW)** is a strong substantive addition: HP=0/72, SI=0/33, TF=0/54 categorical unreachability (54.5% of P2 pool); CE=7.81%, OS=11.67%, CF=33.33% honestly reported including the §3.2.6.1 OS row downgrade (cosmetic-fix avoided).
(4) **Methodological honesty**: §3.5.1 v3b post-hoc declaration, cross-cell exchangeability permutation null (p = 0.9885 vs null mean), Bonferroni × 5 effective α, §5.6.2.1 cutoff sensitivity, §7.1.8 R11 chained-conditioning declaration — all retained or strengthened.
(5) **R-1 P0 blocker closed**: full English translation `论文初稿P2_EN.md` (commit 37fa9bb) executed via BLTCY proxy + Anthropic Opus 4.7 streaming, glossary-driven, with section-level partials cached for incremental update.

#### Round-2 Conditional-Accept Checklist (Mandatory before Accept)

The following items must be addressed in a final minor revision pass (estimated 1–2 days). After these edits, the editorial decision converts to **Accept**.

##### Group A — ESCALATED (must close to remove ✗-blocking concerns from R4)

- **A1** §3.5.1 missing in English manuscript — **fixed in this round** (translated and inserted at line 676 of `论文初稿P2_EN.md`; verify against Chinese authoritative source). [R4 ESCALATED-1, R1 W3]
- **A2** Abstract line 14 H2 wording — **fixed in this round** ("is rejected" → "is not met under the pre-registered point-estimate criterion" in both CN and EN). [R4 ESCALATED-2, R0 §5.7.2-Abstract alignment]
- **A3** §3.2.6.1 OS-row table cell still showed "✗ Tool inexpressible" while §3.2.6.3 prose reports 88.33% disjoint + 11.67% incidental — **fixed in this round** (cell updated to "△ 88.33% disjoint" with §3.2.6.3 reference; operator-level conclusion paragraph also revised to be honest about HP/TF/SI categorical vs OS partial). [R4 strongest residual, R0 W7]
- **A4** §3.2.6.3 LLM-source bias claim numbers — **fixed in this round** (DeepSeek 7/15 → DeepSeek 11/15; "unknown 4/15" removed; reconciled against `data/results/cosmic_ray_12put_ast_diff.json`). [R1 (c), R4]
- **A5** §5.9.2 and §5.9.3 missing in English manuscript — **fixed in this round** (translated and inserted). [R0 NEW P0]
- **A6** Line 1185 dangling "IST 2024" — **fixed in this round** (CN line 1299 + EN line 1293 both edited to remove "IST 2024" and add Tip 2024 estimand caveat). [R0 W6, R2 W5, R4]

##### Group B — Methodology hardening (R1 P1 items)

- **B1** §5.7.3 power analysis: supplement (not replace) plug-in bootstrap power 0.42 with a **stipulated-alternative simulation against truth_δ = 0.474** (~30 lines of code, ~1 hour). [R1 W1]
- **B2** §5.8.4 per-class Friedman: add Kendall's W column; apply Bonferroni × 4; report adjusted p (b-class 0.029 → 0.116). Likely flips "individually significant" to "no class significant after correction" — methodologically more honest at small per-class N. [R1 W4 follow-up]
- **B3** §7.1.2 K_eq sensitivity table: **deliver** {500, 1000, 2000} sweep **OR** downgrade promise to §7.5 limitations. [R1 P1]

##### Group C — Domain literature (R2 P2)

- **C1** §1.3.2 + §8.1: add CPH (Coupling-Effect Hypothesis) reference + 4 missing classics (DeMillo 1978; Andrews et al. 2005; Papadakis et al. 2019; Just et al. FSE 2014). One-paragraph addition to §1.3.2; 4 entries to §8.1. [R2 W9 P2]
- **C2** §1.6.2 toy-scope sentence: append one sentence per R2 W7. [R2 P2]
- **C3** §9.5 Corollary 9.1 attribution: per-C_k attribution still has C2/L4 and C5/L6 swapped from minimal sufficient condition — either fix table or change to generic statement. [R2 W10]
- **C4** Add Vargha & Delaney 2000 (JEBS) to §8.5 + Ammann & Offutt 2008 to §8.1. [R0 P2]

##### Group D — Practical deployability (R3 dissent at Major Revision)

R3 explicitly states D-6 (practical deployability) stays at 3/10 as the binding constraint and recommends Round-2 Major Revision focused on §6.5. To convert R3's verdict to Minor (and avoid the §6.5 chapter becoming the "single most-quoted criticism" at the IST review committee), the following six concrete §6.5 fixes are mandatory:

- **D1** §6.5.3 numeric thresholds (≥ 0.20 / ≥ 0.30 at lines 1387–1388 EN): **delete**. The thresholds were arbitrated to P1 in Round-1 editorial decision §3 Disagreement-3 and were not executed. [R3 W1]
- **D2** §6.5.3 subsection title: rename "Auditors / certification bodies" → "**Research-grade evidence for V&V documentation (long-term aspiration)**". [R3 W1 fix-(b)]
- **D3** §6.5.2 YAML fragment (line 1373 EN): either **excise the YAML** or **remove the env-var trap** (currently hardcodes `SMS_VERSION=v4` + `P2_PRIMARY_VERSION=v3b` in stakeholder-facing PR-CI template, propagating v3b post-hoc selection into adopters' pipelines; threshold 0.10 also contradicts §6.5.3 threshold 0.20). [R3 W3]
- **D4** §6.5.1: add one-paragraph **air-gap incompatibility declaration** (the LLM-call dependency makes P2's mutant generation incompatible with most regulated air-gapped V&V workflows). [R3 W4]
- **D5** §6.5.2: add **PR-CI resource estimate** + reframe to **quarterly audit** rather than per-PR gating. [R3 W5]
- **D6** §1.1 line 38 permission-clause: **delete** the licensing of unqualified "scientific computing" usage in narrative contexts; instead require the "single-output kernels" qualifier in §6.5 stakeholder pain-point sentences (lines 1346, 1359, 1382 EN). [R3 W2 follow-up + permission-clause]
- **D7** §8 References: add **ASME V&V 20-2009** entry; §1.3.2 acknowledge V&V 20 §3 code verification as a complementary V&V layer. [R3 W10]

These D-items are textual / scoping fixes (~1–2 days of careful editing, no new experiments). On their delivery, R3 has explicitly committed to withdraw the Round-2 Major Revision recommendation.

#### What would push back to Major Revision

If on resubmission the Group A items remain unfixed (translation drift / Abstract internal contradiction / OS table cell / LLM source numbers / IST 2024 dangling), the editor will return the manuscript to Major Revision because these are structural integrity failures that any English-only reviewer will identify on first read.

#### What would push to Reject

Nothing in the current revision. The Round-1 reject trigger (v4-pre showing Δδ_LLM > 0.05 outside zero CI) was elected not to be tested; the title rewrite is an editor-acceptable resolution.

---

## 2. Reviewer Verdict Tally

| Reviewer | Round 1 verdict | Round 2 verdict | Δ score |
|---|---|---|---|
| **R0 (EIC)** | Major Revision | **Minor Revision** (conditional Accept after 8-item checklist) | 6.7 → 7.4 (+0.7) |
| **R1 (Methodology)** | Major Revision | **Minor Revision** (6 items, mostly textual) | improved |
| **R2 (Domain)** | Major Revision | **Minor Revision** (4 residual items) | 6.71 → 7.43 (+0.72) |
| **R3 (Perspective)** | Major Revision | **Major Revision round 2 (§6.5-focused)** | 5.57 → 5.79 (+0.22) — D-6 stays 3/10 |
| **R4 (Devil's Advocate)** | NOT Accept (4 CRITICAL) | **Minor Revision** conditional on 5 fixes | 0/4 CRITICAL → 0/0 after Group A fixes |

**Synthesized verdict**: 4/5 reviewers Minor Revision; 1/5 (R3) Major Revision focused on §6.5. Per IRON RULE 4, R4's Round-1 CRITICAL findings cannot block Accept once neutralized; with Group A fixes applied (this round), R4's 5 conditional fixes are satisfied. R3's dissent is preserved as the §6.5 deployability concern in Group D.

---

## 3. Consensus Items (≥3 reviewers independently flagged in Round 2)

| Item | Reviewers | Status after this-round fixes |
|---|---|---|
| §3.5.1 missing in EN | R1, R4 | ✓ fixed (this round) |
| Abstract H2 "is rejected" | R0, R4 | ✓ fixed (this round) |
| Line 1185 "IST 2024" dangling | R0, R2, R4 | ✓ fixed (this round) |
| §3.2.6.1 OS row table cell ✗ vs §3.2.6.3 88.33% prose | R0, R4 | ✓ fixed (this round) |
| LLM source bias numbers (DeepSeek 7/15) | R1, R4 | ✓ fixed (this round) |
| §6.5 deployability (D-6 at 3/10) | R3 (sole dissenter) | ▢ Group D — Round 2 minor revision |

---

## 4. Disagreement Items (1–2 reviewers)

| Item | Reviewer | Editorial arbitration |
|---|---|---|
| §6.5 §6.5.3 auditor pathway numeric thresholds + YAML env-var trap | R3 only | **Mandatory fix (Group D)** — even though only R3 flagged at Round-2 severity, R0 also noted in §3 Disagreement-3 of Round-1 editorial decision; failure to execute the Round-1 arbitration is a procedural defect |
| §5.7.3 stipulated-alternative power simulation | R1 only | **Mandatory P1 fix (Group B1)** — R1's W1 is methodologically substantive |
| §1.3.2 CPH / Andrews / Papadakis citations | R2 only | **Recommended P2 fix (Group C1)** — non-blocking but improves IST literature coverage |
| §1.6.2 toy-scope sentence | R2 only | **Recommended P2 fix (Group C2)** |
| §9.5 Corollary 9.1 attribution swap | R2 only | **Recommended P2 fix (Group C3)** |

---

## 5. Round 3 Expectation

After Group A (already done this round) + Group B + Group C + Group D items:
- **Round 3**: Minor Revision (1 round, ~2 weeks)
- **Round 4**: Accept

If only Group A is closed and Groups B/C/D are partially executed, the editor will return one more Major Revision pass focused on the remaining gaps. The author's Round-1 → Round-2 trajectory shows substantive responsiveness; sustained engagement at the same level should converge to Accept by Round 4.

---

## 6. Provenance and Audit Trail

- **Round-1 review reports** (2026-05-01): `docs/review_2026-05-01/{r0_eic, r1_methodology, r2_domain, r3_perspective, r4_devils_advocate, editorial_decision}.md`
- **Round-1 revision plan**: `docs/superpowers/plans/2026-05-01-p2-reviewer-consensus-revision.md` (executed in commits de422f4..464779b)
- **R2 framework restructure plan**: `docs/superpowers/plans/2026-05-01-p2-r2-methodology-framework.md` (executed in commits 7847dea..9542b0f)
- **NEW-MAJOR-1 12-PUT empirical**: commit `2547b61` (`scripts/run_cosmic_ray_11puts.sh` + `scripts/p2_vs_syntactic_ast_diff_batch.py` + `data/results/cosmic_ray_12put_ast_diff.json`)
- **R-1 English translation**: commit `37fa9bb` (`scripts/translate_paper.py` BLTCY proxy + Opus 4.7 streaming + `论文初稿P2_EN.md`)
- **Round-2 review reports** (this round): `docs/review_2026-05-02/{r0_eic_rereview, r1_methodology_rereview, r2_domain_rereview, r3_perspective_rereview, r4_devils_advocate_rereview, editorial_decision}.md`
- **Round-2 textual fixes** (this round): see Group A items above; commit message will reference R0/R1/R2/R3/R4 W-numbers per fix.

---

*Synthesized 2026-05-02 by editor. Independent re-review reports preserved verbatim under `docs/review_2026-05-02/`.*
