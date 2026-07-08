# TOSEM Experiment Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the acceptance-blocking evidence gaps by separating publishable final results from exploratory process traces, adding new experiments where evidence is missing or statistically weak, and revising the manuscript so negative findings are presented as scientific boundary conditions rather than hidden process failures.

**Architecture:** The repair has three layers: an internal evidence layer that records every run, a decision layer that decides which claims survive into the paper, and a manuscript layer that reports only final, auditable results with appropriate scope. Each task ends with a reviewer checkpoint that verifies whether the original acceptance issue is closed and whether the paper's research question has drifted.

**Tech Stack:** LaTeX manuscript, existing `data/results/*.json` outputs, project reproduction scripts, TOSEM submission package under `submission/TOSEM_regular_20260707`, canonical sources under `source`, and review artifacts under `docs/review_2026-07-08`.

---

## File Map

- Modify: `docs/superpowers/plans/2026-07-08-tosem-accept-loop.md` if the global LOOP acceptance gate needs to reference this repair plan.
- Create: `docs/review_2026-07-08/experiment_repair_matrix.md` to track each acceptance issue, the new experiment or non-experimental remedy, and the final claim status.
- Create: `docs/review_2026-07-08/claim_disclosure_policy.md` to define what belongs in the manuscript versus the internal research ledger.
- Modify: `REPRODUCIBILITY.md` to align expected outputs with final estimands and scripts.
- Modify: `source/main.tex` and `submission/TOSEM_regular_20260707/main.tex` to report final results and foreground publication-relevant negative findings.
- Modify: `source/supplementary.tex` and `submission/TOSEM_regular_20260707/supplementary.tex` to keep detailed final evidence, robustness checks, and appendices synchronized.
- Modify: `source/references.bib` and `submission/TOSEM_regular_20260707/references.bib` if new benchmark, artifact, or dataset citations are added.
- Modify or create: `data/results/*` only through documented experiment scripts, never by hand.

---

### Task 1: Build The Acceptance-Issue Repair Matrix

**Files:**
- Create: `docs/review_2026-07-08/experiment_repair_matrix.md`

- [ ] **Step 1: List each current acceptance issue as a testable repair item**

Record at least these issues:

```markdown
| ID | Issue | Current Evidence | Repair Type | Publishable If | Manuscript Action |
|---|---|---|---|---|---|
| P0-H2-SSOT | H2 mixes MP5 frozen primary with MP1 sensitivity | `rq2_cliffs_delta_v4_mp5.json`, `paper_numbers_v4.json` | Re-analysis, no new experiment first | One primary estimand is declared and all files agree | Report MP5 as primary, MP1 as sensitivity |
| P0-RQ3-DRIFT | RQ3 numbers differ across main, supplement, and reproduction guide | `rq3_friedman_v4.json`, `paper_numbers_v4.json` | Reconciliation | One value set appears everywhere | Synchronize main/supplement/repro guide |
| P1-INDUSTRIAL | Industrial arm is not auditable enough for validation claims | Missing or incomplete case-level ledger | New evidence package or claim downgrade | Case-level artifacts exist and support wording | Either add appendix ledger or downgrade to sanity check |
| P1-S5-PURITY | S5 assumes intended-stratum purity without direct verification | Current evidence is labeling assumption | New validation experiment | Independent audit supports purity rate | Report verified purity or keep as assumption |
| P1-LOW-POWER | H2 effect is directionally positive but not decisive under primary estimand | `delta=0.314`, CI crosses weak threshold | New experiment or stronger analysis | Additional evidence narrows uncertainty or conclusion is qualified | Avoid claiming stable superiority unless supported |
| P1-ZERO-MASS | 45/60 cells have zero SMS and several PUTs have no signal | `paper_numbers_v4.json` | Reframing plus optional stratified analysis | Zero-mass is explained as boundary condition | Foreground as limitation/result, not hidden defect |
| P1-SOURCE-DIVERSITY | Source-diversity claim rests on asymmetric protocol | Existing protocol | New symmetric experiment or downgrade | Symmetric protocol supports mechanism claim | Otherwise remove mechanism claim |
```

- [ ] **Step 2: Assign each item one of three remedies**

Use exactly one remedy per issue:

```markdown
- New experiment: evidence is missing and the claim is important enough to keep.
- Re-analysis: raw evidence exists but the current estimate, contrast, or reporting is inconsistent.
- Claim downgrade/removal: the claim is not essential or would require too much new evidence for this submission.
```

- [ ] **Step 3: Reviewer checkpoint**

Check that every P0/P1 issue from the reviewer panel maps to a remedy. If an issue has no remedy, the plan is incomplete.

---

### Task 2: Define A Manuscript Disclosure Policy

**Files:**
- Create: `docs/review_2026-07-08/claim_disclosure_policy.md`

