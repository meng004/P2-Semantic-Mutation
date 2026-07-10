"""Family-XL PILOT operator specs — CALIBRATION OUTPUT, not a frozen registry.

STATUS (read this first)
------------------------
PREREGISTRATION_STUDY5_v1.md registers the XL pilot (§2e: pairs = the first
two certified roster pairs on two different programs AND languages =
invsqrt.cpp + brent.c per Amendment A1 §9; 1 attempt/operator/slot; pool tag
``v8xl_pilot``) and the XL admission gate (§2c V1–V3), but it does NOT fix
the XL mutation-operator specifications anywhere in §5 — the Study-4 C arm
reused the 12-PUT registry verbatim because its PUTs were ports of the same
programs, an option that does not exist for the external XL corpus. These
pilot specs are therefore authored NOW, as the pilot's calibration output
(clearly labeled), following the registered Study-4 C-arm PATTERN:

* language-agnostic operator semantics rendered per program,
* the registered spec fields (id / category / label / target_locator /
  transformation / rationale) of ``p2.mutators.operator_registry``,
* 3 operators per program, whose targeted strata cover the pair's PRIMARY
  stratum (frozen roster ``primary_mp``) plus two other registry-instantiable
  strata (``target_mp`` below is a design-intent label, not an analysis key).

The CONFIRMATORY XL operator specs must be frozen in a dated §10 entry BEFORE
the confirmatory generation wave; nothing here licenses a confirmatory draw.
Per the §2e firewall these specs may be revised for the confirmatory freeze
only as code/design-debt fixes logged P15+ — never against any pilot SMS
outcome.

Authored 2026-07-10, BEFORE any XL mutant existed (one-shot discipline:
each (operator, slot) is drawn once).
"""
from __future__ import annotations

from p2.mutators.operator_registry import MutationOperator

# Operator ids use the PROGRAM name (shared semantics across that program's
# language pairs, exactly like the Study-4 C arm reused per-program operator
# semantics across languages). Filenames become
# ``{op_id}_{slot}_attemptNN.{ext}`` inside a PER-PAIR cache directory, so
# pairs of the same program never collide.

XL_PILOT_OPERATORS: list[MutationOperator] = [
    # ── invsqrt (pair invsqrt.cpp; primary MP5 f_conv.rate; instantiable
    #    strata {1,2,4,5} per the frozen A1 registry) ─────────────────────
    MutationOperator(
        id="invsqrt_CF1", put="invsqrt", category="CF",
        label="Newton refinement skipped (1 iteration -> 0)",
        target_locator="the Newton-iteration refinement loop/step of the "
                       "fast inverse-square-root routine",
        transformation="remove (or never execute) the single Newton "
                       "refinement iteration so the raw magic-constant "
                       "initial guess is returned unrefined",
        rationale="dropping the refinement pass is a classic performance "
                  "'optimisation' mistake; it inflates the surrogate error "
                  "from ~0.2% to ~3.4%, breaking the method's documented "
                  "fidelity band (target stratum MP5 f_conv.rate, PRIMARY)",
    ),
    MutationOperator(
        id="invsqrt_OS1", put="invsqrt", category="OS",
        label="Newton step '-' -> '+'",
        target_locator="the Newton update expression "
                       "y * (threehalfs - xhalf * y * y) inside the fast "
                       "inverse-square-root routine",
        transformation="flip the subtraction to an addition: "
                       "y * (threehalfs + xhalf * y * y)",
        rationale="single-token sign error in the update rule; destroys the "
                  "reciprocal-square-root identity y(x)*y(1-x)=1 "
                  "(target stratum MP1 f_inv.con)",
    ),
    MutationOperator(
        id="invsqrt_CE1", put="invsqrt", category="CE",
        label="halving constant 0.5 -> 0.6",
        target_locator="the 0.5f halving coefficient (xhalf = 0.5f * x) "
                       "feeding the Newton step",
        transformation="change the halving constant from 0.5 to 0.6",
        rationale="coefficient typo in the derivative term biases every "
                  "refined output, distorting the convex decreasing shape "
                  "envelope (target stratum MP4 f_mono.shape)",
    ),
    # ── brent (pair brent.c; primary MP3 f_conv.lim; instantiable strata
    #    {1,2,3,4} per the frozen A1 registry) ─────────────────────────────
    MutationOperator(
        id="brent_CE1", put="brent", category="CE",
        label="convergence tolerance 1e-12 -> 1e-2",
        target_locator="the absolute-tolerance argument of the interval "
                       "convergence test in the Brent iteration loop "
                       "(gsl_root_test_interval(..., 1e-12, 0.0))",
        transformation="loosen the absolute tolerance from 1e-12 to 1e-2",
        rationale="tolerance-knob mistake typical when porting solver "
                  "configs; the solver stops early and returns roots up to "
                  "~5e-3 off (target stratum MP3 f_conv.lim, PRIMARY)",
    ),
    MutationOperator(
        id="brent_CF1", put="brent", category="CF",
        label="iteration budget 100 -> 3",
        target_locator="the iteration guard of the Brent solve loop "
                       "(iter++ < 100)",
        transformation="reduce the maximum iteration count from 100 to 3",
        rationale="premature-termination control-flow fault; the "
                  "still-converging bracket midpoint is returned, deforming "
                  "the root curve shape (target stratum MP4 f_mono.shape)",
    ),
    MutationOperator(
        id="brent_CE2", put="brent", category="CE",
        label="problem map c = 4x-2 -> 4x-1",
        target_locator="the input-map constant in c = 4.0 * x - 2.0 that "
                       "positions the target equation t^3 + t = c",
        transformation="change the offset from -2.0 to -1.0 (c = 4x - 1)",
        rationale="off-by-constant in the problem transcription; shifts "
                  "every root and destroys the odd symmetry "
                  "y(x) + y(1-x) = 0 (target stratum MP1 f_inv.con)",
    ),
]

# program -> ops (rendered once per pair of that program)
XL_PILOT_OPERATORS_BY_PROGRAM: dict[str, list[MutationOperator]] = {}
for _op in XL_PILOT_OPERATORS:
    XL_PILOT_OPERATORS_BY_PROGRAM.setdefault(_op.put, []).append(_op)

# design-intent stratum coverage (documentation only; primary + two others)
XL_PILOT_TARGET_MP = {
    "invsqrt_CF1": 5, "invsqrt_OS1": 1, "invsqrt_CE1": 4,
    "brent_CE1": 3, "brent_CF1": 4, "brent_CE2": 1,
}
