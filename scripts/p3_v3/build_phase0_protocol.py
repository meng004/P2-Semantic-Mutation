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

ADAPTER_IMPLEMENTATIONS: tuple[tuple[str, str, str], ...] = (
    ("PYTHON_PEP517_V1", "python", "src/p3_v3/adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "src/p3_v3/adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "src/p3_v3/adapters/meson_test_v1.py"),
    (
        "AUTOTOOLS_MAKECHECK_V1",
        "autotools",
        "src/p3_v3/adapters/autotools_makecheck_v1.py",
    ),
)
GENERATOR_IMPLEMENTATIONS: tuple[tuple[str, str], ...] = (
    (
        "JSON_SCHEMA_DRAFT2020_12_V1",
        "src/p3_v3/input_generators/json_schema_draft2020_12_v1.py",
    ),
    ("CLI_TOKEN_GRAMMAR_V1", "src/p3_v3/input_generators/cli_token_grammar_v1.py"),
    (
        "NUMERIC_ARRAY_DOMAIN_V1",
        "src/p3_v3/input_generators/numeric_array_domain_v1.py",
    ),
    ("TEXT_IO_SCHEMA_V1", "src/p3_v3/input_generators/text_io_schema_v1.py"),
    (
        "BINARY_RECORD_SCHEMA_V1",
        "src/p3_v3/input_generators/binary_record_schema_v1.py",
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

    adapter_rows = []
    for adapter_id, ecosystem, relative in sorted(ADAPTER_IMPLEMENTATIONS):
        adapter_rows.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": relative,
                "source_sha256": hashlib.sha256(
                    (ROOT / relative).read_bytes()
                ).hexdigest(),
            }
        )
    adapter_body = {
        "schema_version": "p3-adapter-registry-v1",
        "adapters": adapter_rows,
    }
    outputs["adapter_registry.json"] = canonical_json_bytes(
        {**adapter_body, "artifact_sha256": canonical_sha256(adapter_body)}
    )
    generator_rows = []
    for generator_id, relative in sorted(GENERATOR_IMPLEMENTATIONS):
        generator_rows.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": relative,
                "source_sha256": hashlib.sha256(
                    (ROOT / relative).read_bytes()
                ).hexdigest(),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-common-input-envelope-v1",
                },
                "failure_code": f"{generator_id}_INVALID",
            }
        )
    generator_body = {
        "schema_version": "p3-input-generator-registry-v1",
        "generators": generator_rows,
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
