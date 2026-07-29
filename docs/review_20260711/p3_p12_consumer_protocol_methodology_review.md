# Methodology-Focused Review: P3–P12 Consumer Protocol v1.1.2

> Review date: 2026-07-11  
> Reviewed artifact: `docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md`  
> Companion artifacts: `data/dve/p12_consumer_contract_v1.1.2.json`, `research/evidence/p12_claim_ledger_v1.1.2.yml`  
> Review mode: methodology-focused editorial review  
> Independence disclosure: this is an internal protocol review performed in the P3 workspace, not an external human review and not the P12 cross-vendor LLM audit.

## 1. Editorial verdict

**Decision: CONDITIONAL PASS FOR PROTOCOL FREEZE.**

The protocol is sufficiently specific to freeze P3's consumer-side scientific decisions before P12 W4 outcomes are imported. It closes the most important risks: producer/consumer role conflation, D0 reuse as confirmation, MR-informed D2 admission, result-dependent denominator repair, ambiguity between planned scale and the go/no-go floor, and mislabelling LLM audit as human replication.

The decision is conditional only in the operational sense: P3 must implement and test the consumer validator before importing P12 numbers. That implementation may automate this protocol but may not alter its scientific constants or dispositions. No claim is made that P12 has passed the protocol; P12 W4 evidence does not yet exist in this workspace.

## 2. Reviewer configuration

### Editorial lens

Target: ACM TOSEM empirical software engineering. Focus: whether the protocol produces a credible contribution boundary and prevents the manuscript from strengthening claims after results.

### Methodology lens

Focus: prospective outcome definition, partition independence, sample-size interpretation, run completeness, audit validity, missingness, reproducibility, and claim-to-artifact traceability.

## 3. Major issues reviewed and disposition

| ID | Severity | Review concern | Resolution in frozen protocol | Status |
|---|---|---|---|---|
| R1 | Critical | A producer-side `W4_FINAL PASS` could be treated as automatic acceptance by P3. | Section 1 makes producer PASS necessary but insufficient; P3 independently executes G0–G8. | Closed |
| R2 | Critical | Legacy preregistration still describes generated-family splits, joint S1–S2/S3 confirmation, sign-flip primary inference, and confirmatory DVE-T. | Section 1 explicitly supersedes those consumer-side provisions for the P12 package and fixes v1.1.2 RFDS/S1–S2/BCa semantics. | Closed |
| R3 | Critical | Existing P12 cases could leak into D2 through aliases, forks, cherry-picks, or derived families. | G2 requires identity checks across fault, issue, revision, patch, source, ancestry, and semantic provenance; substantive overlap rejects confirmation. | Closed |
| R4 | Critical | D2 admission might be conditioned on an MR detecting the defect. | Sections 3 and G3 forbid MR, SMS, killability, strategy outcome, and expected direction as admission/exclusion inputs. | Closed |
| R5 | Critical | A failed validation layer could be removed after results and relabelled as a scope limitation. | G6 now makes clean-room, the real five-seat/three-provider LLM panel, and four-human label validity non-removable hard gates. | Closed after revision |
| R6 | Major | The 17-project/60-family floor could be reported as achieving the 20/80 plan. | Section 2 and G4 separate planned attainment from floor-only eligibility; claim C4 remains blocked until counts are recomputed. | Closed |
| R7 | Major | P12 summary statistics could be copied into P3 without an independent estimand check. | G5 reconstructs the run matrix; G7 requires independent RFDS/BCa recomputation from accepted ledgers. | Closed |
| R8 | Major | Infrastructure failures, retries, crashes, and misses could be silently removed. | G3/G5 require immutable terminal classifications, symmetric frozen retries, and preserved failed/inconclusive evidence. | Closed |
| R9 | Major | S1–S3, DVE-T, or D0 could rescue a failed S1–S2 result. | Sections 2, 8, and 9 prohibit rescue and keep these analyses exploratory/secondary. | Closed |
| R10 | Major | LLM audit could be described as unaffiliated human replication. | Delivery, G6, utilization matrix, checklist, machine contract, and claims C8/C9 separate the two. | Closed |
| R11 | Major | P3 could cherry-pick claims from P12's writing handoff. | G8 and the P3 claim ledger allow P3 only to downgrade and require every number to map to an accepted artifact. | Closed |
| R12 | Minor | The machine contract referenced the design basis with a short commit. | Replaced with the full 40-character commit ID. | Closed after revision |

