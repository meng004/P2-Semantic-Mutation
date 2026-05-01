"""One-shot dump of paper-cited numbers from paper_numbers_{v}.json.

Avoids repeated Read calls when refreshing §5.6-5.9 prose. Prints flat
key=value lines suitable for grep-and-paste.

Usage:
    SMS_VERSION=v3 PYTHONPATH=src .venv/bin/python scripts/show_numbers.py
"""
import json
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
VERSION = os.environ.get("SMS_VERSION", "v3")
PN_FILE = ROOT / f"data/results/paper_numbers_{VERSION}.json"

d = json.loads(PN_FILE.read_text())

print(f"=== paper_numbers_{VERSION}.json ===\n")
for sec in ("rq1", "rq2", "rq3", "rq4"):
    print(f"[{sec}]")
    for k, v in d[sec].items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"  {k}.{kk} = {vv}")
        else:
            print(f"  {k} = {v}")
    print()

# LRCA calibration (default + best)
cal_file = ROOT / "data/results/lrca_calibration.json"
if cal_file.exists():
    cal = json.loads(cal_file.read_text())
    print("[lrca_calibration]")
    print(f"  best.ood_band = {cal['best']['ood_band']}")
    print(f"  best.tolerance_multiplier = {cal['best']['tolerance_multiplier']}")
    print(f"  best.h5_cells_pass = {cal['best']['h5_cells_pass']}/60")
    print(f"  best.mean_c1_share = {cal['best']['mean_c1_share']}")
