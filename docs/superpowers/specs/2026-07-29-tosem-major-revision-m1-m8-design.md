# TOSEM Major Revision M1–M8 Design

**Date:** 2026-07-29  
**Target branch:** `cursor/theory-enhancement-t0-6320`  
**Primary manuscript:** `source/main.tex`  
**Supplement:** `source/supplementary.tex`

## 1. Objective and Scope

This revision closes the eight major issues in
`docs/review_20260729/tosem_reviewer_evaluation.md` without collecting
new experimental observations. It treats frozen v3/v4 campaign records
as immutable inputs, permits deterministic recomputation and
cluster-level resampling, and revises the manuscript so that every
quantitative claim is traceable to the declared single source of truth.

The writing policy is evidence-forward rather than defensive:

- retain the falsifiable aligned-greater-than-cross prediction;
- strengthen its interval evidence with PUT-level cluster resampling;
- preserve positive contributions when supported by the frozen data;
- qualify only the estimand, identification boundary, or theorem premise
  that actually requires qualification;
- avoid presenting elementary formal guarantees as deep mathematical
  novelty, while explaining their value as auditable measurement
  scaffolding.

Operator-stratified reruns and expansion to at least 30 PUTs are outside
this revision. They remain future strengthening options, not acceptance
preconditions.

## 2. Authority and Data Flow

The revised numerical authority chain is:

```text
frozen campaign records
  ├─ data/results/sms_track2_v3.json
  ├─ data/results/sms_track2_v4.json
  ├─ data/results/lrca_60cell_v3.json
  ├─ data/results/lrca_60cell_v4.json
  └─ frozen RQ3/RQ4 inputs
          │
          ▼
deterministic analysis scripts
  ├─ MP5-primary aligned/cross statistics and power
  ├─ stipulated-alternative calibration
  ├─ PUT-level cluster bootstrap
  ├─ evaluable-cell LRCA summaries
  └─ gap-premise support count
          │
          ▼
versioned result JSONs
          │
          ▼
data/results/paper_numbers_v4.json
          │
          ├─ source/main.tex
          └─ source/supplementary.tex
```

`paper_numbers_v4.json` becomes the manuscript-level aggregate SSOT.
Specialised result files remain authoritative for their full simulation
or per-cell payloads, but their headline values must be copied into or
referenced by `paper_numbers_v4.json`. `audit_fix_numbers.json` remains
an audit record and is no longer a competing manuscript authority.

Every generated JSON records the frozen primary map, source input files,
seed, resampling count, method, and interpretation boundary needed to
reproduce its headline values.

## 3. Numerical Repairs

### 3.1 M1: MP5-primary power and stipulated alternative

The power scripts must import the frozen pre-registered
`PRIMARY_CELLS_V3` map directly, rather than resolving a mutable
environment-selected map. Both the plug-in exceedance calculation and
the stipulated-alternative mixture calibration use the same MP5
c-class primary convention as the manuscript's headline
`delta = 0.314`.

The regenerated outputs are:

- `data/results/rq2_power_v4.json`;
- `data/results/rq2_power_stipulated_v4.json`.

The observed-distribution table in the manuscript is regenerated from
the MP5 slice. The stipulated JSON records the newly calibrated mixture
weight and simulation results. The text distinguishes:

- threshold exceedance under the observed empirical distribution;
- the probability that a sample-level point estimate clears the H2
  decision boundary under a stipulated truth at that boundary;
- interval precision, which is not interchangeable with either number.

### 3.2 M2: NA-consistent LRCA summaries

`C1_share` and `suspect_share` are undefined for zero-kill cells.
Macro-means therefore use evaluable cells only:

- v3: 12 evaluable cells;
- v4: 15 evaluable cells.

The revised aggregate reports the evaluable-cell macro-mean C1 share,
suspect share, pooled kill-weighted readings, and counts of evaluable
and NA cells. The cross-source narrative reports the expansion from 12
to 15 evaluable cells and the modest macro-mean C1 increase, rather
than the invalid 60-cell means or a 27% improvement claim.

### 3.3 M3: SSOT regeneration

