"""Generate one JSON file per (PUT, MP) cell — 60 files total.

Output: data/mr_export/{put}_MP{k}_mr.json
Schema per file:
  {
    "put": "<put_id>",          # e.g. "a1"
    "mp": <k>,                  # 1..5
    "r_name": "<fn_name>",      # name of the source-input transform
    "R_name": "<fn_name>",      # name of the output verifier
    "primary": <bool>,          # true iff this is the designated primary MR
    "sample_pairs": [           # 3 illustrative (x, r(x), y, y') triples
      {"x": ..., "r_x": ..., "y_orig": ..., "y_new": ..., "holds": <bool>}
    ]
  }
"""

import json
import importlib
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "data" / "mr_export"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (put_id, primary_mp, [mp_k: r_name, R_name])
# Each PUT has exactly one primary MP; the other 4 use trivial MRs.
CELLS = {
    "a1": {"primary": 4, "r": {4: "r_mp4"}, "R": {4: "R_mp4"}},
    "a2": {"primary": 1, "r": {1: "r_mp1"}, "R": {1: "R_mp1"}},
    "a3": {"primary": 3, "r": {3: "r_mp3"}, "R": {3: "R_mp3"}},
    "b1": {"primary": 2, "r": {2: "r_mp2"}, "R": {2: "R_mp2"}},
    "b2": {"primary": 2, "r": {2: "r_mp2"}, "R": {2: "R_mp2"}},
    "b3": {"primary": 1, "r": {1: "r_mp1"}, "R": {1: "R_mp1"}},
    "c1": {"primary": 5, "r": {5: "r_mp5"}, "R": {5: "R_mp5"}},
    "c2": {"primary": 5, "r": {5: "r_mp5"}, "R": {5: "R_mp5"}},
    "c3": {"primary": 5, "r": {5: "r_mp5"}, "R": {5: "R_mp5"}},
    "d1": {"primary": 2, "r": {2: "r_mp2"}, "R": {2: "R_mp2"}},
    "d2": {"primary": 2, "r": {2: "r_mp2"}, "R": {2: "R_mp2"}},
    "d3": {"primary": 2, "r": {2: "r_mp2"}, "R": {2: "R_mp2"}},
}

SAMPLE_XS = [0.2, 0.5, 0.75]


def _scalar_output(y):
    """Reduce array outputs to a single float for JSON storage."""
    if isinstance(y, np.ndarray):
        return float(np.mean(y))
    return float(y)


def generate():
    for put_id, spec in CELLS.items():
        put_mod = importlib.import_module(f"p2.puts.{put_id}")
        mr_mod = importlib.import_module(f"p2.mrs.{put_id}")
        primary_k = spec["primary"]

        for k in range(1, 6):
            r_name = spec["r"].get(k, "r_trivial")
            R_name = spec["R"].get(k, "R_trivial")
            r_fn = getattr(mr_mod, r_name)
            R_fn = getattr(mr_mod, R_name)

            pairs = []
            for x in SAMPLE_XS:
                rx = r_fn(x)
                y_orig = _scalar_output(put_mod.program(x))
                y_new = _scalar_output(put_mod.program(rx))
                holds = bool(R_fn(y_orig, y_new))
                pairs.append({
                    "x": round(x, 4),
                    "r_x": round(float(rx), 6),
                    "y_orig": round(y_orig, 6),
                    "y_new": round(y_new, 6),
                    "holds": holds,
                })

            record = {
                "put": put_id,
                "mp": k,
                "r_name": r_name,
                "R_name": R_name,
                "primary": k == primary_k,
                "sample_pairs": pairs,
            }

            fname = OUT_DIR / f"{put_id}_MP{k}_mr.json"
            fname.write_text(json.dumps(record, indent=2))
            print(f"  wrote {fname.name}")

    total = len(list(OUT_DIR.glob("*.json")))
    print(f"\nDone: {total} JSON files in {OUT_DIR}")


if __name__ == "__main__":
    generate()
