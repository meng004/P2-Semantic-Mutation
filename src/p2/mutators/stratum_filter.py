"""Deterministic single-stratum admission filter for the Study-2 campaign.

Study-1 diagnosis (docs/review_2026-07-08/fixes/s5_purity_findings.md,
data/results/s5_purity_v4.json)
------------------------------------------------------------------------------
Running all five MP invariant checkers on each of the 292 admitted Study-1
mutants (the offline AVP dispatcher src/p2/avp/, 20-repeat majority vote) gave
the invariant-flip distribution {0: 170, 1: 93, >=2: 29}. A mutant *perturbs
invariant k* iff it is KILLED under MP_k; its *flip count* is how many of the
five invariants it perturbs. S5 purity requires each detected mutant to flip
exactly one invariant (so the effect map sigma is single-valued).

The 29 multi-stratum mutants (flip >= 2) were confined to TWO operator families:

  CF (control-flow reversal):     9 / 9   multi-stratum   (b2 MH acceptance flip)
  TF (training/fit-data corrupt): 20 / 54 multi-stratum   (c1/d1/d3 label/data)

The four local-edit families were 100% single-stratum (0 / 229):

  CE (constant error)   OS (operator swap)   HP (hyper-param)   SI (structure/idx)

Mechanism: CF and TF mutate *shared upstream state*. Reversing the MCMC
acceptance inequality inverts the whole chain, breaking MP1 and MP2 at once;
corrupting the training labels/range poisons every downstream prediction, so
the monotonicity (MP2) and partial-order (MP5) relations break simultaneously.
Local edits touch one computational pathway, hence one downstream invariant.
This multi-valued sigma is the root cause of the Study-1 H4 attribution leakage
(35.2% of the RQ2 off-diagonal kill mass came from multi-stratum artefacts, not
genuine cross-stratum detection).

Constraint (Study-2, pre-registered, derived from Study-1 diagnostics only)
------------------------------------------------------------------------------
CF/TF generated mutants must perturb exactly ONE invariant stratum. Enforcement
is two-layered:

  1. Weak spec-level textual guardrail appended to the CF/TF generation prompt
     (`single_stratum_prompt_clause`); insufficient on its own.
  2. Strong deterministic post-generation screen (`decide` / `screen_mutant`):
     a CF/TF candidate is ADMITTED iff its offline invariant-flip count is <= 1,
     using the SAME offline AVP dispatcher and classification as the S5 audit
     (`scripts/compute_s5_purity.py`). Applied uniformly at admission time,
     BEFORE any SMS is computed, IDENTICALLY for every arm and cell. The four
     local-edit families are admitted unconditionally (they never straddle).

Integrity: the constraint is keyed on the Study-1 per-operator audit only; no
Study-2 data exists to peek at. Study-1 pool artefacts are immutable and are
never re-screened; the filter runs on the Study-2 campaign path only, gated by
the pre-registered flag `p2.config.campaign.single_stratum_filter_enabled()`
(default ON).

P8 remediation (2026-07-09, forward-looking apparatus for Study 3)
------------------------------------------------------------------------------
Incident P8 (docs/prereg_v2/H4_DIAGNOSIS.md §2): `_OPID_CAT_RE` anchored after
the operator digits, so the Study-2 cross-source op-id suffix (`c7_TF1_claude`)
made `category_from_op_id` return None; `decide` then treated None as
"unconstrained" and admitted the candidate WITHOUT evaluating its flip count —
a silent no-op for the entire v5 CF/TF screen. Three forward-looking fixes,
disclosed as the Study-3 remediation and touching NO committed v5 artefact or
verdict:
  1. `_OPID_CAT_RE` tolerates the source suffix (categories resolve for every
     v5-style id).
  2. `ALL_FAMILIES` + `active_constrained_categories()` add an all-family screen
     scope selectable per-registration (`screen_all_families_enabled()`); the
     Study-2 default stays {CF,TF}.
  3. `decide` raises loudly on a None category instead of admitting it, so a
     parse failure can never again masquerade as an unconstrained pass.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

# All operator families the campaign knows. A parsed category MUST be one of
# these; anything else (or None) is a wiring defect, not an "unconstrained" pass.
KNOWN_CATEGORIES = frozenset({"CE", "OS", "HP", "TF", "SI", "CF"})

# Operator families that mutate shared upstream state and straddle >= 2 strata
# (Study-1 S5 audit). Under the Study-2 registration only these are screened;
# every other KNOWN family is admitted unconditionally.
CONSTRAINED_CATEGORIES = frozenset({"CF", "TF"})

# All-family screening scope (Study-3 P8 remediation): screen every known family,
# not just {CF,TF}. Selected per-registration via the config flag below; it is
# NEVER the silent default (Study-2 default stays {CF,TF}).
ALL_FAMILIES = KNOWN_CATEGORIES

MP_INDICES = (1, 2, 3, 4, 5)
KILLED = "KILLED"

_FNAME_CAT_RE = re.compile(r"^m\d+_[a-d]\d_([A-Z]{2})\d")   # pool filename form
# Registry op-id form. P8 remediation (2026-07-09): the original anchor
# ``^[a-d][1-8]_([A-Z]{2})\d+$`` rejected the cross-source suffix introduced in
# Study-2 (e.g. ``c7_TF1_claude``), returning None and silently disabling the
# screen for the entire v5 campaign (see docs/prereg_v2/H4_DIAGNOSIS.md §2).
# The trailing ``(?:_[a-z0-9]+)*`` tolerates any ``_claude`` / ``_deepseek`` /
# ``_gpt`` source suffix so categories resolve for all v5-style ids.
_OPID_CAT_RE = re.compile(r"^[a-d][1-8]_([A-Z]{2})\d+(?:_[a-z0-9]+)*$")


def active_constrained_categories() -> frozenset:
    """Categories subject to screening under the ACTIVE registration.

    Study-2 registration screens only {CF, TF} (``CONSTRAINED_CATEGORIES``).
    A Study-3 registration may register an all-family screen (the P8
    remediation); selected via the pre-registered flag
    ``p2.config.campaign.screen_all_families_enabled()`` (default OFF => the
    Study-2 {CF,TF} scope). The scope is a per-registration choice, never
    silently widened.
    """
    from p2.config import campaign  # local import avoids any import cycle
    return ALL_FAMILIES if campaign.screen_all_families_enabled() else CONSTRAINED_CATEGORIES


# ---------------------------------------------------------------------------
# category parsing
# ---------------------------------------------------------------------------
def category_from_filename(filename: str) -> Optional[str]:
    """Operator category from a pool filename, e.g. m10_b2_CF1_claude_a02.py -> CF."""
    m = _FNAME_CAT_RE.match(Path(filename).name)
    return m.group(1) if m else None


def category_from_op_id(op_id: str) -> Optional[str]:
    """Operator category from a registry op id, e.g. b2_CF1 -> CF."""
    m = _OPID_CAT_RE.match(op_id)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# core classification (mirrors scripts/compute_s5_purity.py exactly)
# ---------------------------------------------------------------------------
def classify_flips(labels: Dict[int, str]) -> tuple[int, List[int]]:
    """Return (flip_count, sorted list of perturbed invariant indices).

    A mutant perturbs invariant k iff KILLED under MP_k. Identical to the
    S5-audit definition so admission and audit agree byte-for-byte.
    """
    flipped = sorted(int(k) for k, lab in labels.items() if lab == KILLED)
    return len(flipped), flipped


def is_single_stratum(labels: Dict[int, str]) -> bool:
    """S5-pure admission predicate: flip count <= 1 (silent, or one stratum)."""
    n, _ = classify_flips(labels)
    return n <= 1


@dataclass(frozen=True)
class AdmissionDecision:
    admitted: bool
    category: Optional[str]
    constrained: bool                       # was this category subject to screening?
    flip_count: Optional[int]               # None when not evaluated
    flipped_invariants: List[int] = field(default_factory=list)
    reason: str = ""


def decide(category: Optional[str],
           labels: Optional[Dict[int, str]] = None,
           *, constrained: Optional[frozenset] = None) -> AdmissionDecision:
    """Pure admission decision.

    ``constrained`` is the set of categories subject to screening (defaults to
    the Study-2 ``CONSTRAINED_CATEGORIES`` = {CF,TF}; pass ``ALL_FAMILIES`` for
    an all-family screen). Known-but-unconstrained categories are admitted
    without evaluation. Constrained categories require per-MP labels and are
    admitted iff single-stratum (flip <= 1).

    P8 remediation: a ``None`` category is a *parse failure* (op_id / filename
    did not resolve), NOT an "unconstrained" pass. It raises loudly rather than
    admitting silently — the exact defect that disabled the v5 screen.
    """
    constrained_set = CONSTRAINED_CATEGORIES if constrained is None else constrained
    if category is None:
        raise ValueError(
            "null operator category: op_id / filename failed to parse. A "
            "category that cannot be resolved must NEVER be silently admitted "
            "(incident P8: the v5 single-stratum screen no-op). Fix the id "
            "parsing or exclude the candidate explicitly.")
    is_constrained = category in constrained_set
    if not is_constrained:
        return AdmissionDecision(
            admitted=True, category=category, constrained=False,
            flip_count=None, flipped_invariants=[],
            reason="unconstrained-category",
        )
    if labels is None:
        raise ValueError(
            f"CF/TF admission for category={category!r} requires per-MP labels")
    n, flipped = classify_flips(labels)
    if n <= 1:
        return AdmissionDecision(
            admitted=True, category=category, constrained=True,
            flip_count=n, flipped_invariants=flipped,
            reason=f"single-stratum(flip={n})",
        )
    return AdmissionDecision(
        admitted=False, category=category, constrained=True,
        flip_count=n, flipped_invariants=flipped,
        reason=f"rejected-multistratum(flip={n}:{flipped})",
    )


# ---------------------------------------------------------------------------
# live per-mutant AVP evaluation (heavy path, reuses the S5 dispatcher)
# ---------------------------------------------------------------------------
def _load_sms_campaign():
    """Load scripts/sms_campaign.py by file path (scripts/ is not a package)."""
    root = Path(__file__).resolve().parents[3]
    path = root / "scripts" / "sms_campaign.py"
    spec = importlib.util.spec_from_file_location("_sms_campaign_filter", path)
    mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
    spec.loader.exec_module(mod)                          # type: ignore[union-attr]
    return mod


def evaluate_mutant_labels(put_id: str, mutant_path: Path,
                           repeats: int = 20) -> Dict[int, str]:
    """Run all five offline AVP checkers on ONE mutant; return {mp: label}.

    Reuses ``scripts.sms_campaign.evaluate_cell`` (the same deterministic
    offline dispatcher + majority vote as the S5 audit) by evaluating a
    singleton directory. No network; seed-42 sampler; fixed epsilon.
    """
    mutant_path = Path(mutant_path)
    sms = _load_sms_campaign()
    labels: Dict[int, str] = {}
    with tempfile.TemporaryDirectory() as td:
        dst = Path(td) / mutant_path.name
        shutil.copy(mutant_path, dst)
        for mp in MP_INDICES:
            res = sms.evaluate_cell(put_id, mp, mutant_dir=Path(td), repeats=repeats)
            by_file = {o["file"]: o["label"] for o in res["outcomes"]}
            # EQUIV / SURVIVE both count as "not perturbing invariant mp".
            labels[mp] = by_file.get(mutant_path.name, "SURVIVE")
    return labels


def screen_mutant(put_id: str, mutant_path: Path,
                  category: Optional[str] = None, repeats: int = 20,
                  evaluator: Optional[Callable[[], Dict[int, str]]] = None,
                  constrained: Optional[frozenset] = None
                  ) -> AdmissionDecision:
    """Admission gate for one mutant file.

    `evaluator` (a no-arg callable returning {mp: label}) is injectable for
    tests; when omitted the live AVP dispatcher is used. Known-but-unconstrained
    categories short-circuit and never trigger evaluation. ``constrained``
    defaults to the active registration scope
    (``active_constrained_categories()``). A category that fails to parse (None)
    raises loudly via ``decide`` (P8 remediation).
    """
    mutant_path = Path(mutant_path)
    if category is None:
        category = category_from_filename(mutant_path.name)
    constrained_set = active_constrained_categories() if constrained is None else constrained
    if category not in constrained_set:
        return decide(category, constrained=constrained_set)
    ev = evaluator or (lambda: evaluate_mutant_labels(put_id, mutant_path, repeats))
    return decide(category, ev(), constrained=constrained_set)


def make_screen_fn(repeats: int = 20) -> Callable[[Path, str], bool]:
    """Return a ``screen(path, op_id) -> bool`` suitable for
    ``pool_builder.select_mutants_for_put(..., screen_fn=...)``. Live evaluator.
    """
    def screen(path: Path, op_id: str) -> bool:
        put_id = op_id.split("_", 1)[0]
        category = category_from_op_id(op_id)
        return screen_mutant(put_id, path, category=category, repeats=repeats).admitted
    return screen


# ---------------------------------------------------------------------------
# weak spec-level textual guardrail (layer 1)
# ---------------------------------------------------------------------------
def single_stratum_prompt_clause(category: Optional[str]) -> str:
    """Prompt clause appended for CF/TF generation. Empty for other families.

    Weak on its own (an LLM cannot self-verify the invariant set); the
    deterministic post-generation screen is the load-bearing enforcement.
    """
    if category not in CONSTRAINED_CATEGORIES:
        return ""
    return (
        "\nSINGLE-STRATUM CONSTRAINT (Study-2): this operator must perturb "
        "EXACTLY ONE behavioural invariant. Localise the defect to the single "
        "specified site; do not additionally corrupt shared upstream state "
        "(the chain/target for control-flow ops, or the training data/labels "
        "for fit-data ops) in a way that would break more than one invariant. "
        "Candidates that perturb two or more invariants are rejected at "
        "admission."
    )


# ---------------------------------------------------------------------------
# audit mode over a frozen sms_track2-style matrix (validation)
# ---------------------------------------------------------------------------
def audit_matrix(matrix: dict, puts: Sequence[str],
                 constrained: Optional[frozenset] = None) -> dict:
    """Classify every mutant in an ``sms_track2``-style JSON matrix.

    ``matrix`` maps ``"{PUT}_MP{k}"`` -> cell with an ``"outcomes"`` list of
    ``{"file", "label"}``. Returns per-mutant classifications plus the set of
    multi-stratum detections (flip >= 2). Used to validate the admission logic
    against the frozen Study-1 corpus (must reproduce the known 29) and, with
    ``constrained=ALL_FAMILIES``, the frozen Study-2 v5 corpus (must flag all
    117 construct-level double-flips — the P8 all-family audit).

    ``constrained`` is the screening scope (defaults to the Study-2
    ``CONSTRAINED_CATEGORIES``). ``n_screened_candidates`` counts mutants whose
    category is in scope (the basis for the registered no-op smoke assertion:
    an all-family screen that matches ZERO candidates is a wiring failure).
    """
    from collections import defaultdict

    constrained_set = CONSTRAINED_CATEGORIES if constrained is None else constrained

    per: dict = defaultdict(dict)  # (put, file) -> {mp: label}
    for put in puts:
        for mp in MP_INDICES:
            cell = matrix.get(f"{put}_MP{mp}")
            if not cell:
                continue
            for o in cell.get("outcomes", []):
                per[(put, o["file"])][mp] = o["label"]

    per_mutant = []
    multistratum = []
    n_screened_candidates = 0
    for (put, fname), labels in sorted(per.items()):
        n, flipped = classify_flips(labels)
        category = category_from_filename(fname)
        in_scope = category in constrained_set
        if in_scope:
            n_screened_candidates += 1
        rec = {
            "put": put, "file": fname, "category": category,
            "flip_count": n, "flipped_invariants": flipped,
            "admitted": (n <= 1) or (not in_scope),
            "multistratum": n >= 2,
        }
        per_mutant.append(rec)
        if n >= 2:
            multistratum.append((put, fname, flipped))

    return {
        "n_mutants": len(per_mutant),
        "n_multistratum": len(multistratum),
        "n_screened_candidates": n_screened_candidates,
        "multistratum": multistratum,
        "per_mutant": per_mutant,
    }
