"""Regression test for the SMS -> MS degeneration theorem.

Main text: Theorem \\ref{thm:degeneration} (Section "Degeneration to
Classical Mutation Score"). Supplementary: Appendix G.2 (degenerate-limit
definition, joint conditions L1-L6), Lemmas G.1-G.3, Theorem G.

This module registers the finite-sample instantiation of the degenerate
limit L = L_equiv ^ L_killed ^ L_mut as ``DEGENERATION_L`` and asserts,
on real committed Study-1 v4 mutant pools, that the semantic pipeline's
SMS equals the classical Mutation Score both per-program and per-mutant.

Axis-by-axis realization of the registered configuration:

- L1 (epsilon_eq -> 0): epsilon_eq = 1e-6, the production bitwise
  tolerance (scripts/sms_campaign.py EPSILON_EQ).
- L2 (K_eq -> infinity): the E2 sample set X_eq and the classical
  test-input set T are drawn from the same D_S; classical equivalence is
  judged on X_eq union T, so the equivalence layer and the classical
  oracle observe the same finite input evidence (the almost-everywhere
  limit collapses to exact set equality on finite samples).
- L3 (epsilon_AVP -> 0): epsilon_avp = epsilon_eq = 1e-6 (the
  is_equivalent contract requires equality of the two tolerances).
- L4 (MR set = {MR_eq}, R(y, y') == y = y'): the MR set collapses to a
  single MR_eq with r = id and R = equality within epsilon. Following
  supplementary Lemma G.2, MR_eq is evaluated with the original program
  as reference oracle: AVP(P, MR_eq) = pass iff P matches S_i on the
  classical test-input set T. The AVP dispatcher is rebound to this
  MP_eq verifier for the duration of the test; is_equivalent (E1 ^ E2),
  is_killed (OR-aggregation), run_one_cell (three-state decomposition),
  and compute_sms (denominator arithmetic) run unmodified.
- L5 (rule-based syntactic operators): the committed Study-1 v4 pools
  (data/mutants/{put}_pool_v4, local-edit CE/HP/OS/SI substitution
  operators, V1-V4 mechanically validated).
- L6 (imperative deterministic PUTs): class-A PUTs a1 (Lorenz ODE),
  a2 (LU decomposition), a3 (FDM heat equation); determinism is spot
  checked, and all programs are memoized so that the semantic and the
  classical side observe identical outputs per input.

Expected consequence of Theorem G under this configuration: the
pipeline's three-state decomposition (equiv / killed / survive) matches
the classical decomposition mutant-for-mutant, and therefore
SMS_{i,k,j} == MS_{i,j} exactly for every PUT.
"""

import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import p2.equiv.avp_coherent as avp_coherent_mod
import p2.lrca.killed as killed_mod
from p2.avp.interface import MR, AVPResult
from p2.equiv.sampler import UniformSampler, sample_inputs
from p2.pipeline.run_cell import run_one_cell
from p2.stats.sms import compute_sms

# Sentinel MP index for the degenerate MP_eq stratum (L4). It is not one
# of the five domain MP indices; the rebound dispatcher accepts only it.
MP_EQ_INDEX = 0


@dataclass(frozen=True)
class DegenerationConfig:
    """Registered finite-sample instantiation of the degenerate limit L.

    Fields map one-to-one onto the joint conditions of supplementary
    Appendix G.2 (see module docstring).
    """

    epsilon_eq: float        # L1
    k_eq: int                # L2 (E2 sample budget)
    n_test_inputs: int       # L2 (classical test-input set T)
    epsilon_avp: float       # L3
    mr_name: str             # L4
    pool_version: str        # L5
    puts: tuple              # L6
    sampler_low: float
    sampler_high: float
    seed_eq: int
    seed_test: int


DEGENERATION_L = DegenerationConfig(
    epsilon_eq=1e-6,
    k_eq=40,
    n_test_inputs=16,
    epsilon_avp=1e-6,
    mr_name="MR_eq",
    pool_version="v4",
    puts=("a1", "a2", "a3"),
    sampler_low=0.05,
    sampler_high=0.95,
    seed_eq=42,
    seed_test=7,
)


