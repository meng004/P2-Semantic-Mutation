"""Build per-PUT mutant pools ``data/mutants/{put}{suffix}/`` from an operator cache.

Pool versions (suffix / cache / N-per-PUT / Study):

  v2  _pool      cache        12   Study-1 (FROZEN)
  v3  _pool_v3   cache        30   Study-1 (FROZEN)
  v4  _pool_v4   cache_cross  30   Study-2 (cross-source arm)
  v5  _pool_v5   cache_cross  30   Study-2 (confirmatory / calibration-pilot)

The Study-2 versions (v4/v5) apply the CF/TF single-stratum admission filter
(docs/prereg_v2/CFTF_CONSTRAINT.md) when ``single_stratum_filter_enabled()``.
Study-1 pools (v2/v3) are IMMUTABLE frozen artefacts and are never re-screened.

SAFETY (see docs/prereg_v2/PILOT_LOG.md, incident #1 — the Study-1 v3 wipe):
  * Refuses to run against an EMPTY cache unless ``--allow-empty``.
  * Never OVERWRITES a populated pool with an empty rebuild (a per-PUT empty
    selection is skipped, leaving the existing pool untouched, unless
    ``--allow-empty``).
  * Never deletes a pool directory whose version suffix differs from the one
    being built (``_assert_version_match``).
  * Refuses to (re)build a FROZEN Study-1 version (v2/v3) unless
    ``--allow-frozen`` is passed explicitly.

Records (path, op_id, attempt_idx) provenance to each pool's manifest.json.

Backward compatibility: ``POOL_VERSION`` env still works as the default for
``--pool-version`` (the CLI flag wins when both are given). ``--puts`` defaults
to auto-detection from the cache when omitted (no hardcoded PUT list).
"""
import argparse
import json
import os
import re
import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.pool_builder import select_mutants_for_put
from p2.config.campaign import single_stratum_filter_enabled

# Registration master seed (PREREGISTRATION_STUDY2_v1.1.md §Status). Immaterial
# to the pilot: both pilot PUTs have < N candidates so every eligible mutant is
# taken (min(N, available)); selection order only matters when subsetting.
REGISTERED_SEED = 20260708

# suffix / cache subdir / N-per-PUT / frozen(Study-1) per pool version.
_VERSION_SPEC = {
    "v2": {"suffix": "_pool",    "cache": "cache",       "n": 12, "frozen": True},
    "v3": {"suffix": "_pool_v3", "cache": "cache",       "n": 30, "frozen": True},
    "v4": {"suffix": "_pool_v4", "cache": "cache_cross", "n": 30, "frozen": False},
    "v5": {"suffix": "_pool_v5", "cache": "cache_cross", "n": 30, "frozen": False},
    # Study-3 (v2.0): fresh validated pool built under the P8-remediated
    # all-family screen (P2_SCREEN_ALL_FAMILIES=1). Same N/cache as v4/v5; v5 is
    # a frozen artefact and is never touched by a v6 build.
    "v6": {"suffix": "_pool_v6", "cache": "cache_cross", "n": 30, "frozen": False},
}
# Study-2/3 pool versions the single-stratum filter applies to.
_STUDY2_VERSIONS = frozenset({"v4", "v5", "v6"})

_ATTEMPT_RE = re.compile(r"^([a-d]\d+)_[A-Z]+\d+_[a-z]+_attempt\d+\.py$")


def version_spec(version: str) -> dict:
    """Return the (suffix, cache, n, frozen) spec for a pool version."""
    if version not in _VERSION_SPEC:
        raise ValueError(
            f"unknown pool version {version!r}; known: {sorted(_VERSION_SPEC)}")
    return _VERSION_SPEC[version]


def puts_in_cache(cache_dir: Path) -> list:
    """Auto-detect PUT ids present in a cache directory (sorted, unique)."""
    puts = set()
    for fp in cache_dir.glob("*_attempt*.py"):
        m = _ATTEMPT_RE.match(fp.name)
        if m:
            puts.add(m.group(1))
    return sorted(puts)


def _assert_version_match(pool_dir: Path, suffix: str) -> None:
    """Guard: refuse to delete a pool dir that is not the requested version.

    Prevents the Study-1 wipe class of incident — a v5 build must only ever
    remove a ``_pool_v5`` directory, never a frozen ``_pool_v3`` one.
    """
    name = pool_dir.name
    if not name.endswith(suffix):
        raise RuntimeError(
            f"SAFETY: refusing to delete {name!r} — its suffix does not match "
            f"the requested pool suffix {suffix!r} (wrong-version deletion guard)")
    # Also reject a longer suffix collision, e.g. suffix '_pool' matching
    # '_pool_v3' by endswith. The residual before the suffix must be a PUT id.
    residual = name[: -len(suffix)]
    if not re.fullmatch(r"[a-d]\d+", residual):
        raise RuntimeError(
            f"SAFETY: refusing to delete {name!r} — residual {residual!r} is not "
            f"a bare PUT id for suffix {suffix!r} (wrong-version deletion guard)")


