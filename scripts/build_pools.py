"""Build data/mutants/{put_id}_pool/ for all 12 PUTs from operator cache.
Target pool size: 12 mutants per PUT. Proportional distribution across operators.
Records (path, op_id, attempt_idx) provenance to data/mutants/{put_id}_pool/manifest.json.
"""
import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.pool_builder import select_mutants_for_put

PUTS = ["a1","a2","a3","b1","b2","b3","c1","c2","c3","d1","d2","d3"]
N_PER_PUT = 12
CACHE = ROOT / "data/operator_campaign/cache"

for put_id in PUTS:
    pool_dir = ROOT / f"data/mutants/{put_id}_pool"
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