class _Memo:
    """Memoizing wrapper: every program is evaluated once per input, so
    the semantic pipeline and the classical reference observe identical
    outputs (the L6 deterministic restriction, enforced by construction).
    """

    def __init__(self, fn):
        self.fn = fn
        self.cache = {}

    def __call__(self, x):
        key = float(x)
        if key not in self.cache:
            self.cache[key] = self.fn(key)
        return self.cache[key]


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_put(put_id):
    return _load_module(
        f"_degen_put_{put_id}", ROOT / "src" / "p2" / "puts" / f"{put_id}.py"
    ).program


def _load_pool(put_id, pool_version):
    pool_dir = ROOT / "data" / "mutants" / f"{put_id}_pool_{pool_version}"
    mutants = []
    for py_file in sorted(pool_dir.glob("*.py")):
        mod = _load_module(f"_degen_mut_{put_id}_{py_file.stem}", py_file)
        mutants.append((py_file.name, mod.program))
    return mutants


def _scalar(x):
    return x[0] if getattr(x, "shape", None) == (1,) else x


def _mr_eq(epsilon):
    """L4: single MR_eq, r = id, R(y, y') = ||y - y'|| <= epsilon."""

    def r_identity(x):
        return x

    def R_equality(y, y_prime):
        return bool(
            np.linalg.norm(
                np.asarray(y, dtype=float).flatten()
                - np.asarray(y_prime, dtype=float).flatten()
            )
            <= epsilon
        )

    return MR(r=r_identity, R=R_equality, mp_index=MP_EQ_INDEX, name="MR_eq")


def _make_degenerate_call_avp(oracle, test_inputs):
    """Degenerate AVP for the MP_eq stratum (supplementary Lemma G.2):
    AVP(P, MR_eq) = pass iff for every x in T, R(S_i(r(x)), P(r(x))) holds,
    with the original program S_i as reference oracle. In particular
    AVP(S_i, MR_eq) = pass identically, so the killed predicate
    "AVP(S_i) = pass and AVP(s') = fail" is exactly classical difference
    detection on T.
    """

    def call_avp_eq(program, mr, epsilon):
        if mr.mp_index != MP_EQ_INDEX:
            raise ValueError(
                f"Degenerate limit admits only MP_eq (index {MP_EQ_INDEX}); "
                f"got {mr.mp_index}"
            )
        for x in test_inputs:
            x_in = _scalar(x)
            y_ref = np.asarray(oracle(mr.r(x_in)), dtype=float).flatten()
            y_prog = np.asarray(program(mr.r(x_in)), dtype=float).flatten()
            if not mr.R(y_ref, y_prog):
                return AVPResult.FAIL
        return AVPResult.PASS

    return call_avp_eq


def _differs(orig, mutant, inputs, epsilon):
    """Classical difference detection: exists x with ||S(x) - s'(x)|| > eps.

    Uses the same norm-and-tolerance comparison as p2.equiv.output_equiv
    so that the classical reference and the pipeline agree on boundary
    and NaN semantics.
    """
    for x in inputs:
        x_in = _scalar(x)
        y_orig = np.asarray(orig(x_in), dtype=float).flatten()
        y_mut = np.asarray(mutant(x_in), dtype=float).flatten()
        if np.linalg.norm(y_orig - y_mut) > epsilon:
            return True
    return False


def test_degeneration_configuration_registered():
    """The registered configuration matches the theorem's axes and the
    committed Study-1 v4 pools it names exist on disk."""
    cfg = DEGENERATION_L
    # L1 == L3 realization: the is_equivalent contract requires
    # epsilon_eq == epsilon_avp.
    assert cfg.epsilon_eq == cfg.epsilon_avp
    assert cfg.mr_name == "MR_eq"
    assert cfg.pool_version == "v4"
    for put_id in cfg.puts:
        pool_dir = ROOT / "data" / "mutants" / f"{put_id}_pool_{cfg.pool_version}"
        assert pool_dir.is_dir(), f"missing committed pool {pool_dir}"
        manifest = json.loads((pool_dir / "manifest.json").read_text())
        assert manifest["put"] == put_id
        assert manifest["mutants"], f"empty manifest for {put_id}"
        assert list(pool_dir.glob("*.py")), f"no mutant files in {pool_dir}"