- [ ] **Step 1: Separate internal research records from publication claims**

Use this policy:

```markdown
# Claim Disclosure Policy

The manuscript reports final, pre-submission research results, not a chronological log of exploratory attempts.

Internal ledgers must retain failed, exploratory, and inconclusive runs for audit discipline.

The submitted manuscript must disclose:
- final negative findings that affect the interpretation of the method;
- failed hypotheses when they are part of the stated RQs or final study design;
- limitations that bound the contribution or prevent a strong claim;
- robustness checks that materially change the conclusion.

The submitted manuscript does not need to disclose:
- abandoned pilot configurations;
- intermediate failed runs that were not part of the final study design;
- engineering mistakes corrected before the final protocol;
- exploratory alternatives that do not affect the final claim.

No positive claim may be retained merely because negative process evidence is omitted.
```

- [ ] **Step 2: Apply the policy to current negative findings**

Classify current negatives:

```markdown
| Finding | Publish? | Reason |
|---|---|---|
| H1/H4 fail under final study design | Yes | Directly affects contribution scope |
| H2 is weaker under frozen MP5 than MP1 sensitivity | Yes | Prevents cherry-picking accusation |
| 45/60 cells are zero SMS | Yes | Defines metric boundary and power interpretation |
| Earlier exploratory configurations not used in final estimand | No, unless they explain a robustness result | Process trace, not final research result |
| Failed script invocations caused by local build/aux state | No | Engineering process, not scientific result |
```

- [ ] **Step 3: Reviewer checkpoint**

Ask whether the policy hides a result that changes the final scientific claim. If yes, revise the manuscript; if no, keep it internal.

---

### Task 3: Plan New Experiments For Missing Or Weak Evidence

**Files:**
- Update: `docs/review_2026-07-08/experiment_repair_matrix.md`
- Update: `REPRODUCIBILITY.md`
- Create new result files only through documented scripts under `data/results/`

- [ ] **Step 1: Industrial audit experiment**

Design:

```markdown
Question: Do real-defect cases provide auditable external support for SMS behavior?
Unit: each admitted real-defect case.
Inputs: frozen case list, source commit, mutant ID, MR/test oracle, admission/exclusion rule.
Outputs: `data/results/industrial_case_ledger.json`, `data/results/industrial_summary.json`.
Minimum fields: case_id, source_project, defect_reference, mutant_id, operator, intended_stratum, test_result, real_defect_face_result, admitted, exclusion_reason, artifact_hash.
Stopping rule: all cases in the frozen list are audited once; excluded cases remain in the ledger but are not used for positive claims.
Publishable claim: only "selection-conditioned sanity check" unless the ledger supports a stronger external-validity statement.
```

- [ ] **Step 2: S5 purity validation experiment**

Design:

```markdown
Question: Are S5-labeled mutants actually confined to the intended semantic stratum?
Unit: sampled S5 mutants.
Sampling: stratified random sample across MPs and PUT classes; oversample nonzero SMS cells.
Assessment: two independent annotators or deterministic invariant checks if available.
Outputs: `data/results/s5_purity_audit.json`, `data/results/s5_purity_summary.json`.
Primary metric: verified_pure_rate with confidence interval.
Publishable claim: if purity is high, report verified purity; if not, treat S5 as intended-stratum label only.
```

- [ ] **Step 3: H2 precision extension experiment**

Design:

```markdown
Question: Is the aligned-vs-cross advantage robust under the frozen MP5 primary estimand?
Unit: PUT × MP cell.
Intervention: add more independent PUTs or additional frozen mutants per existing PUT, preserving the same primary estimand.
Primary output: updated aligned/cross means, medians, Cliff's delta, bootstrap CI.
Secondary output: paired or hierarchical model that accounts for PUT-level zero inflation.
Stopping rule: predefine sample expansion before looking at results; stop when the planned expansion is complete, not when significance appears.
Publishable claim: report effect size and uncertainty; claim "robust advantage" only if the CI and sensitivity analyses support it.
```

- [ ] **Step 4: Source-diversity symmetric protocol experiment**

Design:

```markdown
Question: Does source diversity improve mutant quality beyond condition separation?
Unit: generated mutant set under matched prompts, budgets, and filtering rules.
Conditions: symmetric GPT-source and non-GPT-source configurations with identical admission filters.
Outputs: `data/results/source_diversity_symmetric.json`.
Publishable claim: keep a mechanism claim only if the symmetric protocol supports it; otherwise report source diversity as exploratory future work.
```

- [ ] **Step 5: Reviewer checkpoint**

For each proposed experiment, decide whether it is essential for this submission:

```markdown
- Essential: needed to keep a major claim.
- Optional: improves confidence but can be deferred if claim is downgraded.
- Drop: too expensive or not central; remove the corresponding claim.
```

---

