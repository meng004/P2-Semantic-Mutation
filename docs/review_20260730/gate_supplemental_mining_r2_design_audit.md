# Gate SUPPLEMENTAL_MINING_R2_DESIGN — Local Protocol-Revision Audit

- **Environment:** Local Desktop
- **Branch:** `codex/phase3-supplemental-mining-r2-design`
- **Baseline:** `a9101e8e05d3424c075bba5c717e39e299c7900c`
- **Design:** `docs/superpowers/plans/2026-08-02-supplemental-mining-r2.md`
- **Design SHA-256:** `f1095514be068f0295395142afa0a3dc94329b677ca610163cfb460f7b3d46c8`
- **Freeze commit:** `SELF` (resolve with `git rev-parse HEAD` after this commit)
- **Verdict:** `PASS`

## 1. Scope of this gate

This gate reviews only the Supplemental Mining R2 protocol revision. No issue
retrieval, Search API call, candidate creation, A1/A3 adjudication, evidence
collection, readiness execution, canonical-sheet mutation, or freeze-registry
write occurred.

PR #6 was not merged or cherry-picked. Its integration remains a separate
explicit decision.

## 2. Standards axis

**Findings: 0.**

- The change is documentation-only and adds exactly the R2 design plan and
  this local gate report.
- All Local Desktop shell commands used the required `rtk` prefix.
- `git diff --cached --check` returned exit 0.
- No pre-existing source, data, admission, readiness, reproduction, freeze,
  annotation, prediction, or run artifact changed.
- The plan separates Local Desktop design authority from later Cursor VM
  execution and requires a fresh execution branch from the immutable audited
  commit.

One initial read-only `rg` checklist command returned exit 2 because shell
quoting interpreted Markdown backticks. It changed no file and made no network
request. The same checklist was rerun with a single-quoted pattern and returned
exit 0; only the successful rerun is evidence for the requirement check.

## 3. Specification axis

**Findings: 0.**

The design freezes all requested constraints:

1. The six R1 repositories, their order, prefixes, restrictions, eleven
   phrases, `2026-08-01` cutoff, exclusion classes, blind policy, and review
   stopping rule remain unchanged.
2. GitHub GraphQL `Repository.issues` is the only permitted retrieval
   transport. Search API, GraphQL search, REST issue listing, manual search,
   and PR-to-issue resolution are forbidden.
3. A PR, open issue, incomplete page or labels, query identity drift, GraphQL
   error, malformed response, timeout, partial output, or nonzero command exit
   hard-fails without minting a candidate payload.
4. Retrieval must traverse every page for all six repositories and prove
   terminal pagination, stable `totalCount`, exact cursor continuity, unique
   issue identity, closed state, and Issue typename.
5. Snapshot, queue, decision, sheet, evidence, and handoff fields are bound
   explicitly, with one-field mutation negatives at every edge.
6. A2 remains entirely `PENDING`, `analysis_id` remains blank, and downstream
   data and vocabulary remain forbidden.
7. The execution handoff stops before readiness and cannot modify canonical
   sheets or `FREEZE.sha256`.

## 4. Distribution ruling

The accepted starting state is 18 ready defects with two qualifying projects.
Every repository in the unchanged six-repository R1 whitelist currently has
zero accepted-ready defects. Therefore six additional ready defects can add at
most two qualifying projects and cannot reach the frozen H-RANK floor of six.

The design consequently pre-commits three additional ready defects each for
PyMC, GPyTorch, chaospy, and SALib. The fixed success target is at least twelve
additional ready defects, yielding n >= 30 and six qualifying projects. This
satisfies the requested lower bounds of at least six additions and n >= 24
without changing the whitelist. PyTorch and JAX remain searched/reviewed under
the unchanged R1 rule but have zero R2 readiness quota and cannot substitute
for a miss.

## 5. Verification evidence

| Check | Result |
|---|---|
| Baseline/merge-base | both `a9101e8e05d3424c075bba5c717e39e299c7900c` |
| Cached diff check | exit 0 |
| Full test suite | `260 passed, 10 warnings` in 17.74 s |
| Requirement-pattern rerun | exit 0 |
| Unstaged diff | empty before audit-report creation |
| External retrieval | not run |
| Candidate/readiness artifacts | not created |

