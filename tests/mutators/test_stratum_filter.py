"""Unit + audit tests for the CF/TF single-stratum admission filter.

The strongest test (`test_audit_reproduces_study1_29`) replays the frozen
Study-1 60-cell matrix through the filter's classifier and confirms it detects
exactly the 29 known multi-stratum mutants (and the identical file set recorded
in data/results/s5_purity_v4.json). This ties admission and the S5 audit to one
definition. The rest exercise the pure decision logic on synthetic label sets
and the pool-admission integration.
"""
import json
from pathlib import Path

import pytest

from p2.mutators import stratum_filter as sf
from p2.mutators.pool_builder import select_mutants_for_put

ROOT = Path(__file__).resolve().parents[2]

# five-MP label helpers
_SURV = {mp: "SURVIVE" for mp in sf.MP_INDICES}


def _labels(*killed_mps):
    d = dict(_SURV)
    for mp in killed_mps:
        d[mp] = "KILLED"
    return d


# ---------------------------------------------------------------------------
# pure classification
# ---------------------------------------------------------------------------
def test_classify_flips_counts_killed_only():
    assert sf.classify_flips(_labels()) == (0, [])
    assert sf.classify_flips(_labels(2)) == (1, [2])
    assert sf.classify_flips(_labels(1, 2)) == (2, [1, 2])
    assert sf.classify_flips(_labels(2, 5, 1)) == (3, [1, 2, 5])


def test_is_single_stratum_predicate():
    assert sf.is_single_stratum(_labels())          # silent
    assert sf.is_single_stratum(_labels(3))         # one stratum
    assert not sf.is_single_stratum(_labels(1, 2))  # two strata
    assert not sf.is_single_stratum(_labels(2, 5))


# ---------------------------------------------------------------------------
# category parsing
# ---------------------------------------------------------------------------
def test_category_parsers():
    assert sf.category_from_filename("m10_b2_CF1_claude_a02.py") == "CF"
    assert sf.category_from_filename("m19_d1_TF1_claude_a02.py") == "TF"
    assert sf.category_from_filename("m01_a1_CE1_claude_a02.py") == "CE"
    assert sf.category_from_op_id("b2_CF1") == "CF"
    assert sf.category_from_op_id("a2_OS1") == "OS"
    assert sf.category_from_op_id("not-an-id") is None


def test_category_from_op_id_tolerates_source_suffix():
    # P8 remediation: the cross-source suffix introduced in Study-2 must NOT make
    # the parser return None (that was the silent-no-op root cause).
    assert sf.category_from_op_id("c7_TF1_claude") == "TF"
    assert sf.category_from_op_id("a5_OS1_deepseek") == "OS"
    assert sf.category_from_op_id("b2_CF1_gpt") == "CF"
    assert sf.category_from_op_id("d1_SI1_claude") == "SI"
    # legacy suffix-free ids still resolve identically
    assert sf.category_from_op_id("b2_CF1") == "CF"


# ---------------------------------------------------------------------------
# admission decision
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cat", ["CE", "OS", "HP", "SI"])
def test_unconstrained_admitted_without_labels(cat):
    d = sf.decide(cat)  # no labels required
    assert d.admitted and not d.constrained and d.flip_count is None


def test_null_category_raises_loudly():
    # P8 remediation regression (c): a None category is a parse failure and MUST
    # raise, never silently pass as "unconstrained" (the v5 screen no-op bug).
    with pytest.raises(ValueError, match="null operator category"):
        sf.decide(None)
    with pytest.raises(ValueError, match="null operator category"):
        sf.decide(None, _labels(2, 5))


def test_constrained_requires_labels():
    with pytest.raises(ValueError):
        sf.decide("CF")  # CF/TF must supply labels


@pytest.mark.parametrize("cat", ["CF", "TF"])
def test_constrained_single_stratum_admitted(cat):
    d = sf.decide(cat, _labels(2))
    assert d.admitted and d.constrained and d.flip_count == 1


@pytest.mark.parametrize("cat,killed", [("CF", (1, 2)), ("TF", (2, 5)), ("TF", (1, 2, 5))])
def test_constrained_multistratum_rejected(cat, killed):
    d = sf.decide(cat, _labels(*killed))
    assert not d.admitted and d.constrained and d.flip_count == len(killed)
    assert "rejected-multistratum" in d.reason


def test_constrained_silent_admitted():
    # A CF/TF mutant that perturbs nothing (flip 0) is single-stratum-clean.
    d = sf.decide("CF", _labels())
    assert d.admitted and d.flip_count == 0


