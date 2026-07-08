# CF/TF Single-Stratum Admission Filter (Study-2)

**Status:** pre-registered, pre-data. Derived from Study-1 diagnostics only; no
Study-2 mutant data exists at authoring. Default **ON** for Study 2.

**Artefacts:**
- Filter module: `src/p2/mutators/stratum_filter.py`
- Campaign flag: `src/p2/config/campaign.py` (`single_stratum_filter_enabled`)
- Admission hook: `src/p2/mutators/pool_builder.py` (`select_mutants_for_put(..., screen_fn=)`), wired in `scripts/build_pools.py`
- Weak prompt guardrail: `scripts/cross_source_campaign.py`
- Tests: `tests/mutators/test_stratum_filter.py`
- Study-1 evidence: `data/results/s5_purity_v4.json`, `docs/review_2026-07-08/fixes/s5_purity_findings.md`

---

## 1. Diagnosis — why CF/TF straddle strata

The Study-1 S5 audit (`scripts/compute_s5_purity.py`) ran **all five** MP
invariant checkers on each of the 292 admitted mutants (offline AVP dispatcher
`src/p2/avp/`, 20-repeat majority vote). A mutant *perturbs invariant k* iff it
is KILLED under MP_k; its **flip count** is how many invariants it perturbs. S5
purity requires each detected mutant to flip exactly one (so the effect map
`sigma` is single-valued).

Invariant-flip histogram: `{0: 170, 1: 93, 2: 27, 3: 2}` → **29 multi-stratum**
mutants (flip ≥ 2). Every one of them came from just two operator families:

| operator | mutants | detected | pure (flip 1) | multi-stratum (flip ≥ 2) |
|---|---|---|---|---|
| CE (constant error)    | 64 | 27 | 27 | 0 |
| OS (operator swap)     | 60 | 35 | 35 | 0 |
| HP (hyper-parameter)   | 72 | 11 | 11 | 0 |
| SI (structure/index)   | 33 | 11 | 11 | 0 |
| **CF (control flow)**  | 9  | 9  | 0  | **9**  |
| **TF (train/fit data)**| 54 | 29 | 9  | **20** |

Local-edit families are **0/229 multi-stratum**. The 29 exceptions localise to
`B2` (9, CF), `C1` (2, TF), `D1` (9, TF), `D3` (9, TF).

**Mechanism.** CF and TF mutate **shared upstream state** on which several
downstream invariants jointly depend:
- **CF** (`b2_CF1`, MH acceptance `u < accept_ratio` → `u > accept_ratio`):
  reversing the acceptance inequality inverts the whole chain, breaking MP1 and
  MP2 simultaneously (flip `[1,2]`).
- **TF** (`c1/d1/d3 TF1`, label flip `y→1-y`, narrowed train range, permuted
  labels): corrupting the training data poisons every prediction, so the
  monotonicity (MP2) and partial-order (MP5) relations break at once
  (flip `[2,5]`, or `[1,2,5]`).

Local edits touch one computational pathway → one downstream invariant → flip 1.

**Consequence (Study-1 H4 root cause).** A multi-valued `sigma` contaminates the
RQ2 off-diagonal kill mass: 35.2% (31/88) of the off-diagonal came from
multi-stratum artefacts rather than genuine cross-stratum detection. Study 2
constrains CF/TF generation so admitted mutants perturb exactly one stratum,
removing this attribution leakage without touching the LRCA measurement
machinery.

---

## 2. Mechanism chosen — two-layer enforcement

A spec-level textual constraint alone is weak (an LLM cannot self-verify the
invariant set it perturbs), so enforcement is two-layered:

1. **Weak spec-level guardrail (layer 1).** For CF/TF operators only, a
   single-stratum clause is appended to the generation prompt
   (`single_stratum_prompt_clause`). Returns `""` for CE/OS/HP/SI, so their
   prompts are byte-identical to before.

2. **Strong deterministic admission screen (layer 2, load-bearing).** Every
   CF/TF candidate is evaluated against all five offline AVP checkers **before
   any SMS is computed**; it is admitted iff its invariant-flip count ≤ 1. This
   uses the SAME dispatcher and the SAME flip definition as the S5 audit, so
   admission and audit agree by construction. CE/OS/HP/SI are admitted
   unconditionally (they never straddle) and incur zero evaluation cost.

---

## 3. Filter contract

`p2.mutators.stratum_filter`:

