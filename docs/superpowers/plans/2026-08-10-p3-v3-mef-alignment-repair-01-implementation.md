# P3 v3 Minimum-Evidence Alignment Repair 01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the audited P3 v3 minimum-evidence foundation so that subject properties come only from pinned executable adapters, final verification reconstructs evidence from indexed bytes, retries and MR chronology are cryptographically bound, and the synthetic Phase 0 through Phase 7 path is portable, secret-safe, objective, and non-circular.

**Architecture:** Keep the existing five production modules and thin CLI. Deepen the current seams: `preflight.py` owns portable capability checks; `bridge_and_frames.py` executes pinned adapters and derives frames, scale, workloads, common inputs, technique profiles, and sites; `run_records.py` reconstructs attempts, retries, ledgers, and phase receipts; `packages.py` verifies materialized package bytes; `evidence.py` parses exact command schemas and delegates. A canonical evidence index names every required artifact, but PASS is obtained only by independently rebuilding the scientific bindings from source material and attempt records.

**Tech Stack:** Python 3.11 standard library, pytest, Ruff, Git subprocesses with `shell=False`, SHA-256, canonical JSON/JSONL, immutable attempt directories, POSIX durable writes.

## Global Constraints

- Task ID: `P3-V3-MEF-ALIGN-REPAIR-01`.
- Immutable repair base: `9f28080c8b3ed9e25f96a0fcf0444bc92715ca76`.
- Governing scientific-plan SHA-256: `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`.
- Governing evidence-design SHA-256: `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`.
- Parent implementation-plan SHA-256: `7c55ab41327395b819571da3931f142e916ac9d96910fec10b7d3cdd6e6c4ab3`.
- Repair design: `docs/superpowers/specs/2026-08-10-p3-v3-mef-alignment-repair-01-design.md`, SHA-256 `bd7f7f26cbc70fc81a797753507d5f4a2528064827cbd90989789c3afd7ede55`.
- Repair branch: `codex/p3-v3-mef-align-repair-01`.
- Production remains limited to `src/p3_v3/artifacts.py`, `bridge_and_frames.py`, `packages.py`, `preflight.py`, `run_records.py`, and the thin dispatcher `scripts/p3_v3/evidence.py`.
- Do not add a workflow framework, generic schema engine, YAML authority, interactive controller, or sixth production module.
- Every behavior change follows RED -> GREEN -> focused regression -> commit.
- Local Desktop shell commands use `rtk`. Cursor VM commands do not use `rtk`.
- Development failures may be diagnosed and rerun. They are not scientific jobs and do not consume experiment authorization.
- This plan authorizes code, synthetic fixtures, tests, and audit documentation only. It does not authorize network access, P12 reveal, real semantic-mutant construction, real MR execution, scientific jobs, manuscript results, PR creation, or merge.
- RQ1-RQ4 remain `blocked` after completion. Repair completion means only that the minimum-evidence machinery is ready for a separately authorized dry run.
- Preserve user changes outside the files named by a task.

## Frozen schemas

Every indexed file reference has exact keys `path` and `sha256`. Paths are safe, relative, unique, and resolve below the declared root. SHA-256 values are recomputed from bytes.

The adapter function is exact:

~~~python
def discover(
    source_root: Path,
    build_descriptor: Mapping[str, Any],
) -> Mapping[str, Any]:
    ...
~~~

Its result has exactly:

~~~python
{
    "adapter_id",
    "ecosystem",
    "source_files",
    "declarations",
    "public_schemas",
    "sites",
}
~~~

A subject-specification row has exactly:

~~~python
{
    "neutral_snapshot_id",
    "source_root",
    "source_record",
    "build_descriptor",
    "adapter_registry",
    "input_generator_registry",
    "profiling_results",
}
~~~

The evidence index has exactly:

~~~python
{
    "schema_version",
    "phase_coverage",
    "protocol",
    "adapter_registries",
    "input_generator_registries",
    "subjects",
    "packages",
    "mr_chain",
    "job_root",
    "ledger",
    "phase_receipts",
    "p12",
    "claims",
    "artifact_sha256",
}
~~~

`schema_version` is `P3_V3_EVIDENCE_INDEX_V1`. `phase_coverage` is a sorted unique list from `PHASE_0` through `PHASE_7`. Collections required by a listed phase are nonempty. The index self-hash identifies the index only; it never proves referenced artifacts.

---

### Task 1: Restore portable, secret-safe preflight and the quality gate

