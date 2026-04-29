import math


def compute_sms(killed: int, total: int, equiv: int) -> float:
    """SMS = killed / (total − equiv). Returns NaN when denominator is 0."""
    denom = total - equiv
    if denom <= 0:
        return math.nan
    return killed / denom
