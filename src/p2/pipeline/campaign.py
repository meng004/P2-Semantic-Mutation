from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from p2.pipeline.run_cell import run_one_cell, CellResult


@dataclass
class CampaignConfig:
    put_ids: List[str]
    mp_indices: List[int]
    mut_indices: List[int]
    n_repeat: int = 20


def run_campaign(cfg: CampaignConfig, dry_run: bool = False) -> Dict[str, CellResult]:
    """Iterate over (i, k) cells; results keyed by 'i_MPk' string."""
    results: Dict[str, CellResult] = {}
    for i in cfg.put_ids:
        for k in cfg.mp_indices:
            cell_id = f"{i}_MP{k}"
            if dry_run:
                results[cell_id] = CellResult(cell_id=cell_id, sms=0.0)
            else:
                from pathlib import Path
                from p2.pipeline.loaders import load_put, load_mutants, load_mr_set
                from p2.equiv.sampler import UniformSampler
                put_fn = load_put(i, root=Path("src/p2/puts"))
                for j in cfg.mut_indices:
                    mutants = load_mutants(i, k, j, root=Path("data/mutants"))
                    mr_set = load_mr_set(i, k, root=Path("data/mr_export"))
                    sampler = UniformSampler(low=0, high=1, dim=1, seed=42)
                    cr = run_one_cell(
                        put=put_fn, mutants=mutants, mr_set=mr_set,
                        cell_id=f"{i}_MP{k}_mut{j}",
                        sampler=sampler, k_eq=1000,
                        epsilon_eq=1e-6, epsilon_avp=1e-6,
                    )
                    results[cr.cell_id] = cr
    return results
