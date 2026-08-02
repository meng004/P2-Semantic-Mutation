#!/usr/bin/env python3
"""A1d-r1 helpers for C3 Batch 3 repetition matrix and BLAS provenance."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

MATRIX_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "external_slice"
    / "BATCH3_EXECUTION_MATRIX.json"
)
MEMBERSHIP_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "external_slice"
    / "BATCH3_MEMBERSHIP.json"
)

EXPECTED_MEMBERS = [
    "EXT-numpy-01",
    "EXT-scipy-01",
    "EXT-scikit-learn-01",
    "EXT-statsmodels-01",
    "EXT-statsmodels-02",
    "EXT-statsmodels-03",
]

NUMERIC_BLAS_CASES = {
    "EXT-numpy-01",
    "EXT-scipy-01",
    "EXT-scikit-learn-01",
    "EXT-statsmodels-01",
    "EXT-statsmodels-02",
    "EXT-statsmodels-03",
}


def load_execution_matrix(path: Path | None = None) -> dict[str, Any]:
    matrix_path = path or MATRIX_PATH
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    smoke_seeds = list(matrix["smoke"]["seeds"])
    formal_seeds = list(matrix["formal_repetitions"]["seeds"])
    if smoke_seeds != [0]:
        raise ValueError(f"smoke seeds must be [0], got {smoke_seeds}")
    if formal_seeds != [0, 1, 2, 3, 4]:
        raise ValueError(f"formal seeds must be [0,1,2,3,4], got {formal_seeds}")
    if matrix["members"] != EXPECTED_MEMBERS:
        raise ValueError("execution matrix members diverge from frozen Batch 3 IDs")
    return matrix


def assert_membership_byte_identical(
    membership_path: Path | None = None,
    matrix: dict[str, Any] | None = None,
) -> str:
    import hashlib

    path = membership_path or MEMBERSHIP_PATH
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = (matrix or load_execution_matrix())["membership_sha256_expected"]
    if digest != expected:
        raise AssertionError(
            f"BATCH3_MEMBERSHIP.json sha mismatch: {digest} != {expected}"
        )
    members = json.loads(path.read_text(encoding="utf-8"))["members"]
    ids = [row["neutral_id"] for row in members]
    if ids != EXPECTED_MEMBERS:
        raise AssertionError(f"membership IDs mutated: {ids}")
    return digest


def seed_exhibits_contrast(buggy_holds: bool | None, fixed_holds: bool | None) -> bool:
    return buggy_holds is False and fixed_holds is True


def aggregate_formal_verdict(
    per_seed: dict[int, dict[str, Any]],
    formal_seeds: list[int] | None = None,
) -> dict[str, Any]:
    """Aggregate dual-arm contrast across the full formal seed matrix.

    Any missing seed or non-contrast seed yields REPRO_FAILED. Failed seeds
    are never dropped from the report.
    """
    seeds = formal_seeds or [0, 1, 2, 3, 4]
    seed_rows: list[dict[str, Any]] = []
    failing: list[int] = []
    for seed in seeds:
        row = per_seed.get(seed)
        if row is None:
            failing.append(seed)
            seed_rows.append(
                {
                    "seed": seed,
                    "present": False,
                    "contrast": False,
                    "buggy_property_holds": None,
                    "fixed_property_holds": None,
                    "buggy_raw_return_code": None,
                    "fixed_raw_return_code": None,
                }
            )
            continue
        contrast = seed_exhibits_contrast(
            row.get("buggy_property_holds"),
            row.get("fixed_property_holds"),
        )
        if not contrast:
            failing.append(seed)
        seed_rows.append(
            {
                "seed": seed,
                "present": True,
                "contrast": contrast,
                "buggy_property_holds": row.get("buggy_property_holds"),
                "fixed_property_holds": row.get("fixed_property_holds"),
                "buggy_raw_return_code": row.get("buggy_raw_return_code"),
                "fixed_raw_return_code": row.get("fixed_raw_return_code"),
                "input_parity_ok": bool(row.get("input_parity_ok", True)),
            }
        )
        if not row.get("input_parity_ok", True):
            if seed not in failing:
                failing.append(seed)
    proposed = "PASS" if not failing else "REPRO_FAILED"
    return {
        "proposed_crit_dual_arm_repro": proposed,
        "failing_seeds": failing,
        "seed_rows": seed_rows,
        "formal_seeds": seeds,
        "all_seeds_contrasted": not failing,
    }


def save_execution_outputs(
    dest_dir: Path,
    arm: str,
    *,
    payload: dict[str, Any] | None,
    stdout: str,
    stderr: str,
    raw_return_code: int,
) -> dict[str, str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    json_path = dest_dir / f"{arm}.json"
    stdout_path = dest_dir / f"{arm}.stdout.txt"
    stderr_path = dest_dir / f"{arm}.stderr.txt"
    rc_path = dest_dir / f"{arm}.returncode.txt"
    if payload is not None:
        json_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        json_path.write_text("{}\n", encoding="utf-8")
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    rc_path.write_text(f"{raw_return_code}\n", encoding="utf-8")
    return {
        "json": str(json_path),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "raw_return_code": str(rc_path),
    }


def discover_blas_lapack_provider(
    python: Path,
    *,
    label: str,
) -> dict[str, Any]:
    """Record BLAS/LAPACK provider discovery for one installed arm."""
    probe = r"""
