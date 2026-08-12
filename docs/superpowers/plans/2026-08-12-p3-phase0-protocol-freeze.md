# P3 Real Phase 0 Protocol Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. This is Task 1 of
> `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
> (the Exit-(b) charter); its Global Constraints apply verbatim.

**Goal:** Author and freeze the real Phase 0 canonical protocol artifact set
under `data/p3_v3/protocol/`, binding the SHA-pinned governing documents so
that `validate-protocol` exits 0 and every §14 Phase 0 inventory item is
explicit and machine-readable.

**Architecture:** One deterministic builder script regenerates the complete
artifact set from three SHA-pinned sources (scientific plan, RQ-spec v1.3.0,
P12 consumer contract v1.1.2) plus frozen code constants. Prose authorities
are verbatim line-range extracts of the scientific plan with a passport
header; machine authorities are canonical JSON with self-hashes. The frozen
`validate-protocol` CLI is consumed as-is; no production module changes.

**Tech Stack:** Python 3.12 (`/opt/anaconda3/bin/python`, pytest 8.4.2),
stdlib only, existing `src/p3_v3` modules imported read-only for constants
and canonical serialization.

## Global Constraints

- Charter rails apply: no verifier/lock hardening; review scope = the
  acceptance list below; max two repair rounds; root-cause batching; full
  suite only at the freeze point, in a clean worktree, outside the shell
  sandbox.
- All claims remain `blocked`. This task records no scientific result and
  upgrades nothing. No network, P12 access, Cursor VM.
- Authority hash equalities (frozen in `scripts/p3_v3/evidence.py:76-81`):
  scientific plan `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`,
  evidence design `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`.
- Protocol constants must equal the frozen code values (validate-protocol
  enforces): budgets `{"S":10,"M":15,"L":20}`; categories
  `PUBLIC_API, CLI, EXAMPLE, BENCHMARK, PROJECT_TEST`; techniques
  `HYBRID_NATIVE, TENSOR_AUTODIFF, PROBABILISTIC_SURROGATE,
  ITERATIVE_STOCHASTIC, ARRAY_NUMERICAL, SCALAR_CONTROL, TECH_UNCERTAIN`;
  `e_common_count 30`; `e_contract_count 5`; five P12 outcome states;
  estimand `INTENTION_TO_EVALUATE_LOWER_BOUND`; retry limit `3`. These match
  the scientific plan §5.2.2/§5.3/§14 verbatim (checked in Task C).

## Frozen acceptance criteria (review judges only these)

1. `validate-protocol --protocol data/p3_v3/protocol/protocol.json` exits 0
   and returns `{"status": "PASS", ...}`.
2. Every §14 Phase 0 inventory item is bound: RQs + claims/ceilings
   (rq_spec + claim ceiling authority), operator catalogue, cohort/site
   rules, metrics + analysis rules, MR budgets/policy, retry rule, P12
   compatibility (v1.1.2 contract), behavior-frame discovery categories,
   profiling budgets, technique scoring order, E_COMMON=30 / E_CONTRACT=5,
   input-generator/adapter registries (declared-empty V1), missingness
   estimand, environment lock.
3. Builder reruns are byte-identical (determinism check passes).
4. Claim-ceiling rows equal `_REQUIRED_CLAIM_ASSOCIATIONS` and the RQ heading
   regex yields exactly RQ1–RQ4 on both the RQ-spec and the scientific plan.
5. Full `tests/p3_v3` suite passes at the freeze point (clean worktree,
   unsandboxed); no production/test byte changed.
6. Declared-open items are recorded in the task report, not hidden:
   (a) both registries are empty until charter Task 2 supplies real
   implementations, then the builder re-emits protocol V2; (b) the real
   freeze path currently parses `p12_contract` under the synthetic schema
   `P3_V3_P12_CONTRACT_V1`, so binding the real v1.1.2 contract Markdown is a
   declared seam for the later real-freeze implementation; (c) the
   `job_derivation_policy` artifact is lock-time scope, not Phase 0 scope.

## File Structure

- Create: `scripts/p3_v3/build_phase0_protocol.py` (builder, authoring aid)
- Create (generated): `data/p3_v3/protocol/protocol.json`,
  `claim_ceiling_authority.json`, `environment_lock.json`,
  `environments/{construction_a,controlled_b,real_holdout_c}.json`,
  `adapter_registry.json`, `input_generator_registry.json`,
  `operator_catalogue.md`, `mr_policy.md`, `site_policy.md`,
  `analysis_spec.md`, `package_policy.md`
- Create: `docs/review_20260812/phase0_protocol_freeze_task_report.md`
- Modify: charter Task 1 checkboxes + decision ledger
- No changes under `src/p3_v3/`, `scripts/p3_v3/evidence.py`, `tests/`

### Task A: Deterministic builder script

**Files:** Create `scripts/p3_v3/build_phase0_protocol.py`

**Interfaces:**
- Consumes: SHA-pinned plan bytes; `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md`;
  `docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md`;
  constants and `canonical_json_bytes`/`canonical_sha256` from `p3_v3`.
- Produces: the twelve artifacts above; prints `sha256  relative-path` receipt
  lines sorted by path; exit 0.

- [ ] **Step A1: Write the builder exactly as follows**

```python
"""Deterministic builder for the real P3 v3 Phase 0 protocol artifact set.

Regenerates every artifact under data/p3_v3/protocol/ from the SHA-pinned
governing scientific plan, the frozen RQ-spec and P12 consumer contract, and
the frozen p3_v3 code constants. Two consecutive runs must be byte-identical.
The builder performs no network access, records no scientific result, and
upgrades no claim.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from p3_v3 import bridge_and_frames as baf  # noqa: E402
from p3_v3.artifacts import canonical_json_bytes, canonical_sha256  # noqa: E402

PLAN_PATH = (
    ROOT / "docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md"
)
PLAN_SHA256 = "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
EVIDENCE_DESIGN_SHA256 = (
    "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
)
RQ_SPEC_PATH = ROOT / "research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md"
P12_CONTRACT_PATH = (
    ROOT / "docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md"
)
OUT = ROOT / "data/p3_v3/protocol"

# 1-based inclusive line ranges inside the SHA-pinned scientific plan.
EXTRACTS: dict[str, dict] = {
    "operator_catalogue.md": {
        "title": "Semantic operator catalogue and syntactic baseline",
        "authority_id": "p3-v3-phase0-operator-catalogue-v1",
        "sections": [
            ("Section 6 Semantic-mutant population", 550, 691),
            ("Section 7 Traditional syntactic-mutant baseline", 692, 716),
        ],
    },
    "mr_policy.md": {
        "title": "MR inventory, reference-MR isolation, and portfolio policy",
        "authority_id": "p3-v3-phase0-mr-policy-v1",
        "sections": [
            ("Section 5.1 P12 populations and reference-MR isolation", 208, 249),
            ("Section 8 MR inventory and evaluated MR sets", 717, 782),
        ],
    },
    "site_policy.md": {
        "title": "Subject, site identity, behavior frame, and evaluation-input policy",
        "authority_id": "p3-v3-phase0-site-policy-v1",
        "sections": [
            ("Section 5.2.1 Experimental unit and site identity", 321, 344),
            (
                "Section 5.2.2 Public Behavior Frame, Profiling Workload, and "
                "Evaluation Inputs",
                345,
                447,
            ),
        ],
    },
    "analysis_spec.md": {
        "title": "Metrics and prespecified analysis",
        "authority_id": "p3-v3-phase0-analysis-spec-v1",
        "sections": [
            ("Section 10 Metrics", 809, 850),
            ("Section 11 Prespecified analysis", 851, 997),
        ],
    },
    "package_policy.md": {
        "title": "Blinded bridge and phase-separated package policy",
        "authority_id": "p3-v3-phase0-package-policy-v1",
        "sections": [
            ("Section 5.1.1 P12-bound blinded fixed-snapshot bridge", 250, 307),
            ("Section 12 Non-circular mapping of P12 faults", 998, 1055),
        ],
    },
}

CLAIM_ASSOCIATIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("C1_ARTIFACT_FIRST_SEMANTIC_MUTANT_PROTOCOL", ("RQ1", "RQ2", "RQ3", "RQ4")),
    ("C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES", ("RQ1",)),
    ("C3_SEMANTIC_CONSTRUCT_DISTINCTNESS", ("RQ2",)),
    ("C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION", ("RQ3",)),
    ("C5_P12_CRITERION_INCREMENTAL_VALUE", ("RQ4",)),
    ("C6_UNIVERSAL_SUPERIORITY_CEILING", ("RQ3", "RQ4")),
    ("C7_LANGUAGE_INDEPENDENT_AUTOMATION_CEILING", ("RQ1",)),
    ("C8_PROFILING_REPRESENTATIVENESS_CEILING", ("RQ1",)),
)

ENVIRONMENTS: tuple[tuple[str, str, str, str], ...] = (
    (
        "CONSTRUCTION_A",
        "p3-v3-phase-env-construction-a-v1",
        "PACKAGE_A_CONSTRUCTION",
        "environments/construction_a.json",
    ),
    (
        "CONTROLLED_B",
        "p3-v3-phase-env-controlled-b-v1",
        "PACKAGE_B_CONTROLLED_EXECUTION",
        "environments/controlled_b.json",
    ),
    (
        "REAL_HOLDOUT_C",
        "p3-v3-phase-env-real-holdout-c-v1",
        "PACKAGE_C_REAL_HOLDOUT",
        "environments/real_holdout_c.json",
    ),
)

PASSPORT = """# P3 v3 Phase 0 authority: {title}