`scripts/build_paper_numbers.py` is revised so its v4 output consumes
the frozen MP5-primary contrast, NA-consistent LRCA summaries, corrected
Friedman result, power outputs, cluster bootstrap, and premise-support
count. It must not silently fall back to the withdrawn MP1 post-hoc
configuration.

The regenerated `paper_numbers_v4.json` removes or replaces the five
known conflicts:

- aligned mean from the withdrawn primary configuration;
- Cliff's delta from the withdrawn primary configuration;
- all-60 suspect mean under the invalid zero-kill encoding;
- H4 pass count under that encoding;
- stale Friedman statistic.

Directly coupled stale interpretation fields in
`h5_sensitivity_v4.json` and `rq3_friedman_v4.json` are regenerated or
rewritten to match the manuscript's not-evaluable and exploratory
readings.

## 4. M4: PUT-Level Cluster Bootstrap

The resampling unit is the PUT. Each bootstrap draw samples 12 PUT
identifiers with replacement. For every sampled PUT, its one aligned
cell and four cross cells are carried together, preserving the
within-PUT dependence structure and the 1:4 aligned/cross ratio.
Cliff's delta is recomputed on each draw.

The implementation uses seed 42 and 100,000 cluster-bootstrap draws. It writes
`data/results/rq2_cluster_bootstrap_v4.json`, including:

- point estimate;
- 95% percentile cluster-bootstrap interval;
- fraction of bootstrap deltas at or below zero;
- resampling unit and primary-map metadata;
- a vacant-cell sensitivity computed under the same PUT-cluster
  principle.

The manuscript retains the directional result that aligned SMS exceeds
cross SMS in this design. It describes the cluster interval as
dependence-aware evidence for this frozen 12-PUT sample, not as a broad
population guarantee. The vacant-cell sensitivity remains visible and
is not used to erase the primary prediction.

## 5. M5: Gap-Premise Support and Mechanism Interpretation

The audit script counts, per cell, whether the checker stratum has any
positive-weight generation-time fiber in the admitted mutant pool:

```text
Cov(R) ∩ {j : w_j > 0} = ∅
```

The result JSON records:

- total cells for which this observable antecedent holds;
- aligned and cross breakdowns;
- zero and nonzero SMS breakdowns within that subset;
- the cells involved, for auditability.

The manuscript restricts the corollary's zero-prediction reading to
this observable antecedent subset and separately states that S5 purity
and exact-checker assumptions are not established by the provenance
labels. Nonzero kills in the subset are treated as empirical evidence
of those wider premise violations, consistent with the reported
exactness defect.

The decoupling discussion retains alignment as a plausible mechanism
but presents two observationally non-identifiable explanations:

1. the evaluated MR family observes different effect fibers; and
2. MR families differ in detection strength or tolerance margins.

No per-operator causal interpretation is made from the mixed pool.

## 6. M6: Formal Positioning and Lemma Alignment

RQ1, the introduction, and the contribution summary describe the
theoretical layer as **formal measurement scaffolding and guarantees**.
The contribution is the explicit, auditable connection among the
effect-map vocabulary, degeneration, interval accounting, detection
window, and gap diagnostics. The manuscript does not claim that the
proof techniques themselves are mathematically deep.

Lemma G.1 keeps the separation between the equivalence-limit axes and
the killed-limit axis. Its proof is repaired by observing that, under
the fixed reference-anchored identity switch, limiting E2 already
forces exact same-input agreement; E1 is then satisfied by equality.
The proof no longer invokes `epsilon_AVP -> 0`, which belongs to L3.

The kill-witness statement is split into:

- an unconditional classification fact: the killed predicate includes
  an E1 verdict difference, so a killed mutant is routed to
  `CONFIRMED_NON_EQUIVALENT` under the declared three-state protocol;
- a conditional quantitative upgrade: under R2 stability, a kill
  yields an observed-output divergence exceeding
  `epsilon_eq`.

Supporting proof detail moves to supplementary Appendix G.

## 7. M7: Neutral LRCA Calibration and Future Estimand

The Study Design section reports the LRCA threshold grid as calibration
of the diagnostic labels only. It does not announce an H4 result,
compare against a nonexistent 80% threshold, or call H4 unattainable.

The Results section retains the not-evaluable verdict because the
pre-registered 60-cell macro-mean is undefined on 45 zero-kill cells.
It commits the next evaluation to a pre-registered estimand:

