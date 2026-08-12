# Task Report — Real Source-Derived Feature Rule Engine (Charter Task 2)

- Date: 2026-08-12
- Charter: `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` (Task 2)
- Implementation plan: `docs/superpowers/plans/2026-08-12-p3-task2-real-feature-rule-engine.md`
- Commits: `47935727` (feat: rule engine + registries + protocol V2),
  `4ecefc57` (test: fixture-tree collection guard)
- Verdict: **GREEN — all frozen acceptance criteria met**
- Claims: all remain `blocked`. No verifier/lock/schema key change, no P12
  access, no network, no VM.

## 1. What changed

1. **E_COMMON ordinal spec-fidelity fix (RED→GREEN).** The emission loops in
   `bridge_and_frames.build_common_inputs`, the fixed-source validator's
   ordinal check, and `packages.verify_common_input_evidence` re-derivation
   moved from the unpinned `1..30` convention to the preregistered `0..29`
   derivation (evidence design L459-461; scientific plan §5.2.2). Seeds now
   equal `SHA256(canonical_json({domain:"P3-E-COMMON-SEED-v1",
   controlled_subject_source_id, ordinal}))[:8]` for ordinals 0..29, and
   schema assignment is `eligible[ordinal % k]`. The `E_CONTRACT` side was
   already 0-based. Six test anchors and the packages ordinal mutation probe
   were flipped accordingly. No schema key or type changed.
2. **Real `PYTHON_PEP517_V1` adapter**
   (`src/p3_v3/adapters/python_pep517_v1.py`): source-derived discovery from
   snapshot bytes only (pyproject.toml via `tomllib`, modules via `ast`),
   implementing the frozen rule documented in its docstring: five behavior
   categories, `__all__`/underscore visibility, signature→schema mapping
   (numeric/text/binary/JSON/CLI; zero-param binds `{"kind": "NO_INPUT"}`),
   inlined excluded-path rule, path-evidenced EXAMPLE/BENCHMARK/PROJECT_TEST
   whose bodies are never parsed, and canonical function/method sites.
   The former fixture adapter's manifest pass-through pattern is now
   test-only; real subjects get derived records.
3. **Three fail-closed placeholder adapters** (`cmake_ctest_v1`,
   `meson_test_v1`, `autotools_makecheck_v1`): the frozen allowlist requires
   exactly four registered confirmatory adapters, so the unimplemented
   ecosystems are registered as stubs that raise on any invocation
   (`E_ADAPTER_EXECUTION`) rather than fabricating or passing through
   discovery.
4. **Five real E_COMMON generators**
   (`src/p3_v3/input_generators/*.py`): deterministic SHA-256 seed-stream
   construction of schema-conforming payloads with canonical envelopes and
   stable `<ID>_INVALID` failure codes.
5. **Registry V2 + protocol V2.** `build_phase0_protocol.py` now populates
   both registries from the real implementation files.
6. **Collection guard** (`tests/p3_v3/conftest.py`): the fixture repo
   legitimately contains `test_*.py` files (the PROJECT_TEST discovery rule
   needs them), so the fixtures subtree is excluded from pytest collection.
   This was the task's single repair round (cap: two).

## 2. Receipts

- Protocol V2: `validate-protocol` PASS,
  `protocol_sha256 f0bbd6334e161fd165e560b3e67809da354f256592a993a08d83436bb85ec64a`
  (supersedes V1 `6fbbf13b…c6ce787`; no downstream consumer had bound V1).
  Double-run determinism: `DETERMINISM_OK`.
- Registry hashes: adapter
  `9b241fa2827a739b857885cfb932032650df3084fd16931707459da0ede7be74`
  (4 rows), input-generator
  `0bddbed8cec85ae9df0ac6ea73eabb8248d77b1de80aa950b993c81b90958013`
  (5 rows); both pass their structure validators.
- New rule-class tests: 19 (adapter 7, generators 11, end-to-end 1),
  covering category completeness, `__all__`/privacy, schema-mapping classes,
  determinism, pyproject fail-closure, the test/example schema wall,
  canonical sites, generator determinism/conformance/failure codes, and the
  real pipeline to 30 executable common inputs with ordinals 0..29.
- Freeze-point suite: **`868 passed in 381.36s (0:06:21)`, pytest exit 0**
  (clean worktree at `4ecefc57`, outside the shell sandbox, 2026-08-12).
  Pre-commit unsandboxed spot run of the three fast files: `340 passed`.
- Ruff: `All checks passed!` on every created/modified file (0.15.12).

## 3. Ordinal-fix citation trail

- Scientific plan §5.2.2 (`fea00496…3830`): "generate exactly 30
  subject-level candidates with ordinals `0..29` … The seed is the first
  unsigned 64 bits of SHA256(canonical_json({domain: "P3-E-COMMON-SEED-v1",
  controlled_subject_source_id, ordinal}))".
- Evidence design (`7e614e96…2fa9`) L459-461: "Candidate ordinal `i` is
  `0..29`; its seed is the …".
- Both documents are byte-bound into protocol V1/V2, which made the 1-based
  implementation a preregistration-fidelity defect; it is fixed before any
  real input exists, so no recorded evidence is affected.

## 4. Declared-open items (fail-visible)

1. CMAKE/MESON/AUTOTOOLS discovery rules are not implemented; their
   ecosystems are registered fail-closed and stay unusable until a frozen
   discovery rule lands (needed only when non-Python subjects enter the
   study).
2. The five E_CONTRACT generators remain contract-phase scope (Phase 2 slot
   freeze), unchanged from the Task 1 report.
3. The real-freeze `p12_contract` loading seam (synthetic schema
   `P3_V3_P12_CONTRACT_V1`) is unchanged, as declared in the Task 1 report.

## 5. Next step on the critical path

Minimum-foundation blocker 1 is closed: real Phase 1/2 feature records are
now derived from source through hash-bound implementations. The next gate is
charter Task 3 — P12 custodian bridge intake — which requires user
authorization and custodian materials. Remaining local work before Phase 2
execution: the real-freeze p12_contract seam and the Phase 2 profiling
runner (both later-phase scope).
