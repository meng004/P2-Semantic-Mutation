# Study-5 Family-MR — Arm-L battery elicitation prompt template (v1.0, FROZEN)

**Status**: written 2026-07-10, BEFORE any Family-MR Arm-L elicitation call
(pilot or confirmatory) and BEFORE any L-side outcome exists. Pinned by
sha256 of this file; the pin is recorded in PREREGISTRATION_STUDY5_v1.md §10
(Amendment A2) and echoed into every elicitation log row. The registration
(§2d) fixed the template's required CONTENT (PUT source + registered `MPk`
label + NOETHER family symbol + one-line definitional gloss, Mode-M noted for
MP5 + executable-MR output format contract) and deferred the verbatim text to
this pre-run hash-pin slot; this file discharges that slot. It is used
VERBATIM and IDENTICALLY for all four vendor lineages (`claude-fable-5`
session harness; `gpt-5.5` / `gemini-3.5-flash` / `grok-4.1`→`grok-4.3`
gateway). One-shot: each (PUT, stratum, vendor) cell is elicited exactly once
(registration §5c/§7); no re-rolls, no revision, no per-vendor wording
differences.

## Registered serving parameters (fixed here, pre-run)

| Parameter | Value |
|---|---|
| temperature | 0.7 (Study-4 generator precedent, `_generate_one`) |
| requested max_tokens | 2500 (per-model `min_max_tokens` floors from `configs/study4_models.json` still apply on top; gemini floor 2000) |
| retries | transport/quota only (429/5xx/timeouts, x3 exponential backoff); a returned completion IS the draw (P14 precedent: transport errors are not draws; returned-but-unusable completions are) |
| messages | single user turn, content = the rendered template below |
| MR count per cell | 1 to 3 instances (fixed by the output-format contract) |
| certification | V1/V2 executability ONLY (registration §2d); no quality filtering, no tuning, no re-elicitation |

## Template (rendered once per (PUT, stratum) cell; `{...}` are the only substitution points)

````text
You are writing metamorphic relations (MRs) for a numerical program under test.

## Program under test ({put_id})

```python
{put_source}
```

The program exposes `program(x)`, mapping a scalar float `x` in [0, 1] to a
scalar float output. Treat it as a scientific-computing kernel; the source
above is its complete definition.

## Target MR family

{stratum_block}

Write metamorphic relations of THIS family only, for this program.

## How your MRs are evaluated (fixed harness semantics)

Each MR instance k is a pair of Python functions:

- `r_k(x)` — input transformation: deterministic, maps a float x in [0, 1] to
  a float in [0, 1], always finite;
- `R_k(y_orig, y_new)` — output relation: deterministic total predicate on the
  pair (program(x), program(r_k(x))), returning a bool; it must return False
  for non-finite inputs rather than raising.

The harness checks an MR against an implementation as follows:

{eval_block}

An MR is useful when this check PASSES on a correct implementation (this will
be verified: an MR violated by the unmutated program is dropped) and FAILS on
a faulty one. You will never see any faulty variant; encode properties that
any correct implementation of this program must satisfy.

## Output format (strict)

Reply with exactly ONE fenced Python code block and no other code blocks.
Inside it, define 1 to 3 MR instances named exactly `r_1`/`R_1`, `r_2`/`R_2`,
`r_3`/`R_3`. Only `import math` and/or `import numpy as np` are permitted; no
I/O, no randomness, no other imports. Module-level constants are allowed.
Comments are fine; keep all prose outside the code block.

This is a one-shot elicitation: your reply is certified for executability
as-is and is never revised.
````

## `{stratum_block}` — fixed per registered stratum (Vocabulary table, registration p.2)