| symbol | contract |
|---|---|
| `CONSTRAINED_CATEGORIES` | `frozenset({"CF","TF"})` — the only screened families. |
| `classify_flips(labels) -> (n, [mp…])` | flip count + perturbed invariants from `{mp: "KILLED"/"SURVIVE"/"EQUIV"}`. Mirrors `compute_s5_purity.py`. |
| `is_single_stratum(labels) -> bool` | `flip_count <= 1`. |
| `decide(category, labels=None) -> AdmissionDecision` | pure gate. Unconstrained → admit without labels. CF/TF → require labels, admit iff flip ≤ 1 (raises if labels missing). |
| `evaluate_mutant_labels(put_id, path, repeats=20)` | live: run all 5 AVP checkers on one mutant (reuses `sms_campaign.evaluate_cell`; seed-42 sampler, no network). |
| `screen_mutant(put_id, path, category=None, repeats=20, evaluator=None)` | admission gate for one file; `evaluator` injectable for tests. |
| `make_screen_fn(repeats=20) -> screen(path, op_id) -> bool` | adapter for `pool_builder.select_mutants_for_put(screen_fn=)`. |
| `single_stratum_prompt_clause(category) -> str` | layer-1 clause; `""` unless CF/TF. |
| `audit_matrix(matrix, puts) -> dict` | classify a frozen `sms_track2`-style matrix (validation). |

**Properties (all required by registration):**
- **Deterministic:** offline AVP dispatcher, seed-42 sampler, fixed epsilon,
  20-repeat majority vote — no randomness, no network.
- **Applied at admission time,** before any SMS is computed (hook in
  `select_mutants_for_put`, i.e. the pool-build step §2.3 of the runbook).
- **Identical for all arms/cells:** the same `screen_fn` gates the cross and
  same arms and every PUT; it cannot bias proportional selection.
- **Declared** here and in the runbook; flagged, default ON.

---

## 4. Audit-mode validation (strongest check)

Replaying the frozen Study-1 60-cell matrix (`data/results/sms_track2_v4.json`)
through `audit_matrix` reproduces the multi-stratum set exactly:

```
n_mutants            = 292
n_multistratum       = 29        (matches s5_purity_v4.json byte-for-byte)
categories flagged   = {CF, TF}
per-PUT              = B2:9, C1:2, D1:9, D3:9
admission-rejected  = 29  (all CF/TF, all flip >= 2)
```

**29/29 recall** against the independently-computed S5 SSOT
(`test_audit_reproduces_study1_29`). The live path was additionally confirmed on
a real mutant: `m10_b2_CF1_claude_a02.py` → live screen `flip=2 [1,2]` →
rejected, matching the audit.

---

## 5. Integrity

- Constraint keyed on the **Study-1 per-operator audit only**; no Study-2 data
  exists to peek at. Derivation disclosed in §1.
- The **37 Study-1 operator specs are byte-unchanged**
  (`test_old_put_operators_unchanged`); the constraint is a campaign-config flag,
  not a registry edit — history is not mutated.
- Study-1 frozen pools (`v2`/`v3`) are **never re-screened**; `build_pools.py`
  wires the screen only for Study-2 pool versions (`v4`/`v5`) and only when the
  flag is ON.
- Disabling the filter (`P2_SINGLE_STRATUM_FILTER=0`) is a **disclosed
  deviation** from registration.

---

## 6. Exact registry / config diffs

**New files**
- `src/p2/mutators/stratum_filter.py` — the filter (contract in §3).
- `src/p2/config/campaign.py` — `single_stratum_filter_enabled()` (env
  `P2_SINGLE_STRATUM_FILTER`, default `1`/ON).
- `tests/mutators/test_stratum_filter.py` — 23 tests incl. audit-mode 29/29.

**`src/p2/mutators/pool_builder.py`** — `select_mutants_for_put` gains an
optional `screen_fn: Callable[[Path, str], bool] | None = None`; when supplied,
a candidate must pass both `_is_valid_program` and `screen_fn`. Default `None`
preserves legacy behaviour byte-for-byte.

**`scripts/build_pools.py`** — imports `single_stratum_filter_enabled`; builds
`SCREEN_FN = make_screen_fn(repeats=20)` when the flag is ON **and**
`POOL_VERSION in ("v4","v5")`; passes `screen_fn=SCREEN_FN` to
`select_mutants_for_put`.

**`scripts/cross_source_campaign.py`** — imports the flag +
`single_stratum_prompt_clause`; appends the CF/TF clause to the generation
prompt when the flag is ON (no-op for CE/OS/HP/SI).

**Operator registry (`operator_registry.py`): unchanged.** The constraint is not
a spec edit.
