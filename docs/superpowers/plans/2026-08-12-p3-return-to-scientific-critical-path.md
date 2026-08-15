# P3 Return to Scientific Critical Path Plan

> **For agentic workers:** This is the routing charter that resumes the frozen
> scientific study. For each task below, first produce a task-scoped
> implementation plan with `superpowers:writing-plans`, then execute it with
> `superpowers:executing-plans` (or subagent-driven-development), exactly as
> the governing scientific plan's header mandates. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Produce RQ1–RQ4 evidence by resuming the scientific execution
sequence (Phase 0 → 1 → 2 → 3) of the governing plan, starting from the real
Phase 0 protocol freeze; stop building verification infrastructure.

**Decision basis:** Exit (b) of the 2026-08-12 retrospective review
(`docs/review_20260812/authority_lock_r5_retrospective_root_cause_and_goal_alignment_review.md`).
The External Authority Lock is frozen at commit
`bdf6a7cb9f34ab31e52a7b75a6e32369840b9b65` (849/849 tests pass) per the Freeze
Record appended to
`docs/superpowers/plans/2026-08-11-p3-v3-external-authority-lock-implementation.md`.
It is a reproducibility support artifact, off the argumentation critical path.

**Governing documents (unchanged, not re-frozen here):**

- Scientific plan:
  `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`
  (execution sequence §14, deferral rule §18, remediation matrix row 41)
- Evidence design:
  `docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md`
- Minimum-foundation plan and its four recorded blockers:
  `docs/superpowers/plans/2026-08-08-p3-v3-minimum-evidence-foundation-implementation.md`
- Frozen toolchain: `scripts/p3_v3/evidence.py` CLI (eleven commands including
  `freeze-authority-lock`, `validate-protocol`, `verify-bridge`,
  `build-frames`, `run-preflight`, `close-phase`, `verify-evidence`) plus
  `src/p3_v3/{artifacts,bridge_and_frames,packages,preflight,run_records}.py`.

## Global Constraints (anti-spiral rails, from the retrospective review)

1. **No verifier or lock hardening.** The verifier is consumed as-is at the
   frozen commit. Backlog item F1 (per-class credential normalization) is
   implemented only if lock work is explicitly resumed by the user; F2/F3 are
   adjudicated non-blocking and receive no patches. Any new hardening idea
   goes to the Freeze Record backlog, never into a task of this plan.
2. **Bounded review scope with a repair cap.** Every task freezes its
   acceptance-criteria list before implementation. Independent review judges
   PASS/BLOCK only against that list. Out-of-list findings are recorded to
   backlog. Hard cap: two repair rounds per task; a third finding cycle stops
   work and escalates to the user with the open list.
3. **Root-cause batching for repairs.** Before repairing any finding,
   enumerate the entire defect class (all input forms, all sibling call
   sites — controller and subject side) and fix the class in one batch commit
   with property-style tests where applicable. Never patch only the
   demonstrated probe.
4. **Fast/slow test discipline.** Iterate on task-scoped test files
   (seconds). Run the full `tests/p3_v3` suite only at task freeze points and
   only in a clean worktree (~6 min), never in the 1.4 GB-untracked main
   checkout (39 min). Receipt runs must execute **outside syscall sandboxes**:
   under the Cursor shell sandbox the preflight/capability probes fail
   spuriously (observed 2026-08-12: 158 failed + 57 errors sandboxed vs 849
   passed unsandboxed at the same commit).
5. **Scientific ceiling unchanged.** RQ1–RQ4 and all C1–C8 claims remain
   `blocked` until the Phase 8 evidence gate. No network, P12 access, push,
   PR, merge, or Cursor VM launch without a separate explicit user
   authorization.
6. **§18 deferral rule is binding.** Minimum-foundation blockers 2
   (`verify-mr-inventory` semantics), 3 (claim-evidence / RQ4 `P12_PAIRED`
   validators), and 4 (synthetic Phase 0→7 commitment-opening path) belong to
   later deliverables (Phases 4/7/8) and are **out of scope** until the
   controlled-experiment deliverable demonstrates its end-to-end path.

---

### Task 1: Real Phase 0 — author and freeze the canonical scientific protocol

**Files:**
- Create: `data/p3_v3/protocol/` artifact set (canonical JSON; exact file
  layout fixed by the task-scoped implementation plan after reading the
  `validate-protocol` schema in `scripts/p3_v3/evidence.py`)
