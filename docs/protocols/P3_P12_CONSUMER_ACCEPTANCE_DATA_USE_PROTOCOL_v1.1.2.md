# P3–P12 Consumer Acceptance and Data-Use Protocol v1.1.2

> Status: **FROZEN CONSUMER CONTRACT**  
> Freeze date: 2026-07-11 (Asia/Shanghai)  
> Consumer: P3 Semantic Mutation / TOSEM v1.1.2  
> Producer: P12 Defect4MR independent evidence workflow  
> Scientific design basis: `docs/superpowers/specs/2026-07-11-tosem-v1.1.2-real-fault-dve-design.md`  
> Machine-readable companion: `data/dve/p12_consumer_contract_v1.1.2.json`  
> Claim-control companion: `research/evidence/p12_claim_ledger_v1.1.2.yml`

## 1. Purpose and binding effect

This protocol fixes, before P12 supplies its W4 evidence package, how P3 will receive, validate, classify, analyze, and cite P12 evidence. It prevents P3 from selecting favorable P12 artifacts, changing denominators after seeing outcomes, promoting exploratory evidence to confirmation, or strengthening manuscript claims beyond the accepted evidence.

P12 is the evidence producer. P3 is a read-only consumer after the P12 W3 freeze. A P12 `W4_FINAL PASS` is necessary but not sufficient for P3 acceptance: P3 independently runs the consumer gates in this protocol. P3 never edits a delivered P12 package. Corrections require a new P12 package version, immutable producer commit, and new release tag.

This protocol supersedes conflicting consumer-side provisions in `docs/prereg/DVE_prereg_v1.md`. In particular, v1.1.2 uses newly admitted real historical semantic faults as D2, RFDS as the primary endpoint, S1 versus S2 as the sole confirmatory comparison, a two-level BCa interval as the primary interval, and project-level sign-flip only as sensitivity. The older generated-family split, joint S1-versus-S2/S3 confirmation, and confirmatory DVE-T rules are not applicable to the P12 package.

## 2. Frozen scientific contract

The following values cannot change after observing P12 D2 outcomes:

| Item | Frozen value |
|---|---|
| Primary comparison | S1 residual-guided versus S2 classical-mutation-guided |
| Primary endpoint | RFDS, project-equal mean real-fault-family detection |
| Portfolio budget | `k = 4` per project, equal for S1 and S2 |
| MID | `0.10 RFDS` |
| Primary interval | Two-level BCa bootstrap: projects, then real-fault families within project |
| Statistical decision | One-sided 95% lower bound above 0 for superiority |
| Practical-importance decision | One-sided 95% lower bound above 0.10 |
| Sensitivity | Project-level exact sign-flip, labelled symmetry-dependent sensitivity |
| Exploratory endpoint | DVE-T; cannot rescue the primary comparison |
| Planned scale | 20 analyzable projects, 80 new D2 families, 160 D1 families |
| Go/no-go floor | 17 analyzable projects and 60 new D2 families |
| Project concentration | No project contributes more than 20% of D2 families |
| Minimum within-project D2 | At least two admitted D2 families per primary-analysis project |
| S2 richness | At least 20 `R0`-surviving first-order mutants from at least three operator families per project |

Reaching the floor does not mean reaching the planned scale. A package with 17–19 projects or 60–79 D2 families may be eligible for the frozen confirmatory analysis, but every paper location must disclose that the planned scale was not achieved. Below either floor, P3 rejects confirmatory use and may retain the package only as exploratory evidence.

## 3. Evidence partitions and permitted uses

| Partition | Content | Permitted P3 use | Prohibited P3 use |
|---|---|---|---|
| D0 | Existing P3 results; 35 P12 `verified_full` defects; 34 mutation cases; 1,124 mutants; rehearsals and legacy ledgers | Instrument development, feasibility, taxonomy, positive controls, cost calibration, historical context | D2 denominator, confirmatory RFDS, sample-size attainment, headline external-validity claim |
| D1 | New MR-free semantic development families | S1 development, residual-family signal, portfolio construction, robustness diagnostics | Real-fault detection claim, D2 substitution, post-D2 tuning |
| D2 | New independently admitted real historical semantic fault families | Sole real-fault confirmatory outcome domain | MR-informed admission, removal of MR misses, reuse of D0 cases or clones, post-opening family changes |
| D3 | Transfer, positive controls, platform-gated cases, secondary audits | Exploratory and mechanism analysis | Rescuing a failed S1–S2 comparison, filling D2 recruitment shortfalls |

