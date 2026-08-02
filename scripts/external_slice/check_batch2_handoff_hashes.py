#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_c3_batch2_a1c import handoff_hash_checker, ROOT
raise SystemExit(handoff_hash_checker(ROOT / 'data/external_slice/HANDOFF_REPRO_BATCH2.json'))
