#!/usr/bin/env python3
"""Run every prereg analysis script in --smoke mode; nonzero exit on failure."""
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "analysis_hzero.py", "analysis_hdisc.py", "analysis_hcons.py",
    "analysis_hdose.py", "analysis_hcal_hrank.py", "analysis_hxi.py",
    "analysis_hfix.py",
]

here = Path(__file__).parent
failed = []
for s in SCRIPTS:
    r = subprocess.run([sys.executable, str(here / s), "--smoke"],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        failed.append(s)
print(f"\n{len(SCRIPTS) - len(failed)}/{len(SCRIPTS)} smoke tests passed")
sys.exit(1 if failed else 0)