The ten warnings are the existing scikit-learn Gaussian-process convergence
warnings and statsmodels mixed-model boundary warning; there were no failures.

## 6. Successor state

This gate unlocks exactly one next action after the freeze commit is pushed: a
fresh Cursor VM/session may create
`cursor/grok-phase3-supplemental-mining-r2` from the immutable freeze commit
and execute the plan. It does not unlock readiness, canonical freeze, C4,
annotation, category mapping, prediction, detection, or PR #6 integration.

## 7. SUPPLEMENTAL_MINING_R2_DESIGN-r1 correction handoff

- **Record type:** append-only correction handoff; the original audit record
  above is unchanged.
- **Correction baseline:** `6fc5b6fde8d87b284b60b46033ce6632b979e456`
- **Correction payload:** `1ed9fb2dc2714cb452bba4016d6093cefb36204d`
- **Correction audit commit:** `SELF`; its direct parent must be
  `1ed9fb2dc2714cb452bba4016d6093cefb36204d`.
- **Corrected plan SHA-256:**
  `04b6b08c344b550c9ce11b8bb0fca57a0cb00fcb5f7bffceb4d49ab71155e8d5`
- **Gate requested:** `SUPPLEMENTAL_MINING_R2_DESIGN-r1`
- **Review state:** `PENDING_LOCAL_R1_REVIEW`

### 7.1 Correction scope

The payload closes `R2-DESIGN-CURSOR-RTK-001`: every `rtk` prefix was removed
from the Cursor VM commands in section 7 Tasks 1, 2, 3, and 6. The plan now
freezes the environment rule explicitly: Cursor VM commands must not use
`rtk`; only Local Desktop commands use `rtk`.

No repository, phrase, cutoff, exclusion, blind-policy rule, quota, stopping
rule, transport invariant, field binding, negative test, or successor gate was
changed. No Cursor branch was created, and no search, candidate generation, or
readiness command ran.

### 7.2 Correction verification

| Check | Result |
|---|---|
| Cursor command-prefix scan | raw exit 1, no output |
| `git diff --check` | exit 0 |
| Requested bare `rtk python3 -m pytest -q` | exit 1: system Python has no `pytest` module |
| Repository `.venv` without src layout | exit 2: nine collection errors for missing `p2` |
| Repository-mandated full suite with `.venv` and `PYTHONPATH=src` | `260 passed, 10 warnings` in 16.31 s |
| Corrected plan hash | `04b6b08c344b550c9ce11b8bb0fca57a0cb00fcb5f7bffceb4d49ab71155e8d5` |

The authoritative full-suite command was:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

The two earlier test invocations failed only because they omitted repository
environment prerequisites; they did not execute or modify scientific data.

### 7.3 Locked successor

Push the correction payload and this direct-child audit commit, then stop.
Creation of `cursor/grok-phase3-supplemental-mining-r2` remains locked until a
new Local Desktop session independently verifies this handoff and records
`SUPPLEMENTAL_MINING_R2_DESIGN-r1` as passing. PR #6 integration remains a
separate explicit decision.

## 8. SUPPLEMENTAL_MINING_R2_DESIGN-r1 independent re-review

- **Reviewed commit:** `d95d6277ee09479d638bb83d75562e9dc4348031`
- **Direct parent:** `1ed9fb2dc2714cb452bba4016d6093cefb36204d`
- **Corrected plan SHA-256:**
  `04b6b08c344b550c9ce11b8bb0fca57a0cb00fcb5f7bffceb4d49ab71155e8d5`
- **Standards findings:** 0
- **Specification findings:** 0
- **Verdict:** `PASS_WITH_DISCLOSURE`

The re-review independently confirmed the direct-child lineage, exact plan
hash, clean diff, and Cursor command policy. The only occurrences of `rtk` in
the plan are the policy sentences that prohibit it in Cursor VM and require it
on Local Desktop; no Cursor command carries that prefix. The repository
environment test command completed with `260 passed, 10 warnings`.

The disclosure is procedural: Cursor execution was started before this
independent result was recorded, contrary to section 7.3. This re-review closes
the design correction itself but does not retroactively validate that execution
or any artifact produced by it. Those artifacts require a separate execution
gate.