**Files:**
- Modify: `src/p3_v3/preflight.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_preflight.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Add `_parse_darwin_vm_stat(raw: bytes) -> int`.
- Change `_available_memory_bytes(executor=subprocess.run) -> int | None`.
- Preflight receipt exposes `repository_identity`, `origin_transport`, and `origin_sha256`, never raw origin.

- [ ] **Write RED tests.** Freeze a `vm_stat` fixture with page size and the free, inactive, speculative, and purgeable page classes. Assert the result equals page size multiplied by their sum. Cover malformed page size, missing class, duplicate class, noninteger value, nonzero process status, timeout, and invalid bytes; these return `None` and keep positive minimum-memory checks fail-closed.

- [ ] **Add the secret mutation.** Use origin `https://audit-user:TOP_SECRET_TOKEN@github.com/meng004/P3-Semantic-Mutation.git`. Require identity `github.com/meng004/P3-Semantic-Mutation`, transport `HTTPS`, and SHA-256 of the exact raw origin. Assert receipt bytes, errors, and stdout contain neither user nor token.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_preflight.py tests/p3_v3/test_cli.py -q
~~~

Expected: Darwin positive-memory and secret-absence tests fail.

- [ ] **Implement minimal GREEN.** Prefer positive POSIX `SC_PAGE_SIZE * SC_AVPHYS_PAGES`. On Darwin run exact argv `["vm_stat"]` with `shell=False`, captured streams, no check, and five-second timeout. Parse ASCII strictly, require all four page classes exactly once, and return a positive byte count. Normalize SSH/HTTPS identity in memory; persist only normalized identity, transport, and raw-value hash. Restore intentional `# noqa: E402` comments after the CLI path bootstrap and delete duplicate dictionary keys.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_preflight.py tests/p3_v3/test_cli.py -q
rtk python3.11 -m ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git add src/p3_v3/preflight.py scripts/p3_v3/evidence.py tests/p3_v3/test_preflight.py tests/p3_v3/test_cli.py
rtk git commit -m "fix(p3-v3): make preflight portable and secret-safe"
~~~

