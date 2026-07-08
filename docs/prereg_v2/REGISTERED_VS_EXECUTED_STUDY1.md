# Study-1 Conformance Table — Registered vs Executed

**Purpose**: an exhaustive, honest audit of what Study 1 pre-registered against
what the manuscript actually executed and reported. Doubles as the manuscript's
conformance-table content (integration into `source/main.tex` deferred).

**Registration audited**:
`docs/experiment_documentation/EXPERIMENT_DESIGN.md` @
`0f2509527f346f9433c3cf90959bb07d80601a23` (Zenodo `10.5281/zenodo.20250664`) +
the frozen hypothesis block in `source/main.tex` §Hypotheses (L580–625).
**Executed source**: `source/main.tex` (3056 ll.) + `source/supplementary.tex`
(1513 ll.) + `data/results/*.json`. Reviewer cross-checks:
`docs/review_2026-07-08/{r1_methodology,r3_statistics}.md`.

**Convention**: a *deviation* means the protocol/analysis differed from
registration, **not** a registered test returning a negative verdict. A
hypothesis that was run exactly as registered and came back "not met" is **not**
a deviation — it is a faithful negative and is marked as such.

---

## Headline

**22 registered items audited. 11 executed exactly as registered (incl. 3
registered hypotheses that faithfully returned "not met"). 11 deviations — every
one disclosed in the manuscript or supplementary; none silent, none
selective-reporting.** The deviations are dominated by honest demotions (v3b
withdrawn), version/pool provenance nits flagged by reviewers (Friedman v3 vs v4,
H2 headline pool), and post-hoc *additions clearly labeled as such* (OR=21
incidence, stipulated power, disconfirmation criteria). One reproducibility gap
(industrial arm external-only) has been closed by depositing
`data/results/industrial_percase_v1.json`.

| Category | Count |
|---|---|
| Executed exactly as registered | 11 |
| — of which registered hypotheses returning faithful "not met" | 3 (H1, H2-δ, H4) |
| Deviations, all disclosed | 11 |
| — silent / undisclosed deviations | **0** |
| — selective-reporting / HARKing | **0** |

---

## Full conformance table

