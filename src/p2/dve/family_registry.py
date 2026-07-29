"""Fault-Card family registry with nested (PUT, mechanism/template) IDs.

Plan v1.1.1 §3.3 / round-3 amendment 2. Families are nested in PUTs; cross-PUT
similar mechanisms share a *mechanism class*, not a family id. The registry is
frozen (content hash recorded) BEFORE any dev/holdout split; merges/splits are
forbidden after freeze.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

_SOURCE_TYPES = {"requirement", "algorithm_spec", "historical_fault", "fmea"}
_GRADES = {"A", "B", "C", "D"}


@dataclass(frozen=True)
class Provenance:
    source_type: str          # one of _SOURCE_TYPES
    reference: str            # resolvable: doc section / DOI / issue|commit URL
    timestamp: str            # ISO date recorded at entry (passed in, not now())
    role: str                 # entering role id

    def validate(self) -> None:
        if self.source_type not in _SOURCE_TYPES:
            raise ValueError(f"illegal provenance source_type: {self.source_type}")
        if not self.reference:
            raise ValueError("provenance requires a resolvable reference")


@dataclass(frozen=True)
class FaultCard:
    card_id: str
    put: str
    mechanism_class: str      # cross-PUT class (quota + DVE-T mapping)
    provenance: Provenance
    grade: str                # A/B/C/D or REJECTED/UNCERTAIN
    instances: List[str] = field(default_factory=list)  # mutant ids


class FamilyRegistry:
    """Groups fault cards into families nested in PUTs, then freezes."""

    def __init__(self) -> None:
        self._cards: Dict[str, FaultCard] = {}
        self._frozen_hash: Optional[str] = None

    # -- construction (only allowed before freeze) --
    def add_card(self, card: FaultCard) -> None:
        self._require_mutable()
        card.provenance.validate()
        if card.grade not in _GRADES and card.grade not in {"REJECTED", "UNCERTAIN"}:
            raise ValueError(f"illegal grade: {card.grade}")
        if card.card_id in self._cards:
            raise ValueError(f"duplicate card_id: {card.card_id}")
        self._cards[card.card_id] = card

    def merge_or_split(self, reassign: Dict[str, str]) -> None:
        """Reassign card_id -> new mechanism_class (boundary change).

        Only permitted before freeze (round-3: no merge/split after split, and
        the split follows the freeze).
        """
        self._require_mutable()
        for cid, new_cluster in reassign.items():
            c = self._cards[cid]
            self._cards[cid] = FaultCard(c.card_id, c.put, new_cluster,
                                         c.provenance, c.grade, list(c.instances))

    # -- family view --
    def family_id(self, card: FaultCard) -> str:
        return f"{card.put}::{card.mechanism_class}"

    def families(self, grades: Optional[set] = None) -> Dict[str, List[str]]:
        """Return {family_id: [card_id, ...]} optionally filtered by grade."""
        out: Dict[str, List[str]] = {}
        for c in self._cards.values():
            if grades is not None and c.grade not in grades:
                continue
            out.setdefault(self.family_id(c), []).append(c.card_id)
        return out

    def primary_families(self) -> Dict[str, List[str]]:
        """A/B/C families only (primary denominator; plan §4.1)."""
        return self.families(grades={"A", "B", "C"})

    def mechanism_classes(self) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for c in self._cards.values():
            out.setdefault(c.mechanism_class, []).append(c.card_id)
        return out

    # -- freeze --
    def content_hash(self) -> str:
        payload = sorted(
            (c.card_id, c.put, c.mechanism_class, c.grade,
             c.provenance.source_type, c.provenance.reference,
             tuple(sorted(c.instances)))
            for c in self._cards.values()
        )
        blob = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()

    def freeze(self) -> str:
        if self._frozen_hash is not None:
            raise RuntimeError("registry already frozen")
        self._frozen_hash = self.content_hash()
        return self._frozen_hash

    @property
    def frozen_hash(self) -> Optional[str]:
        return self._frozen_hash

    def _require_mutable(self) -> None:
        if self._frozen_hash is not None:
            raise RuntimeError("registry is frozen; boundary changes forbidden")