- No production-module changes expected; `validate-protocol` is consumed
  as frozen.

**Interfaces:**
- Consumes: scientific plan §3 (RQs), §4 (claims/ceilings), §5.2–§5.5
  (strata, cohorts), §6 (semantic-mutant population, budgets), §7 (syntactic
  baseline), §8 (MR inventory rules), §10 (metrics), §11 (analysis rules),
  §13.4 (retry policy), §14 Phase 0 inventory: operator catalogue, exact
  `B_S=10`/`B_M=15`/`B_L=20` profiling budgets, category-balanced technique
  interval scoring, exact 30-ordinal `E_COMMON` and five-per-slot
  `E_CONTRACT` construction rules, input-generator registry/schema
  assignment, P12 missingness estimand, environment lock.
- Produces: one frozen protocol artifact set whose
  `validate-protocol --protocol <file>` run exits 0, plus its SHA-256
  receipt recorded in the task report.

**Acceptance criteria (frozen for review):**
1. Every §14 Phase 0 inventory item above is present and machine-readable;
   the exit criterion is the plan's own: "all outcome-dependent choices are
   explicit and machine-readable".
2. All numeric budgets match the scientific plan verbatim (B_S/B_M/B_L,
   30 `E_COMMON` ordinals, 5 `E_CONTRACT` per slot, confirmatory floors).
3. `validate-protocol` exits 0 on the artifact set; full `tests/p3_v3`
   suite still passes at the task freeze point (clean worktree).
4. No claim status changes; no new production module.

- [x] Write task-scoped implementation plan (`writing-plans`) —
  `docs/superpowers/plans/2026-08-12-p3-phase0-protocol-freeze.md`
- [x] Execute with review checkpoint at plan level and at GREEN (user
  pre-authorized plan+execute on 2026-08-12; validate-protocol PASS,
  protocol_sha256 `6fbbf13bc900ff3c3a2d77f33321c4d693c34a5ea5cafb90a3cd84059c6ce787`)
- [x] Record protocol SHA-256 set in the task report and commit —
  `docs/review_20260812/phase0_protocol_freeze_task_report.md`