# ---------------------------------------------------------------------------
# screen_mutant with an injected (offline) evaluator
# ---------------------------------------------------------------------------
def test_screen_mutant_injected_evaluator_rejects_multi(tmp_path):
    f = tmp_path / "m10_b2_CF1_claude_a02.py"
    f.write_text("def program(x):\n    return float(x)\n")
    dec = sf.screen_mutant("b2", f, evaluator=lambda: _labels(1, 2))
    assert not dec.admitted and dec.flipped_invariants == [1, 2]


def test_screen_mutant_injected_evaluator_admits_single(tmp_path):
    f = tmp_path / "m10_b2_CF1_claude_a02.py"
    f.write_text("def program(x):\n    return float(x)\n")
    dec = sf.screen_mutant("b2", f, evaluator=lambda: _labels(2))
    assert dec.admitted and dec.flip_count == 1


def test_screen_mutant_unconstrained_never_evaluates(tmp_path):
    f = tmp_path / "m01_a2_CE1_claude_a02.py"
    f.write_text("def program(x):\n    return float(x)\n")

    def _boom():
        raise AssertionError("evaluator must not run for CE")

    dec = sf.screen_mutant("a2", f, evaluator=_boom)
    assert dec.admitted and not dec.constrained


# ---------------------------------------------------------------------------
# weak prompt clause
# ---------------------------------------------------------------------------
def test_prompt_clause_only_for_cftf():
    assert sf.single_stratum_prompt_clause("CE") == ""
    assert sf.single_stratum_prompt_clause("OS") == ""
    assert "SINGLE-STRATUM CONSTRAINT" in sf.single_stratum_prompt_clause("CF")
    assert "SINGLE-STRATUM CONSTRAINT" in sf.single_stratum_prompt_clause("TF")


# ---------------------------------------------------------------------------
# pool-admission integration (screen_fn wired into select_mutants_for_put)
# ---------------------------------------------------------------------------
def test_select_mutants_screen_excludes_rejected(tmp_path):
    # two valid CF candidates for a fake PUT; screen rejects the "bad" one.
    good = tmp_path / "b2_CF1_claude_attempt01.py"
    bad = tmp_path / "b2_CF1_claude_attempt02.py"
    for p in (good, bad):
        p.write_text("def program(x):\n    return float(x)\n")

    def screen(path, op_id):
        return "attempt02" not in path.name  # reject the multi-stratum one

    kept = select_mutants_for_put("b2", 5, tmp_path, seed=42, screen_fn=screen)
    names = {p.name for p, _ in kept}
    assert good.name in names and bad.name not in names


def test_select_mutants_no_screen_is_unchanged(tmp_path):
    a = tmp_path / "b2_CF1_claude_attempt01.py"
    a.write_text("def program(x):\n    return float(x)\n")
    kept = select_mutants_for_put("b2", 5, tmp_path, seed=42)  # screen_fn=None
    assert {p.name for p, _ in kept} == {a.name}


# ---------------------------------------------------------------------------
# AUDIT-MODE VALIDATION — strongest test: reproduce the known 29 on Study-1
# ---------------------------------------------------------------------------
def test_audit_reproduces_study1_29():
    matrix = json.loads(
        (ROOT / "data/results/sms_track2_v4.json").read_text())
    puts = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]
    audit = sf.audit_matrix(matrix, puts)

    assert audit["n_mutants"] == 292
    assert audit["n_multistratum"] == 29, audit["n_multistratum"]

    # every multi-stratum detection is a CF or TF mutant
    cats = {sf.category_from_filename(f) for _, f, _ in audit["multistratum"]}
    assert cats == {"CF", "TF"}, cats

    # byte-identical file set to the frozen S5 SSOT
    s5 = json.loads((ROOT / "data/results/s5_purity_v4.json").read_text())
    s5_multi = {
        (put, fn)
        for put, rec in s5["per_put"].items()
        for fn in rec["multistratum_detail"]
    }
    audit_multi = {(put, fn) for put, fn, _ in audit["multistratum"]}
    assert audit_multi == s5_multi
    assert len(s5_multi) == 29


def test_audit_admission_matches_flip_rule():
    # In audit mode, a CF/TF multi-stratum mutant is NOT admitted; a pure or
    # silent one is; and CE/OS/HP/SI are always admitted regardless of flips.
    matrix = json.loads(
        (ROOT / "data/results/sms_track2_v4.json").read_text())
    puts = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]
    audit = sf.audit_matrix(matrix, puts)
    rejected = [r for r in audit["per_mutant"] if not r["admitted"]]
    assert len(rejected) == 29
    assert all(r["category"] in ("CF", "TF") and r["flip_count"] >= 2
               for r in rejected)


