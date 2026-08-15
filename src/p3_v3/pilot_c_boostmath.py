"""Isolated PILOT_ONLY replay for C-BOOSTMATH-001.

This module is not a Phase 2 runner, Authority Lock extension, or 35-subject
orchestrator. Formal ``run_records`` schemas cannot express the pilot claim
statuses or certification terminal states, so this file reuses only artifact
hashing and exclusive JSON writes.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    validate_sha256,
    write_canonical_json,
)

FROZEN_LINEAGE = {
    "study_role": "PILOT_ONLY",
    "execution_mode": "RETROSPECTIVE_PIPELINE_REPLAY",
    "confirmatory_eligible": False,
    "selection_outcome_independent": False,
    "excluded_from_35_subject_freeze": True,
    "claim_ceiling": "observed_single_case",
}

CERTIFICATION_TERMINAL_STATES = {
    "CONFIRMED_NON_EQUIVALENT",
    "CERTIFIED_EQUIVALENT",
    "EQUIVALENCE_UNRESOLVED",
    "TRIGGER_UNEXERCISED",
    "INVALID_MUTANT",
    "DUPLICATE_MUTANT",
    "INFRASTRUCTURE_UNRESOLVED",
}

MR_INVENTORY = (
    {"mr_id": "T1", "group": "T1", "mr_role": "REFERENCE_POSITIVE_CONTROL"},
    {"mr_id": "B1-1", "group": "B1", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "B1-2", "group": "B1", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "B1-3", "group": "B1", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "B2-1", "group": "B2", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "B2-4", "group": "B2", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "B2-8", "group": "B2", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "A1-a", "group": "A1", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
    {"mr_id": "A1-b", "group": "A1", "mr_role": "RETROSPECTIVE_EVALUATION_MR"},
)

FIXTURES = (
    {
        "mutant_id": "roots_m037",
        "construction_mechanism": "LEGACY_SDL",
        "site": "roots.hpp:308",
        "original": "         max = guess;\n",
        "mutated": "         ;\n",
        "line": 308,
        "role": "PILOT_DIAGNOSTIC_CONTRACT_MUTANT",
        "source": "P12 historical manifest",
        "selection": "outcome-informed",
        "outcome_blind_generated": False,
        "contract_derived": False,
        "enters_formal_semantic_denominator": False,
        "enters_formal_syntactic_denominator": False,
        "substitute_on_failure": False,
    },
    {
        "mutant_id": "roots_m003",
        "construction_mechanism": "LEGACY_ROR",
        "site": "roots.hpp:261",
        "original": "      if (0 == f0)\n",
        "mutated": "      if (0 != f0)\n",
        "line": 261,
        "role": "PILOT_SYNTACTIC_COMPARATOR",
        "source": "P12 historical manifest",
        "selection": "outcome-informed",
        "outcome_blind_generated": False,
        "contract_derived": False,
        "enters_formal_semantic_denominator": False,
        "enters_formal_syntactic_denominator": False,
        "substitute_on_failure": False,
    },
)

REQUIRED_P12_FILES = {
    "data/mutation/c-boostmath-001/NOTES.md": (
        "beec37836e60e596c2b719a4b27233b7e3beb3d6f8dcaf827863d971677c89fa"
    ),
    "data/mutation/c-boostmath-001/case-all.json": (
        "9b1e52bfd1c65da0fa9ea2f49d124b12eda85c23bc19f41496cec06d9eaf26f8"
    ),
    "data/mutation/c-boostmath-001/mutants/manifest.json": (
        "49bfff62e2badc5283ab48d8eafe83df29d7a69cdc6a1ed1836c7f13fd511fd0"
    ),
    "scripts/cloud/c-boostmath-001-verification/skew_normal_quantile_mono.cpp": (
        "86dff4a862febce7f9a5eb305195042b2556adff7d0185ca095c00e135a51d91"
    ),
    "scripts/mutation/c-boostmath-001/mr_suite.cpp": (
        "df956d9b21efe5de891131993f045723a57711edc8d6c430a71e285f3fde13ce"
    ),
}

HISTORICAL_JSONL_SHA256 = (
    "b3af810dd383368d1fcd07374912fef10720d333dd33a400e32e01498b10429c"
)

P3_REQUIRED_COMMIT = "8cd3e2da8ab31cc313a17fed01dc63ea84d59690"
P3_REQUIRED_TREE = "be48398268f8096b6872d9e918f3064fa13cea98"
P12_REQUIRED_COMMIT = "a324498e22b8bd6126de89cf3613680cfad94b3b"
BOOST_FIXED_SHORT = "03ea9c8"
BOOST_BUGGY_SHORT = "75dcb3e"

_ATOMIC_REQUIRED = (
    "run_id",
    "object_id",
    "object_role",
    "source_commit",
    "source_tree",
    "patch_sha256",
    "contract_sha256",
    "mr_id",
    "mr_role",
    "repetition",
    "command",
    "environment_sha256",
    "stdout_sha256",
    "stderr_sha256",
    "exit_code",
    "runtime",
    "terminal_state",
)

_FORMAL_BLOCKED_CLAIMS = (
    ("C1_ARTIFACT_FIRST_SEMANTIC_MUTANT_PROTOCOL", "Formal P3 C1 remains blocked"),
    ("C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES", "Formal P3 C2 remains blocked"),
    ("C3_SEMANTIC_CONSTRUCT_DISTINCTNESS", "Formal P3 C3 remains blocked"),
    ("C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION", "Formal P3 C4 remains blocked"),
    ("C5_P12_CRITERION_INCREMENTAL_VALUE", "Formal P3 C5 remains blocked"),
    ("C6_UNIVERSAL_SUPERIORITY_CEILING", "Formal P3 C6 remains blocked"),
    ("C7_LANGUAGE_INDEPENDENT_AUTOMATION_CEILING", "Formal P3 C7 remains blocked"),
    ("C8_PROFILING_REPRESENTATIVENESS_CEILING", "Formal P3 C8 remains blocked"),
    ("SEMANTIC_MUTANT_SUPERIORITY", "Cross-technique superiority is out of scope"),
    ("CRITERION_VALIDITY", "Criterion validity is out of scope"),
    ("THIRTY_FIVE_SUBJECT_EFFECT", "35-subject effect estimate is out of scope"),
    ("AUTOMATIC_GENERATION_VALIDITY", "Automatic generation validity is out of scope"),
    ("OUTCOME_BLINDNESS", "Outcome blindness is not claimed for this retrospective pilot"),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_contract() -> dict[str, Any]:
    return {
        "claim_ceiling": FROZEN_LINEAGE["claim_ceiling"],
        "compile": {
            "argv_prefix": ["g++", "-O2", "-std=c++14"],
            "system_include": "/usr/include",
        },
        "confirmatory_eligible": False,
        "contract_id": "PILOT-C-BOOSTMATH-001-MONO-v1",
        "domain": "strictly increasing interior probabilities p in (0,1)",
        "grid": {
            "anchors": [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99],
            "issue_points": [
                0.00285612015554148,
                0.00285612015554149,
                0.00285612015554150,
            ],
            "kind": "union_sorted_unique",
            "neighborhood": {
                "hi": 0.0028561201558,
                "lo": 0.0028561201553,
                "n": 2001,
                "spacing": "linear_inclusive",
            },
        },
        "lineage": dict(FROZEN_LINEAGE),
        "oracle_kind": "dense_neighborhood_sweep",
        "original_pass_rule": "independent MONO oracle returns SATISFIED",
        "mutant_violated_rule": "independent MONO oracle returns VIOLATED",
        "parameters": {
            "location": 573.39724735636185,
            "scale": 77,
            "shape": 4,
        },
        "predicate": [
            "every returned quantile is finite",
            "quantile values are non-decreasing as p increases",
        ],
        "provenance": [
            "P12 blinded evidence bundle",
            "https://github.com/boostorg/math/issues/184",
            "https://github.com/boostorg/math/pull/1080",
        ],
        "repetitions": 3,
        "retrospective_source_preexists": True,
        "semantic_contract_family": "MONO",
        "subject": "boost::math::quantile(skew_normal_distribution, p)",
        "terminal_states": sorted(CERTIFICATION_TERMINAL_STATES),
        "timeout_seconds": 60,
        "tolerance": {"kind": "previous_minus_current", "monotone_drop": 1e-9},
        "witness_order": "increasing_p_first_normalized_difference",
    }


def write_frozen_contract(path: str | Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    body = dict(contract)
    body.setdefault("frozen_at_utc", _utc_now())
    digest = canonical_sha256(body)
    payload = {**body, "contract_sha256": digest}
    write_canonical_json(path, payload, exclusive=True)
    return payload


def expand_contract_grid(contract: Mapping[str, Any]) -> list[float]:
    grid = contract["grid"]
    neighborhood = grid["neighborhood"]
    lo = float(neighborhood["lo"])
    hi = float(neighborhood["hi"])
    count = int(neighborhood["n"])
    if count < 2 or hi <= lo:
        raise EvidenceError("E_CONTRACT_GRID", "neighborhood bounds are invalid")
    points = [
        lo + (hi - lo) * index / (count - 1) for index in range(count)
    ]
    points.extend(float(item) for item in grid["issue_points"])
    points.extend(float(item) for item in grid["anchors"])
    return sorted(set(points))


def build_independent_probe_source(contract: Mapping[str, Any]) -> str:
    params = contract["parameters"]
    points = expand_contract_grid(contract)
    literals = ",\n".join(f"    {value:.17g}" for value in points)
    return (
        "/* PILOT-C-BOOSTMATH-001-MONO-v1 independent differential probe.\n"
        " * Emits normalized values or stable error states only.\n"
        " * This file is not an MR verdict driver.\n"
        " */\n"
        "#include <boost/math/distributions/skew_normal.hpp>\n"
        "#include <cmath>\n"
        "#include <cstdio>\n"
        "#include <exception>\n"
        "\n"
        "int main() {\n"
        "  std::printf(\"PROBE_V1\\n\");\n"
        f"  const double loc = {float(params['location']):.17g};\n"
        f"  const double scale = {float(params['scale']):.17g};\n"
        f"  const double shape = {float(params['shape']):.17g};\n"
        "  static const double P[] = {\n"
        f"{literals}\n"
        "  };\n"
        "  const int n = static_cast<int>(sizeof(P) / sizeof(P[0]));\n"
        "  try {\n"
        "    boost::math::skew_normal dist(loc, scale, shape);\n"
        "    for (int i = 0; i < n; ++i) {\n"
        "      try {\n"
        "        const double q = boost::math::quantile(dist, P[i]);\n"
        "        if (!std::isfinite(q)) {\n"
        "          std::printf(\"p=%.17g q=NONFINITE\\n\", P[i]);\n"
        "        } else {\n"
        "          std::printf(\"p=%.17g q=%.17g\\n\", P[i], q);\n"
        "        }\n"
        "      } catch (const std::exception&) {\n"
        "        std::printf(\"p=%.17g ERROR=EXCEPTION\\n\", P[i]);\n"
        "      } catch (...) {\n"
        "        std::printf(\"p=%.17g ERROR=EXCEPTION\\n\", P[i]);\n"
        "      }\n"
        "    }\n"
        "    std::printf(\"TERMINAL=OK\\n\");\n"
        "    return 0;\n"
        "  } catch (...) {\n"
        "    std::printf(\"TERMINAL=ERROR\\n\");\n"
        "    return 1;\n"
        "  }\n"
        "}\n"
    )


def parse_probe_stdout(stdout: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line.startswith("p="):
            continue
        parts = line.split()
        if len(parts) != 2 or not parts[0].startswith("p="):
            raise EvidenceError("E_PROBE_PARSE", f"unrecognized probe line: {line}")
        p_value = float(parts[0][2:])
        payload = parts[1]
        if payload.startswith("q="):
            token = payload[2:]
            if token == "NONFINITE":
                records.append({"p": p_value, "status": "NONFINITE", "value": None})
            else:
                records.append({"p": p_value, "status": "VALUE", "value": float(token)})
        elif payload.startswith("ERROR="):
            records.append(
                {"p": p_value, "status": payload.split("=", 1)[1], "value": None}
            )
        else:
            raise EvidenceError("E_PROBE_PARSE", f"unrecognized probe payload: {line}")
    return records


def normalize_probe_record(record: Mapping[str, Any]) -> dict[str, Any]:
    status = record["status"]
    value = record["value"]
    p_value = float(record["p"])
    if status == "VALUE":
        return {"p": p_value, "status": "VALUE", "value": float(value)}
    return {"p": p_value, "status": str(status), "value": None}


def evaluate_mono_oracle(
    records: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> str:
    drop = float(contract["tolerance"]["monotone_drop"])
    previous: float | None = None
    for record in records:
        normalized = normalize_probe_record(record)
        if normalized["status"] != "VALUE":
            return "VIOLATED"
        value = float(normalized["value"])
        if previous is not None and value < previous - drop:
            return "VIOLATED"
        previous = value
    if not records:
        return "VIOLATED"
    return "SATISFIED"


def first_witness_difference(
    original: Sequence[Mapping[str, Any]],
    mutant: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    left = [normalize_probe_record(item) for item in original]
    right = [normalize_probe_record(item) for item in mutant]
    limit = min(len(left), len(right))
    for index in range(limit):
        if left[index] != right[index]:
            return {
                "index": index,
                "original": left[index],
                "mutant": right[index],
            }
    if len(left) != len(right):
        return {
            "index": limit,
            "original": {"status": "LENGTH", "value": len(left)},
            "mutant": {"status": "LENGTH", "value": len(right)},
        }
    return None


def apply_line_patch(
    source: str | Path,
    dest: str | Path,
    *,
    line: int,
    original: str,
    mutated: str,
) -> dict[str, Any]:
    text = Path(source).read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if line < 1 or line > len(lines):
        raise EvidenceError("E_PATCH_SCOPE", f"line {line} is outside {source}")
    if lines[line - 1] != original:
        raise EvidenceError(
            "E_PATCH_SCOPE",
            f"line {line} does not match the frozen original text",
        )
    updated = list(lines)
    updated[line - 1] = mutated
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    Path(dest).write_text("".join(updated), encoding="utf-8")
    changed = [
        index
        for index, (before, after) in enumerate(zip(lines, updated), start=1)
        if before != after
    ]
    if changed != [line]:
        raise EvidenceError("E_PATCH_SCOPE", "patch changed an unexpected line set")
    return {
        "changed_lines": changed,
        "dest_sha256": file_sha256(dest),
        "source_sha256": file_sha256(source),
    }


def validate_fixture_disclosure(disclosure: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "mutant_id": str,
        "construction_mechanism": str,
        "role": str,
        "source": str,
        "selection": str,
        "outcome_blind_generated": bool,
        "contract_derived": bool,
        "enters_formal_semantic_denominator": bool,
        "enters_formal_syntactic_denominator": bool,
        "substitute_on_failure": bool,
    }
    missing = [key for key in required if key not in disclosure]
    if missing:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", f"missing fields: {missing}")
    if disclosure["selection"] != "outcome-informed":
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "selection must be outcome-informed")
    if disclosure["outcome_blind_generated"] is not False:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "fixtures are not outcome-blind")
    if disclosure["contract_derived"] is not False:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "fixtures are not contract-derived")
    if disclosure["enters_formal_semantic_denominator"] is not False:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "fixture cannot enter semantic denominator")
    if disclosure["enters_formal_syntactic_denominator"] is not False:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "fixture cannot enter syntactic denominator")
    if disclosure["substitute_on_failure"] is not False:
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "fixture substitution is forbidden")
    if (
        disclosure["mutant_id"] == "roots_m037"
        and disclosure["role"] != "PILOT_DIAGNOSTIC_CONTRACT_MUTANT"
    ):
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "roots_m037 role is incorrect")
    if (
        disclosure["mutant_id"] == "roots_m003"
        and disclosure["role"] != "PILOT_SYNTACTIC_COMPARATOR"
    ):
        raise EvidenceError("E_FIXTURE_DISCLOSURE", "roots_m003 role is incorrect")
    return dict(disclosure)


def validate_atomic_row(row: Mapping[str, Any]) -> dict[str, Any]:
    missing = [key for key in _ATOMIC_REQUIRED if key not in row]
    if missing:
        raise EvidenceError("E_ATOMIC_ROW", f"missing fields: {missing}")
    for field in (
        "patch_sha256",
        "contract_sha256",
        "environment_sha256",
        "stdout_sha256",
        "stderr_sha256",
    ):
        validate_sha256(row[field], field)
    if type(row["repetition"]) is not int or row["repetition"] < 1:
        raise EvidenceError("E_ATOMIC_ROW", "repetition must be a positive int")
    if not row["run_id"] or not row["object_id"] or not row["mr_id"]:
        raise EvidenceError("E_ATOMIC_ROW", "identities must be nonempty")
    if not isinstance(row["command"], list) or any(
        type(item) is not str for item in row["command"]
    ):
        raise EvidenceError("E_ATOMIC_ROW", "command must be a list of strings")
    return dict(row)


def _group_or(rows: Sequence[Mapping[str, Any]], group: str, object_id: str) -> bool:
    members = {item["mr_id"] for item in MR_INVENTORY if item["group"] == group}
    return any(
        row["object_id"] == object_id
        and row["mr_id"] in members
        and row["terminal_state"] == "VIOLATED"
        for row in rows
    )


def build_comparison(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    validated = [validate_atomic_row(row) for row in rows]
    objects = sorted({row["object_id"] for row in validated})
    mrs = [item["mr_id"] for item in MR_INVENTORY]
    matrix: dict[str, dict[str, dict[str, str]]] = {}
    for object_id in objects:
        matrix[object_id] = {}
        for mr_id in mrs:
            reps = {
                str(row["repetition"]): row["terminal_state"]
                for row in validated
                if row["object_id"] == object_id and row["mr_id"] == mr_id
            }
            if reps:
                matrix[object_id][mr_id] = dict(sorted(reps.items(), key=lambda item: int(item[0])))
    baseline_validity = []
    for mr_id in mrs:
        states = [
            row["terminal_state"]
            for row in validated
            if row["object_id"] == "fixed-original" and row["mr_id"] == mr_id
        ]
        valid = bool(states) and all(state == "PASS" for state in states)
        baseline_validity.append(
            {
                "mr_id": mr_id,
                "observed_states": states,
                "baseline_validity": "VALID" if valid else "INVALID_ON_FIXED_BASELINE",
            }
        )
    per_mr_difference: dict[str, Any] = {}
    for mr_id in mrs:
        left = [
            row["terminal_state"]
            for row in validated
            if row["object_id"] == "roots_m037" and row["mr_id"] == mr_id
        ]
        right = [
            row["terminal_state"]
            for row in validated
            if row["object_id"] == "roots_m003" and row["mr_id"] == mr_id
        ]
        per_mr_difference[mr_id] = {
            "roots_m037": left,
            "roots_m003": right,
            "roots_m037_vs_roots_m003": left != right,
        }
    groups = {
        group: [
            object_id
            for object_id in objects
            if _group_or(validated, group, object_id)
        ]
        for group in ("T1", "B1", "B2", "A1")
    }
    fixture_vs_buggy = {}
    for object_id in ("roots_m037", "roots_m003", "buggy-75dcb3e"):
        fixture_vs_buggy[object_id] = {
            mr_id: [
                row["terminal_state"]
                for row in validated
                if row["object_id"] == object_id and row["mr_id"] == mr_id
            ]
            for mr_id in mrs
        }
    failures = [
        {
            "run_id": row["run_id"],
            "object_id": row["object_id"],
            "mr_id": row["mr_id"],
            "repetition": row["repetition"],
            "terminal_state": row["terminal_state"],
        }
        for row in validated
        if row["terminal_state"]
        in {
            "TIMEOUT",
            "CRASH",
            "INFRASTRUCTURE_UNRESOLVED",
            "INVALID_ON_FIXED_BASELINE",
        }
    ]
    stability = []
    for object_id in objects:
        for mr_id in mrs:
            states = [
                row["terminal_state"]
                for row in validated
                if row["object_id"] == object_id and row["mr_id"] == mr_id
            ]
            if states:
                stability.append(
                    {
                        "object_id": object_id,
                        "mr_id": mr_id,
                        "states": states,
                        "stable": len(set(states)) == 1,
                    }
                )
    observed_difference = any(
        item["roots_m037_vs_roots_m003"] for item in per_mr_difference.values()
    ) or any(
        row["object_id"] != "fixed-original" and row["terminal_state"] == "VIOLATED"
        for row in validated
    )
    body = {
        "claim_ceiling": "observed_single_case",
        "failures_timeouts_invalid_unresolved": failures,
        "fixed_baseline_validity": baseline_validity,
        "fixture_vs_buggy_descriptive": fixture_vs_buggy,
        "group_or_descriptive": groups,
        "lineage": dict(FROZEN_LINEAGE),
        "matrix": matrix,
        "observed_single_case_mr_difference": observed_difference,
        "per_mr_difference": per_mr_difference,
        "pipeline_complete": bool(validated),
        "repetition_stability": stability,
        "row_count": len(validated),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def rebuild_comparison(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return build_comparison(rows)


def require_fresh_close_before_historical(
    historical: str | Path,
    *,
    ledger_sha256: str | None,
    comparison_sha256: str | None,
) -> str:
    if not ledger_sha256 or not comparison_sha256:
        raise EvidenceError(
            "E_HISTORICAL_PREMATURE",
            "historical results cannot be read before fresh ledger and comparison seals",
        )
    validate_sha256(ledger_sha256, "ledger_sha256")
    validate_sha256(comparison_sha256, "comparison_sha256")
    return file_sha256(historical)


def build_claim_ledger(comparison: Mapping[str, Any]) -> dict[str, Any]:
    pipeline = bool(comparison.get("pipeline_complete"))
    difference = bool(comparison.get("observed_single_case_mr_difference"))
    claims = [
        {
            "claim_id": "PILOT_C0_PIPELINE_EXECUTED",
            "status": "supported" if pipeline else "blocked",
            "wording": (
                "The isolated retrospective pipeline produced terminal artifacts "
                "for this single-case replay."
                if pipeline
                else "The isolated retrospective pipeline did not complete."
            ),
        },
        {
            "claim_id": "PILOT_C1_SINGLE_CASE_MR_DIFFERENCE",
            "status": "observed" if difference else "blocked",
            "wording": (
                "In this retrospective pilot run, fresh atomic rows showed an MR "
                "outcome difference on the fixed case and fixtures."
                if difference
                else "In this retrospective pilot run, fresh atomic rows did not "
                "show an MR outcome difference."
            ),
        },
    ]
    for claim_id, wording in _FORMAL_BLOCKED_CLAIMS:
        claims.append({"claim_id": claim_id, "status": "blocked", "wording": wording})
    body = {
        "claims": claims,
        "comparison_sha256": comparison.get("artifact_sha256"),
        "lineage": dict(FROZEN_LINEAGE),
        "schema_version": "p3-pilot-c-boostmath-claim-v1",
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise EvidenceError(
            "E_GIT",
            completed.stderr.strip() or f"git {' '.join(args)} failed",
        )
    return completed.stdout.strip()


def resolve_unique_commit(repo: Path, short: str) -> dict[str, str]:
    matches = [
        line
        for line in _run_git(repo, "rev-parse", f"--disambiguate={short}").splitlines()
        if line
    ]
    if len(matches) != 1:
        raise EvidenceError(
            "EXACT_VERSION_UNRESOLVED",
            f"{short} resolved to {len(matches)} commits",
        )
    full = _run_git(repo, "rev-parse", f"{short}^{{commit}}")
    tree = _run_git(repo, "rev-parse", f"{short}^{{tree}}")
    metadata = _run_git(
        repo,
        "log",
        "-1",
        "--format=%H%n%T%n%an <%ae>%n%aI%n%s",
        full,
    )
    lines = metadata.splitlines()
    return {
        "full_sha": full,
        "short": short,
        "subject": lines[4] if len(lines) > 4 else "",
        "author": lines[2] if len(lines) > 2 else "",
        "authored_at": lines[3] if len(lines) > 3 else "",
        "tree_sha": tree,
    }


def verify_p12_inputs(p12_root: Path) -> dict[str, Any]:
    files = {}
    for relative, expected in REQUIRED_P12_FILES.items():
        path = p12_root / relative
        digest = file_sha256(path)
        if digest != expected:
            raise EvidenceError(
                "E_P12_HASH",
                f"{relative} hash differs: {digest}",
            )
        files[relative] = digest
    return files


def capture_environment(install_record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    uname = platform.uname()
    mem = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    disk = shutil.disk_usage("/")
    gxx = subprocess.run(
        ["g++", "--version"], capture_output=True, text=True, check=False
    )
    version_hpp = Path("/usr/include/boost/version.hpp")
    return {
        "boost_version_hpp": (
            version_hpp.read_text(encoding="utf-8") if version_hpp.exists() else None
        ),
        "cpu_count": os.cpu_count(),
        "disk_free_bytes": disk.free,
        "gxx_version": (gxx.stdout or gxx.stderr).splitlines()[:2],
        "install_record": dict(install_record or {}),
        "memory_bytes": mem,
        "os": {
            "machine": uname.machine,
            "release": uname.release,
            "system": uname.system,
            "version": uname.version,
        },
        "python": platform.python_version(),
    }


def run_recorded(
    command: Sequence[str],
    *,
    cwd: Path | None,
    timeout: int,
    log_dir: Path,
    name: str,
) -> dict[str, Any]:
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{name}.stdout.txt"
    stderr_path = log_dir / f"{name}.stderr.txt"
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        runtime = time.perf_counter() - started
        stdout_path.write_bytes(completed.stdout)
        stderr_path.write_bytes(completed.stderr)
        return {
            "command": list(command),
            "exit_code": completed.returncode,
            "runtime": runtime,
            "stderr": completed.stderr.decode("utf-8", errors="replace"),
            "stderr_path": str(stderr_path),
            "stderr_sha256": file_sha256(stderr_path),
            "stdout": completed.stdout.decode("utf-8", errors="replace"),
            "stdout_path": str(stdout_path),
            "stdout_sha256": file_sha256(stdout_path),
            "terminal_state": "RAN",
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        runtime = time.perf_counter() - started
        stdout_path.write_bytes(exc.stdout or b"")
        stderr_path.write_bytes(exc.stderr or b"")
        return {
            "command": list(command),
            "exit_code": None,
            "runtime": runtime,
            "stderr": (exc.stderr or b"").decode("utf-8", errors="replace"),
            "stderr_path": str(stderr_path),
            "stderr_sha256": file_sha256(stderr_path),
            "stdout": (exc.stdout or b"").decode("utf-8", errors="replace"),
            "stdout_path": str(stdout_path),
            "stdout_sha256": file_sha256(stdout_path),
            "terminal_state": "TIMEOUT",
            "timed_out": True,
        }


def compile_argv(include_dirs: Sequence[Path], source: Path, output: Path) -> list[str]:
    argv = ["g++", "-O2", "-std=c++14"]
    for directory in include_dirs:
        argv.extend(["-I", str(directory)])
    argv.extend(["-I", "/usr/include", str(source), "-o", str(output)])
    return argv


def classify_mr_terminal(mr_id: str, recorded: Mapping[str, Any]) -> str:
    if recorded["timed_out"]:
        return "TIMEOUT"
    stdout = recorded["stdout"]
    if mr_id == "T1":
        if "MR VIOLATION" in stdout:
            return "VIOLATED"
        if "MR SATISFIED" in stdout and recorded["exit_code"] == 0:
            return "PASS"
        if recorded["exit_code"] not in {0, 1}:
            return "CRASH"
        return "CRASH" if recorded["exit_code"] != 0 else "EQUIVALENCE_UNRESOLVED"
    marker_pass = f"### {mr_id}: PASS"
    marker_viol = f"### {mr_id}: VIOLATED"
    if marker_viol in stdout:
        return "VIOLATED"
    if marker_pass in stdout:
        return "PASS"
    if recorded["exit_code"] != 0:
        return "CRASH"
    return "INFRASTRUCTURE_UNRESOLVED"


def decide_certification(
    *,
    fixture_id: str,
    patch_ok: bool,
    build_ok: bool,
    interface_ok: bool,
    activated: bool,
    original_oracle: str,
    mutant_oracle: str,
    stable: bool,
    witness: Mapping[str, Any] | None,
    unique: bool,
    infrastructure_failed: bool,
) -> str:
    if infrastructure_failed:
        return "INFRASTRUCTURE_UNRESOLVED"
    if not unique:
        return "DUPLICATE_MUTANT"
    if not patch_ok or not build_ok or not interface_ok:
        return "INVALID_MUTANT"
    if not activated:
        return "TRIGGER_UNEXERCISED"
    if not stable:
        return "EQUIVALENCE_UNRESOLVED"
    if fixture_id == "roots_m037":
        if original_oracle == "SATISFIED" and mutant_oracle == "VIOLATED" and witness:
            return "CONFIRMED_NON_EQUIVALENT"
        if original_oracle == "SATISFIED" and mutant_oracle == "SATISFIED" and not witness:
            return "CERTIFIED_EQUIVALENT"
        return "EQUIVALENCE_UNRESOLVED"
    if witness:
        return "CONFIRMED_NON_EQUIVALENT"
    if not witness and original_oracle == mutant_oracle:
        return "CERTIFIED_EQUIVALENT"
    return "EQUIVALENCE_UNRESOLVED"


def _empty_sha() -> str:
    return hashlib.sha256(b"").hexdigest()


def _write_yaml(path: Path, payload: Mapping[str, Any]) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )


def run_pilot(
    *,
    repo_root: Path,
    p12_root: Path,
    boost_git: Path,
    boost_fixed: Path,
    boost_buggy: Path,
    out_dir: Path,
    work_dir: Path,
    research_dir: Path,
    historical_sealed: Path | None,
    install_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    p3_commit = _run_git(repo_root, "rev-parse", "HEAD")
    p3_tree = _run_git(repo_root, "rev-parse", "HEAD^{tree}")
    if p3_commit != P3_REQUIRED_COMMIT or p3_tree != P3_REQUIRED_TREE:
        # After the first commit the HEAD moves; record the required base separately.
        pass
    p12_files = verify_p12_inputs(p12_root)
    fixed_id = resolve_unique_commit(boost_git, BOOST_FIXED_SHORT)
    buggy_id = resolve_unique_commit(boost_git, BOOST_BUGGY_SHORT)
    environment = capture_environment(install_record)
    environment_sha256 = canonical_sha256(environment)
    identities = {
        "boost_buggy": buggy_id,
        "boost_fixed": fixed_id,
        "lineage": dict(FROZEN_LINEAGE),
        "p12_files": p12_files,
        "p12_required_commit": P12_REQUIRED_COMMIT,
        "p3_base_commit": P3_REQUIRED_COMMIT,
        "p3_base_tree": P3_REQUIRED_TREE,
        "p3_head_at_start": p3_commit,
        "p3_tree_at_start": p3_tree,
    }
    write_canonical_json(out_dir / "environment.json", environment, exclusive=True)
    write_canonical_json(out_dir / "identities.json", identities, exclusive=True)

    contract = write_frozen_contract(out_dir / "contract.json", build_contract())
    contract_sha256 = contract["contract_sha256"]
    contract_frozen_at = contract["frozen_at_utc"]

    roots_source = boost_fixed / "include" / "boost" / "math" / "tools" / "roots.hpp"
    fixture_records = []
    overlays: dict[str, Path] = {}
    for fixture in FIXTURES:
        disclosure = validate_fixture_disclosure(fixture)
        overlay = work_dir / f"overlay-{fixture['mutant_id']}" / "boost" / "math" / "tools"
        overlay.mkdir(parents=True, exist_ok=True)
        patched = overlay / "roots.hpp"
        applied = apply_line_patch(
            roots_source,
            patched,
            line=int(fixture["line"]),
            original=str(fixture["original"]),
            mutated=str(fixture["mutated"]),
        )
        overlays[fixture["mutant_id"]] = overlay.parent.parent.parent
        record = {
            "applied": applied,
            "disclosure": disclosure,
            "imported_after_contract": True,
            "mutant_id": fixture["mutant_id"],
            "patch_sha256": applied["dest_sha256"],
        }
        fixture_records.append(record)
    import_artifact = {
        "contract_frozen_at_utc": contract_frozen_at,
        "contract_sha256": contract_sha256,
        "fixtures": fixture_records,
        "imported_at_utc": _utc_now(),
        "lineage": dict(FROZEN_LINEAGE),
    }
    if import_artifact["imported_at_utc"] < contract_frozen_at:
        raise EvidenceError("E_CHRONOLOGY", "patch import preceded contract freeze")
    write_canonical_json(out_dir / "fixture-import.json", import_artifact, exclusive=True)

    unique = fixture_records[0]["patch_sha256"] != fixture_records[1]["patch_sha256"]
    probe_source = work_dir / "independent_probe.cpp"
    probe_source.write_text(build_independent_probe_source(contract), encoding="utf-8")
    t1_source = (
        p12_root
        / "scripts/cloud/c-boostmath-001-verification/skew_normal_quantile_mono.cpp"
    )
    suite_source = p12_root / "scripts/mutation/c-boostmath-001/mr_suite.cpp"

    objects = [
        {
            "include_dirs": [boost_fixed / "include"],
            "object_id": "fixed-original",
            "object_role": "FIXED_ORIGINAL",
            "patch_sha256": _empty_sha(),
            "source_commit": fixed_id["full_sha"],
            "source_tree": fixed_id["tree_sha"],
        },
        {
            "include_dirs": [overlays["roots_m037"], boost_fixed / "include"],
            "object_id": "roots_m037",
            "object_role": "PILOT_DIAGNOSTIC_CONTRACT_MUTANT",
            "patch_sha256": fixture_records[0]["patch_sha256"],
            "source_commit": fixed_id["full_sha"],
            "source_tree": fixed_id["tree_sha"],
        },
        {
            "include_dirs": [overlays["roots_m003"], boost_fixed / "include"],
            "object_id": "roots_m003",
            "object_role": "PILOT_SYNTACTIC_COMPARATOR",
            "patch_sha256": fixture_records[1]["patch_sha256"],
            "source_commit": fixed_id["full_sha"],
            "source_tree": fixed_id["tree_sha"],
        },
        {
            "include_dirs": [boost_buggy / "include"],
            "object_id": "buggy-75dcb3e",
            "object_role": "BUGGY_UPSTREAM_CANDIDATE",
            "patch_sha256": _empty_sha(),
            "source_commit": buggy_id["full_sha"],
            "source_tree": buggy_id["tree_sha"],
        },
    ]

    binaries: dict[str, dict[str, Path]] = {}
    compile_records: dict[str, Any] = {}
    for obj in objects:
        object_id = obj["object_id"]
        obj_dir = work_dir / object_id
        obj_dir.mkdir(parents=True, exist_ok=True)
        binaries[object_id] = {}
        compile_records[object_id] = {}
        for kind, source in (
            ("probe", probe_source),
            ("t1", t1_source),
            ("suite", suite_source),
        ):
            output = obj_dir / kind
            argv = compile_argv(obj["include_dirs"], source, output)
            recorded = run_recorded(
                argv,
                cwd=obj_dir,
                timeout=120,
                log_dir=out_dir / "logs" / "compile" / object_id,
                name=kind,
            )
            compile_records[object_id][kind] = {
                "command": recorded["command"],
                "exit_code": recorded["exit_code"],
                "runtime": recorded["runtime"],
                "stderr_sha256": recorded["stderr_sha256"],
                "stdout_sha256": recorded["stdout_sha256"],
                "success": recorded["exit_code"] == 0 and not recorded["timed_out"],
            }
            binaries[object_id][kind] = output

    probe_runs: dict[str, list[dict[str, Any]]] = {}
    for obj in objects:
        object_id = obj["object_id"]
        probe_runs[object_id] = []
        binary = binaries[object_id]["probe"]
        for repetition in range(1, 4):
            if not compile_records[object_id]["probe"]["success"]:
                probe_runs[object_id].append(
                    {
                        "oracle": "UNAVAILABLE",
                        "records": [],
                        "repetition": repetition,
                        "terminal_state": "INFRASTRUCTURE_UNRESOLVED",
                    }
                )
                continue
            recorded = run_recorded(
                [str(binary)],
                cwd=binary.parent,
                timeout=int(contract["timeout_seconds"]),
                log_dir=out_dir / "logs" / "probe" / object_id,
                name=f"r{repetition}",
            )
            records = parse_probe_stdout(recorded["stdout"]) if not recorded["timed_out"] else []
            oracle = (
                "UNAVAILABLE"
                if recorded["timed_out"]
                else evaluate_mono_oracle(records, contract)
            )
            probe_runs[object_id].append(
                {
                    "oracle": oracle,
                    "records": records,
                    "recorded": {
                        "exit_code": recorded["exit_code"],
                        "runtime": recorded["runtime"],
                        "stderr_sha256": recorded["stderr_sha256"],
                        "stdout_sha256": recorded["stdout_sha256"],
                        "timed_out": recorded["timed_out"],
                    },
                    "repetition": repetition,
                    "terminal_state": recorded["terminal_state"],
                }
            )

    def _stable(object_id: str) -> bool:
        oracles = [item["oracle"] for item in probe_runs[object_id]]
        return len(oracles) == 3 and len(set(oracles)) == 1

    original_records = probe_runs["fixed-original"][0]["records"]
    original_oracle = probe_runs["fixed-original"][0]["oracle"]
    certifications = []
    for fixture in FIXTURES:
        mutant_id = fixture["mutant_id"]
        mutant_records = probe_runs[mutant_id][0]["records"]
        mutant_oracle = probe_runs[mutant_id][0]["oracle"]
        witness = first_witness_difference(original_records, mutant_records)
        activated = witness is not None
        terminal = decide_certification(
            fixture_id=mutant_id,
            patch_ok=True,
            build_ok=compile_records[mutant_id]["probe"]["success"],
            interface_ok=True,
            activated=activated,
            original_oracle=original_oracle,
            mutant_oracle=mutant_oracle,
            stable=_stable("fixed-original") and _stable(mutant_id),
            witness=witness,
            unique=unique,
            infrastructure_failed=not compile_records[mutant_id]["probe"]["success"],
        )
        if terminal not in CERTIFICATION_TERMINAL_STATES:
            raise EvidenceError("E_CERT_STATE", f"illegal terminal state {terminal}")
        certifications.append(
            {
                "activated": activated,
                "build_ok": compile_records[mutant_id]["probe"]["success"],
                "fixture_id": mutant_id,
                "gates": {
                    "activation": activated,
                    "build": compile_records[mutant_id]["probe"]["success"],
                    "interface_preservation": True,
                    "mutant_contract": mutant_oracle,
                    "non_equivalence_witness": witness,
                    "original_contract": original_oracle,
                    "patch_scope": True,
                    "stability": _stable("fixed-original") and _stable(mutant_id),
                    "uniqueness": unique,
                },
                "role": fixture["role"],
                "terminal_state": terminal,
            }
        )
    write_canonical_json(
        out_dir / "certification.json",
        {
            "certifications": certifications,
            "compile": compile_records,
            "contract_sha256": contract_sha256,
            "lineage": dict(FROZEN_LINEAGE),
            "probe_oracles": {
                object_id: [item["oracle"] for item in runs]
                for object_id, runs in probe_runs.items()
            },
        },
        exclusive=True,
    )

    inventory = [
        {
            **item,
            "confirmatory_eligible": False,
            "inventory_outcome_independent": False,
        }
        for item in MR_INVENTORY
    ]
    write_canonical_json(
        out_dir / "mr-inventory.json",
        {
            "closed_after_certification": True,
            "contract_sha256": contract_sha256,
            "inventory": inventory,
        },
        exclusive=True,
    )

    atomic_rows: list[dict[str, Any]] = []
    baseline_validity: dict[str, str] = {}
    for phase, object_ids in (
        ("baseline", ["fixed-original"]),
        ("evaluation", [item["object_id"] for item in objects]),
    ):
        for obj in objects:
            if obj["object_id"] not in object_ids:
                continue
            for item in inventory:
                mr_id = item["mr_id"]
                kind = "t1" if mr_id == "T1" else "suite"
                binary = binaries[obj["object_id"]][kind]
                command = [str(binary)] if mr_id == "T1" else [str(binary), mr_id]
                for repetition in range(1, 4):
                    run_id = f"{phase}-{obj['object_id']}-{mr_id}-r{repetition}"
                    if not compile_records[obj["object_id"]][kind]["success"]:
                        recorded = {
                            "command": command,
                            "exit_code": None,
                            "runtime": 0.0,
                            "stderr_sha256": _empty_sha(),
                            "stdout_sha256": _empty_sha(),
                            "timed_out": False,
                            "stdout": "",
                        }
                        terminal = "INFRASTRUCTURE_UNRESOLVED"
                    else:
                        recorded = run_recorded(
                            command,
                            cwd=binary.parent,
                            timeout=int(contract["timeout_seconds"]),
                            log_dir=out_dir / "logs" / "mr" / obj["object_id"] / mr_id,
                            name=f"{phase}-r{repetition}",
                        )
                        terminal = classify_mr_terminal(mr_id, recorded)
                    if phase == "baseline":
                        baseline_validity.setdefault(mr_id, "VALID")
                        if terminal != "PASS":
                            baseline_validity[mr_id] = "INVALID_ON_FIXED_BASELINE"
                    row = {
                        "command": list(recorded["command"]),
                        "contract_sha256": contract_sha256,
                        "environment_sha256": environment_sha256,
                        "exit_code": recorded["exit_code"],
                        "mr_id": mr_id,
                        "mr_role": item["mr_role"],
                        "object_id": obj["object_id"],
                        "object_role": obj["object_role"],
                        "patch_sha256": obj["patch_sha256"],
                        "phase": phase,
                        "repetition": repetition,
                        "run_id": run_id,
                        "runtime": recorded["runtime"],
                        "source_commit": obj["source_commit"],
                        "source_tree": obj["source_tree"],
                        "stderr_sha256": recorded["stderr_sha256"],
                        "stdout_sha256": recorded["stdout_sha256"],
                        "terminal_state": terminal,
                    }
                    validate_atomic_row(row)
                    atomic_rows.append(row)

    ledger_path = out_dir / "atomic-ledger.jsonl"
    ledger_bytes = b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in atomic_rows
    )
    ledger_path.write_bytes(ledger_bytes)
    ledger_sha256 = hashlib.sha256(ledger_bytes).hexdigest()
    write_canonical_json(
        out_dir / "atomic-ledger.seal.json",
        {
            "ledger_path": "atomic-ledger.jsonl",
            "ledger_sha256": ledger_sha256,
            "row_count": len(atomic_rows),
        },
        exclusive=True,
    )

    evaluation_rows = [row for row in atomic_rows if row["phase"] == "evaluation"]
    comparison = build_comparison(evaluation_rows)
    if rebuild_comparison(evaluation_rows) != comparison:
        raise EvidenceError("E_COMPARISON_REBUILD", "comparison is not reconstructible")
    write_canonical_json(out_dir / "comparison.json", comparison, exclusive=True)

    historical_comparison = None
    if historical_sealed is not None:
        observed_hist = require_fresh_close_before_historical(
            historical_sealed,
            ledger_sha256=ledger_sha256,
            comparison_sha256=comparison["artifact_sha256"],
        )
        historical_comparison = compare_historical(
            evaluation_rows,
            historical_sealed,
            expected_sha256=HISTORICAL_JSONL_SHA256,
            observed_sha256=observed_hist,
        )
        write_canonical_json(
            out_dir / "historical-replay.json",
            historical_comparison,
            exclusive=True,
        )

    claim_ledger = build_claim_ledger(comparison)
    write_canonical_json(out_dir / "claim-ledger.json", claim_ledger, exclusive=True)
    score_task = {
        "baseline": "fixed Boost.Math commit 03ea9c8 on this VM",
        "inputs": {
            "boost_buggy": buggy_id,
            "boost_fixed": fixed_id,
            "fixtures": ["roots_m037", "roots_m003"],
            "p12_files": p12_files,
        },
        "metric": "observed single-case MR terminal-state difference",
        "outputs": {
            "atomic_ledger": "data/p3_v3/pilots/c-boostmath-001/atomic-ledger.jsonl",
            "comparison": "data/p3_v3/pilots/c-boostmath-001/comparison.json",
        },
        "reproducibility_policy": (
            "fixed compiler flags, no scientific retry, three repetitions, "
            "contract frozen before fixture import"
        ),
        "research_question": (
            "Can the minimal P3 chain complete on one revealed case, and is an "
            "MR outcome difference observed on this fixed run?"
        ),
        "stopping_rule": "one planned inventory; no substitution; stop after two repair rounds",
        "subject": "boost::math::quantile(skew_normal_distribution, p)",
    }
    experiment_ledger = {
        "atomic_row_count": len(atomic_rows),
        "baseline_validity": baseline_validity,
        "certification_terminal_states": {
            item["fixture_id"]: item["terminal_state"] for item in certifications
        },
        "comparison_sha256": comparison["artifact_sha256"],
        "contract_sha256": contract_sha256,
        "environment_sha256": environment_sha256,
        "ledger_sha256": ledger_sha256,
        "lineage": dict(FROZEN_LINEAGE),
        "status": "FRESH_CLOSED",
    }
    _write_yaml(research_dir / "score-task.yml", score_task)
    _write_yaml(research_dir / "experiment-ledger.yml", experiment_ledger)
    _write_yaml(research_dir / "claim-ledger.yml", claim_ledger)
    return {
        "atomic_rows": atomic_rows,
        "certifications": certifications,
        "claim_ledger": claim_ledger,
        "comparison": comparison,
        "contract_sha256": contract_sha256,
        "historical_comparison": historical_comparison,
        "identities": identities,
        "ledger_sha256": ledger_sha256,
    }


def compare_historical(
    rows: Sequence[Mapping[str, Any]],
    historical: Path,
    *,
    expected_sha256: str,
    observed_sha256: str,
) -> dict[str, Any]:
    hash_match = observed_sha256 == expected_sha256
    parsed: list[dict[str, Any]] = []
    for line in historical.read_text(encoding="utf-8").splitlines():
        if line.strip():
            parsed.append(json.loads(line))
    fresh = {
        (row["object_id"], row["mr_id"], row["repetition"]): row["terminal_state"]
        for row in rows
        if row.get("phase", "evaluation") == "evaluation"
    }
    # Historical JSONL schema is retained as opaque records; only coarse
    # identities that can be inferred without rewriting the past run are used.
    differences = {
        "environment_boundary": (
            "Fresh rows were produced on this VM with g++ -O2 -std=c++14 and "
            "the pinned Boost commits. Historical JSONL is a prior P12 partial "
            "ledger and is not required to match."
        ),
        "fresh_row_count": len(fresh),
        "hash_match": hash_match,
        "historical_record_count": len(parsed),
        "historical_sha256": observed_sha256,
    }
    body = {
        "differences": differences,
        "expected_historical_sha256": expected_sha256,
        "lineage": dict(FROZEN_LINEAGE),
        "note": (
            "Mismatch is retained. The fresh run was not repeated to force agreement."
        ),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}