P3 accepts a D2 family only when P12 recorded its admission before MR mapping and before S1/S2 execution. MR detectability, SMS, killability, anticipated effect direction, and strategy success are forbidden admission or exclusion inputs. An MR miss remains in the denominator.

## 4. Required P12 delivery

P3 accepts only a versioned package anchored by all of the following:

1. `release/provider/p12-p3-v1.1.2/evidence-package.json` and its SHA-256;
2. immutable P12 commit and annotated tag `p12-evidence-v1.1.2` or a declared successor version;
3. W1, W2, W3, W4_PREOPEN, and W4_FINAL machine states and reports;
4. frozen P3 consumer contract as received by P12;
5. P12 W3 freeze manifest and tag;
6. D0 exclusion registry and D0/D2 zero-overlap report;
7. D1, sealed D2, MR-catalogue, S1-portfolio, and S2-portfolio manifests;
8. D2 commitment ledger proving one opening only;
9. D2 admission/rejection ledger, including negative and uncertain candidates;
10. complete S1/S2 execution-run ledger, raw-artifact hashes, retry and infrastructure-status ledger;
11. primary, sensitivity, and exploratory analysis outputs kept distinct;
12. clean-room replay ledger and key-sample summary;
13. five-seat blinded cross-vendor LLM audit ledger and aggregate report;
14. four-human-rater label-validity ledger under the declared protocol;
15. workflow amendment ledger, deviations, limitations, and failed/inconclusive runs;
16. raw-artifact archive or DOI locations with checksums;
17. `score-task.yml`, `experiment-ledger.yml`, `claim-ledger.yml`, and P12 evidence-package handoff.

External human audit or replication, when present, is delivered as a separate optional record with personnel independence and sample scope. Its absence does not fail the P3 consumer gate. LLM audit must never be labelled external human replication.

## 5. P3 consumer-side acceptance states

P3 assigns one package-level state:

- `ACCEPT`: all hard gates pass; the package may enter the uses allowed by its achieved scale and claim ledger.
- `QUARANTINE`: transport, metadata, or reproducibility material is incomplete but can be corrected without changing scientific identities, outcomes, denominators, or frozen decisions. No manuscript number may be imported while quarantined.
- `REJECT_CONFIRMATORY`: a hard scientific-integrity gate fails. The package may be archived and discussed as a failed/exploratory attempt, but cannot support confirmatory P3 claims.
- `SCOPE_DOWNGRADE`: integrity gates pass, but a prespecified scale, validation, or coverage condition permits only a narrower/exploratory interpretation.

`QUARANTINE` cannot be used to repair an outcome-dependent defect. D0/D2 overlap, outcome-informed admission, a second holdout opening, denominator editing, silent model substitution, or freeze drift are `REJECT_CONFIRMATORY` conditions.

## 6. Consumer acceptance gates

### G0 — Transport and identity

Checks:

- package file parses and uses the expected schema version;
- package hash, every referenced artifact hash, P12 commit, and release tag agree;
- no referenced file escapes the package or declared raw archive;
- no credential, private pre-release holdout payload, or mutable external link is treated as evidence;
- the P3 contract hash/version in P12 matches this contract.

Failure disposition: missing transport metadata is `QUARANTINE`; hash mismatch, tag movement, or unexplained artifact replacement is `REJECT_CONFIRMATORY`.

### G1 — Producer workflow and freeze chronology

Checks:

- all five P12 states W1, W2, W3, W4_PREOPEN, and W4_FINAL report machine `PASS`;
- W3 precedes portfolio sealing and D2 opening;
- D1, D2, MR catalogue, seeds, code, environments, S1 and S2 portfolio hashes were frozen before opening;
- every amendment after W3 has a version bump, cause, scope, and impact statement;
- P3 remained read-only after P12 freeze.

