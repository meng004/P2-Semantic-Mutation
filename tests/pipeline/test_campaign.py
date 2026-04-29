from unittest.mock import MagicMock, patch
from p2.pipeline.campaign import run_campaign, CampaignConfig


@patch("p2.pipeline.campaign.run_one_cell")
def test_campaign_iterates_60_cells(mock_run):
    mock_run.return_value = MagicMock(sms=0.5)
    cfg = CampaignConfig(
        put_ids=["A1", "A2", "A3", "B1", "B2", "B3",
                 "C1", "C2", "C3", "D1", "D2", "D3"],
        mp_indices=[1, 2, 3, 4, 5],
        mut_indices=[1, 2, 3, 4, 5],
    )
    results = run_campaign(cfg, dry_run=True)
    assert len(results) == 60  # 12 PUT × 5 MP


def test_loaders_module_importable():
    from p2.pipeline import loaders
    assert hasattr(loaders, "load_put")
    assert hasattr(loaders, "load_mutants")
    assert hasattr(loaders, "load_mr_set")
