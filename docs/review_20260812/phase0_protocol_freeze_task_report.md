# Task Report — Real Phase 0 Protocol Freeze (Charter Task 1)

- Date: 2026-08-12
- Charter: `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` (Task 1)
- Implementation plan: `docs/superpowers/plans/2026-08-12-p3-phase0-protocol-freeze.md`
- Checkpoint note: the user pre-authorized "write the task plan and execute"
  on 2026-08-12, waiving the plan-level pause; all gates below were still run.
- Verdict: **GREEN — all frozen acceptance criteria met**
- Claims: all remain `blocked`. No scientific result, no P12 access, no
  network, no VM, no production/test byte changed.

## 1. Protocol identity

- `protocol.json` SHA-256 (= `validate-protocol` receipt):
  **`6fbbf13bc900ff3c3a2d77f33321c4d693c34a5ea5cafb90a3cd84059c6ce787`**
- CLI output: `{"protocol_sha256":"6fbbf13b…c6ce787","status":"PASS"}`, exit 0
  (`PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py
  validate-protocol --protocol data/p3_v3/protocol/protocol.json`)
- Authority equalities embedded and verified by the frozen validator:
  scientific plan `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`,
  evidence design `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`.

## 2. Artifact receipt table (SHA-256, builder output)

```text
0d7d67d14a4eb532f52b401f71491739a60f9399f65d12384b2dc60c0de35a88  data/p3_v3/protocol/adapter_registry.json
4c6ebb1702c191d8bf2f1c85501798e01ce9fd00311e0542b67056aa24cdada4  data/p3_v3/protocol/analysis_spec.md
1f46b7cd97e6ddf6d65f6c52a552f4e4b6680a987a088d4f5a65ebc19bf017ed  data/p3_v3/protocol/claim_ceiling_authority.json
7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f  data/p3_v3/protocol/environment_lock.json
0d03dc4c36bab04181420dd5c0ac8d4179e177d669d6b05c3582748e69b5d929  data/p3_v3/protocol/environments/construction_a.json
3095c4ebb935046bf049363c7112443023f36bd95cc1ae671401ea4d53619c3b  data/p3_v3/protocol/environments/controlled_b.json
83a1c4c83511b8ee63f6290a8bc058598833e9f1a0b4b61a6e22e17d8e55ceb2  data/p3_v3/protocol/environments/real_holdout_c.json
0100f3de340754b94561e0535df09b58fc9b02032738e0e4015e1ef0a19cd489  data/p3_v3/protocol/input_generator_registry.json
50ef365198279c4ea9fcfd8e627660f686cfa7c963eeb2ba21f16aba64d8021f  data/p3_v3/protocol/mr_policy.md
060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635  data/p3_v3/protocol/operator_catalogue.md
febddb20eb0ca2d35f816357a9996c254f4a7c6c1118da8435b106fe33276e6d  data/p3_v3/protocol/package_policy.md
6fbbf13bc900ff3c3a2d77f33321c4d693c34a5ea5cafb90a3cd84059c6ce787  data/p3_v3/protocol/protocol.json
9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7  data/p3_v3/protocol/site_policy.md
684ba68d21f6284375acf589069b7a9a611cf352f117b8ebacc6ef3a0f79d0c6  research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md
6247f3063952fa7c133ca574b5f9667c51b8d4636d84c40bce2753cf9e8bc427  docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md
```

Builder: `scripts/p3_v3/build_phase0_protocol.py` (deterministic; asserts the
governing-plan pin before extracting; Ruff 0.15.12 `All checks passed!`).

## 3. Cross-check receipts (Task C)

- **C1 RQ parity:** frozen regex over RQ-spec v1.3.0 and the scientific plan
  both yield exactly `['RQ1','RQ2','RQ3','RQ4']`.
- **C2 claim parity:** `(claim_id, rqs)` projection of
  `claim_ceiling_authority.json` equals `_REQUIRED_CLAIM_ASSOCIATIONS` in
  `scripts/p3_v3/evidence.py` (`CLAIM_PARITY True`); all eight rows
  `initial_status: blocked`, consistent with
  `research/evidence/p3_claim_ledger_v1.3.0.yml`.
- **C3 budget verbatim:** plan L361 and L1154 carry `B_S=10`/`B_M=15`/`B_L=20`;
  protocol `profiling_budgets == {"S":10,"M":15,"L":20}`,
  `e_common_count == 30`, `e_contract_count == 5`,
  `infrastructure_retry_limit == 3` (all `True`).
- **C4 determinism:** two consecutive builder runs printed byte-identical
  receipts (`DETERMINISM_OK`).

## 4. Freeze-point suite receipt (Task D)

`849 passed in 332.32s (0:05:32)`, pytest exit 0 — clean worktree
`.worktrees/p3-v3-mef-align-repair-01` at `bdf6a7cb`, run **outside** the
shell sandbox (per charter Global Constraint 4), 2026-08-12. No production or
test byte was changed by this task.

## 5. Declared-open items (fail-visible, not hidden)

1. **Registries are empty V1.** `adapter_registry.json` and
   `input_generator_registry.json` are schema-valid with zero entries because
   no real adapter/input-generator implementation exists yet (only synthetic
   test fixtures). Charter Task 2 supplies real implementations, after which
   the builder re-emits protocol V2 and `validate-protocol` is rerun. No
   downstream consumer has bound protocol V1 yet, so re-emission is safe.
2. **P12-contract loading seam.** Protocol V1 binds the real frozen consumer
   contract `docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md`
   (the scientifically honest referent). The current freeze path
   (`freeze-authority-lock`) still parses the `p12_contract` artifact under
   the synthetic schema `P3_V3_P12_CONTRACT_V1`; the real-freeze
   implementation (Phase 2 execution scope) must load the real contract or a
   machine-readable companion bound to it.
3. **`job_derivation_policy` is lock-time scope.** It is required by the
   Authority Inputs at freeze time, not by the Phase 0 protocol file; it will
   be authored with the real job lists (Phase 5/7 scope).

## 6. Next step on the critical path

Charter Task 2: implement the source-derived public-workload / scale /
technique / applicability rule engine (minimum-foundation blocker 1), then
populate both registries and re-emit protocol V2. Charter Task 3 (P12
custodian bridge intake) remains gated on user authorization.