### Task 2: Execute pinned adapters and derive public behavior and scale

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`
- Create: `tests/p3_v3/fixtures/adapters/python_pep517_v1.py`
- Create: `tests/p3_v3/fixtures/adapters/cmake_ctest_v1.py`
- Modify: `tests/p3_v3/fixtures/public_behavior/python.json`
- Modify: `tests/p3_v3/fixtures/public_behavior/cmake.json`
- Modify: `tests/p3_v3/fixtures/public_behavior/unsupported.json`

**Interfaces:**
- Change `validate_adapter_registry(registry, implementation_root) -> dict[str, Any]`.
- Add `run_adapter_discovery(source_root, build_descriptor, registry, adapter_id) -> dict[str, Any]`.
- Add `derive_source_scale(source_root, discovery) -> dict[str, Any]`.
- Change `build_public_behavior_frame(source_record, discovery) -> dict[str, Any]`.

- [ ] **Write adapter RED tests.** Create Python and CMake synthetic projects with different public declarations, schemas, source files, and syntax-aware sites. Register fixture modules by exact path and SHA-256. Prove that only the verified module executes. Reject changed implementation bytes, unregistered modules, wrong adapter ID, missing/extra result keys, unsafe or duplicate source paths, and caller-supplied discoveries. Shuffled lists must yield byte-identical normalized artifacts. Unsupported technology yields `ADAPTER_UNSUPPORTED` with no manual fallback.

- [ ] **Write scale RED tests.** Exercise 9,999 -> S, 10,000 -> M, 99,999 -> M, and 100,000 -> L effective lines. Count nonblank, noncomment lines under frozen adapter comment rules. Reject vendored, generated, VCS, environment, build-output, and fixture paths. Assert no API accepts a caller scale class.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py -q -k "adapter or discovery or scale or public_schema"
~~~

Expected: executable discovery and scale interfaces are absent; the old declaration path remains.

- [ ] **Implement minimal GREEN.** Resolve implementation files below the verified root, hash before import, use a unique internal module name, validate the exact signature/result, and normalize every collection before hashing. Reopen only validated source files for scale. Emit sorted per-file counts, total, derived class, adapter identity, discovery SHA-256, and self-hash. Build the public frame from discovery only and preserve `public_schemas`.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py -q -k "adapter or discovery or scale or public_schema"
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/fixtures/adapters tests/p3_v3/fixtures/public_behavior
rtk git commit -m "fix(p3-v3): derive public frames from pinned adapters"
~~~

### Task 3: Remove caller-controlled subject authority and repair profiling fallback

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `tests/p3_v3/test_synthetic_phase_path.py`

**Interfaces:**
- Add `derive_subject_material(subject_spec, bridge_record) -> dict[str, Any]`.
- Change `build_subject_frames(bridge, derived_subjects, construct_limit) -> dict[str, Any]`.
- Change CLI `build-frames` to require `--subject-specs` and remove `--declarations`, `--features`, and `--scale-class`.

- [ ] **Write CLI authority RED tests.** Require the new option and reject every removed option before output creation. Require exactly one exact-schema subject row per bridge neutral ID; reject missing, duplicate, or extra rows before adapter execution.

- [ ] **Write two-subject RED tests.** Use Python/S and CMake/M subjects. Require distinct discovery, scale, frame, workload, common-input, technique-profile, and site hashes. Reversing subject-spec rows must not change aggregate bytes.

- [ ] **Write executable common-input RED tests.** Feed adapter `public_schemas` through the pinned generator registry. Require exactly 30 predetermined rows per supported subject, ordinals 1 through 30, schema/generator provenance, deterministic seeds/hashes, and at least one `EXECUTABLE` row. Unsupported subjects remain explicitly unavailable.

- [ ] **Write profiling fallback RED test.** Make tuple ordering select `behavior-z` but behavior-ID ordering select `behavior-a`. Exhaust unseen diversity and require `behavior-a` next.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py -q -k "subject_spec or caller_authority or common_input or fallback or two_subject"
~~~

Expected: removed options still work, common inputs are unavailable, or fallback selects the wrong row.

- [ ] **Implement the only subject flow.**

~~~text
verified source/build
-> pinned adapter discovery
-> discovery receipt
-> public frame with schemas
-> derived scale
-> outcome-blind profiling workload
-> 30 predetermined common inputs
-> profiling results bound to workload
-> failure-conservative technique profile
-> derived canonical sites
-> derived subject record
~~~

The caller supplies none of declarations, scale, workload SHA, sites, or technique labels. Correct fallback: initial category pass uses lowest diversity/behavior tuple; later unseen rounds prefer lowest diversity; after unseen signatures are exhausted use lowest remaining behavior ID only.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py -q -k "subject_spec or caller_authority or common_input or fallback or two_subject"
rtk git add src/p3_v3/bridge_and_frames.py scripts/p3_v3/evidence.py tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py
rtk git commit -m "fix(p3-v3): derive subject strata and sites"
~~~

### Task 4: Bind retry identity and MR chronology

**Files:**
- Modify: `src/p3_v3/run_records.py`
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_run_records.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Add `retry_invariant(intent) -> dict[str, Any]`.
- Change `reduce_attempts` to compare canonical retry invariants.
- Change `validate_mr_inventory(candidate, receipt, final_inventory, portfolios)`.

- [ ] **Write retry RED tests.** After attempt 1 ends `FAIL_INFRASTRUCTURE`, mutate one of job ID, protocol, phase, argv, cwd, environment, input hashes, seed, timeout, object/MR/input/repetition/environment identity, or job role. Every mutation fails. Only `attempt` may change, and a fourth total attempt fails.

- [ ] **Write MR-chain RED tests.** Use exact artifact types candidate frame -> custodian receipt -> final inventory -> portfolios. Each child binds its parent's canonical SHA-256. Mutate each type, parent, self-hash, receipt state, inventory reference, or portfolio reference. A literal chronology list with four unrelated hashes fails.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_bridge_and_frames.py -q -k "retry or mr_chain or chronology"
~~~

- [ ] **Implement minimal GREEN.** Validate the exact intent schema, remove only `attempt`, and compare canonical bytes. Permit a retry only after `FAIL_INFRASTRUCTURE`. Validate all four MR artifacts, fail-closed receipt, exact parent links, uniqueness, and portfolio membership.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_bridge_and_frames.py -q -k "retry or mr_chain or chronology"
rtk git add src/p3_v3/run_records.py src/p3_v3/bridge_and_frames.py tests/p3_v3/test_run_records.py tests/p3_v3/test_bridge_and_frames.py
rtk git commit -m "fix(p3-v3): bind retries and mr chronology"
~~~

### Task 5: Reconstruct complete evidence sets from one index

**Files:**
- Modify: `src/p3_v3/run_records.py`
- Modify: `src/p3_v3/packages.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_run_records.py`
- Modify: `tests/p3_v3/test_packages.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Add `reconstruct_attempt_events(job_root: Path) -> list[dict[str, Any]]`.
- Add `verify_attempt_tree(job_root, ledger) -> list[dict[str, Any]]`.
- Add `verify_phase_receipt(receipt, events, expected_jobs, output_manifest) -> None`.
- Add `verify_materialized_package(package_root, manifest) -> dict[str, Any]`.
- Make `verify-evidence --index PATH` the sole final-verifier input.

