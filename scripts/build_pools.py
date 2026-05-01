"""Build data/mutants/{put_id}_pool[_v3]/ for all 12 PUTs from operator cache.

v2 pool: 12 mutants/PUT, dir suffix _pool
v3 pool: 30 mutants/PUT, dir suffix _pool_v3 (set POOL_VERSION='v3')

Records (path, op_id, attempt_idx) provenance to manifest.json.
"""
import json
import os
import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.pool_builder import select_mutants_for_put

PUTS = ["a1","a2","a3","b1","b2","b3","c1","c2","c3","d1","d2","d3"]
POOL_VERSION = os.environ.get("POOL_VERSION", "v3")
_N_MAP = {"v2": 12, "v3": 30, "v4": 30}
_SUFFIX_MAP = {"v2": "_pool", "v3": "_pool_v3", "v4": "_pool_v4"}
N_PER_PUT = _N_MAP.get(POOL_VERSION, 12)
SUFFIX = _SUFFIX_MAP.get(POOL_VERSION, "_pool")
CACHE = (ROOT / "data/operator_campaign/cache_cross"
         if POOL_VERSION == "v4" else ROOT / "data/operator_campaign/cache")
print(f"Building POOL_VERSION={POOL_VERSION} N_PER_PUT={N_PER_PUT} "
      f"SUFFIX={SUFFIX} CACHE={CACHE.name}")

for put_id in PUTS:
    pool_dir = ROOT / f"data/mutants/{put_id}{SUFFIX}"
    if pool_dir.exists():
        shutil.rmtree(pool_dir)
    pool_dir.mkdir(parents=True)
    selected = select_mutants_for_put(put_id, N_PER_PUT, CACHE, seed=42)
    manifest = []
    for idx, (src_path, op_id) in enumerate(selected, 1):
        attempt = src_path.stem.split("_attempt")[1]
        dest_name = f"m{idx:02d}_{op_id}_a{attempt}.py"
        shutil.copy(src_path, pool_dir / dest_name)
        manifest.append({
            "rank": idx, "filename": dest_name,
            "operator": op_id, "attempt_idx": int(attempt),
            "source_relpath": str(src_path.relative_to(ROOT)),
        })
    (pool_dir / "manifest.json").write_text(
        json.dumps({"put": put_id, "n_target": N_PER_PUT,
                    "n_actual": len(selected), "mutants": manifest},
                   indent=2, ensure_ascii=False)
    )
    print(f"{put_id}: {len(selected)} mutants → {pool_dir}")
