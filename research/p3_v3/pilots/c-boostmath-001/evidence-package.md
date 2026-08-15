# PILOT_ONLY evidence package: C-BOOSTMATH-001

Status: `PENDING_SOL_REVIEW`
Authorization: `NOT AUTHORIZED FOR 35-SUBJECT EXPANSION`
Claim ceiling: `observed_single_case`

## Lineage

```text
study_role: PILOT_ONLY
execution_mode: RETROSPECTIVE_PIPELINE_REPLAY
confirmatory_eligible: false
selection_outcome_independent: false
excluded_from_35_subject_freeze: true
claim_ceiling: observed_single_case
```

This package answers only whether the isolated execution chain completed on
one already-revealed case, and whether an MR outcome difference was observed
on this fixed VM, fixed case, and fixed fixtures. It does not support
semantic-versus-syntactic superiority, group ranking, generalization, RQ1–RQ4
support, C1–C8 upgrades, or any overall mutation-score or significance claim.

## Pipeline

1. Contract freeze: `data/p3_v3/pilots/c-boostmath-001/contract.json`
2. Mutant fixture import: `data/p3_v3/pilots/c-boostmath-001/fixture-import.json`
3. Independent certification: `data/p3_v3/pilots/c-boostmath-001/certification.json`
4. MR inventory freeze: `data/p3_v3/pilots/c-boostmath-001/mr-inventory.json`
5. Atomic ledger: `data/p3_v3/pilots/c-boostmath-001/atomic-ledger.jsonl`
6. Comparison: `data/p3_v3/pilots/c-boostmath-001/comparison.json`
7. Historical replay after fresh close:
   `data/p3_v3/pilots/c-boostmath-001/historical-replay.json`
   and `historical-replay-detail.json`

Chronology: contract `frozen_at_utc=2026-08-15T09:13:33.635399Z` precedes
fixture import `imported_at_utc=2026-08-15T09:13:33.636880Z`. Both bind
`contract_sha256=2b79fd46cc188d53f8438ee3c6edec182fbe56c77dc34c7221be2419f4b1dd17`.

## Certification terminal states

| Fixture | Role | Terminal state |
|---|---|---|
| roots_m037 | PILOT_DIAGNOSTIC_CONTRACT_MUTANT | CONFIRMED_NON_EQUIVALENT |
| roots_m003 | PILOT_SYNTACTIC_COMPARATOR | CONFIRMED_NON_EQUIVALENT |

Independent probe oracles (three repetitions, stable):

- fixed-original: SATISFIED
- roots_m037: VIOLATED
- roots_m003: SATISFIED (syntactic comparator; MONO violation was not required)
- buggy-75dcb3e: VIOLATED

roots_m037 is not reported as an outcome-blind formal P3 semantic mutant.
roots_m003 is not reported as a contract-derived mutant. Neither fixture
enters a formal semantic or syntactic denominator.

## Observed single-case MR difference

In this retrospective pilot run, fresh atomic rows showed MR outcome
differences on the fixed inventory:

- T1: roots_m037 `CRASH` versus roots_m003 `PASS` (and versus fixed-original `PASS`)
- B1-2: roots_m003 `VIOLATED` versus roots_m037 `PASS`

The roots_m037 T1 crash stderr records
`boost::math::evaluation_error` with a huge current guess. That is a
scientific terminal state, not an infrastructure retry.

All nine MRs were `VALID` on the fixed original (three `PASS` repetitions
each). No mutant, input, or MR was replaced.

## Comparison paths

- Matrix and group-OR table: `data/p3_v3/pilots/c-boostmath-001/comparison.json`
- Reconstruction check: `rebuild_comparison(evaluation_rows) == comparison`
- Evaluation rows: 108 (4 objects × 9 MRs × 3 repetitions)
- Total atomic rows: 135 (includes the required fixed-original baseline phase)

Group-OR here is descriptive only. T1 group-OR contains `buggy-75dcb3e`
because that arm’s T1 state is `VIOLATED`. roots_m037 T1 is `CRASH`, so it
does not enter that OR.

## Fresh versus historical

Historical `results-partial.jsonl` SHA-256 matched
`b3af810dd383368d1fcd07374912fef10720d333dd33a400e32e01498b10429c`.
Content was parsed only after the fresh ledger and comparison were sealed.

Mapped states for the two imported fixtures agreed on every MR
(`survive/pass` → `PASS`, `kill/oracle_violated` → `VIOLATED`,
`kill/crash_rc-6` → `CRASH`). Historical JSONL also contains other mutants
that this pilot did not rerun. The fresh run was not repeated to force
agreement.

## Claim ledger

See `research/p3_v3/pilots/c-boostmath-001/claim-ledger.yml`.

- `PILOT_C0_PIPELINE_EXECUTED`: supported
- `PILOT_C1_SINGLE_CASE_MR_DIFFERENCE`: observed
- All P3 C1–C8 and every cross-project / superiority / criterion /
  35-subject / generation-validity / outcome-blindness claim: blocked