- primary: pooled suspect kills divided by all LRCA-evaluated kills;
- secondary: evaluable-cell macro-mean;
- zero-kill cells: NA, never imputed as zero or one;
- decision timing: fixed before examining the next campaign's H4
  result.

## 8. M8: Structural Surgery

### 8.1 Main-text architecture

The current theory nested under the problem-formulation section becomes
an independent section titled:

> Formal Measurement Scaffolding and Guarantees

The main text keeps:

- the compact vocabulary and SMS definition;
- the effect-map/fiber model;
- concise statements and interpretations of the degeneration,
  duality, detection-window, interval, and gap guarantees;
- the empirical hooks that make the premises auditable.

Appendix G receives lemma-level derivations, detailed proof cases,
exception-set discussion, endpoint motions, identifiability arguments,
and the repaired witness proof.

### 8.2 De-duplication

The revision removes repeated versions of:

- the E1-and-E2 conservatism explanation;
- the killed predicate formula;
- v3/v4 protocol asymmetry;
- power caveats and effective-sample-size discussion;
- stakeholder deployment qualifications already stated in the
  appendix.

One authoritative explanation remains in the earliest necessary
location; later sections refer back to it.

### 8.3 Float hygiene

Every table and figure receives:

- a stable label;
- an explicit in-text `Table~\ref{...}` or `Figure~\ref{...}` callout;
- a caption that remains meaningful after floating.

Every figure receives an ACM `\Description{...}`. Ambiguous phrases
such as “the table below” or “this table” are replaced by explicit
cross-references.

### 8.4 Length target

The main manuscript target is 16,000–18,000 prose words under a single,
documented counting method. The reduction comes from moving proof detail
and deleting repetition, not from deleting the research questions,
negative results, cluster-bootstrap evidence, industrial arm, or
limitations needed to interpret the construct.

## 9. Directly Coupled Minor Repairs

The revision also fixes minor residues that are inseparable from M1–M8:

- conclusion language for the 34-defect face becomes explicitly
  selection-conditioned;
- operator-MP causal wording becomes aligned-versus-cross wording;
- forward pointers are added before notation or exact-checker concepts
  first used;
- the stochastic-window necessity remark is narrowed to the
  boundary-attaining noise model;
- the undecidability proof sketch adds the restricted-template padding
  qualification;
- deployment use of the aligned mean is presented as an observed range
  or descriptive reference, not an engineering threshold;
- highlights are reduced to the venue-compatible range if they remain
  in the submission source.

Bibliographic metadata repair that requires a new external identifier
is not invented; unverifiable metadata is either replaced by an
available archived access path already present in the repository or
reported as an unresolved bibliography issue.

## 10. Verification and Acceptance Criteria

The revision is accepted only if all of the following hold:

1. Running the numerical scripts from the frozen inputs deterministically
   regenerates their committed JSON outputs.
2. `paper_numbers_v4.json` contains the MP5-primary headline values and
   no withdrawn MP1 or invalid zero-kill aggregate as a primary field.
3. Every quantitative statement touched by M1–M7 matches a committed
   JSON field.
4. The PUT-level cluster bootstrap records its seed, draw count, primary
   map, resampling unit, point estimate, interval, and sensitivity.
5. The premise-support count is reproducible from per-mutant provenance
   labels and lists its audited cells.
6. Lemma G.1 no longer relies on L3, and the kill-witness statement
   separates unconditional classification from the R2-conditional
   quantitative witness.
7. The manuscript contains no remaining 27% C1 improvement claim,
   invalid 0.164-to-0.209 evaluable-cell comparison, obsolete 80% H4
   threshold, or primary use of delta 0.439.
8. All main-text floats are explicitly referenced, and all figures have
   `\Description`.
9. The main manuscript compiles without undefined references or fatal
   LaTeX errors.
10. The documented word-count method reports 16,000–18,000 main-text
    prose words, or the final report identifies the exact residual
    excess and why further deletion would remove required evidence.
11. Existing automated tests pass, and new analysis logic has focused
    regression tests for primary-map locking, NA aggregation, cluster
    resampling shape, and premise-count classification.
