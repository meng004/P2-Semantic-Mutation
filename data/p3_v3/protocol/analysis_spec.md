# P3 v3 Phase 0 authority: Metrics and prespecified analysis

> Authority ID: p3-v3-phase0-analysis-spec-v1
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830
> Source sections (verbatim, 1-based inclusive plan lines): Section 10 Metrics (L809-L850); Section 11 Prespecified analysis (L851-L997)
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

## 10. Metrics

For MR set `R`, confirmed semantic-mutant set `M`, frozen semantic-contract
family set `F_target = {INV, MONO, CONV, DYN, CMP}`, represented family set
`F_cert`, and kill indicator `K_R(m)`:

```text
SMS_instance(R) = sum_m K_R(m) / |M|

SMS_family(R) = (1 / |F_cert|) * sum_f [sum_{m in M_f} K_R(m) / |M_f|]

CDC = |F_cert| / |F_target|
```

`SMS_family` is never interpreted without construct-domain coverage `CDC` and
the exact `F_cert` set. A target family with no confirmed item is
`UNMEASURED`, not covered and not missed. Cross-cohort score comparisons use the
intersection of represented frozen families and report the excluded family set.
The patch-mechanism IDs `CE/OS/HP/TF/SI` never appear in this formula.

Required controlled-mutant outputs:

- family-balanced `SMS_family` as the primary score;
- construct-domain coverage `CDC` and every `UNMEASURED` target family;
- instance-weighted `SMS_instance`;
- conservative lower and upper bounds including equivalence-unresolved items;
- family residual `1 - SMS_f(R)`;
- each MR's marginal and unique contribution;
- pairwise kill-vector overlap and redundancy;
- wall-clock and CPU cost per additional semantic kill;
- complete construction, certification, and execution funnels.

Required real-fault outputs:

- the primary intention-to-evaluate lower-bound P12 detection rate within the
  declared MR-detectable benchmark, plus the prespecified upper-bound and
  complete-case sensitivities;
- detection by `DIRECT` semantic-contract family, size, technique, and repository;
- missed real faults associated with semantic-contract-family residuals;
- all P12 exclusions, mapping uncertainties, `SCIENTIFIC_INCONCLUSIVE`, and
  `INFRASTRUCTURE_UNRESOLVED` executions.

## 11. Prespecified analysis

### 11.1 RQ1

Report counts and project-clustered bootstrap 95% confidence intervals for
certification yield. Report all seven terminal states by semantic-contract
family, construction mechanism, scale, and technique. Do not test a post hoc
universal success threshold.

Broad cross-stratum constructibility wording requires:

- complete category accounting and profiling-result funnels for every selected
  subject;
- at least 75 confirmed non-equivalent semantic mutants;
- at least eight confirmed mutants in each primary semantic-contract family;
- at least 15 confirmed mutants in each represented size stratum;
- at least eight confirmed mutants in each claimed technique stratum;
- no subject contributing more than 12.5% of the semantic denominator;
- at least 15 subjects from at least eight repositories;
- each claimed semantic-contract family, size stratum, or technique stratum to
  contain at least three subjects from at least two repositories.

If a condition fails, retain the results and restrict the claim to represented
subjects and families. These are minimum diversity gates, not power-derived
proof of population-wide constructibility or prevalence.

Technique-specific wording additionally requires at least one successful
Profiling Workload row supporting the primary technique for every contributing
subject. Subjects with `TECH_UNCERTAIN` or only static technique evidence remain
in overall constructibility results but not in technique-specific claims.

### 11.2 RQ2

Report normalized-patch and mutant-tree exact overlap with exact binomial
intervals, plus contract-category coverage. Compare semantic and syntactic
execution funnels using paired subject-level differences and project-clustered
bootstrap intervals. Do not infer testing value from AST or patch distance.

### 11.3 RQ3

For every MR-set portfolio, report all metrics in Section 10. The exhaustive or
descriptive lattice receives descriptive summaries only. Confirmatory contrasts
use the frozen fixed-budget sample, normalize weights to one per subject ×
budget cell, and resample or permute entire projects. Compare portfolios at the
same MR count and measured execution budget. Control family-level secondary
comparisons using Benjamini–Hochberg at `q = 0.05`.

Primary RQ3 scores use only `E_COMMON`. Contract-conditioned `E_CONTRACT`
results are reported as a separate sensitivity and cannot be pooled into,
substituted for, or used to select the primary semantic or syntactic score.

The paper must report surviving semantic-contract families and concrete
residuals even when aggregate scores are high.

### 11.4 RQ4

