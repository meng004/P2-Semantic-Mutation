# Claim Disclosure Policy For TOSEM Repair

Date: 2026-07-08

Purpose: define what belongs in the submitted manuscript and what remains in the internal research ledger during the TOSEM repair loop.

## Core Rule

The manuscript reports final, pre-submission research results, not a chronological log of exploratory attempts.

Internal ledgers must retain failed, exploratory, and inconclusive runs for audit discipline. The submitted paper does not need to narrate those process details unless they affect the final research claim.

No positive claim may be retained merely because negative process evidence is omitted.

## Must Be Disclosed In The Manuscript

- Final negative findings that affect interpretation of SMS or the stated hypotheses.
- Failed hypotheses that are part of the final RQ/hypothesis design.
- Robustness or sensitivity checks that materially change the interpretation of a headline result.
- Limitations that bound the contribution, external validity, reproducibility, or construct validity.
- Missing evidence when the manuscript would otherwise imply that evidence exists.

## Need Not Be Disclosed In The Manuscript

- Abandoned pilot configurations that are not part of the final study design.
- Intermediate failed runs that were corrected before the final protocol and do not affect any retained claim.
- Local engineering failures such as broken auxiliary build state.
- Exploratory alternatives that do not change the final result, final method, or final conclusion.
- Internal reviewer deliberation artifacts, except when they identify a scientific limitation that remains true.

## Current Finding Classification

| Finding | Publish? | Reason | Required wording discipline |
|---|---|---|---|
| H1 fails under the final pre-registered study design. | Yes | It directly limits operator implementability claims. | State as a final result; do not call it a process failure. |
| H4 fails under the final pre-registered study design. | Yes | It directly limits LRCA mass / suspect-share claims. | State as a final result and connect to SMS sparsity. |
| H2 is weaker under frozen MP5 than under MP1 sensitivity. | Yes | It affects the interpretation of the main aligned-vs-cross contrast and prevents cherry-picking concerns. | Report MP5 as primary, MP1 as sensitivity. |
| 45 of 60 PUT--MP cells have zero SMS. | Yes | It defines a boundary condition for the metric and affects power/precision. | Foreground as sparsity, not as an incidental nuisance. |
| RQ3 values changed after synchronization to `rq3_friedman_v4.json`. | Yes, as final value only | The final value must be consistent; obsolete values do not need a narrative history. | Use the final value everywhere; no process story. |
| Industrial real-defect artifacts are not yet package-complete. | Yes, unless completed before submission | Without evidence, validation-strength wording would overclaim. | Either provide ledger or downgrade to sanity check. |
| S5 purity has not been independently verified. | Yes, unless completed before submission | Without purity evidence, alignment claims are construct-limited. | Call S5 an intended-stratum label unless the audit supports stronger wording. |
| Earlier exploratory configurations not used in the final estimand. | No, unless they explain a final robustness result | They are process history rather than final research result. | Keep in internal ledger only. |
| Failed local LaTeX/build attempts caused by auxiliary state. | No | They are engineering process, not scientific evidence. | Do not mention in manuscript. |

## Reviewer Checkpoint 2

- This policy does not authorize hiding final-study negative findings.
- This policy does authorize omitting process-only failures that do not alter the final study design, final result, or final claim.
- Any positive wording that depends on an omitted negative process result must be downgraded or removed.
- Topic drift check: the final manuscript should read as a study of SMS validity boundaries, not as a chronological account of a repair process.