| # | Registered item (EXPERIMENT_DESIGN.md / frozen hypotheses) | Executed as | Deviation? | Disclosed where |
|---|---|---|---|---|
| 1 | **RQ set** RQ1 distribution / RQ2 aligned-cross / RQ3 cross-class / RQ4 SMS-vs-PC | Manuscript renumbers: RQ1↦Theorem 9.1, RQ2↦structural audit, RQ3 distribution, RQ4 discrimination+industrial, RQ5 cross-class | **Yes — labeling**: RQ numbers remapped between design doc and paper | `main.tex` §RQ (L540–575); each RQ restated in full |
| 2 | **SMS metric** `killed/(killed+survive)`, E1∧E2 equivalence | Executed verbatim; degeneration to MS via Theorem 9.1 | No | `main.tex` §2 metric; Thm 9.1 |
| 3 | **H1** ≥4/5 operators yield ≥5 non-equiv mutants on ≥9/12 PUTs | Executed on v4; threshold **NOT MET** | No (faithful negative) | `main.tex` L180; `supplementary.tex` L754–758 ("threshold itself ≥5 … not met") |
| 4 | **H2 magnitude** Cliff's δ ≥ 0.474 (Romano large) | Executed; **NOT MET** (δ=0.314 MP5-held headline; 0.439 MP1); read as point-estimate, not confirmatory | No on the verdict (faithful negative); see #5, #6 for pool nits | `main.tex` L207–209 (design), L2049–2064, permissions row L1926 |
| 5 | **H2 headline pool** = MP5-held (δ=0.314) | Table `tab:p2-09` / abstract show aligned 0.275 / cross 0.061 = the **MP1** pool (δ=0.439), next to the 0.314 verdict | **Yes — pool provenance**: displayed means belong to a different pool variant than the reported δ | Reviewer-flagged (r3 M2); paper labels v3/v4 pools but the means↔δ mismatch persists |
| 6 | **H2 power** on the registered pool | Stipulated-alternative + power/exceedance tables computed on the **δ=0.439** unconditioned pool while the verdict uses δ=0.314 | **Yes — object mismatch** (r1 M3) | `main.tex` L2116–2130; disclosed but not reconciled to one SSOT top-line |
| 7 | **H2 odds-ratio** OR ≥ 3.0 | Executed; degenerates to +∞ under zero-inflation; reported "met" but explicitly non-evidential | **Yes — degenerate criterion**, honestly labeled | `main.tex` L208, L1959 ("formally infinite"), permissions row |
| 8 | **H3** within-class sign test 4/4 **and** CV(ΔSMS) < 0.5 | Executed; sign test **4/4 MET**; CV reported | No | `main.tex` L605–606, §5.3 |
| 9 | **H4** mean suspect_share ≤ 0.20 across 60 cells | Executed; **NOT MET** (mean 0.79; only 12/60 cells pass) | No (faithful negative) | `main.tex` L608, L1813–1817 ("H4 is unattainable") |
| 10 | **Primary-MP convention** c-class held at MP5 (pre-registered) | Executed: MP5 held for all H1–H4 verdicts on v3 and v4 | No | `main.tex` L1382–1395 |
| 11 | **v3b ablation variant** (c-class MP5→MP1, data-driven) listed in design §4.2 | **Withdrawn** from verdicts: permutation null (p=0.989) shows δ-inflation indistinguishable from random reselection; demoted, not reported as a verdict | **Yes — honest demotion** (selection-on-response removed; the Study-2 motivation) | `main.tex` L1384–1395; §3.4 |
| 12 | **Cliff's δ 95% CI** BCa bootstrap B=10,000 | Executed; headline CI [0.014, 0.622] (δ=0.314) | No | `main.tex` L2050; `rq2_cliffs_delta_v4_mp5.json` |
| 13 | **Friedman χ²** cross-class + Bonferroni | Reported χ²=15.30, p=0.0041 from the **v3** pool while adjacent class-means are **v4**; per-class Bonferroni×4 | **Yes — stale version** (r3 M3): v3 Friedman beside v4 means; verdict unchanged | `main.tex` L2536/L2940; v4 SSOT `rq3_friedman_v4.json` gives χ²=16.76 |
| 14 | **Mixed-effects primary model** `sms ~ C(class)+C(operator)+(1|put)` | **Singular** (boundary-zero PUT variance); fell back to Friedman as robustness | **Yes — analysis fallback**, disclosed | `main.tex` §5.3; `rq3_mixed_effects_v4.json` |
| 15 | **Spearman ρ / Kendall τ** (SMS vs Pattern Coverage) | Executed; ρ=0.16 p=0.61, descriptive/hypothesis-generating only; n=12 under-powered | No (registered as descriptive) | `main.tex` §5.4, permissions row ("none; hypothesis-generating") |
| 16 | **Equivalence** E1∧E2, K_eq=1000, ε=1e-9 | Executed verbatim | No | `main.tex` §equiv; design §4.3 |
| 17 | **Three-source cross campaign** (Claude+GPT+DeepSeek, identical prompt) | Executed; 333 attempts, 298 confirmed, 292 into pool | No | `main.tex` L1670–1677 |
| 18 | **Review protocol** (implicit: consistent pipeline across arms) | v3 used dual-blind reviewer; **v4 used V1–V4 mechanical gates only** (no reviewer LLM) | **Yes — protocol asymmetry**, declared confound (the Study-2 fix) | `main.tex` L1678–1690 ("Declared confound: protocol asymmetry") |
| 19 | **Industrial arm** 4-group Wilcoxon, Holm family {T1>B1,T1>A1,B1>B2}, census fixed by verification | Executed; T1>B1 Holm p=0.046; census **grew 30→34** (effect narrowed) | **Yes — census growth**, disclosed as fragility | `main.tex` L2542, L2447–2451 (30→34 narrowing + sensitivity rerun) |
| 20 | **Industrial reproducibility** (SSOT for the arm) | Originally external Zenodo only (not repo-recomputable, r3 M1 / r1 M1); per-case matrix **now deposited** in-repo | **Yes — provenance gap, now closed** | `data/results/industrial_percase_v1.json` (34 cases, V=279.5, p=0.0148 recomputable) |
| 21 | **Nonzero-SMS incidence** (OR=21, Fisher) | **Not in registration**; added post-hoc, demoted to "no licensed verdict / zero evidential weight" | **Yes — post-hoc addition**, labeled (Study-2 pre-registers it, H2-4) | `main.tex` L1961–1965; r3 focus 2 |
| 22 | **Disconfirmation criteria** ("what would count against the construct") | Added and explicitly **stated post hoc**, after the verdicts | **Yes — post-hoc addition**, labeled (Study-2 registers a priori, §8) | `main.tex` L611–623 ("We state these criteria post hoc … and label them accordingly") |

---

## Notes on the two remaining reviewer-flagged nits (items 5, 6, 13)

These are internal version/pool provenance inconsistencies, not integrity issues:
each individual number is correct on its own pool; the defect is that two adjacent
statistics in the same subsection are computed on different pool variants (MP1 vs
MP5; v3 vs v4). They are disclosed and reviewer-noted; Study 2 removes the ambiguity
by fixing a single deterministic primary-MP rule (§4 of the Study-2 registration)
and a single SSOT per statistic. They do not change any verdict.

## Integrity summary

- **Zero silent deviations.** Every departure from the registration is stated in
  the manuscript or supplementary, with a location above.
- **Zero selective reporting / HARKing.** All four failed hypotheses (H1, H2-δ,
  H3-CV partial, H4) are reported; the one under-reported *favourable* result
  (OR=21 incidence) was demoted, not promoted — the opposite of cherry-picking.
- **The deviations cluster into exactly the five lessons Study 2 is designed to
  close** (see `PREREGISTRATION_STUDY2.md` §9): unpowered thresholds (4,5,6),
  primary-MP post-hoc temptation (11), census timing/reproducibility (19,20),
  protocol asymmetry (18), incidence-estimand post-hoc (21), disconfirmation
  post-hoc (22).
