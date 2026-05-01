from pathlib import Path
from typing import Callable, List
from p2.avp.interface import MR


def load_put(put_id: str, root: Path) -> Callable:
    """Import PUT module by id; expects src/p2/puts/{put_id}.py with `program` callable."""
    import importlib
    mod = importlib.import_module(f"p2.puts.{put_id.lower()}")
    return mod.program


def load_mutants(put_id: str, mp_index: int, mut_index: int, root: Path) -> List[Callable]:
    """Load all double-confirmed mutants from data/mutants/{put}_MP{k}_mut{j}/*.py."""
    cell_dir = root / f"{put_id}_MP{mp_index}_mut{mut_index}"
    mutants: List[Callable] = []
    for py_file in sorted(cell_dir.glob("*.py")):
        spec_name = f"_mutant_{py_file.stem}"
        import importlib.util
        spec = importlib.util.spec_from_file_location(spec_name, py_file)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        mutants.append(mod.program)
    return mutants


def load_mr_set(put_id: str, mp_index: int, root: Path) -> List[MR]:
    """Load MR set from root/{put_id}_MP{mp_index}_mr.json."""
    import json
    import importlib
    mr_file = root / f"{put_id}_MP{mp_index}_mr.json"
    if not mr_file.exists():
        return []
    data = json.loads(mr_file.read_text())
    out: List[MR] = []
    for entry in data:
        r_mod = importlib.import_module(entry["r_module"])
        R_mod = importlib.import_module(entry["R_module"])
        out.append(MR(
            r=getattr(r_mod, entry["r_func"]),
            R=getattr(R_mod, entry["R_func"]),
            mp_index=mp_index, name=entry["name"],
        ))
    return out
