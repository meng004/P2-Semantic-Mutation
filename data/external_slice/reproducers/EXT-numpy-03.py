#!/usr/bin/env python3
"""Dual-arm trigger for EXT-numpy-03 (numpy issues #25661/#25679).

Same seed, inputs, and property check for buggy and fixed arms.
Issue-described behaviour: irfft/hfft with explicit n differing from the
input-derived length must match a naive DFT reference.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def naive_irfft(X, n):
    import numpy as np

    m = len(X)
    full = np.zeros(n, dtype=complex)
    for k in range(min(m, n // 2 + 1)):
        full[k] = X[k]
    for k in range(1, (n + 1) // 2):
        full[n - k] = np.conj(full[k])
    x = np.array(
        [np.sum(full * np.exp(2j * np.pi * np.arange(n) * t / n)) for t in range(n)]
    ) / n
    return x.real


def naive_hfft(x, n):
    import numpy as np

    return naive_irfft(np.conj(x), n) * n


def evaluate(seed: int) -> dict:
    import numpy as np

    rng = np.random.RandomState(seed)
    checks = []
    ok = True

    x5 = np.arange(5) + 1j * np.ones(5)
    for n in (6, 8, 10, 12):
        got = np.fft.hfft(x5, n=n)
        want = naive_hfft(x5, n)
        d = float(np.max(np.abs(got - want)))
        bad = d > 1e-10 * max(1, n)
        checks.append({"name": f"hfft_len5_n{n}", "maxdiff": d, "ok": not bad})
        ok &= not bad

    for m, n in ((5, 6), (5, 10), (5, 12), (8, 8), (8, 20)):
        X = rng.randn(m) + 1j * rng.randn(m)
        X[0] = X[0].real
        got = np.fft.irfft(X, n=n)
        want = naive_irfft(X, n)
        d = float(np.max(np.abs(got - want)))
        bad = d > 1e-10 * max(1, n)
        checks.append({"name": f"irfft_len{m}_n{n}", "maxdiff": d, "ok": not bad})
        ok &= not bad

    for n in (7, 8, 16, 33):
        x = rng.randn(n)
        d = float(np.max(np.abs(np.fft.irfft(np.fft.rfft(x), n=n) - x)))
        bad = d > 1e-12 * n
        checks.append({"name": f"roundtrip_n{n}", "maxdiff": d, "ok": not bad})
        ok &= not bad

    return {
        "neutral_id": "EXT-numpy-03",
        "seed": seed,
        "input": {
            "hfft_input_len": 5,
            "hfft_n_values": [6, 8, 10, 12],
            "irfft_cases": [[5, 6], [5, 10], [5, 12], [8, 8], [8, 20]],
            "roundtrip_n_values": [7, 8, 16, 33],
        },
        "observed_output": {"checks": checks, "all_ok": ok},
        "expected_property": (
            "numpy.fft.hfft/irfft with explicit n not equal to the input-derived "
            "length match a naive DFT reference within tolerance; implied-size "
            "round-trips also succeed."
        ),
        "property_holds": bool(ok),
        "package_version": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "exit_status": 0 if ok else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    payload = evaluate(args.seed)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"property_holds": payload["property_holds"], "package_version": payload["package_version"]}))
    return int(payload["exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
