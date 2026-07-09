"""Study-2 campaign feature flags (pre-registered defaults).

single_stratum_filter_enabled():
    When ON, the CF/TF single-stratum admission filter
    (``p2.mutators.stratum_filter``) screens every generated CF/TF mutant
    BEFORE it enters a pool: a candidate is admitted iff its offline
    invariant-flip count is <= 1 (see docs/prereg_v2/CFTF_CONSTRAINT.md).
    Default ON for Study 2 per PREREGISTRATION_STUDY2. The four local-edit
    families (CE/OS/HP/SI) are never screened.

    Study-1 artefacts are immutable and are never re-screened. The flag gates
    only the Study-2 generation path (cross + same arms, applied identically).

    Override with the env var ``P2_SINGLE_STRATUM_FILTER`` (``0``/``off``/``false``
    to disable — a disclosed deviation from registration).
"""
import os

_OFF = {"0", "off", "false", "no", ""}


def single_stratum_filter_enabled() -> bool:
    return os.environ.get("P2_SINGLE_STRATUM_FILTER", "1").strip().lower() not in _OFF


def screen_all_families_enabled() -> bool:
    """All-family single-stratum screen scope (Study-3 P8 remediation).

    OFF by default => the Study-2 registered scope
    (``p2.mutators.stratum_filter.CONSTRAINED_CATEGORIES`` = {CF, TF}). A
    Study-3 registration turns it ON (all six known families screened at
    admission) via ``P2_SCREEN_ALL_FAMILIES=1``. The screen scope is a
    per-registration choice and is never silently widened. See
    docs/prereg_v2/H4_DIAGNOSIS.md §2 (incident P8) and
    docs/prereg_v2/PREREGISTRATION_STUDY3_v2.md (H4''-strict).
    """
    return os.environ.get("P2_SCREEN_ALL_FAMILIES", "0").strip().lower() not in _OFF
