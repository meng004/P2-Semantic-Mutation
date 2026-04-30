"""Smoke test for sms_campaign.evaluate_cell on a known cell."""
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("sms_campaign", ROOT / "scripts" / "sms_campaign.py")
sms_campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sms_campaign)


def test_evaluate_cell_a2_pilot():
    """Pilot a2_MP1_mut1 already has known SMS=1.0 from pilot_results.json."""
    summary = sms_campaign.evaluate_cell(
        put_id="a2", mp_k=1,
        mutant_dir=ROOT / "data" / "mutants" / "a2_MP1_mut1",
    )
    assert summary["inst"] == 5
    assert summary["sms"] == 1.0
