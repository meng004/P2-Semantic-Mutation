"""Study-4 pool wiring — resolve_pool_dir(v7/v7_same/v7c) + build_pools py/c.

PREREGISTRATION_STUDY4 §7 SSOT pools:
  v7      -> {put}_pool_v7      (cross-source Python arm  -> sms_track2_v7.json)
  v7_same -> {put}_pool_v7_same (same-source Python arm   -> sms_track2_v7_same.json)
  v7c     -> {put}_pool_v7c     (C-port H-LANG arm        -> sms_track2_v7c.json)

The confirmatory H4-graded analyzer needs build_pools' RENAMED filenames
(m{idx}_{op}_a{attempt}) so category_from_filename parses the operator category
— the raw study-4 cache names ({op}_srcN_attemptNN) do not. These tests prove the
rename + selection + C(.c) path work offline (no gcc, no network).
"""
import importlib.util
from pathlib import Path

from p2.mutators.stratum_filter import category_from_filename

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SMS = _load("sms_campaign_bp_test", "scripts/sms_campaign.py")
BP = _load("build_pools_bp_test", "scripts/build_pools.py")


# ── resolve_pool_dir ───────────────────────────────────────────────────────

def test_resolve_pool_dir_study4_versions():
    for pv in ("v7", "v7_same", "v7c"):
        d = SMS.resolve_pool_dir("c7", pv)
        assert d.name == f"c7_pool_{pv}", d
        assert d.parent.name == "mutants"


def test_resolve_pool_dir_v7_is_strict_no_study1_fallback():
    # A missing v7 dir must resolve to the version dir (visible inst=0), never a
    # Study-1 _pool_v3 fallback.
    assert SMS.resolve_pool_dir("a1", "v7").name == "a1_pool_v7"


# ── build_pools spec table ─────────────────────────────────────────────────

def test_version_spec_study4():
    assert BP.version_spec("v7")["suffix"] == "_pool_v7"
    assert BP.version_spec("v7")["lang"] == "py"
    assert BP.version_spec("v7_same")["suffix"] == "_pool_v7_same"
    assert BP.version_spec("v7c")["lang"] == "c"
    assert all(not BP.version_spec(v)["frozen"] for v in ("v7", "v7_same", "v7c"))


# ── build_pools: Python arm (v7) renames so category is parseable ───────────

def _write_py_mutant(cache, op_id, src, attempt):
    (cache / f"{op_id}_{src}_attempt{attempt:02d}.py").write_text(
        "def program(x):\n    return float(x) + 0.5\n")


def test_build_pools_v7_python_renames_and_categorizes(tmp_path):
    cache = tmp_path / "cache_study4" / "cross"
    cache.mkdir(parents=True)
    # study-4 vendor-neutral source tags (src1/2/3) with digits
    for src in ("src1", "src2", "src3"):
        for a in (1, 2, 3):
            _write_py_mutant(cache, "c7_OS1", src, a)
    mut = tmp_path / "mutants"
    res = BP.build_pools(["c7"], "v7", cache, mutants_dir=mut, verbose=False)
    assert res[0]["n_actual"] > 0
    pool = mut / "c7_pool_v7"
    files = sorted(f.name for f in pool.glob("*.py"))
    assert files, "no mutants copied into the pool"
    # every renamed file is category-parseable by the H4 audit
    for fn in files:
        assert category_from_filename(fn) == "OS", fn
    assert (pool / "manifest.json").exists()


# ── build_pools: C arm (v7c) globs .c, no Python re-validation ──────────────

def _write_c_mutant(cache, op_id, src, attempt):
    (cache / f"{op_id}_{src}_attempt{attempt:02d}.c").write_text(
        "double program(double x){ return x + 0.5; }\n")


def test_build_pools_v7c_c_grid(tmp_path):
    cache = tmp_path / "cache_clang"
    cache.mkdir(parents=True)
    for src in ("src1", "src2", "src3"):
        for a in (1, 2):
            _write_c_mutant(cache, "a3_SI1", src, a)
    mut = tmp_path / "mutants"
    res = BP.build_pools(["a3"], "v7c", cache, mutants_dir=mut, verbose=False)
    assert res[0]["n_actual"] > 0
    pool = mut / "a3_pool_v7c"
    cfiles = sorted(f.name for f in pool.glob("*.c"))
    assert cfiles, "no .c mutants copied into the C pool"
    assert all(fn.endswith(".c") for fn in cfiles)
    assert not list(pool.glob("*.py"))       # C pool holds no Python


def test_puts_in_cache_c_lang_detects_src_tags(tmp_path):
    cache = tmp_path / "cache_clang"
    cache.mkdir(parents=True)
    _write_c_mutant(cache, "b2_SI1", "src2", 1)
    assert BP.puts_in_cache(cache, lang="c") == ["b2"]
    assert BP.puts_in_cache(cache, lang="py") == []   # no .py present