### Task 2: Blocker 1 — source-derived feature rule engine for real records

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py` (feature-record derivation seams)
- Test: `tests/p3_v3/test_bridge_and_frames.py` (+ fixtures under
  `tests/p3_v3/fixtures/`)

**Interfaces:**
- Consumes: Task 1 frozen protocol (budgets, scoring, applicability
  predicate definitions).
- Produces: deterministic derivation of public-workload, scale-stratum,
  technique, and applicability feature records from source bytes, replacing
  declared-only records, so real Phase 1/2 feature records become
  authoritative (closes minimum-foundation blocker 1 — the only blocker on
  the Phase 1/2 critical path).

**Acceptance criteria (frozen for review):**
1. Feature records for the synthetic fixtures are derived from source, not
   caller declarations; shuffled-input byte-identical regeneration holds.
2. Applicability yields the frozen terminal split (`NOT_APPLICABLE` only via
   the static semantic predicate; unobserved dynamic sites stay
   `UNPROFILED`).
3. Existing 849-test suite remains green; new tests cover each rule class
   (not each example) per Global Constraint 3.
4. No verifier, lock, package, or run-records schema change.

- [x] Write task-scoped implementation plan (`writing-plans`) —
  `docs/superpowers/plans/2026-08-12-p3-task2-real-feature-rule-engine.md`
- [x] Execute with review checkpoint; two-repair-round cap applies (one
  repair round used: fixture-tree pytest collection guard)
- [x] Freeze-point full suite run in clean worktree; commit —
  `868 passed in 381.36s`, exit 0, unsandboxed, at `4ecefc57`;
  commits `47935727` + `4ecefc57`; report
  `docs/review_20260812/task2_rule_engine_task_report.md`

### Task 3: Phase 1 intake — P12 custodian bridge (user gate)

**Files:**
- Create: `docs/superpowers/plans/<DATE>-p3-phase1-bridge-intake.md`
  (checklist + verification runbook; produced only after the user schedules
  custodian delivery)

**Interfaces:**
- Consumes: custodian-delivered pinned release identity, P12 package root,
  complete bridge, eligible count, and salted fixed-tree commitments
  (scientific plan §5.1.1, §14 Phase 1).
- Produces: `verify-bridge --repo-root <root> --lock <lock>` PASS receipt and
  frozen Phase 1 frames via `build-frames`, closing Phase 1's exit criterion
  (byte-identical regeneration from shuffled inputs; no dynamic result,
  contract, mutant, MR, or real-fault outcome read).

**Checkpoint:** requires the user to (a) authorize custodian engagement and
(b) supply the bridge materials. This task cannot start autonomously.

- [x] User authorizes Phase 1 intake and supplies bridge materials
  (2026-08-13: approved delivery sequence executed; bridge intake receipts
  in `2026-08-12-p3-phase1-bridge-intake.md` §6)
- [x] Verify bridge, derive frames, close Phase 1 with receipts
  (verify-bridge PASS 2026-08-13, `aba70e89b603…`; adapters real since
  Task 4 GREEN at `b5e1645c`; frames frozen 2026-08-14/15 at `54a72576`
  after CA-01/CA-02. Actual funnel 3/9/23, not the planned 3/5/27.
  Final review PASS archived at
  `docs/review_20260815/phase1_sol_high_final_review.md`
  (file SHA-256
  `95345c4229e8e3dedd21e3f7da022fc5daeceb1018392dc1d0e3e35b00fa5a7d`).
  Status: `PHASE1_CLOSED`. Claims stay `blocked`.)

### Sequencing note

Task 1 and Task 2 are independent and may proceed in parallel worktrees;
Task 3 blocks on the user. Phase 2 (preflight, pilot, profiling) and Phase 3
(semantic-mutant construction via the frozen proposer protocol, Cursor VM,
separate authorization) follow under the scientific plan once Tasks 1–3
close. Each subsequent phase gets its own task-scoped plan; none may add
infrastructure beyond what its phase's exit criterion names.

## Non-goals (binding)

- No Authority Lock round-6, no F2/F3 patches, no threat-model expansion.
- No minimum-foundation blockers 2–4 work.
- No generic schema algebra, claim-state framework, orchestration layer,
  launch-packet self-hashing (scientific plan §18 deferred list).
- No manuscript results, no claim upgrades, no P12 reveal.

## Decision ledger

- 2026-08-12: Charter created under Exit (b). Authority Lock frozen at
  `bdf6a7cb`; freeze receipt 849/849. Next action: Task 1 implementation
  plan (local, no additional authorization needed), unless the user
  reprioritizes.
- 2026-08-12 (later): Task 1 executed GREEN. Protocol V1 frozen,
  `protocol_sha256 6fbbf13bc900ff3c3a2d77f33321c4d693c34a5ea5cafb90a3cd84059c6ce787`;
  validate-protocol PASS; determinism check passed; freeze-point suite
  `849 passed in 332.32s` (clean worktree, unsandboxed). Registries are
  declared-empty V1 pending Task 2 real implementations (protocol V2
  re-emit). Next action: Task 2 implementation plan.
- 2026-08-12 (night): Task 3 intake instructions delivered. Custodian helper
  `scripts/p3_v3/build_p12_bridge.py` (frozen-formula hashes, fresh nonces,
  sealed reveal ledger) and runbook
  `docs/superpowers/plans/2026-08-12-p3-phase1-bridge-intake.md` added;
  end-to-end smoke: build → commit → lock → verify-bridge PASS. Awaiting
  custodian materials (contract decision, eligible inventory, archives,
  descriptors, consumer lock).
- 2026-08-12 (later still): Task 2 executed GREEN (blocker 1 closed).
  E_COMMON ordinals fixed to the preregistered 0..29 derivation; real
  PYTHON_PEP517_V1 adapter + three fail-closed placeholder adapters + five
  real E_COMMON generators landed as hash-bound registry implementations;
  registries populated and protocol V2 re-emitted
  (`f0bbd6334e161fd165e560b3e67809da354f256592a993a08d83436bb85ec64a`,
  validate-protocol PASS). Freeze-point suite `868 passed in 381.36s`
  (clean worktree at `4ecefc57`, unsandboxed). Next action: Task 3 (P12
  custodian bridge intake) — blocked on user authorization and materials.
- 2026-08-13: Task 3 bridge intake executed GREEN under the user-approved
  delivery sequence. Custodian side: 8 fixed identities corrected by the
  per-record evidence audit (squash-merge PR heads → landed mainline
  commits; `PIN_CONFLICT 0` after); `P12-BRIDGE-SNAPSHOT-RULE-v2` frozen
  (ls-tree regular-file construction + frozen-formula transient exclusion +
  deterministic PAX tar; 25/35 trees affected; pilot regression
  byte-identical). P12 release commit
  `d57fa8119e47baf88c5bcff2d67346864cf3672d` (tag `p3-bridge-v1`): 35-record
  blinded bridge + ADOPTED consumer contract v2.0.0 + release package
  (root `cf2803d5…`). P3 acceptance: verify-bridge PASS
  (`aba70e89b603…`); neutral-named archives/descriptors 35/35 hash-matched;
  protocol V3 re-emitted binding contract v2.0.0
  (`4c25da539017…`, validate-protocol PASS) — contract §11 freeze complete.
  Package C sealed custodian-side. Next action: real cmake/meson/autotools
  adapters (task-scoped plan), then Phase 1 frame derivation.
- 2026-08-13 (freeze receipt): full suite `868 passed in 364.65s` in the
  clean worktree `.worktrees/p3-v3-bridge-intake-freeze` at `940909f3`,
  unsandboxed; worktree removed after the run. Intake commits: `eb51036f`
  (bridge acceptance + delivery), `940909f3` (protocol V3 re-emit).
- 2026-08-13 (night): Task 4 executed GREEN under standing user
  authorization — real cmake/meson/autotools discovery adapters
  (plan `2026-08-13-p3-task4-real-build-adapters.md`, subagent-driven:
  gpt-5.6-sol-high implementers, claude-fable-5-thinking-max reviewers,
  fix rounds within cap, plan amendments rounds 1-2 recorded). Scale
  engine gained fortran/cuda; shared block v1.1 fixed masking/site/
  decodability defects lockstep with a pairwise drift guard. Protocol V4
  re-emitted (`240d8270d418…`, validate PASS). Blind smoke over the 28
  delivered subjects: 23 OK, 5 verbatim fail-closed receipts
  (`CMakeLists.txt is absent`; frozen hash-bound descriptors, honest ITT
  funnel entries). Freeze receipt `893 passed in 361.79s` (clean worktree
  at `b5e1645c`, unsandboxed). Commits `3745c66d..b5e1645c`; report
  `docs/review_20260813/task4_adapters_task_report.md`. Next action:
  Phase 1 frame derivation task-scoped plan (charter Task 3 second
  checkbox).
- 2026-08-14/15: Phase 1 frames derived under CA-01/CA-02. Original
  90 MiB gate correctly stopped the driver after production pass 1
  (`E_ARTIFACT_SIZE`; `subject-frames.json` = 101,778,506 bytes;
  schema unchanged; raw JSON not stripped). Sol High CA-01 review
  PASS authorized the 128 MiB root-only exception and gzip transport.
  Shuffle pass 2 (no pass-1 rerun, no checkpoint substitute) exit 0,
  13,440.041 s, 281/281, all raw SHA-256 identical,
  `shuffle_byte_identical=true`. Actual funnel **3/9/23** (planned
  3/5/27 remains expectation only). Four extra Python fail-closed
  reasons kept verbatim (`pyproject.toml is absent` ×2; `pyproject
  [project].name is absent` ×2); not relabeled `EXECUTABLE`. Python
  coverage drop is a Phase 1 limitation. Git stores
  `subject-frames.json.gz` (`gzip -n -9`, Apple gzip 479); raw JSON
  remains local scientific identity
  `588ff83530c16ef2647b523c157bf5585320dae17754918364db8bd96c5e304b`.
  Freeze `934 passed in 564.00s` at `54a72576`. Protocol V4 unchanged.
  Claims stay `blocked`. Commits `693ae67f` (amendment), `54a72576`
  (frames).
- 2026-08-15 (Sol High final review): independent read-only verdict PASS
  archived at
  `docs/review_20260815/phase1_sol_high_final_review.md`
  (file SHA-256
  `95345c4229e8e3dedd21e3f7da022fc5daeceb1018392dc1d0e3e35b00fa5a7d`).
  Status: `PHASE1_CLOSED`; claims remain `blocked`; no Phase 2 execution
  is authorized.
