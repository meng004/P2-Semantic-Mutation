"""Dev/holdout split committer with SHA-256 commitment and one-shot guard.

Plan v1.1.1 §3.4. The holdout family-id list + salt is hashed and the hash is
published *before* any strategy runs; the holdout is revealed (opened) exactly
once, only after strategy outputs are sealed. This makes non-circularity a
third-party-auditable fact, not a claim.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence


def _commit_hash(holdout_families: Sequence[str], salt: str) -> str:
    payload = {"holdout": sorted(holdout_families), "salt": salt}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


@dataclass
class SplitCommitment:
    commit_hash: str
    n_dev: int
    n_holdout: int
    strata: Dict[str, int]
    seed: int
    registry_hash: str          # must match the frozen registry (ordering guard)


class Splitter:
    """Stratified family-level 50:50 split, committed then opened once."""

    def __init__(self, registry_hash: str) -> None:
        self._registry_hash = registry_hash
        self._dev: Optional[List[str]] = None
        self._holdout: Optional[List[str]] = None
        self._salt: Optional[str] = None
        self._commitment: Optional[SplitCommitment] = None
        self._opened = False

    def commit(self, families_by_stratum: Dict[str, Sequence[str]],
               salt: str, seed: int) -> SplitCommitment:
        """Split each stratum's families 50:50 and publish the commitment.

        families_by_stratum: {stratum_key: [family_id, ...]}. Stratum keys
        encode (PUT x mechanism-class x modal grade) per plan §3.4.
        """
        if self._commitment is not None:
            raise RuntimeError("split already committed")
        import numpy as np
        rng = np.random.default_rng(seed)
        dev: List[str] = []
        holdout: List[str] = []
        strata_counts: Dict[str, int] = {}
        for stratum, fams in sorted(families_by_stratum.items()):
            fam = sorted(fams)
            perm = rng.permutation(len(fam))
            n_hold = len(fam) // 2
            for j, idx in enumerate(perm):
                (holdout if j < n_hold else dev).append(fam[idx])
            strata_counts[stratum] = len(fam)
        self._dev, self._holdout, self._salt = sorted(dev), sorted(holdout), salt
        self._commitment = SplitCommitment(
            commit_hash=_commit_hash(self._holdout, salt),
            n_dev=len(dev), n_holdout=len(holdout),
            strata=strata_counts, seed=seed,
            registry_hash=self._registry_hash,
        )
        return self._commitment

    @property
    def dev_families(self) -> List[str]:
        """Dev families are visible for building the guidance signal."""
        if self._dev is None:
            raise RuntimeError("not committed")
        return list(self._dev)

    def open_holdout(self, strategy_outputs_sealed: bool) -> List[str]:
        """Reveal the holdout exactly once, only after outputs are sealed."""
        if self._commitment is None:
            raise RuntimeError("not committed")
        if not strategy_outputs_sealed:
            raise RuntimeError("holdout cannot be opened before strategy outputs are sealed")
        if self._opened:
            raise RuntimeError("holdout already opened (one-shot); reopening is forbidden")
        self._opened = True
        return list(self._holdout)

    def verify_commitment(self, holdout: Sequence[str], salt: str,
                          published_hash: str) -> bool:
        """Third-party verification after the salt is released."""
        return _commit_hash(holdout, salt) == published_hash