### Task 4: Reframe Non-Significant Results Without Over-Disclosure

**Files:**
- Modify: `source/main.tex`
- Modify: `submission/TOSEM_regular_20260707/main.tex`
- Modify: `source/supplementary.tex`
- Modify: `submission/TOSEM_regular_20260707/supplementary.tex`

- [ ] **Step 1: Foreground final-study negative results**

Use publication-level wording:

```latex
The study does not support a uniformly positive SMS signal across all programs and metamorphic properties. Instead, SMS is sparse: 45 of 60 PUT--MP cells have zero SMS, and the prespecified H1 and H4 criteria are not met. We therefore interpret SMS as a boundary-sensitive diagnostic rather than as a general-purpose adequacy score.
```

- [ ] **Step 2: Avoid reporting process-only failures**

Do not add narrative like:

```latex
We tried several earlier configurations and many failed to produce significant results.
```

Use final-study framing instead:

```latex
Sensitivity analyses show that the aligned-vs-cross contrast is directionally stable but estimator-dependent; the frozen-primary MP5 contrast is weaker than the MP1 sensitivity estimate.
```

- [ ] **Step 3: Match conclusion strength to evidence**

Allowed if no new H2 experiment succeeds:

```latex
These results provide qualified evidence that alignment can increase SMS under the frozen-primary design, while also showing that the effect is sparse and sensitive to the primary-MP choice.
```

Forbidden unless new evidence supports it:

```latex
These results validate SMS as a robust industrial semantic adequacy metric.
```

- [ ] **Step 4: Reviewer checkpoint**

Verify that every negative result included is part of the final study design or changes interpretation. Verify that omitted process negatives do not contradict any retained positive claim.

---

### Task 5: Synchronize Source, Submission, And Reproducibility Artifacts

**Files:**
- Modify: `source/main.tex`
- Modify: `source/supplementary.tex`
- Modify: `source/references.bib`
- Modify: `submission/TOSEM_regular_20260707/main.tex`
- Modify: `submission/TOSEM_regular_20260707/supplementary.tex`
- Modify: `submission/TOSEM_regular_20260707/references.bib`
- Modify: `REPRODUCIBILITY.md`
- Modify: `venues/tosem/build.py`

- [ ] **Step 1: Make source files the canonical manuscript**

Copy no claims by hand without checking the corresponding result file. The submission package must be rebuildable from `source/` without reintroducing old wording.

- [ ] **Step 2: Align numeric claims**

Use these known current values unless superseded by new experiments:

```markdown
H2 frozen primary: mean_aligned=0.213325, mean_cross=0.0766729, Cliff's delta=0.314236.
H2 MP1 sensitivity: mean_aligned=0.275, mean_cross=0.0612, Cliff's delta=0.4392.
RQ3 Friedman: chi2=16.7586, p=0.002153.
RQ4 Pattern Coverage mean: 0.750.
Zero SMS cells: 45/60.
```

- [ ] **Step 3: Reviewer checkpoint**

Search the source and submission package for obsolete values and overclaims. No obsolete value may remain unless explicitly labeled as a sensitivity or historical comparison.

---

### Task 6: Final LOOP Review Gate

**Files:**
- Create or update: `docs/review_2026-07-08/final_loop_review.md`

- [ ] **Step 1: Run evidence checks**

Required checks:

```markdown
- All manuscript numbers trace to result files.
- All final positive claims are supported, observed, or qualified.
- All blocked claims are removed from abstract, contributions, results, and conclusion.
- Missing experiments are either completed or their corresponding claims are downgraded.
```

- [ ] **Step 2: Run build checks**

Required outcome:

```markdown
- Main PDF builds cleanly.
- Supplementary PDF builds cleanly.
- No undefined citations or references.
- No source/submission drift for final claims.
```

- [ ] **Step 3: Run academic reviewer re-review**

Acceptance gate:

```markdown
- EIC: Minor Revision or better.
- Methodology reviewer: Minor Revision or better.
- Domain reviewer: Minor Revision or better.
- Perspective reviewer: Minor Revision or better.
- Devil's Advocate: zero CRITICAL issues.
```

- [ ] **Step 4: Decide next loop**

If any reviewer remains at Major Revision, add a new row to `experiment_repair_matrix.md` and repeat only the affected task. If all gates pass, freeze the submission package.

---

## Self-Review

- Spec coverage: The plan covers missing experiments, non-significant evidence, stronger alternative methods, negative-result foregrounding, and the distinction between internal process evidence and publishable final results.
- Placeholder scan: No task relies on "TBD" or unspecified remedies; each acceptance issue is mapped to a concrete experiment, re-analysis, or claim downgrade.
- Topic-drift check: The paper remains about semantic mutation testing and SMS validity boundaries; the repair does not turn it into a generic negative-results paper or a process diary.
