def compute_rates(inst: int, equiv: int, killed: int, survive: int, n_target: int = 15) -> dict:
    """RQ1 four rates: inst_rate, equiv_rate, survive_rate."""
    return {
        "inst_rate": inst / n_target if n_target > 0 else 0.0,
        "equiv_rate": equiv / inst if inst > 0 else 0.0,
        "survive_rate": survive / inst if inst > 0 else 0.0,
    }