def build_pools(puts, version, cache_dir, mutants_dir=None, seed=REGISTERED_SEED,
                allow_empty=False, allow_frozen=False, screen_fn=None,
                verbose=True):
    """Build pools for ``puts`` at ``version`` from ``cache_dir``.

    Returns a list of per-PUT result dicts. Raises RuntimeError on the
    frozen-version and empty-cache safety gates.
    """
    spec = version_spec(version)
    suffix, n_per_put, frozen = spec["suffix"], spec["n"], spec["frozen"]
    mutants_dir = Path(mutants_dir) if mutants_dir else ROOT / "data/mutants"
    cache_dir = Path(cache_dir)

    if frozen and not allow_frozen:
        raise RuntimeError(
            f"SAFETY: {version} is a FROZEN Study-1 pool version — refusing to "
            f"rebuild it. Pass allow_frozen=True (CLI: --allow-frozen) only if "
            f"you really intend to touch immutable Study-1 artefacts.")

    if not cache_dir.exists() or not any(cache_dir.glob("*_attempt*.py")):
        if not allow_empty:
            raise RuntimeError(
                f"SAFETY: cache {cache_dir} is empty/absent — refusing to build "
                f"(this would wipe existing pools and rebuild them empty). Pass "
                f"allow_empty=True (CLI: --allow-empty) to override.")

    if screen_fn is None and single_stratum_filter_enabled() and version in _STUDY2_VERSIONS:
        from p2.mutators.stratum_filter import make_screen_fn
        screen_fn = make_screen_fn(repeats=20)

    if verbose:
        print(f"Building version={version} suffix={suffix} N={n_per_put} "
              f"cache={cache_dir.name} seed={seed} "
              f"puts={puts} "
              f"single_stratum_filter={'ON' if screen_fn else 'OFF'}")

    results = []
    for put_id in puts:
        pool_dir = mutants_dir / f"{put_id}{suffix}"
        # Select FIRST (no deletion yet) so an empty result cannot destroy an
        # existing populated pool.
        selected = select_mutants_for_put(put_id, n_per_put, cache_dir, seed=seed,
                                          screen_fn=screen_fn)
        if not selected and not allow_empty:
            if verbose:
                print(f"{put_id}: 0 eligible mutants — SKIP (existing pool left "
                      f"untouched; pass --allow-empty to force an empty pool)")
            results.append({"put": put_id, "n_actual": 0, "skipped": True,
                            "pool_dir": str(pool_dir)})
            continue
        if pool_dir.exists():
            _assert_version_match(pool_dir, suffix)
            shutil.rmtree(pool_dir)
        pool_dir.mkdir(parents=True)
        manifest = []
        for idx, (src_path, op_id) in enumerate(selected, 1):
            attempt = src_path.stem.split("_attempt")[1]
            dest_name = f"m{idx:02d}_{op_id}_a{attempt}.py"
            shutil.copy(src_path, pool_dir / dest_name)
            try:
                relpath = str(src_path.relative_to(ROOT))
            except ValueError:            # cache outside ROOT (e.g. tmp in tests)
                relpath = str(src_path)
            manifest.append({
                "rank": idx, "filename": dest_name,
                "operator": op_id, "attempt_idx": int(attempt),
                "source_relpath": relpath,
            })
        (pool_dir / "manifest.json").write_text(
            json.dumps({"put": put_id, "version": version,
                        "n_target": n_per_put, "n_actual": len(selected),
                        "seed": seed, "single_stratum_filter": bool(screen_fn),
                        "mutants": manifest},
                       indent=2, ensure_ascii=False)
        )
        if verbose:
            print(f"{put_id}: {len(selected)} mutants → {pool_dir}")
        results.append({"put": put_id, "n_actual": len(selected),
                        "skipped": False, "pool_dir": str(pool_dir)})
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool-version", "--pool_version", dest="pool_version",
                   default=os.environ.get("POOL_VERSION"),
                   help="pool version (v2/v3/v4/v5). Defaults to $POOL_VERSION.")
    p.add_argument("--puts", default=None,
                   help="comma-separated PUT ids (e.g. a2,b4). Default: "
                        "auto-detect from the cache dir.")
    p.add_argument("--cache-dir", dest="cache_dir", default=None,
                   help="explicit mutant cache dir (default: derived from version "
                        "— cache_cross for v4/v5, cache for v2/v3).")
    p.add_argument("--mutants-dir", dest="mutants_dir", default=None,
                   help="explicit output root for pools (default data/mutants).")
    p.add_argument("--pool-suffix", dest="pool_suffix", default=None,
                   help="override the pool directory suffix (default: derived "
                        "from version). Must be consistent with --pool-version.")
    p.add_argument("--seed", type=int, default=REGISTERED_SEED,
                   help=f"selection seed (default {REGISTERED_SEED}, registration).")
    p.add_argument("--allow-empty", dest="allow_empty", action="store_true",
                   help="permit running against an empty cache / writing empty pools.")
    p.add_argument("--allow-frozen", dest="allow_frozen", action="store_true",
                   help="permit (re)building a FROZEN Study-1 version (v2/v3).")
    args = p.parse_args(argv)

    if not args.pool_version:
        p.error("no pool version: pass --pool-version or set $POOL_VERSION")
    version = args.pool_version
    spec = version_spec(version)

    if args.pool_suffix and args.pool_suffix != spec["suffix"]:
        p.error(f"--pool-suffix {args.pool_suffix!r} conflicts with version "
                f"{version} (expected {spec['suffix']!r}). Change --pool-version "
                f"instead of forcing an inconsistent suffix.")

    cache_dir = (Path(args.cache_dir) if args.cache_dir
                 else ROOT / "data/operator_campaign" / spec["cache"])
    if args.puts:
        puts = [s.strip() for s in args.puts.split(",") if s.strip()]
    else:
        puts = puts_in_cache(cache_dir)
        if not puts:
            p.error(f"no PUTs given and none auto-detected in {cache_dir}")

    build_pools(puts, version, cache_dir,
                mutants_dir=args.mutants_dir, seed=args.seed,
                allow_empty=args.allow_empty, allow_frozen=args.allow_frozen)


if __name__ == "__main__":
    main()