| MPk | Block text (verbatim) |
|---|---|
| MP1 | **MP1 — conservation.** NOETHER MR family `f_inv.con`, parent MetaPattern `m_inv` (invariance under a group action G on the input space): a transformed input must leave the conserved / invariant output property unchanged. Mode-I (direct oracle on the output pair). |
| MP2 | **MP2 — monotonicity.** NOETHER MR family `f_mono.stat`, parent MetaPattern `m_mono` (monotonicity with respect to a partial order O<= on inputs): an order-directed input transformation must move the output in the corresponding direction. Mode-I (direct oracle on the output pair). |
| MP3 | **MP3 — convergence order.** NOETHER MR family `f_conv.lim`, parent MetaPattern `m_conv` (convergence under a parametrised limit L*): as the discretisation / tolerance parameter is refined, the output must approach its limit at the expected rate. Mode-I (direct oracle on the output pair). |
| MP4 | **MP4 — dynamics/shape.** NOETHER MR family `f_mono.shape`, parent MetaPattern `m_mono` (D* trajectory-shape refinement): a shape-preserving input transformation must leave the qualitative trajectory / shape of the output unchanged. Mode-I (direct oracle on the output pair). |
| MP5 | **MP5 — method-comparison.** NOETHER MR family `f_conv.rate`, parent MetaPattern `m_conv` (E* refinement). Mode-M (RELATIVE oracle): the relation compares two evaluations of the same quantity against each other (e.g. a higher-fidelity vs a lower-fidelity regime), not against an absolute reference. |

## `{eval_block}` — fixed per registered stratum (frozen harness `p2.avp` dispatcher semantics, stated identically to every vendor)

| MPk | Block text (verbatim) |
|---|---|
| MP1 | 30 samples x ~ U(0,1) (fixed seed): with y = program(x) and y' = program(r_k(x)), the check passes iff R_k(y, y') is True for EVERY sample. |
| MP2 | 50 samples x ~ U(0,1) (fixed seed): d_i = float(program(r_k(x))) - float(program(x)), sign-flipped to -abs(d_i) whenever R_k(y, y') is False; the check passes iff all d_i are exactly 0, or a one-sided Wilcoxon signed-rank test finds the d_i significantly GREATER than 0 (alpha = 0.05). Design r_k so a correct implementation yields transformed output >= original output systematically, and R_k to assert that ordering. |
| MP3 | The harness probes program(h) at h in {0.1, 0.05, 0.025, 0.0125}, fits the empirical convergence order of abs(program(h) - 1.0) in log-log, and passes iff the fitted order is within +/-0.2 of 2.0. Your r_k / R_k must still be present and executable (they are part of the battery interface), even though this family's numeric check is driven by the fixed refinement probe. |
| MP4 | 10 samples x ~ U(0,1) (fixed seed): the DTW distance between program(x) and program(r_k(x)), normalised by trajectory length, must average <= 1e-6; choose r_k to be an exact output-preserving symmetry of a correct implementation. R_k must still be present and executable. |
| MP5 | 50 samples x ~ U(0,1) (fixed seed): d_i = float(program(r_k(x))) - float(program(x)), sign-flipped to -abs(d_i) whenever R_k(y, y') is False; the check passes iff all d_i are exactly 0, or a one-sided Wilcoxon signed-rank test finds the d_i significantly GREATER than 0 (alpha = 0.05). This family is Mode-M (relative oracle): r_k should move the program to a comparably-valid evaluation regime of the same quantity, and R_k should assert the relative ordering / agreement of the two evaluations. |

## Design notes (recorded at freeze, pre-outcome)

1. The per-stratum evaluation semantics are stated to ALL FOUR vendors
   identically because (i) the registered V1/V2 gate is *executability within
   the frozen harness MR-interface*, which is only a meaningful gate if the
   interface semantics are part of the contract, and (ii) the claude-family
   slot is served by the session harness (registration §5a), which has
   unavoidable code-level exposure to the `p2.avp` dispatcher; embedding the
   same semantics in every vendor's prompt equalises that asymmetry instead of
   leaving it as a hidden claude-side advantage. This is an interface
   disclosure fixed before any outcome, not tuning (no mutant, kill outcome,
   or SMS informs it).
2. The 1-to-3 MR count bound, naming convention, [0,1] domain closure of r_k,
   import allowlist (math / numpy), and determinism requirement are part of
   the output-format contract; violations fail V1 as format/executability
   failures and are disclosed per vendor.
3. Elicitation-side blinding (registration §5b): the prompt contains the PUT
   source and the stratum block ONLY — no mutant, no kill outcome, no SMS, no
   arm label, no mention of the registered R batteries.