- [ ] **Preserve the published forgery as RED.** Index zero manifests, zero receipts, zero slots, 30 rows containing only `{"status":"FABRICATED"}`, a fabricated self-hashed summary, and minimal blocked claims. Require nonzero exit and no PASS receipt.

- [ ] **Write index RED tests.** Reject extra/missing keys, unsafe or duplicate paths, hash mismatch, unknown phase, noncanonical bytes, empty collections required by phase coverage, and unindexed files.

- [ ] **Write attempt/receipt RED tests.** Reconstruct events ordered by phase, job ID, attempt, and ordinal. Require byte equality to ledger. Reject missing/extra attempt, gap, altered event, reordered ledger, or drifted intent. Recompute receipt ledger prefix, expected jobs, output manifest, terminal counts, and phase status.

- [ ] **Write package/common/slot RED tests.** Compare each package manifest to exact materialized path, mode, size, and bytes. Reject extras, omissions, changes, symlinks, and unsafe paths. Validate exact common-input rows, ordinals, subject/workload/generator/schema identities, seeds, hashes, validity receipts, and pre-consumer chronology. Validate slot coordinate and A/B input-role separation.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_packages.py tests/p3_v3/test_cli.py -q -k "evidence_index or forged or reconstruct or phase_receipt or materialized_package or common_input or slot"
~~~

Expected: the shallow verifier accepts forgery or new reconstruction APIs are absent.

- [ ] **Implement minimal GREEN.** Parse exact canonical index bytes, verify each referenced file first, and delegate schemas to production modules. Enumerate only the frozen attempt grammar and reject unknown files/gaps. Rebuild the event stream and byte-compare the ledger. Recompute each receipt. Walk materialized packages without following symlinks. Require all phase-implied collections nonempty.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_packages.py tests/p3_v3/test_cli.py -q -k "evidence_index or forged or reconstruct or phase_receipt or materialized_package or common_input or slot"
rtk git add src/p3_v3/run_records.py src/p3_v3/packages.py scripts/p3_v3/evidence.py tests/p3_v3/test_run_records.py tests/p3_v3/test_packages.py tests/p3_v3/test_cli.py
rtk git commit -m "fix(p3-v3): reconstruct complete evidence sets"
~~~

### Task 6: Rebuild subjects, P12 summary, and claims in final verification

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `src/p3_v3/run_records.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`
- Modify: `tests/p3_v3/test_run_records.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Add `rebuild_indexed_subject(subject_index, bridge_record) -> dict[str, Any]`.
- Add `recompute_p12_summary(denominator, terminal_results) -> dict[str, Any]`.
- Add `validate_claim_ledger(claims) -> dict[str, Any]`.

- [ ] **Write subject-rederivation RED tests.** Index source/build, registries, frame, scale, workload/results, common inputs, technique profile, and sites. Final verification reruns the adapter and every deterministic derivation. Mutate and rehash declaration, scale, workload, site, technique label, schema, source byte, or adapter byte; all fail.

- [ ] **Write P12-summary RED tests.** Match Phase 7 terminal results from the reconstructed attempt tree one-to-one to the frozen denominator. Recompute all five outcome counts, intention-to-evaluate lower bound, upper bound, complete-case estimate/denominator, and missingness. Reject omitted/extra/duplicate identities, altered outcome, declared-only results, or a fabricated rehashed summary.

- [ ] **Write claims RED tests.** Exact claim schema binds claim ID, RQ, indexed evidence references, status, and self-hash. Require all claims `blocked`. Reject extra/missing claims, unindexed evidence, `ready`, `supported`, or result prose. Verify protocol registry/policy hashes against indexed bytes.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q -k "rederive or p12_summary or denominator or claim_ledger or protocol_binding"
~~~

- [ ] **Implement minimal GREEN.** Start every subject verification from indexed source/build and verified registries, regenerate each deterministic artifact, and compare canonical bytes. Read P12 outcomes only from reconstructed terminal events. Validate exact claims and keep all blocked. PASS output reports index hash and verified counts, not a scientific claim.

- [ ] **Verify and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q -k "rederive or p12_summary or denominator or claim_ledger or protocol_binding"
rtk git add src/p3_v3/bridge_and_frames.py src/p3_v3/run_records.py scripts/p3_v3/evidence.py tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py
rtk git commit -m "fix(p3-v3): rebuild p12 evidence from results"
~~~

### Task 7: Close the two-subject synthetic Phase 0 through Phase 7 path

**Files:**
- Modify: `tests/p3_v3/test_synthetic_phase_path.py`
- Modify: `tests/p3_v3/test_artifacts.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `docs/release_2026-08-10/p3_v3_mef_align_evidence_map.md`