Primary RQ4 analysis uses the pre-outcome frozen `P12_PAIRED` membership,
including every mapping state, and only its pre-frozen `E_COMMON` job inventory.
It is performed on project × fixed-budget aggregates. The report first gives pairing
coverage by project, fault, and exact fixed version, including every failed or
missing controlled profile. After Phase 7 mapping but before real-fault MR
outcomes are executed or opened, compare `P12_PAIRED` with `P12_FULL` on
project, scale, implementation-technique,
semantic-fault-family, Public Behavior Frame category coverage, Profiling
Workload selected fraction, profile status, and build availability covariates.
Publish the complete behavior-discovery, profiling, and controlled-profile
funnels and every exclusion/failure reason. Within
a project × budget cell,
portfolio-level semantic score, syntactic score, and real-fault detection are
averaged using the frozen equal cell weights. Overlapping portfolios do not
become independent observations.

Each planned real-fault row terminates as `MR_VIOLATION`, `MR_SATISFIED`,
`DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION`, `SCIENTIFIC_INCONCLUSIVE`, or
`INFRASTRUCTURE_UNRESOLVED`. The primary intention-to-evaluate lower bound keeps
every planned row: only the two violation states contribute one. The upper-bound
sensitivity additionally counts the two unresolved states as one, while
`MR_SATISFIED` remains zero. Complete-case analysis is secondary. Outcome or
execution success cannot change `P12_PAIRED` membership, job membership, or
weights, and both unresolved classes are reported separately.

The response for a project × budget cell is the equal-fault, equal-portfolio
detection fraction, and model loss is Bernoulli cross-entropy evaluated on that
fraction. Each held-out project's loss is first averaged across its available
fixed budgets; `Delta_sem` is then the equal-project mean difference. Fault,
portfolio, or budget multiplicity therefore cannot increase a project's weight.

Before outcome opening, use P12 project and fault counts plus a grid of plausible
intraclass correlations and detection rates to simulate the minimum detectable
change in leave-one-project-out log loss. Predictive modelling is eligible only
under a prospectively compatible successor P12 contract and when all existing
P12 v1.1.2 confirmatory floors are met: at least 17 analyzable projects, at least
60 real-fault families, at least two families per project, and no project
contributing more than 20% of the faults. A successor P12 contract may raise but
not lower these floors without a separately reviewed amendment.

If eligible, compare two deliberately small regularized models:

- `MSYN`: budget, execution cost, and `MS_syntax_strict`;
- `MBOTH`: the same predictors plus `SMS_family` and `CDC`.

Hyperparameters are fixed by an inner leave-one-project-out loop. The outer
leave-one-project-out predictions are the only inputs to the primary log-loss
comparison. The primary incremental statistic is:

```text
Delta_sem = logloss(MSYN) - logloss(MBOTH)
```

A positive value favors incremental semantic information. A central claim of
incremental value requires the project-clustered bootstrap 95% interval for
`Delta_sem` to lie entirely above zero, no complete or quasi-complete separation,
and the simulation-based sensitivity report to show that effects of the
observed magnitude were identifiable under the achieved cluster structure.
Otherwise the result is reported as observed, qualified, insufficient, or
blocked according to the claim ledger.

Secondary analyses are:

- Kendall association between project-budget semantic adequacy and real-fault
  detection, using project-clustered intervals;
- odds ratio for a real fault remaining undetected when its `DIRECT`
  semantic-contract family is a residual family of `R`, restricted to
  `P12_DIRECT` and explicitly
  labelled mechanism-concordance evidence;
- `ADJACENT` mapping sensitivity;
- budget-matched syntactic sampling sensitivity;
- leave-one-technique and leave-one-size-stratum sensitivity;
- leave-one-Profiling-Workload-category sensitivity when at least two categories
  were successfully profiled;
- static-only implementation classification with unresolved cases mapped to
  `TECH_UNCERTAIN`;
- `P12_FULL` case-series results without paired or mapping-based inference;
- lower/upper model sensitivity using syntactic and semantic equivalence bounds.
- lower/upper P12 missingness sensitivity and complete-case P12 results.

Without the compatible successor contract, below the 17-project/60-family floor,
or when event distribution makes the regularized model unidentified, RQ4 is a
bounded project-level case series. No predictive-validity or incremental-value
claim is allowed.

Even when all gates pass, primary RQ4 inference is restricted to the
prospectively paired, constructible P12 subdomain represented by `P12_PAIRED`.
Coverage comparisons diagnose selection but do not authorize transport to
`P12_FULL`. Results for `P12_FULL`, its unpaired remainder, or unavailable
profiles are descriptive case-series evidence only.