Failure disposition: missing report is `QUARANTINE`; chronological contradiction, unversioned scientific change, or P3 write access is `REJECT_CONFIRMATORY`.

### G2 — Partition isolation and provenance

Checks:

- every evidence item has exactly one partition;
- the 35 legacy P12 defects, 34 mutation cases, 1,124 mutants, their patch/issue/family aliases, and all P3 legacy data occur only in D0/D3;
- D0/D2 overlap is zero by fault ID, repository/revision, patch hash, source hash, issue/PR identity, fork/cherry-pick ancestry, and semantic provenance fingerprint;
- D1 contains no D2 issue, patch, reproducer, Fault Card, outcome, or derived template;
- the MR catalogue contains no D2 fault identity, outcome, or mechanism distribution learned from D2.

Failure disposition: unresolved missing provenance is `QUARANTINE`; any substantive D0/D2 overlap or cross-branch leakage is `REJECT_CONFIRMATORY`.

### G3 — D2 admission independence and family integrity

Checks:

- every D2 admission decision predates MR execution and strategy outcome;
- permitted admission dimensions are authenticity, traceable provenance, buggy/fixed revisions or qualified certificate, semantic relevance, reproducibility, buildability, and license compatibility;
- prohibited MR/SMS/outcome fields did not influence admission or rejection;
- family boundaries were frozen before commitment;
- backports, patch variants, reproducer variants, and generated descendants share one family;
- rejected, uncertain, MR-missed, crash, timeout, and infrastructure cases remain traceable.

Failure disposition: correctable missing administrative fields are `QUARANTINE`; outcome-informed selection, family reshaping after results, or deletion of unfavorable cases is `REJECT_CONFIRMATORY`.

### G4 — Scale, diversity, and baseline adequacy

Checks:

- observed analyzable project, D1-family, and D2-family counts are recomputed from manifests;
- every primary project has at least two D2 families;
- no project contributes over 20% of D2;
- S2 richness and MR-catalogue floors hold for every primary project;
- exclusions and replacements occurred before opening under frozen rules.

Disposition:

| Observed state | P3 disposition |
|---|---|
| At least 20 projects, 80 D2, and 160 D1; other checks pass | `ACCEPT`, planned scale achieved |
| At least 17 projects and 60 D2, but below a planned target | `ACCEPT` for frozen analysis with mandatory under-target qualification |
| Below 17 projects or 60 D2 | `SCOPE_DOWNGRADE`; no confirmatory claim |
| Project concentration/family/S2 floor repaired after outcomes | `REJECT_CONFIRMATORY` |

### G5 — Run-matrix completeness and denominator preservation

Checks:

- P3 reconstructs the expected project × D2 family × strategy matrix from sealed manifests;
- S1 and S2 receive the same budget and execution opportunity;
- each planned cell has exactly one terminal scientific result or an explicitly separate infrastructure state;
- retry rules are frozen and symmetric;
- crashes, timeouts, misses, invalid outputs, and infrastructure failures are not silently removed or conflated;
- family and project denominators are unchanged after opening;
- raw result hashes regenerate the compact run ledger.

Failure disposition: unavailable raw archive is `QUARANTINE`; missing or selectively removed run cells, asymmetric retries, or denominator changes are `REJECT_CONFIRMATORY`.

### G6 — Validation and audit

Hard checks:

- clean-room automated reproduction passes the frozen key-sample rule;
- the LLM audit contains exactly five distinct model/version identities from at least three provider organizations, with no provider contributing more than two seats;
- panel packets were blinded and outputs are hash-verifiable; abstentions and disagreements remain visible;
- four-human-rater label validity satisfies the frozen protocol and thresholds;
- audit failures trigger the declared full-layer review/demotion rule rather than selective repair.

Failure disposition: temporarily unavailable audit artifacts are `QUARANTINE`. Failure of clean-room key-sample reproduction, the five-seat/three-provider LLM panel, or four-human-rater label validity is `REJECT_CONFIRMATORY`. `SCOPE_DOWNGRADE` is available only for a failed audit layer declared exploratory before outcomes; none of these three hard checks is removable from the v1.1.2 confirmatory package. P3 cannot invent missing panel seats or call LLM output human replication.