@pytest.mark.parametrize("put_id", DEGENERATION_L.puts)
def test_sms_equals_ms_under_degeneration(put_id, monkeypatch):
    """Theorem thm:degeneration: under the registered degenerate limit,
    SMS == MS per-program and the three-state decomposition matches the
    classical decomposition per-mutant, on the committed v4 pools."""
    cfg = DEGENERATION_L

    put = _Memo(_load_put(put_id))
    named_mutants = _load_pool(put_id, cfg.pool_version)
    assert named_mutants, f"no committed mutants for {put_id}"
    mutants = [_Memo(program) for _, program in named_mutants]

    sampler = UniformSampler(
        low=cfg.sampler_low, high=cfg.sampler_high, dim=1, seed=cfg.seed_eq
    )
    x_eq = sample_inputs(sampler, cfg.k_eq)
    t_inputs = UniformSampler(
        low=cfg.sampler_low, high=cfg.sampler_high, dim=1, seed=cfg.seed_test
    ).sample(cfg.n_test_inputs)

    # Two deterministic boundary controls so that the equality is
    # exercised on all three states of the decomposition, not only on
    # killed mutants (the committed a-class v4 pools contain no
    # equivalent or surviving mutants under this configuration):
    # (i) identity control: the PUT itself must be judged equivalent by
    #     E1 ^ E2 and excluded from the denominator on both sides
    #     (Lemma G.1 direction);
    # (ii) point-defect control: differs from the PUT only on one input
    #     that lies in X_eq but not in T, so it must be non-equivalent
    #     yet undetected, i.e. a survivor, on both sides.
    x_defect = float(_scalar(x_eq[0]))
    raw_put_for_defect = _load_put(put_id)

    def point_defect(x):
        y = raw_put_for_defect(float(x))
        return y + 1.0 if float(x) == x_defect else y

    idx_identity = len(mutants)
    mutants.append(put)
    idx_defect = len(mutants)
    mutants.append(_Memo(point_defect))
    n = len(mutants)

    # L6 spot check: the PUT is deterministic on repeated evaluation.
    raw_put = _load_put(put_id)
    for x in x_eq[:3]:
        x_in = float(_scalar(x))
        assert raw_put(x_in) == raw_put(x_in)

    # L4: rebind the AVP dispatcher to the MP_eq verifier in both
    # consumer namespaces (E1 arm and killed predicate).
    call_avp_eq = _make_degenerate_call_avp(put, t_inputs)
    monkeypatch.setattr(avp_coherent_mod, "call_avp", call_avp_eq)
    monkeypatch.setattr(killed_mod, "call_avp", call_avp_eq)

    # Semantic pipeline, unmodified machinery.
    result = run_one_cell(
        put=put,
        mutants=mutants,
        mr_set=[_mr_eq(cfg.epsilon_avp)],
        cell_id=f"{put_id}_MPeq_{cfg.pool_version}",
        sampler=sampler,
        k_eq=cfg.k_eq,
        epsilon_eq=cfg.epsilon_eq,
        epsilon_avp=cfg.epsilon_avp,
    )

    # Classical reference, computed independently of the pipeline:
    # equiv^classic = output-equal on all observed inputs (X_eq union T);
    # killed^classic = difference detected on the test-input set T.
    equiv_classic = []
    killed_classic = []
    for idx, mutant in enumerate(mutants):
        differs_on_eq = _differs(put, mutant, x_eq, cfg.epsilon_eq)
        differs_on_t = _differs(put, mutant, t_inputs, cfg.epsilon_avp)
        if not differs_on_eq and not differs_on_t:
            equiv_classic.append(idx)
        elif differs_on_t:
            killed_classic.append(idx)

    # Per-mutant: the three-state decomposition coincides exactly.
    assert result.equiv_indices == equiv_classic
    assert result.killed_indices == killed_classic
    assert result.inst_count == n
    assert (
        result.equiv_count + result.killed_count + result.survive_count == n
    )

    # Boundary controls landed where the theorem requires, on both sides.
    assert idx_identity in result.equiv_indices
    assert idx_identity in equiv_classic
    assert idx_defect not in result.equiv_indices
    assert idx_defect not in result.killed_indices
    assert idx_defect not in killed_classic  # survivor on both sides
    assert result.survive_count >= 1

    # Per-program: SMS == MS through the SSOT formula.
    denom = n - len(equiv_classic)
    assert denom > 0, f"degenerate cell for {put_id} has empty denominator"
    ms_classic = compute_sms(len(killed_classic), n, len(equiv_classic))
    assert not math.isnan(ms_classic)
    assert result.sms == pytest.approx(ms_classic, rel=0, abs=0)