# ---------------------------------------------------------------------------
# ALL-FAMILY SCREEN SCOPE (Study-3 P8 remediation)
# ---------------------------------------------------------------------------
def test_all_family_scope_screens_os_and_si():
    # Under the all-family scope, previously-unconstrained OS/SI become
    # screenable: a multi-stratum OS/SI mutant is rejected; a single one admitted.
    for cat in ("OS", "SI"):
        rej = sf.decide(cat, _labels(2, 5), constrained=sf.ALL_FAMILIES)
        assert not rej.admitted and rej.constrained and rej.flip_count == 2
        ok = sf.decide(cat, _labels(2), constrained=sf.ALL_FAMILIES)
        assert ok.admitted and ok.constrained
    # default scope still admits OS/SI unconditionally (Study-2 behaviour)
    assert sf.decide("OS", _labels(2, 5)).admitted


def test_active_constrained_categories_config(monkeypatch):
    monkeypatch.delenv("P2_SCREEN_ALL_FAMILIES", raising=False)
    assert sf.active_constrained_categories() == sf.CONSTRAINED_CATEGORIES
    monkeypatch.setenv("P2_SCREEN_ALL_FAMILIES", "1")
    assert sf.active_constrained_categories() == sf.ALL_FAMILIES
    assert sf.ALL_FAMILIES == frozenset({"CE", "OS", "HP", "TF", "SI", "CF"})


# ---------------------------------------------------------------------------
# AUDIT-MODE VALIDATION — Study-2 v5: all-family screen flags the known 117
# ---------------------------------------------------------------------------
def test_all_family_audit_flags_study2_v5_117():
    """Regression (a): the 117 committed multi-stratum v5 mutants are correctly
    categorised (op_id parser fixed) AND would be flagged/rejected by an
    all-family screen in audit mode. Validated against the frozen SSOT
    data/results/h4_leakage_diagnosis_v5.json (which this must NOT alter)."""
    matrix = json.loads((ROOT / "data/results/sms_track2_v5.json").read_text())
    diag = json.loads(
        (ROOT / "data/results/h4_leakage_diagnosis_v5.json").read_text())
    puts = sorted({k.split("_MP")[0] for k in matrix})
    assert len(puts) == 28

    audit = sf.audit_matrix(matrix, puts, constrained=sf.ALL_FAMILIES)

    # the all-family screen actually matched candidates (no silent no-op)
    assert audit["n_screened_candidates"] > 0

    # exactly the 117 known double-flips are flagged, byte-identical file set
    diag_files = {(r["put"], r["file"]) for r in diag["per_mutant"]}
    audit_files = {(p, f) for p, f, _ in audit["multistratum"]}
    assert len(diag_files) == 117
    assert audit_files == diag_files

    # every one is rejected (not admitted) under the all-family scope
    flagged = {(r["put"], r["file"]) for r in audit["per_mutant"]
               if not r["admitted"]}
    assert flagged == diag_files

    # family breakdown matches the diagnosis (OS 27, CF 9, TF 72, SI 9)
    from collections import Counter
    fam = Counter(sf.category_from_filename(f) for _, f, _ in audit["multistratum"])
    assert dict(fam) == {"OS": 27, "CF": 9, "TF": 72, "SI": 9}

    # the fixed op_id parser now resolves every v5-style build id (was all None)
    opids = {r["build_op_id"] for r in diag["per_mutant"]}
    assert all(sf.category_from_op_id(o) is not None for o in opids)


def test_default_scope_audit_v5_only_flags_cf_tf_screenable():
    # Under the Study-2 DEFAULT {CF,TF} scope, the audit rejects only the CF/TF
    # double-flips (81), leaving OS/SI (36) admitted — the by-design coverage gap
    # the all-family scope closes. Confirms the two scopes are distinct.
    matrix = json.loads((ROOT / "data/results/sms_track2_v5.json").read_text())
    puts = sorted({k.split("_MP")[0] for k in matrix})
    audit = sf.audit_matrix(matrix, puts)  # default {CF,TF}
    rejected = [r for r in audit["per_mutant"] if not r["admitted"]]
    assert all(r["category"] in ("CF", "TF") for r in rejected)
    assert len(rejected) == 81