- [ ] **Replace the old path with production-driven RED.** Use two subjects, Python PEP 517 and CMake/CTest, and derived S and M classes. Execute pinned synthetic adapters and produce at least one executable common input each. Materialize Phase 0 through Phase 7 attempts, ledger, receipts, package roots, slots, MR chain, P12 denominator/results/summary, claims, and index through production APIs and CLI.

- [ ] **Add a rehash-resistant mutation matrix.** Mutate adapter byte/output, source scale, schema, workload, common input, fallback order, technique label, site, retry argv/seed, event, ledger, receipt, package byte, slot coordinate, MR parent, denominator, P12 result/summary, claim status, index membership, and origin receipt. Recompute local self-hashes; final verification must still fail.

- [ ] **Run RED.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_synthetic_phase_path.py -q
~~~

Expected: the prior one-subject/shallow path cannot meet the indexed two-subject contract.

- [ ] **Implement GREEN.** Keep socket blocking active. Use no real P12, mutant, MR, or scientific job. Require exact completion metadata: claims blocked, no real P12 access, zero real scientific jobs, two subjects, two ecosystems, and scale classes M/S.

- [ ] **Rewrite the evidence map.** Each design requirement cites an enforcing production function, a positive test, a mutation test, and the end-to-end boundary when relevant. Remove old `25/25` and `20/20` claims unless recomputed row by row. State that the map proves infrastructure semantics only.

- [ ] **Run complete acceptance and commit.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3 -q
rtk env PYTHONPATH=src python3.11 -m pytest -q
rtk python3.11 -m ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git diff --check 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76
rtk git status --short
rtk git add tests/p3_v3/test_synthetic_phase_path.py tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py docs/release_2026-08-10/p3_v3_mef_align_evidence_map.md
rtk git commit -m "test(p3-v3): close repair evidence matrix"
~~~

### Task 8: Freeze, independently review, and hand off

- [ ] **Verify identity and scope.**

~~~bash
rtk git rev-parse HEAD
rtk git status --porcelain=v1
rtk git diff --name-only 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76..HEAD
rtk git log --oneline --reverse 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76..HEAD
~~~

Only planned production, fixtures, tests, design/plan, and evidence-map paths may differ.

- [ ] **Repeat acceptance from the fixed candidate.**

~~~bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3 -q
rtk env PYTHONPATH=src python3.11 -m pytest -q
rtk python3.11 -m ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git diff --check 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76
rtk git status --porcelain=v1
~~~

Record exact counts, durations, Python version, commit, tree, and clean status. Do not reuse the former Cursor `129/609` counts.

- [ ] **Run two independent read-only reviews.** Review A checks scientific specification and non-circular authority. Review B checks operational reachability, portability, secrets, evidence reconstruction, and standards. Both lock commit, tree, design SHA, plan SHA, and clean status. Neither inherits the other's conclusion.

- [ ] **If either review finds an issue, return to RED.** Add a focused negative test, repair, rerun all acceptance, freeze a new identity, and restart both reviews. Do not call a blocked candidate complete.

- [ ] **After dual PASS, produce this handoff schema.**

~~~text
P3_V3_MEF_ALIGN_REPAIR_01_COMPLETE
task_id: P3-V3-MEF-ALIGN-REPAIR-01
base_commit: 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76
repair_branch: codex/p3-v3-mef-align-repair-01
final_commit: exact 40-hex commit
final_tree: exact 40-hex tree
focused_tests: exact observed result
repository_tests: exact observed result
ruff: PASS
diff_check: PASS
worktree_clean: true
independent_spec_audit: PASS with audit SHA-256
independent_operational_audit: PASS with audit SHA-256
claims_status: blocked
real_p12_access: false
real_scientific_jobs: 0
~~~

Do not push, create a PR, merge, access P12, or start a Cursor scientific VM without separate user authorization.

## Completion Boundary

Completion establishes only that a later, separately authorized experiment can create auditable evidence without caller-supplied subject properties, fabricated-summary acceptance, retry drift, chronology self-certification, platform-specific bootstrap failure, or credential persistence. It establishes no P3 scientific result and does not unblock RQ1-RQ4.