> Authority ID: {authority_id}
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: {plan_sha256}
> Source sections (verbatim, 1-based inclusive plan lines): {sources}
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

"""


def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def _extract(plan_lines: list[str], start: int, end: int) -> str:
    if not (1 <= start <= end <= len(plan_lines)):
        raise SystemExit(f"line range {start}..{end} outside plan")
    return "\n".join(plan_lines[start - 1 : end]).rstrip() + "\n"


def main() -> int:
    plan_raw = PLAN_PATH.read_bytes()
    if hashlib.sha256(plan_raw).hexdigest() != PLAN_SHA256:
        raise SystemExit("governing scientific plan bytes differ from pin")
    plan_lines = plan_raw.decode("utf-8").split("\n")

    outputs: dict[str, bytes] = {}

    for name, spec in EXTRACTS.items():
        sources = "; ".join(
            f"{label} (L{start}-L{end})" for label, start, end in spec["sections"]
        )
        body = PASSPORT.format(
            title=spec["title"],
            authority_id=spec["authority_id"],
            plan_sha256=PLAN_SHA256,
            sources=sources,
        )
        parts = [
            _extract(plan_lines, start, end) for _label, start, end in spec["sections"]
        ]
        outputs[name] = (body + "\n".join(parts)).encode("utf-8")

    claim_body = {
        "schema_version": "p3-claim-ceiling-authority-v1",
        "claims": [
            {"claim_id": claim_id, "rqs": list(rqs), "initial_status": "blocked"}
            for claim_id, rqs in CLAIM_ASSOCIATIONS
        ],
    }
    claim_artifact = {**claim_body, "artifact_sha256": canonical_sha256(claim_body)}
    outputs["claim_ceiling_authority.json"] = canonical_json_bytes(claim_artifact)

    environment_rows = []
    for role, env_id, package, rel in ENVIRONMENTS:
        descriptor = {
            "schema_version": "p3-v3-phase-environment-descriptor-v1",
            "environment_id": env_id,
            "environment_role": role,
            "phase_package": package,
            "controller_python_target": "3.11",
            "controller_runtime_dependencies": [],
        }
        outputs[rel] = canonical_json_bytes(descriptor)
        environment_rows.append(
            {
                "environment_role": role,
                "environment_id": env_id,
                "environment_sha256": canonical_sha256(descriptor),
            }
        )
    environment_lock = {
        "schema_version": "P3_V3_ENVIRONMENT_LOCK_V1",
        "required_capabilities": ["CPU", "DISK", "MEMORY"],
        "forbidden_credential_fields": [
            "authorization",
            "credential",
            "password",
            "token",
        ],
        "environments": environment_rows,
    }
    outputs["environment_lock.json"] = canonical_json_bytes(environment_lock)

    adapter_body = {"schema_version": "p3-adapter-registry-v1", "adapters": []}
    outputs["adapter_registry.json"] = canonical_json_bytes(
        {**adapter_body, "artifact_sha256": canonical_sha256(adapter_body)}
    )
    generator_body = {
        "schema_version": "p3-input-generator-registry-v1",
        "generators": [],
    }
    outputs["input_generator_registry.json"] = canonical_json_bytes(
        {**generator_body, "artifact_sha256": canonical_sha256(generator_body)}
    )

    def digest(name: str) -> str:
        return hashlib.sha256(outputs[name]).hexdigest()

    protocol_body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
        "rq_spec_sha256": hashlib.sha256(RQ_SPEC_PATH.read_bytes()).hexdigest(),
        "claim_ceiling_sha256": digest("claim_ceiling_authority.json"),
        "p12_contract_sha256": hashlib.sha256(
            P12_CONTRACT_PATH.read_bytes()
        ).hexdigest(),
        "operator_catalogue_sha256": digest("operator_catalogue.md"),
        "adapter_registry_sha256": digest("adapter_registry.json"),
        "input_generator_registry_sha256": digest("input_generator_registry.json"),
        "mr_policy_sha256": digest("mr_policy.md"),
        "site_policy_sha256": digest("site_policy.md"),
        "analysis_spec_sha256": digest("analysis_spec.md"),
        "package_policy_sha256": digest("package_policy.md"),
        "environment_lock_sha256": digest("environment_lock.json"),
        "profiling_budgets": dict(baf.PROFILING_BUDGETS),
        "behavior_category_order": list(baf.BEHAVIOR_CATEGORY_ORDER),
        "technique_order": list(baf._TECHNIQUE_ORDER),
        "e_common_count": baf.E_COMMON_COUNT,
        "e_contract_count": baf.E_CONTRACT_COUNT,
        "p12_outcome_states": list(baf.P12_OUTCOME_STATES),
        "p12_primary_estimand": baf.P12_PRIMARY_ESTIMAND,
        "infrastructure_retry_limit": baf.INFRASTRUCTURE_RETRY_LIMIT,
    }
    protocol = {**protocol_body, "artifact_sha256": canonical_sha256(protocol_body)}
    outputs["protocol.json"] = canonical_json_bytes(protocol)

    for rel, raw in outputs.items():
        _write(OUT / rel, raw)
    for rel in sorted(outputs):
        print(f"{hashlib.sha256(outputs[rel]).hexdigest()}  data/p3_v3/protocol/{rel}")
    print(f"{hashlib.sha256(RQ_SPEC_PATH.read_bytes()).hexdigest()}  {RQ_SPEC_PATH.relative_to(ROOT)}")
    print(
        f"{hashlib.sha256(P12_CONTRACT_PATH.read_bytes()).hexdigest()}  {P12_CONTRACT_PATH.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step A2: Run the builder once**

Run: `/opt/anaconda3/bin/python scripts/p3_v3/build_phase0_protocol.py`
Expected: 15 receipt lines (13 generated artifacts + rq_spec + p12 contract),
exit 0, files present under `data/p3_v3/protocol/`.

### Task B: Validation gate

- [ ] **Step B1: validate-protocol PASS**

Run: `PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py
validate-protocol --protocol data/p3_v3/protocol/protocol.json`
Expected: `{"status": "PASS", "protocol_sha256": "<64 hex>"}` and exit 0.
(PASS also proves the file is byte-canonical, because the CLI loads it with
`read_canonical_json`.)

### Task C: Cross-checks (authority coherence)

- [ ] **Step C1: RQ heading parity** — run the frozen regex
  `^### (RQ[0-9]+)(?:：|[ \t]+[—-][ \t]+)` (multiline) over both the RQ-spec
  and the scientific plan; each must yield exactly
  `['RQ1','RQ2','RQ3','RQ4']`.
- [ ] **Step C2: claim associations parity** — load
  `data/p3_v3/protocol/claim_ceiling_authority.json`, project
  `(claim_id, tuple(rqs))`, compare to `_REQUIRED_CLAIM_ASSOCIATIONS`
  imported from `scripts/p3_v3/evidence.py` via importlib; expect equal.
- [ ] **Step C3: budget verbatim check** — `rg -n "B_S=10.*B_M=15.*B_L=20"`
  on the scientific plan must hit (§14 Phase 0), and `protocol.json`
  `profiling_budgets` must equal `{"S":10,"M":15,"L":20}`.
- [ ] **Step C4: determinism** — hash all artifact bytes, rerun the builder,
  hash again; the two receipt outputs must be identical.

### Task D: Freeze receipt

- [ ] **Step D1: full suite in the clean worktree, outside the sandbox**

Run in `.worktrees/p3-v3-mef-align-repair-01`:
`PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3 -q`
Expected: `849 passed` and pytest exit 0 (no production/test byte changed by
this task; the worktree cannot see the new untracked data files).

### Task E: Task report, charter update, commit

- [ ] **Step E1:** write
  `docs/review_20260812/phase0_protocol_freeze_task_report.md` with: the
  SHA-256 receipt table, validate-protocol output, cross-check outputs,
  freeze-point suite receipt, and the three declared-open items from
  acceptance criterion 6.
- [ ] **Step E2:** tick charter Task 1 checkboxes and append the decision
  ledger entry (protocol V1 frozen; registries declared-empty pending
  Task 2 re-emit).
- [ ] **Step E3:** commit the exit-(b) decision documents (review archive,
  freeze record edit, charter) as one `docs(p3)` commit, then commit this
  plan, the builder, the artifact set, the task report, and the charter
  update as one `feat(p3-v3)` task-scoped commit.

## Self-review

- Spec coverage: every §14 Phase 0 inventory item maps to a binding
  (acceptance criterion 2); registries and the p12-contract loading seam are
  declared-open, not silently absent.
- No placeholders: builder code, line ranges, expected outputs, and commands
  are literal; extraction ranges were verified against the plan's heading
  line numbers (§5.1@208, §5.1.1@250, §5.2.1@321, §5.2.2@345, §5.3@448,
  §6@550, §7@692, §8@717, §9@783, §10@809, §11@851, §12@998, §13@1056).
- Type consistency: schema versions and key sets copied from
  `_PROTOCOL_SCHEMA`, `_CLAIM_CEILING_SCHEMA`, `_ENVIRONMENT_LOCK_SCHEMA`,
  `_PREPARED_ENVIRONMENT_SCHEMA`, registry schemas, and the frozen constants
  in `src/p3_v3/bridge_and_frames.py:37-241`.