### G7 — Independent analysis compatibility

P3 does not accept P12's summary statistics by inspection. P3 regenerates the analysis input from accepted run ledgers and independently checks:

- `RFDS_p(R) = mean_g det(R,g)` over accepted D2 families within project;
- `Delta_real = mean_p[RFDS_p(S1) - RFDS_p(S2)]`, with projects equally weighted;
- two-level BCa resampling preserves paired strategy outcomes;
- the one-sided lower bounds for 0 and MID 0.10 are reported separately;
- sign-flip is sensitivity and states its symmetry assumption;
- DVE-T and every S1–S3/S4 comparison are labelled exploratory/secondary;
- missingness and ceiling analyses include MR misses rather than deleting them;
- P12 and P3 recomputations match within frozen numerical tolerance.

Failure disposition: software/environment incompatibility is `QUARANTINE`; estimand, comparator, endpoint, denominator, or confirmatory-label drift is `REJECT_CONFIRMATORY`.

### G8 — Claim and disclosure control

Checks:

- every number intended for the manuscript maps to an accepted run/output/table/hash;
- P12's claim ledger and P3's claim ledger agree on evidence identity, with P3 allowed only to downgrade;
- negative and contradictory results are disclosed;
- common authorship, P12 status, D0 reuse, D2 non-overlap, and package version are disclosed;
- benchmark/governance work is not presented as P3's principal contribution;
- limitations include under-target scale, role overlap, residual leakage risk, MR ceiling, platform exclusions, and lack of external human replication when applicable.

Failure disposition: wording defects are corrected before writing. A blocked claim cannot be repaired through prose.

## 7. Data-import and derivation workflow

P3 follows this immutable flow:

```text
immutable P12 package
  -> G0 transport/hash validation
  -> G1–G3 chronology, partition, and admission audit
  -> G4 scale/baseline classification
  -> G5 run-matrix reconstruction
  -> G6 audit/clean-room validation
  -> accepted raw ledger snapshot
  -> P3-derived analysis table
  -> G7 independent recomputation
  -> G8 claim-ledger update
  -> manuscript tables/figures/prose
```

Directories used when implementation begins:

```text
data/external/p12/v1.1.2/original/     # immutable delivered package
data/external/p12/v1.1.2/quarantine/   # rejected/quarantined copies and reports
data/derived/p12/v1.1.2/               # reproducibly generated P3 analysis inputs
reports/p12_acceptance/v1.1.2/         # machine and reviewer-facing gate reports
```

The original directory is never rewritten. Derived files record source hashes, command, P3 commit, configuration, seed, timestamp, and output hash. Failed imports and analyses remain in the experiment ledger.

## 8. Data-to-paper utilization matrix

| Evidence/result | Allowed manuscript location | Required wording/status | Forbidden use |
|---|---|---|---|
| W1 synthetic workflow | Method/Artifact | workflow tested; no empirical claim | Results evidence |
| W2 D0 rehearsal | Method/Threats/Artifact | observed or qualified calibration | real-fault confirmation |
| D1 construction and dev results | Method/dev diagnostics | development evidence | external-validity headline |
| D2 corpus counts | Method/Results | distinguish planned target from floor | calling floor “target achieved” |
| S1–S2 RFDS | Results/Abstract only after G7/G8 | exact supported/qualified wording | substitution with S1–S3 or DVE-T |
| MID decision | Results/Abstract only if lower bound > 0.10 | practical importance | point estimate alone |
| Sign-flip | Sensitivity | symmetry-dependent sensitivity | randomization-test claim |
| DVE-T | Exploratory Results/Discussion | exploratory | rescue of failed primary |
| LLM panel | Validation/Threats | blinded cross-vendor LLM audit | external human replication |
| Four-human labels | Validation | human label-validity evidence | independent replication unless personnel qualify |
| Optional unrelated human replication | Validation/Artifact | exact independent sample and scope | implying full replication from an audit sample |
| Negative/null result | Results/Discussion | report directly with applicability boundary | deletion or outcome swapping |

## 9. Decision and wording rules

### 9.1 Primary outcome