import json
import sys
out = {
    "python": sys.version.split()[0],
    "numpy": None,
    "scipy": None,
    "numpy_show_config": "",
    "scipy_show_config": "",
    "numpy_config_keys": [],
    "errors": [],
}
try:
    import numpy as np
    out["numpy"] = getattr(np, "__version__", None)
    try:
        from io import StringIO
        buf = StringIO()
        np.show_config(stream=buf)
        out["numpy_show_config"] = buf.getvalue()
    except TypeError:
        from io import StringIO
        import contextlib
        buf = StringIO()
        with contextlib.redirect_stdout(buf):
            np.show_config()
        out["numpy_show_config"] = buf.getvalue()
    cfg = getattr(np, "__config__", None)
    if cfg is not None and hasattr(cfg, "get_info"):
        for key in (
            "blas_opt_info",
            "lapack_opt_info",
            "blas_mkl_info",
            "openblas_info",
            "blas_ilp64_opt_info",
        ):
            try:
                info = cfg.get_info(key)
            except Exception as exc:  # noqa: BLE001
                out["errors"].append(f"{key}:{exc!r}")
                continue
            if info:
                out["numpy_config_keys"].append(
                    {"key": key, "libraries": info.get("libraries"),
                     "library_dirs": info.get("library_dirs")}
                )
except Exception as exc:  # noqa: BLE001
    out["errors"].append(f"numpy:{exc!r}")
try:
    import scipy
    out["scipy"] = getattr(scipy, "__version__", None)
    from io import StringIO
    import contextlib
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        scipy.show_config()
    out["scipy_show_config"] = buf.getvalue()
except Exception as exc:  # noqa: BLE001
    out["errors"].append(f"scipy:{exc!r}")
print(json.dumps(out, sort_keys=True))
"""
    cmd = [str(python), "-c", probe]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    parsed: dict[str, Any] | None = None
    if proc.returncode == 0 and (proc.stdout or "").strip():
        try:
            parsed = json.loads(proc.stdout.strip().splitlines()[-1])
        except json.JSONDecodeError:
            parsed = None
    provider = summarize_provider(parsed)
    return {
        "label": label,
        "command": cmd,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "exit_code": proc.returncode,
        "parsed": parsed,
        "provider_summary": provider,
    }


def summarize_provider(parsed: dict[str, Any] | None) -> str:
    if not parsed:
        return "unknown"
    blob = "\n".join(
        [
            parsed.get("numpy_show_config") or "",
            parsed.get("scipy_show_config") or "",
            json.dumps(parsed.get("numpy_config_keys") or []),
        ]
    ).lower()
    for name in (
        "mkl",
        "openblas",
        "accelerate",
        "blis",
        "atlas",
        "netlib",
        "lapack",
        "blas",
    ):
        if re.search(rf"\b{name}\b", blob):
            return name
    if "libraries" in blob:
        return "configured-other"
    return "unknown-or-unreported"


def assert_arm_input_parity(
    buggy_payload: dict[str, Any] | None,
    fixed_payload: dict[str, Any] | None,
    seed: int,
) -> bool:
    if buggy_payload is None or fixed_payload is None:
        return False
    if buggy_payload.get("seed") != seed or fixed_payload.get("seed") != seed:
        return False
    return buggy_payload.get("input") == fixed_payload.get("input")