## 4. Statistical-method review

### Estimand alignment

The consumer protocol matches the v1.1.2 design: project-equal mean paired RFDS difference for S1 versus S2. It does not confuse SMS with a real-fault detection rate. MR misses remain in the D2 denominator, which is essential to avoid a selection-conditioned estimate.

### Interval and decision rules

The two-level BCa interval is correctly made primary, with projects and families-within-project as resampling levels and paired strategy outcomes preserved. The protocol distinguishes superiority (`lower bound > 0`) from practical importance (`lower bound > 0.10`). The project sign-flip appears only as a symmetry-dependent sensitivity analysis.

### Scale and external validity

The protocol correctly treats 20 projects/80 D2/160 D1 as the plan and 17 projects/60 D2 as the minimum confirmatory eligibility floor. Floor-only execution remains confirmatory under the frozen estimand if all other gates pass, but necessarily receives an under-target qualification. Below the floor, evidence becomes non-confirmatory rather than being repaired by D3 or legacy cases.

### Missingness and infrastructure

The protocol requires a complete expected matrix and prevents infrastructure states from being silently counted as scientific misses. The future validator must implement a frozen rule for whether unresolved infrastructure cells cause quarantine or rejection; it may not choose treatment after observing strategy differences. The current protocol already requires that rule to be frozen and symmetric before execution.

## 5. Internal-validity review

Strong controls:

- chronological freeze and one-shot opening;
- consumer-side hash and tag verification;
- multi-identity D0 exclusion rather than filename matching;
- D2 admission before MR mapping/outcomes;
- immutable negative/rejected evidence;
- equal S1/S2 opportunity and denominator preservation;
- independent P3 recomputation;
- hard separation of LLM audit, four-rater label validity, and optional external human replication.

Residual threats that must remain in the paper:

1. P12 and P3 may share authorship even though procedural branches are isolated.
2. Open-source fault availability may shape project and mechanism coverage.
3. Family boundaries and semantic-property certificates include human judgement.
4. The five-model audit is heterogeneous machine judgement, not independent human reproduction.
5. The minimum floor can yield wider uncertainty and narrower external validity than the planned target.
6. Some real semantic faults may be outside the detection ceiling of all frozen MRs.

## 6. Claim-integrity review

The initial ledger is appropriately conservative:

- only existence of the prospective consumer protocol is `supported`;
- D0 use is `qualified` and cannot be upgraded to confirmation;
- P12 workflow compliance, achieved scale, RFDS superiority, practical importance, and LLM audit are blocked pending accepted artifacts;
- DVE-T is speculative/exploratory;
- external human replication remains blocked and optional.

This prevents an unfinished P12 experiment from leaking directional statements into the P3 Abstract, Contributions, Results, or Conclusion.

## 7. Required operational follow-up

The following are implementation gates, not reasons to reopen the scientific design:

1. implement a P3-side validator for the machine contract and P12 evidence-package schema;
2. create negative fixtures for hash mismatch, D0/D2 alias overlap, outcome-informed admission, second opening, missing run cells, provider concentration, and estimand drift;
3. implement immutable `original`, `quarantine`, and reproducible `derived` directories;
4. implement run-matrix reconstruction and an independent RFDS/BCa comparison against P12;
5. emit a machine acceptance state plus a human-readable G0–G8 report;
6. update the claim ledger only from accepted artifact hashes.

Until these steps are tested, P3 may freeze this protocol and organize manuscript sections, but it must not import P12 result numbers.

## 8. Final assessment against TOSEM concerns

| Concern | Assessment after revision |
|---|---|
| Prospective design and researcher degrees of freedom | Strong |
| Independence and leakage control | Strong procedurally; shared-authorship limitation remains |
| Real-fault authenticity and selection bias | Strong if P12 ledgers pass G2/G3 |
| Baseline fairness | Strong if G4/G5 verify S2 richness and equal opportunity |
| Statistical estimand and inference | Strong and internally consistent |
| Reproducibility and artifact traceability | Strong design; validator implementation pending |
| Negative-result interpretability | Strong; no rescue or endpoint switching |
| External replication | Correctly limited; optional human replication not overstated |

**Bottom line:** the protocol is fit to freeze before P12 outcomes. It materially improves the credibility of the future TOSEM submission, but it is not itself empirical evidence and does not reduce the necessity of completing P12 W4 at the planned scale with all hard validations.