- Lower bound `<= 0`: no clean decision-value gain.
- Lower bound `> 0` but `<= 0.10`: statistical superiority within the accepted sample; no practical-importance claim.
- Lower bound `> 0.10`: statistical superiority and frozen-MID practical importance within the accepted sample.
- A favorable S1–S3, S4, DVE-T, D0, or mechanism result cannot rescue a failed S1–S2 primary result.

### 9.2 Scope modifiers

All outcome wording is additionally constrained by:

- planned scale achieved versus floor-only;
- project/domain coverage;
- real-fault MR-detectability ceiling;
- project concentration and platform exclusions;
- clean-room and audit scope;
- whether external human replication actually occurred.

### 9.3 Negative results

A null or negative result remains publishable evidence if isolation, scale, run completeness, and validation gates pass. P3 then positions SMS as a diagnostic construct rather than a demonstrated decision-value guide. Endpoints, comparators, denominators, and claim criteria are not changed.

## 10. Claim-status policy

P3 uses: `supported`, `observed`, `qualified`, `insufficient`, `blocked`, and `speculative`.

- Abstract and Contributions: `supported` or explicitly scoped `qualified` only.
- Results: `supported`, `observed`, or scoped `qualified` only.
- Discussion: the same statuses plus clearly marked interpretations.
- Limitations/Future Work: may include `insufficient`, `blocked`, or `speculative` as non-findings.
- P3 may downgrade a P12 claim but never upgrade it without additional accepted evidence.
- Numbers without an accepted artifact path/hash remain blocked.

The authoritative initial statuses are in `research/evidence/p12_claim_ledger_v1.1.2.yml`.

## 11. LOOP operating procedure for every package version

### L — Locate and lock

- record P12 package version, commit, tag, transport hash, P3 commit, and contract version;
- copy the package to the immutable original area;
- lock the expected files, gates, counts, and analysis configuration;
- confirm no P12 outcomes have been used to modify this protocol.

### O — Observe failures

- run every consumer gate against both the package and negative controls;
- record every mismatch, missing file, audit disagreement, negative result, and infrastructure failure;
- do not continue from a failed hard gate by editing the delivered package.

### O — Operate minimally

- for correctable transport/metadata problems, request a new P12 version;
- change only consumer tooling needed to implement this frozen contract;
- any scientific-contract change requires a versioned deviation before viewing the affected outcome.

### P — Prove and preserve

- rerun all gates and independent analysis from the immutable package;
- preserve failed attempts and compare P12/P3 results;
- generate package-level state, claim-ledger changes, limitations, and the manuscript-ready evidence handoff;
- commit the acceptance report before importing numbers into the manuscript.

## 12. Deviations and versioning

A deviation record must state: identifier, date, triggering evidence, old rule, new rule, who knew which outcomes, affected partitions/claims, severity, and disposition. It never overwrites this file.

- editorial clarification without scientific effect: patch version;
- schema/tooling change without estimand effect: minor version plus regression evidence;
- endpoint, comparator, denominator, admission, scale floor, interval, or claim-rule change: new major preregistration version; v1.1.2 evidence cannot be silently pooled.

P12 corrections require an immutable successor package and tag. P3 keeps all earlier packages and acceptance reports.

## 13. Protocol acceptance checklist

Before P3 consumes P12 numbers, all statements below must be true:

- [ ] The machine-readable contract matches this protocol.
- [ ] P12 acknowledges the same contract version before D2 opening.
- [ ] P12 W3 freeze precedes all D2 outcomes.
- [ ] G0–G8 have recorded dispositions.
- [ ] Original and derived directories are separate and hashed.
- [ ] The expected run matrix was reconstructed independently.
- [ ] P3 independently reproduced RFDS and the primary interval.
- [ ] Planned target and go/no-go floor are reported separately.
- [ ] Claim-ledger changes cite accepted artifacts.
- [ ] LLM audit is not described as human replication.
- [ ] External human audit/replication is stated only if it occurred.
- [ ] Null, negative, failed, and infrastructure outcomes remain visible.
- [ ] No blocked claim appears as an Abstract, Contribution, Result-as-fact, or Conclusion claim.

Until this checklist passes, P3 may organize the manuscript skeleton but may not write P12 result numbers or directional conclusions into the paper.
