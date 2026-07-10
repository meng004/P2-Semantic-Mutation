# Pre-Registration — Study 5 (Confirmatory) — v1.0 (2026-07-10)

**Paper**: *When Same-Prompt LLM Source Diversity Doesn't Help — Semantic
Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific
Computing Kernels* (P2/P3, IST/TOSEM multi-study architecture).

**This document is a NEW confirmatory registration** in the lineage
`PREREGISTRATION_STUDY2.md` (v1.0, commit `072a015`) →
`PREREGISTRATION_STUDY2_v1.1.md` (v1.1, 2026-07-08) →
`PREREGISTRATION_STUDY3_v2.md` (v2.0, 2026-07-09) →
`PREREGISTRATION_STUDY4_v1.md` (v1.0 + amendments v1.1/v1.2, 2026-07-09) →
**this v1.0 (Study 5)**. It does **not** amend or re-open any frozen
registration; Studies 2–4 are closed and their confirmatory verdicts stand
FROZEN and UNCHANGED — including Study-4 `H2-2 = BOUNDED_NULL`,
`H4'''-graded = CONFIRM` (graded attribution at adequate pooled n), and
`H-LANG = NOT_CONFIRMED` (the recorded falsification of language-invariance on
the 7-PUT C grid **stands as recorded**; Family XL below is a new registration
on new material, not a re-roll). Study 5 registers **three confirmatory
families** and **one reliability measurement** on **fresh data that does not
yet exist**.

**Editorial stance (encoded).** This registration is written to ARGUE, not
merely report. Each family attacks one honestly-diagnosed root cause of a
Study-4 verdict and commits to a verdict either way: Family XL re-poses the
language-invariance claim on an **external** cross-language corpus at a power
target the Study-4 grid could not reach; Family OS removes the
specification-compression limitation that bounded H2-2; Family MR is the
sharpest test yet of the *MR-design-is-the-lever* thesis (mutants frozen,
battery source varied). Under-recruitment / under-certification gates are
registered so a weak result is reported as weak, never disguised.

**Status**: FROZEN before any **Study-5** data generation (2026-07-10).
Frozen apparatus: this file + the `--study5` extension of
`scripts/power_analysis_study4.py` (power/feasibility SSOT
`data/results/power_study5.json`, seed 20260708, MC budget B = 10,000) + the
pre-frozen analysis-script contracts of §6 (`compute_hlang_delta.py`
`--study5-family xl` additive preset; **NEW** frozen
`scripts/compute_mr_diversity_delta.py`; `compute_dualblind_delta.py`
unchanged). Master seed `20260708` (registration seed convention retained).
Any change after this freeze is a logged, dated entry in §10, not an edit to
the frozen body.

---

## Vocabulary note (NOETHER canonical, presentation layer)

This registration uses the CANONICAL vocabulary of the companion theory paper
NOETHER (`NOETHER_paper_submission.pdf`; `docs/prereg_v2/NOETHER_ALIGNMENT.md`
v2 section, normative):

- **Five MetaPatterns** (Layer 1): `m_inv` (invariance, group action G),
  `m_mono` (monotonicity, partial order O≤), `m_adj` (adjoint, T*), `m_rev`
  (time reversal, 𝒯*rev), `m_conv` (convergence, parametrised limit ℒ*).
- **Ten MR families** (Layer 2, `f_parent.child`), of which the five
  registered P3 strata are:

  | Registered stratum (provenance label) | NOETHER MR family | Parent MetaPattern | MR mode |
  |---|---|---|---|
  | MP1 conservation | `f_inv.con` | `m_inv` | Mode-I |
  | MP2 monotonicity | `f_mono.stat` | `m_mono` | Mode-I |
  | MP3 convergence order | `f_conv.lim` | `m_conv` | Mode-I |
  | MP4 dynamics/shape | `f_mono.shape` | `m_mono` (𝒟* refinement) | Mode-I |
  | MP5 method-comparison | `f_conv.rate` | `m_conv` (ℰ* refinement) | **Mode-M** (relative oracle) |

- **MR battery** = P3's per-PUT set of executable MR instances (NOETHER's ρ
  level). The historical P3 term "MR family" is not used for this object, to
  avoid collision with NOETHER's Layer-2 primitive.
- **Provenance constraint (NOETHER_ALIGNMENT §B, in force).** All frozen cell
  keys, class rules, scripts, and SSOTs keep the registered `MPk` labels
  verbatim (`A2_MP1`, `PRIMARY_CELLS_V3`, A→MP1/B→MP2/C→MP5/D→MP2). No
  sentence in this registration claims any prior artifact was registered under
  NOETHER `f_x.y` names; the family symbols carry the semantic narrative only.

---

## 0. Status, lineage, attestation

### 0.1 Pre-data attestation (Study-5 data specifically)

> **This registration was drafted and frozen before any STUDY-5 data
> generation. No Study-5 mutant, XL corpus roster, certified program-language
> pair, open-specification mutant, LLM-prompted MR battery, L-side SMS cell,
> census shadow verdict, or any Study-5 outcome exists or was visible to the
> authors of this registration.** Verification performed at drafting
> (2026-07-10) — ALL of the following verified ABSENT:
> `configs/xl_roster.json`, `docs/prereg_v2/XL_CORPUS_SPEC.md`,
> `data/results/sms_track2_v8xl.json`, `data/results/hlang2_delta_v8xl.json`,
> `data/results/sms_track2_v8_open.json`,
> `data/results/dualblind_delta_delta_v8_open.json`,
> `data/results/sms_track2_v8_mrL.json`,
> `data/results/sms_track2_v8_mrL_same.json`,
> `data/results/mr_diversity_delta_v8.json`,
> `data/results/review_shadow_kappa_v8_full.json`; no `v8xl` / `v8open` /
> `v8mr` mutant pool exists.
>
> **Tag-namespace disclosure.** `data/mutants/{a2,b4}_pool_v8_pilot_{same,cross}`
> EXIST at freeze. These are **Study-4 calibration-pilot artifacts**
> (`scripts/pilot_smoke_study4.py`, `POOL_VERSION = "v8_pilot"`, generated
> 2026-07-09 on the pilot PUTs `{a2, b4}` only), firewall-excluded from every
> confirmatory statistic of every study. They contain no Study-5 information.
> To avoid tag collision, Study-5 pilot pools use the tags `v8xl_pilot` /
> `v8open_pilot` / `v8mr_pilot` (§2e).
>
> **Prior-study data (v4–v7) IS seen, and its use is declared openly, in two
> distinct roles:**
> 1. **Design calibration** (standard registered-science practice, as in every
>    prior study of this lineage): the Study-4 C-arm pool
>    (`sms_track2_v7c.json`, observed `delta_C = +0.2449`) calibrates the
>    primary Family-XL power DGP; the Study-4 Python cross arm
>    (`sms_track2_v7.json`, observed `delta = 0.4445`) calibrates the
>    sensitivity DGP; the v7 per-PUT SMS variance calibrates Family-MR power;
>    the v4 hurdle DGP is reused verbatim for Family-OS power (as in v1.1 and
>    Study 4).
> 2. **Frozen reused substrate** (registered here, before any Study-5
>    outcome): Family MR reuses the two Study-4 arm SSOTs as its R side
>    (**reused, not rerun** — sha256-pinned in the frozen analyzer); Family OS
>    reuses the Study-4 cross-source arm as its registered-specification
>    comparator arm (sha256 pin in §3.2). Reusing a CLOSED, frozen artifact as
>    a comparator is not selection on the Study-5 response, because no Study-5
>    response exists; the frozen values cannot be influenced by anything done
>    now.
>
> Every confirmatory verdict is computed on fresh Study-5 data through the
> pre-frozen scorers (§6), never *as* a v4–v7 re-analysis.

### 0.2 Diff table (Study-5 additions over the frozen Study-4 v1.0+v1.1+v1.2)

| # | Clause | Prior state | Study-5 v1.0 | Justification |
|---|---|---|---|---|
| T1 | Language invariance | Study-4 Family L: 7-PUT hand-written C port; `NOT_CONFIRMED` at disclosed power 0.6865 | **Family XL** (H-LANG-2): EXTERNAL cross-language corpus, registered deterministic selection protocol (§2b), certification as an ADMISSION gate (§2c), power target from the deflated Study-4 point estimate (§4) | root causes §1.2: port compromise, knowingly sub-0.80 power, certification not an admission gate, port-authorship confound |
| T2 | Source diversity | Study-4 H2-2 `BOUNDED_NULL` with disclosed limitation: registered operator specs compress vendor freedom | **Family OS** (H2-3): prompts specify ONLY the target stratum (registered MPk = NOETHER family), same four vendors; estimand + three-way rule v1.1-VERBATIM | removes the specification-compression limitation; the sharp follow-up the Study-4 §5e disclosure demands |
| T3 | MR-design-is-the-lever | asserted via H2-2 BOUNDED_NULL (generation-side null) | **Family MR** (H2-4): mutant pools FROZEN byte-identical (v7, reused not rerun); battery source varied (registered NOETHER-derived vs LLM-prompted) | the sharpest test: if MR design is the lever, algebra-derived batteries must dominate on identical mutants |
| T4 | Reviewer reliability | post-hoc stratified sample n=189 (`review_shadow_kappa_v7.json`) | **full-census reliability measurement**: both shadow vendors over ALL 2036 frozen packets, per-stratum decomposition | upgrades a sample-based post-hoc check to a registered census MEASUREMENT (no hypothesis, no verdict) |
| T5 | Code provenance | Study-4 C kernels hand-written by the study authors | **author-directed principles P1/P2** (§1.6): external code first; hand-written code confined to the adapter layer | removes the port-authorship confound entirely |
| T6 | Analyzer contracts | `compute_hlang_delta.py` (7-PUT C grid), `compute_dualblind_delta.py`, `compute_h4_graded.py --pooled` | ADDITIVE `--study5-family xl` preset (default byte-unchanged, verified); **NEW** frozen `compute_mr_diversity_delta.py` (exit 2 absent inputs, exit 3 R-pin mismatch); `compute_dualblind_delta.py` serves OS as-is | same gold-standard ordering: scorers frozen before generation |
| T7 | Power SSOT | `power_study4.json` | `power_study5.json` via the ADDITIVE `--study5` entry point (default Study-4 run byte-unchanged; re-run at freeze reproduced `power_study4.json` byte-identically) | §4; seed 20260708, MC budget 10,000 |
| T8 | Not re-registered | — | H2-1', H1', H3', H4''-strict, H4'''-graded, H2-2, Study-4 H-LANG: all settled/closed; re-runnable descriptively only (Family X) | no needless multiplicity on settled verdicts |
| T9 | Incident ledger | ends at P14 (Study-4 C-arm pilot) | continues at **P15+** (§10) | append-only provenance |

Attestation applies to every row: *frozen before any Study-5 data generation;
no Study-5 outcome was visible; v4–v7 used only as declared in §0.1.*

---

## 1. Motivation — the Study-4 verdicts and their root causes, honestly

### 1.1 What Study 4 found (recorded verdicts, unchanged)

| Family | Verdict | Key numbers |
|---|---|---|
| H2-1' (descriptive re-run context) | CONFIRM | delta = 0.4445, one-sided 95% LB 0.2771 (Python cross arm) |
| H2-2 (Family B) | **BOUNDED_NULL** | Delta-delta = +0.0147, CI [−0.0210, +0.0686], half-width 0.0448 ≤ 0.14 |
| H4'''-graded (Family H) | **CONFIRM** (graded attribution at adequate n) | pooled n_rich = 32 ≥ 24, share 0.2917, boot LB 0.2188 > 0.15 |
| H-LANG (Family L) | **NOT_CONFIRMED** | delta_C = +0.2449, one-sided 95% LB −0.0357; n = 7, registered power 0.6865 |

### 1.2 H-LANG root-cause analysis (final-review; design debt named)

The Study-4 falsification of language-invariance is recorded and **stands**.
The final-review root-cause analysis, however, identifies four items of
*design debt* that make the NOT_CONFIRMED evidentially weaker than the
registered claim deserved:

1. **The 7/12 port compromise.** The C port achieved 7 of 12 PUTs; the 5
   ML-library kernels were excluded as unportable (`C_PORT_SPEC.md` §3). The
   grid that tested the bold claim was the *feasibility residue* of a port,
   not a designed sample.
2. **Power 0.69, knowingly below 0.80.** Amendment v1.1 recomputed H-LANG
   power honestly at n = 7 (0.6865) and ran the leg anyway, disclosed. That
   was the registered-honest choice *given the grid*; the debt is that the
   grid itself was accepted. A one-shot falsification test run at 0.69 power
   cannot cleanly separate "construct fails in C" from "grid too small":
   indeed the point estimate was **positive** (+0.2449) with a lower bound
   crossing 0. Study 5 does not reinterpret the verdict; it re-poses the
   hypothesis on a grid sized from the *deflated* observed effect (§4).
3. **Certification was not an admission gate.** `C_PORT_SPEC.md` recorded
   per-PUT agreement contracts *descriptively at authoring time*; no
   registered rule excluded a weakly-certified kernel BEFORE mutant
   generation (c2 was admitted at ~7.3e-3 absolute design-distributional
   agreement, three orders looser than the deterministic 1e-9 kernels).
   Study 5 registers the certification gate as an **admission rule** (§2c).
4. **Port-authorship confound.** The Study-4 C kernels were written by the
   study's own authors. Even authored blind to outcomes, a self-written port
   leaves open "the port, not the language, carries the effect (or its
   absence)". Family XL removes this confound **entirely** by testing on
   externally authored, independently maintained implementations (§1.6, §2b).

### 1.3 H2-2 root cause: registered specs compress vendor freedom

Study 4's H2-2 BOUNDED_NULL was reported with a disclosed limitation: both
arms executed the **same registered operator specifications** — every vendor
received the same transformation spec for the same slot. The prompt design
deliberately controlled the *task* to isolate the *source*; the cost is that
it compresses the space in which source diversity could express itself
(vendors differ most in what they *choose* to do, not in how they execute a
fixed instruction). The licensed BOUNDED_NULL claim is therefore about
**same-prompt** source diversity, exactly as the paper title states. Family OS
(H2-3) opens the specification to the stratum level — prompts name only the
target NOETHER MR family — and asks whether *open-specification* source
diversity moves the dual-blind Delta-delta. Either outcome is informative:
CONFIRM bounds the generality of the same-prompt null; BOUNDED_NULL extends it
to the open-spec regime.

### 1.4 H2-4: the sharpest test of "MR design is the lever"

The P-series thesis is that the *metamorphic-relation design* — algebra-derived
per the NOETHER constructive procedure — is the lever that moves semantic
mutation scores, while generation-side source diversity is not. Studies 2–4
tested the second half. Family MR tests the first half directly, with the
cleanest possible manipulation: **freeze the mutants byte-identically** (the
Study-4 v7 pools, reused not rerun, sha256-pinned) and vary ONLY the source of
the MR battery that scores them (registered algebra-derived vs LLM-prompted,
executability-certified, never tuned). If the thesis is right, the registered
batteries dominate. If the LLM batteries match or beat them, that is reported
as REVERSED / BOUNDED_EQUIVALENCE and counts against the thesis (§8).

### 1.5 Reviewer reliability: from sample to census

The post-hoc Study-4 shadow check (`review_shadow_kappa_v7.json`, stratified
n = 189) found kappa-vs-frozen 0.4427 (`gpt-5.5`) / 0.3606
(`gemini-3.5-flash`), between-shadows kappa 0.8037, and near-zero agreement on
the bounds-fixed-GP CONFIRMED stratum (0.00 / 0.0357). A 189-packet sample
with strata that small cannot support per-stratum conclusions. Study 5
registers the **full-census upgrade**: both shadow vendors over **all 2036
frozen review packets** (730 same / 638 cross / 540 recruit / 128 C), reported
with per-stratum decomposition — registered as a **reliability MEASUREMENT**,
not a hypothesis: no threshold, no verdict, frozen labels never modified
(§3.4).

### 1.6 Author-directed design constraints (verbatim, English translation)

The author has directed two principles that override the initial Study-5
design (which had proposed self-authored Julia and C ports); they are recorded
here verbatim as registered design constraints:

> **P1. If external repositories exist, do NOT hand-write code. No
> self-authored ports/kernels unless no external implementation exists (then
> hand-port only as a per-family disclosed fallback).**
>
> **P2. Code selection order: FIRST the experimental purpose + MetaPattern +
> MR-family instantiability, THEN diversity and multi-language breadth.**

Consequences encoded in this registration: (i) the two originally-drafted
port families (Julia full-grid; C completion of the 5 unportable kernels) are
**replaced** by the single external-corpus Family XL; (ii) hand-written code
appears ONLY in the adapter/oracle layer (subprocess line protocol as in
`src/p2/cport`, MR batteries, admission tooling) — never in a program under
test; (iii) the selection protocol (§2b) fixes required MR-family coverage
FIRST and treats language breadth as a ranking criterion, not a goal in
itself; (iv) if a required family has no external pair after the full
registered candidate sweep, the fallback is a hand-port with the same
certification gate, registered per-program and disclosed (§2b step 6).

---

## 2. Subjects and materials

### 2a. Rosters

- **Family XL roster**: n_target external **program-language pairs** (a pair =
  one program in one non-Python language, certified against its Python-side
  reference), selected by the deterministic protocol of §2b and frozen in
  `configs/xl_roster.json` + `docs/prereg_v2/XL_CORPUS_SPEC.md` via dated
  pre-data Amendment A1 **before any XL mutant generation**. Floor n ≥ 12;
  target n = the frozen-curve minimum n reaching 0.80 power under the primary
  DGP (= 20, §4a) if the corpus supplies it; budget cap 28 pairs.
- **Family OS and Family MR rosters** = the frozen 28-PUT confirmatory set
  (30 − pilots `{a2, b4}`; class balance 7/6/7/8: A a1,a3,a4,a5,a6,a7,a8;
  B b1,b2,b3,b5,b6,b7; C c1,c2,c3,c4,c5,c6,c7; D d1,d2,d3,d4,d5,d6,d7,d8),
  identical IDs to Studies 2–4.
- **Reliability census frame** = all 2036 frozen Study-4 blinded review
  packets (730 same / 638 cross / 540 recruit / 128 C; the
  `data/study4_packets/review_*/ _blind_map.json` frames, exactly the v7
  shadow-check frame with sampling removed).

### 2b. Family XL — registered selection protocol (deterministic, auditable)

This protocol is the heart of Family XL. It is executed AFTER this freeze and
BEFORE any mutant generation; its complete audit trail (every candidate
considered, every screening decision, the full ranking table, every
certification result) is frozen in `docs/prereg_v2/XL_CORPUS_SPEC.md`
(Amendment A1). **No step consults any mutation outcome, SMS value, or any
behavioral property beyond the certification measurements of §2c.**

**Step 1 — Required family coverage first (P2).** The five registered strata
(MP1 = `f_inv.con`, MP2 = `f_mono.stat`, MP3 = `f_conv.lim`,
MP4 = `f_mono.shape`, MP5 = `f_conv.rate`) are the fixed coverage targets.
Grid-level hard constraint: **every one of the five families must be
instantiable on at least 2 selected programs**. Program-level preference:
candidates on which all five families are instantiable rank first (Step 4).
Instantiability is judged from the program's governing structure against the
family's scope precondition (NOETHER's interface-exposure gate), documented
per candidate in the audit trail BEFORE any behavioral run.

**Step 2 — Registered candidate sources (external, in this fixed order).**

| # | Source | Languages |
|---|---|---|
| 1 | `TheAlgorithms/Python` ↔ `TheAlgorithms/C` ↔ `TheAlgorithms/C-Plus-Plus` ↔ `TheAlgorithms/Java` ↔ `TheAlgorithms/Go` ↔ `TheAlgorithms/Rust` (same-named algorithm across the language repos) | Python + C/C++/Java/Go/Rust |
| 2 | GNU GSL (C) ↔ scipy (Python) | C |
| 3 | Julia stdlib / SciML ↔ scipy | Julia |
| 4 | Apache Commons Math (Java) ↔ scipy | Java |
| 5 | Boost.Math (C++) ↔ scipy | C++ |

**Equation-governed numerics are preferred** — integrators, interpolation,
root-finding, special functions, statistical estimators — because NOETHER's
per-instance count law (|𝕄(𝒜_P)| = number of non-empty structural
components) predicts that discrete/combinatorial algorithms instantiate few
families (NOETHER's own worked instance: 𝒜_sort yields 2), so they cannot
serve the five-family grid.

**Step 3 — Selection criteria (registered NOW, before looking at any
candidate's behavior).** A candidate program is admissible iff:
1. **License** permits research use and adaptation (any OSI-approved license;
   copyleft sources are vendored under `third_party/` with attribution).
2. **Deterministic**, or stochastic with a seedable / injectable RNG.
3. **Single-entry numeric interface** adaptable to `double program(double x)`,
   `x ∈ [0,1]` (scalar in/out; fixed auxiliary parameters frozen in the
   adapter shim and documented per pair).
4. **≥ 2 languages available externally**: a Python-side reference (external
   Python implementation or the scipy/numpy reference the non-Python source
   documents itself against) + ≥ 1 non-Python implementation.

**Step 4 — Deterministic ranking.** Each admissible candidate is scored
`(c, ℓ)` where `c ∈ {0..5}` = number of the five strata instantiable on it
(Step 1 documentation) and `ℓ` = number of distinct non-Python languages with
a same-semantics external implementation. Sort key, total order:
**c descending, then ℓ descending, then source-list index (Step 2) ascending,
then program name ascending (ASCII)**. No behavioral quantity enters the key.

**Step 5 — Greedy roster construction.** Walk the sorted list; each admitted
program contributes one pair per external non-Python language that passes the
§2c certification gate. Stop when (i) certified pairs ≥ n_target AND (ii)
every family is instantiable on ≥ 2 selected programs; if the sweep exhausts
all candidates first, the achieved roster is frozen as-is and the shortfall
disclosed. Pair ids contain no underscore (frozen cell-key convention
`PAIRID_MPk`, e.g. `BRENT.C_MP3`); the roster JSON schema is fixed by
`compute_hlang_delta.load_xl_roster` (frozen).

**Step 6 — Fallback (P1 exception clause).** If after the full sweep some
family is instantiable on < 2 programs, a hand-port is permitted for THAT
family only, registered per-program in Amendment A1 BEFORE porting, subject to
the same §2c certification gate, and disclosed in every report of Family XL.

**Per-pair primary stratum (registered category → stratum map).** Each
selected program receives its primary stratum by the first matching row of
this table (deterministic; the row order mirrors NOETHER's canonical
structural-component ordering restricted to the five strata: G > O≤ > ℒ* >
𝒟* > ℰ*); the map is data-independent and frozen in the roster
(`primary_mp`); v3b-style selection on the response is prohibited:

| Kernel category (governing structure) | Primary stratum | NOETHER family |
|---|---|---|
| conservation/invariant-structured kernels (integrators with a conserved quantity; linear-algebra invariants; special functions with symmetry/reflection identities) | MP1 | `f_inv.con` |
| statistical estimators / probabilistic kernels (posterior means, MC estimators, resampling statistics) | MP2 | `f_mono.stat` |
| discretised / iterative solvers with a mesh, step, or tolerance knob (quadrature, root-finding, fixed-step ODE/FDM) | MP3 | `f_conv.lim` |
| trajectory / qualitative-shape kernels (monotone envelopes, shape-constrained dynamics) | MP4 | `f_mono.shape` |
| method-comparison / surrogate / fidelity-ordered kernels (two-method or surrogate-vs-target structure) | MP5 | `f_conv.rate` |

Cells: each certified pair × 5 strata (a stratum not instantiable on the
program yields a registered-vacant cell, excluded by the standard `_is_excluded`
rule); aligned = the pair's primary cell, cross = its other adjudicated cells.

**MR batteries for XL programs.** Batteries are algebra-derived per the
registered NOETHER constructive procedure, authored per PROGRAM (shared
semantics across that program's language pairs, adapted only through the
numeric interface), authored BEFORE any mutant generation and blind to all
mutants, certified V1/V2, and documented in `XL_CORPUS_SPEC.md`. Under P1,
MR batteries and adapters are apparatus (oracle layer), not programs under
test; they are the only hand-written code in Family XL.

### 2c. Family XL — registered port-equivalence CERTIFICATION GATE (admission rule)

For every candidate pair (program, language L), BEFORE any mutant is
generated:

- **Dense-grid differential check.** Evaluate both sides on the 201-point
  grid `x_i = i/200, i = 0..200`. The pair PASSES iff for all i:
  `|y_L(x_i) − y_py(x_i)| ≤ 1e-6 · max(|y_py(x_i)|, 1)` (relative tolerance
  with unit absolute floor), with both sides finite.
- **Registered per-pair exception classes** (documented in
  `XL_CORPUS_SPEC.md` per pair BEFORE its certification run):
  1. *Chaotic / solver-tolerance-bounded kernels*: tolerance relaxed to the
     documented solver band, at most `1e-5` relative (the Study-4 a1
     precedent), with the bound and its derivation recorded.
  2. *RNG-stream-dependent kernels*: admissible ONLY if the L implementation
     **reproduces the Python draw stream exactly** (identical generator
     algorithm and seed; verified by bit-comparing the first 10,000 draws),
     after which the standard tolerance applies to the outputs. A stochastic
     pair that cannot reproduce the draw stream FAILS certification. (The
     Study-4 C-port "distributional equivalence" contract is **not** carried
     over: it is the loophole that admitted weaker-certified kernels, §1.2
     item 3.)
- **A pair failing certification is EXCLUDED before any mutant is generated**,
  with the failure measurements disclosed in `XL_CORPUS_SPEC.md`. There is no
  post-generation exclusion path: once a pair's mutants exist, the pair is in
  the one-shot grid (§7).
- The achieved certified n is reported, and the achieved power is READ OFF the
  frozen §4 curve (largest tabulated n ≤ achieved n; no post-data simulation).

**Adapter layer (the only hand-written execution code).** Each pair is wrapped
by the registered subprocess line protocol of `src/p2/cport` (`CPutProgram`
pattern): persistent line REPL, one `x` per stdin line → one `%.17g` float per
stdout line, per-call timeout → `nan`, crashed child auto-restart. Toolchains:
`gcc -std=c99 -O0 -Wall -lm` (C), `g++ -O0 -Wall` (C++), `javac/java` (Java),
`go build` (Go), `rustc -O0` (Rust), `julia` (Julia). Admission gate mapping
for XL mutants (per `C_PORT_SPEC.md` §5 precedent): V1 = source
compiles/parses in the pair's toolchain; V2 = adapter-finite on the probe set
{0.1, 0.3, 0.5, 0.7, 0.9}; V3 = non-trivial (> 1e-6 deviation vs the pair's
unmutated original); V4 folded into V1 (must expose the `program` entry).

### 2d. Family MR — battery elicitation and certification materials

- **Arm R (registered batteries)**: the per-cell SMS of the frozen Study-4 arm
  SSOTs `sms_track2_v7.json` / `sms_track2_v7_same.json` — **reused, not
  rerun**; sha256 freeze pins (verified at run time by the frozen analyzer,
  exit 3 on mismatch):
  - `sms_track2_v7.json` = `13c6e0f81b5a6c423e7e5b5dd3c6f669ff9eeda62e67b060e827978d8b22c792`
  - `sms_track2_v7_same.json` = `c7931a74785da22c1f8aca90604125924e2546988e5ad4d23efec12438a1b4af`
- **Arm L (LLM-prompted batteries)**: for each of the 28 confirmatory PUTs ×
  each of the 5 strata, each of the four Study-4 vendor lineages
  (`claude-fable-5` harness; `gpt-5.5` / `gemini-3.5-flash` /
  `grok-4.1`→`grok-4.3` gateway) is prompted ONCE (one-shot, §7) to write MR
  instances, given ONLY: the PUT source + the target stratum name (the
  registered `MPk` label, its NOETHER family symbol, and the one-line
  definitional gloss of the Vocabulary table — for MP5 including its Mode-M
  relative-oracle character) + the executable-MR output format contract.
  Prompt template pinned by file hash before the run.
- **Certification (executability only, never tuned)**: V1 = the MR parses and
  executes on the unmutated PUT through the frozen MR harness; V2 = the MR is
  not violated by the unmutated PUT. MRs failing V1/V2 are dropped with
  per-vendor counts disclosed. **No MR is ever run against any mutant before
  the battery freeze**; no iteration, reranking, or selection against kill
  behavior is permitted (that would tune the battery on the response).
- **Cell battery**: the UNION of the four vendors' certified MRs for that
  cell. Per-vendor sub-battery results are recorded for descriptive breakdown.
- **Scoring**: the frozen `sms_campaign` machinery scores the byte-identical
  v7 mutant pools under the L batteries → `sms_track2_v8_mrL.json` (cross-arm
  pool) and `sms_track2_v8_mrL_same.json` (same-arm pool). No new mutants, no
  new review: the v7 admission/review labels are frozen and shared by both
  arms (identical pool ⇒ identical labels ⇒ the only manipulated variable is
  the battery).

### 2e. Calibration pilots (code-fix-only firewall, per grid)

- **XL pilot**: the first two certified pairs in frozen roster order that
  belong to two different programs AND two different languages (deterministic
  pick), run at 1 attempt/operator/slot, pool tag `v8xl_pilot`. Exercises:
  adapter REPL per toolchain, LLM→language-L generation + fence stripping,
  V1–V3 admission, blinded-packet export/ingest, cport-style SMS adapter.
- **OS pilot**: `{a2, b4}` (the standing pilot PUTs, excluded from the
  confirmatory roster), open-spec prompts, 1 attempt/slot, tag `v8open_pilot`.
  Exercises: open-spec prompt template on all four vendors, packet blinding
  (no vendor tag, no arm label, no spec-source leak), ingest.
- **MR pilot**: `{a2, b4}`, battery elicitation from all four vendors + V1/V2
  certification + L-scoring on the {a2, b4} v7-era pilot cells only, tag
  `v8mr_pilot`.
- **Firewall (verbatim discipline).** Pilots are excluded from every
  confirmatory analysis. Pilot outcomes may fix **code defects only** (harness
  wiring, fence-stripping, admission tooling, packet blinding, adapter
  determinism) — never thresholds, estimands, DGP calibration, the primary
  map, rosters, prompt semantics, or vendor role assignments. Every
  pilot-triggered change is logged in `docs/prereg_v2/PILOT_LOG.md`
  (append-only) and in §10 as **P15+** BEFORE the corresponding confirmatory
  run begins.

---

## 3. Confirmatory hypotheses and decision rules (all thresholds NOW)

Format: statistic · threshold (power justification) · test · α · decision rule
· licensed verdict. Three confirmatory families, each a single test (§6
multiplicity table); one registered measurement.

### 3.1 Family XL — H-LANG-2, cross-language invariance on an external corpus

- **Rationale.** NOETHER derives MetaPatterns as closure-guaranteed
  equivalence classes over the operator algebra of the governing equations,
  not surface syntax; the construct should be language-invariant. Study-4's
  Family L recorded NOT_CONFIRMED on a 7-PUT self-authored C port at 0.69
  power with a positive point estimate. Family XL re-poses the claim on
  **externally authored** implementations (no port-authorship confound), a
  **certified** grid (admission gate §2c), and a **power-targeted** n (§4).
  The Study-4 verdict stands as recorded; this is a new registration on new
  material, not a re-roll.
- **Statistic**: two-sample Cliff's `delta_XL` between the aligned (primary
  stratum, per the frozen roster map) and cross (other adjudicated cells) SMS
  slices over the certified pairs.
- **Test**: one-sided 95% percentile-bootstrap lower bound on `delta_XL > 0`
  (multinomial two-sample bootstrap, B = 10,000, seed 20260708 — byte-identical
  bootstrap to H2-1'/H-LANG). α = 0.05, one-sided. Family XL (single test).
- **Decision rule (FROZEN)**:
  - certified pairs n < 8 → **UNDER_CERTIFIED** (registered gate, §2c/§6
    analyzer; delta_XL and its bound reported factually; **the gate cannot be
    moved**);
  - n ≥ 8 AND lower bound > 0 → **CONFIRM cross-language invariance** (the
    aligned>cross direction replicates on external cross-language code);
  - n ≥ 8 AND lower bound ≤ 0 → **NOT_CONFIRMED** — a genuine, reportable
    falsification of language-invariance, this time on an external corpus at
    a power-targeted n; not hedged away.
- **Licensed verdict**: a language-invariance *direction* claim on external
  code, not a magnitude-equality claim across languages, and not a
  rehabilitation of the Study-4 Family-L verdict.

### 3.2 Family OS — H2-3, open-specification source diversity

- **Design.** One fresh arm, the **open-specification arm**: the 28-PUT grid
  with the Study-4 cross-source slot structure (3 slots →
  `gpt-5.5` / `gemini-3.5-flash` / `grok-4.1`→`grok-4.3`, one lineage per
  slot, identical attempt budget), except the generation prompt specifies
  ONLY the target stratum — PUT source + the registered `MPk` label with its
  NOETHER family symbol and one-line gloss (MP1 `f_inv.con`, MP2
  `f_mono.stat`, MP3 `f_conv.lim`, MP4 `f_mono.shape`, MP5 `f_conv.rate`,
  Mode-M noted for MP5) + output-format/admission constraints. **No operator
  specification, no exemplar transformation** — the vendor chooses the
  semantic fault. Prompt template hash-pinned pre-run.
- **Comparator arm** = the FROZEN Study-4 cross-source arm
  (`sms_track2_v7.json`, sha256
  `13c6e0f81b5a6c423e7e5b5dd3c6f669ff9eeda62e67b060e827978d8b22c792`,
  reused not rerun) — the registered-specification arm with the SAME vendor
  set, so the only manipulated variable is specification openness.
  *Disclosed limitation*: the comparator was drawn in Study 4
  (non-contemporaneous serving mix, §5); drawn is drawn — no redraw.
- **Statistic**: `Delta-delta_OS = delta(open-spec arm) − delta(registered-spec
  arm)`, paired on the 28 confirmatory PUTs under the identical dual-blind
  protocol (§5).
- **Test**: paired-role bootstrap (block-resample the 28 PUTs, SAME resample
  both arms), 95% two-sided CI, B = 10,000, seed 20260708. α = 0.05,
  two-sided. Family OS (single test).
- **Decision rule (v1.1 VERBATIM in form)**:
  - CI **excludes 0** → **CONFIRM** a specification-openness/source-diversity
    effect of magnitude ≥ 0.20;
  - CI **includes 0 AND half-width ≤ 0.14** → **BOUNDED NULL** (no ≥ 0.20
    effect detectable even with open specifications — extends the
    MR-design-is-the-lever thesis from same-prompt to open-spec);
  - CI **includes 0 AND half-width > 0.14** → **UNDER-RECRUITED**
    (inconclusive; gate cannot be moved).
- **Registered secondary (descriptive, NO verdict)**: the within-arm
  **semantic-diversity index** — per cell (PUT × stratum), the count of
  distinct flip-set signatures (the sorted tuple of strata flipped, computed
  by the frozen S5 `audit_matrix(..., constrained=ALL_FAMILIES)` machinery)
  among detected admitted mutants — compared across the open-spec and
  registered-spec arms (distributions, medians, per-class breakdown). Formula
  frozen HERE; reported descriptively regardless of the primary outcome;
  never promoted to a verdict.
- **Licensed verdict**: a directional/bounded claim about
  open-specification source diversity under the matched dual-blind protocol.

### 3.3 Family MR — H2-4, MR-side diversity (the sharpest lever test)

- **Estimand**: paired per-PUT battery-level SMS difference
  `delta_MR = SMS_R − SMS_L` on the FROZEN v7 mutant pools (§2d): per PUT and
  arm, battery-level SMS = mean SMS over the PUT's adjudicated cells; per-PUT
  unit = mean over the arms carrying the PUT on both sides; point = mean over
  the 28 confirmatory PUTs.
- **Test**: PUT-level paired block bootstrap of the mean difference
  (B = 10,000, seed 20260708). α = 0.05. Family MR (single test).
- **Decision ladder (FROZEN; top-down, first hit wins — implemented verbatim
  in the frozen analyzer)**:
  0. paired PUTs n < 24 → **UNDER_RECRUITED** (registered recruitment gate —
     e.g. L batteries failing V1/V2 on too many PUTs; achieved n and delta_MR
     reported factually; **gate cannot be moved**);
  1. one-sided 95% lower bound > 0 → **CONFIRM** — algebra-derived batteries
     dominate: MR design is the lever;
  2. two-sided 95% CI entirely below 0 → **REVERSED** — LLM-prompted batteries
     dominate; reported factually; counts against the thesis (§8);
  3. CI includes 0 AND half-width ≤ 0.14 → **BOUNDED_EQUIVALENCE** — no
     battery-source effect larger than the registered margin;
  4. else → **UNDER_RECRUITED** (factual report).
- **Scale disclosure (registered NOW).** The ±0.14 half-width margin is kept
  verbatim from the H2-2 rule for form-identity, but delta_MR lives on the
  SMS scale (v7 per-PUT mean SMS ≈ 0.10): the §4 projection puts the achieved
  half-width at ≤ 0.035 under every calibrated scenario, so the ladder will in
  practice be decided at steps 1/2. The margin is disclosed as loose relative
  to the scale and is NOT tightened post-hoc (that would be a
  threshold move after seeing data).
- **Licensed verdict**: a battery-source dominance / equivalence claim on
  identical mutants; never a claim about generation-side diversity.

### 3.4 Registered reliability MEASUREMENT (not a hypothesis): full-census shadow kappa

- **What**: both shadow vendors (`gpt-5.5`, `gemini-3.5-flash`) re-review ALL
  **2036** frozen Study-4 blinded review packets (730 same / 638 cross / 540
  recruit / 128 C) under the exact frozen `review_prompt` of each packet
  (text-only judgment, as in the v7 check).
- **Reported**: kappa vs frozen labels per vendor; kappa between shadows;
  per-stratum decomposition by (i) arm, (ii) frozen label
  (CONFIRMED/REJECTED), (iii) the v7 A/B/C strata (REJECTED /
  bounds-fixed-GP-CONFIRMED / other CONFIRMED) for comparability with the
  n = 189 sample; per-vendor error/refusal counts.
- **Registered as a MEASUREMENT**: no hypothesis, no threshold, no verdict, no
  gate. The frozen labels are NEVER modified regardless of what the census
  shows; the census quantifies reviewer-vendor reliability for the paper's
  threats section. If the gateway quota interrupts the census it resumes
  where it stopped (a census has no sampling-selection issue).
- **SSOT**: `data/results/review_shadow_kappa_v8_full.json`.

### 3.5 NOT re-registered (multiplicity control)

H2-1', H1', H3' (Study 2), H4''-strict (Study 3), H4'''-graded and H2-2
(Study 4, closed), and Study-4 H-LANG (closed, stands as recorded) are **not**
re-registered. They may be re-run descriptively on Study-5 pools for
continuity, labelled exploratory (Family X), never as confirmatory verdicts.
The `compute_dualblind_delta.py` output block `H2_1_aligned_dominates_cross`
computed on the open-spec arm is likewise **exploratory only** (Family X); the
Family-OS verdict is licensed exclusively by its `H2_2_...` block.

---

## 4. Sample sizes and power (SSOT: `data/results/power_study5.json`)

Produced by the frozen ADDITIVE extension
`PYTHONPATH=src python3 scripts/power_analysis_study4.py --study5`
(seed 20260708; Monte-Carlo budget n_sim = 10,000 per design point; inner
bootstrap 400 — the identical machinery of the `power_study4.json` H-LANG
entry; the default Study-4 invocation is byte-unchanged and was verified at
freeze to reproduce `power_study4.json` byte-identically). All numbers below
are embedded from the executed run.

### 4a. Family XL — direction power by n (achieved-n lookup curve, FROZEN)

Design: each certified pair contributes 1 aligned + 4 cross cells
(n_aligned = n, n_cross = 4n). Two calibration legs, both
design-from-prior-study (§0.1):

| DGP leg | Source | Observed anchor | DGP true delta | n=8 | n=10 | n=12 | n=16 | n=20 | n=24 | n=28 | min n ≥ 0.80 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **PRIMARY (deflated)** | `sms_track2_v7c.json` (Study-4 C arm) | delta_C = +0.2449 | 0.2376 | 0.3826 | 0.5118 | 0.6114 | 0.7632 | **0.8484** | 0.9036 | 0.9481 | **20** |
| SENSITIVITY (Python-scale) | `sms_track2_v7.json` (Study-4 Python cross arm) | delta = 0.4445 | 0.4532 | 0.7428 | 0.8275 | 0.8850 | 0.9515 | 0.9803 | 0.9921 | 0.9969 | 10 |

- **The primary leg deliberately assumes the DEFLATED Study-4 C-arm point
  estimate**, not the Python-scale effect: powering the re-test on the
  optimistic effect would repeat the Study-4 design debt (§1.2 item 2).
- **Registered n rule**: floor n ≥ 12; **target n = 20** (the
  frozen-curve minimum n reaching 0.80 under the primary DGP), taken from the
  external corpus if Step 5 of §2b supplies it, capped at 28 pairs; the
  achieved certified n is disclosed and the achieved power is READ OFF this
  frozen curve (largest tabulated n ≤ achieved n; no post-data simulation, no
  threshold move). If the corpus cannot reach n = 12 the shortfall is
  disclosed; below n = 8 the registered UNDER_CERTIFIED gate fires (§3.1).
- Under the sensitivity (Python-scale) DGP the grid is well-powered from
  n = 10.

### 4b. Family OS — Delta-delta power (v1.1 methodology verbatim)

Reruns the registered v1.1/Study-4 machinery on the v4 hurdle DGP (identical
seed stream; the entry reproduces the Study-4 numbers exactly):

| Quantity | Value |
|---|---|
| Registered n | 28 paired PUTs (per arm n_aligned = 28, n_cross = 112) |
| Detectable magnitude | \|Delta-delta\| ≥ 0.20 |
| Calibrated paired rho | 0.759 |
| Paired SE @ n=28 | 0.0716 |
| **Power @ n=28, dd=0.20** | **0.7928** (marginal, just below 0.80 — exactly as disclosed in v1.1 and Study 4; the three-way rule licenses UNDER-RECRUITED when the CI is wide, so no threshold is moved) |
| Empirical anchor | the Study-4 H2-2 achieved half-width was 0.0448 (`dualblind_delta_delta_v7.json`), well inside the 0.14 gate — the projection is conservative |

### 4c. Family MR — power from the v7 SMS variance

Calibration (`sms_track2_v7.json` + `sms_track2_v7_same.json`, 28 PUTs):
per-PUT battery-level mean SMS 0.1060 (cross arm) / 0.1036 (same arm);
arm-averaged between-PUT SD **sigma_put = 0.0663**; between-arm per-PUT
correlation **rho_v7 = 0.9837** (the pairing-rho ceiling; the R-vs-L pairing
rho on identical pools is unknown pre-data, so power is reported over a rho
grid with rho = 0 as the worst-case floor). sigma_d = sigma_put·√(2(1−rho));
SE = sigma_d/√28; one-sided z test at α = 0.05 (normal-approximation MC,
40,000 draws/point, seed 20260708+5):

| rho | SE @ n=28 | projected CI95 half-width | power @ delta_MR=0.02 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|---|
| 0.00 (worst case) | 0.0177 | 0.0347 | 0.3036 | 0.8803 | 1.000 | 1.000 |
| 0.50 | 0.0125 | 0.0245 | 0.4839 | 0.9908 | 1.000 | 1.000 |
| 0.75 | 0.0089 | 0.0174 | 0.7292 | 1.000 | 1.000 | 1.000 |
| 0.9837 (v7 ceiling) | 0.0023 | 0.0044 | 1.000 | 1.000 | 1.000 | 1.000 |

- The family is well-powered (≥ 0.88 even at the rho = 0 floor) for any
  battery-source effect of ≥ 0.05 SMS — half the observed per-PUT mean.
- The projected half-width is ≤ 0.035 in every scenario, far inside the
  registered 0.14 equivalence margin: the ±0.14 gate is disclosed as loose on
  this scale (§3.3) and is kept verbatim, not tuned.

### 4d. Reliability census — feasibility (no power concept applies)

A census has no sampling error against its own frame: 2036 packets × 2
vendors ≈ 4,072 gateway calls (max_tokens 2000), the only feasibility
quantity; quota interruptions pause/resume without selection risk (§3.4).

---

## 5. Protocol — generation, review, arbitration, serving economics

### 5a. Serving stack — Study-4 v1.2 economics, unchanged

Identical to the Study-4 as-executed v1.2 disclosure
(PREREGISTRATION_STUDY4_v1.md §0.4/§5b–§5e):

| Role | Served by | Model |
|---|---|---|
| Claude-family roles: OS-arm blinded review (all packets), MR battery elicitation (claude slot), XL generation claude slots, XL blinded review | **session harness** | claude-family |
| Non-Anthropic generators / battery authors: OS arm 3 slots, MR L-battery 3 vendor slots, XL non-claude slots, census shadow reviewers | **gateway** | `gpt-5.5` / `gemini-3.5-flash` / `grok-4.1`→`grok-4.3` |
| Arbitration on review disagreement | **gateway** | `gpt-5.5` (different vendor from the reviewer) |

Within-family serving heterogeneity (gateway vs harness of the same Anthropic
lineage) is disclosed exactly as in v1.2 §5e; it moves no between-arm
contrast. Exact resolved model ids (incl. the `grok-4.1`→`grok-4.3` remap) are
recorded in the campaign SSOT at run time.

### 5b. Dual-blind core — UNCHANGED

Generation → **blind review** (reviewer sees only mutant code + PUT source +
the cell's stratum/admission rubric; generator/vendor identity, arm label,
prompt-specification level, battery source, and SMS withheld) → **arbitration**
on disagreement → **freeze then score** (SMS computed only after review labels
are frozen and committed). Analyst blindness preserved. Admission screens run
at generation/admission, before any SMS, identically for every cell.

- **OS-arm review-packet asymmetry (disclosed).** The frozen comparator arm's
  labels were adjudicated in Study 4 against packets carrying operator specs;
  open-spec packets carry the stratum spec instead (there is no operator spec
  to show). The admissibility rubric (genuine behavioral change, plausibility,
  non-equivalence) is identical; the packet-content difference is a disclosed
  limitation of the frozen-comparator design (§3.2).
- **Family MR needs no review**: no new mutants exist; the frozen v7
  admission/review labels are shared by construction (§2d). Its blinding
  obligation is elicitation-side: battery authors see the PUT source + stratum
  name ONLY — never any mutant, kill outcome, or SMS.

### 5c. One-shot confirmatory rule — VERBATIM discipline (Study-4 §5d)

**Confirmatory generation/elicitation runs ONCE per the registered budget per
arm** — per-cell targets, seeds (20260708), vendor role assignments, and
prompt-template versions pinned by file hash. **Regeneration, cherry-picking
cells or vendors, re-eliciting a battery, re-rolling an arm, re-certifying a
failed pair after its mutants exist, or moving any threshold after ANY
confirmatory outcome is visible is a protocol violation that must be reported
as such** in §10 and in the paper. Confirmatory analysis runs **only** through
the pre-frozen scripts (§6). The calibration pilots (§2e) are the only place
live outcomes are seen before the confirmatory freeze, and they may fix code
defects only.

---

## 6. Analysis plan — SSOT paths + pre-frozen analyzers

### 6a. SSOT paths (Study 5)

| Artifact | Path |
|---|---|
| Power/feasibility SSOT | `data/results/power_study5.json` |
| XL roster (Amendment A1, pre-mutant) | `configs/xl_roster.json` + `docs/prereg_v2/XL_CORPUS_SPEC.md` |
| XL pool SSOT | `data/results/sms_track2_v8xl.json` |
| XL verdict | `data/results/hlang2_delta_v8xl.json` |
| OS arm pool SSOT | `data/results/sms_track2_v8_open.json` |
| OS verdict | `data/results/dualblind_delta_delta_v8_open.json` |
| OS comparator (frozen, pinned) | `data/results/sms_track2_v7.json` (sha256 `13c6e0…b22c792`) |
| OS secondary (descriptive) | `data/results/flipset_diversity_v8.json` |
| MR L-side pools | `data/results/sms_track2_v8_mrL.json`, `data/results/sms_track2_v8_mrL_same.json` |
| MR verdict | `data/results/mr_diversity_delta_v8.json` |
| Reliability census | `data/results/review_shadow_kappa_v8_full.json` |

### 6b. Analysis-script contracts (pre-frozen BEFORE generation)

- **`scripts/compute_hlang_delta.py --study5-family xl`** (ADDITIVE preset;
  frozen now). Reads the frozen roster (`configs/xl_roster.json`: grid +
  per-pair `primary_mp`; pair ids underscore-free) and the XL pool SSOT;
  computes `delta_XL` and its one-sided 95% percentile-bootstrap lower bound
  (byte-identical bootstrap to H2-1'/H-LANG; B = 10,000, seed 20260708);
  applies the frozen §3.1 rule including the `UNDER_CERTIFIED` gate
  (`XL_MIN_N_PAIRS = 8`); writes `hlang2_delta_v8xl.json`. **Exit 2** if the
  roster or pool SSOT is absent (nothing exists at freeze — verified). The
  DEFAULT invocation (Study-4 H-LANG) is byte-unchanged — verified at freeze
  by recomputing the frozen `hlang_delta_v7c.json` report in-memory and
  checking full equality (same additive pattern as Study-4's
  `compute_h4_graded.py --pooled`).
- **`scripts/compute_mr_diversity_delta.py`** (NEW — frozen now). Implements
  §3.3 exactly: R-side = the two sha256-PINNED frozen v7 SSOTs (**exit 3** on
  pin mismatch — quiet substitution impossible); L-side = the two
  `v8_mrL` SSOTs (**exit 2** while absent — verified at freeze); per-PUT
  battery-level SMS via the SAME `_is_excluded`/`_parse_cell` imported from
  the frozen `compute_dualblind_delta.py`; paired PUT-level block bootstrap
  (B = 10,000, seed 20260708); frozen ladder incl. the n ≥ 24 recruitment
  gate; writes `mr_diversity_delta_v8.json` with per-PUT and per-arm detail.
- **`scripts/compute_dualblind_delta.py`** — serves Family OS **AS-IS, no code
  change**: invoked with `--cross data/results/sms_track2_v8_open.json
  --same data/results/sms_track2_v7.json
  --out data/results/dualblind_delta_delta_v8_open.json`. Its `verdict_h2_2`
  three-way rule is the registered §3.2 rule verbatim (CONFIRM / BOUNDED_NULL
  / UNDER_RECRUITED at 0.20/0.14); the arm-name conventions map open-spec →
  `--cross` slot, registered-spec comparator → `--same` slot, so
  `Delta-delta_OS = delta(open) − delta(registered)` by construction. Its
  `H2_1` output block on the open arm is exploratory (Family X, §3.5); its
  `STUDY1_DD` sign flag is retained descriptively.
- **`scripts/review_shadow_kappa.py --full`** (census mode for the §3.4
  measurement): the v7 script's `frame()` without `sample()` — all 2036
  packets, both vendors, per-stratum decomposition, artefact
  `review_shadow_kappa_v8_full.json`. The flag is a code-level addition to a
  NON-confirmatory measurement tool; it is logged in §10 when added and the
  frozen labels are never written to.
- **`scripts/compute_flipset_diversity.py`** (descriptive secondary, §3.2):
  computes the frozen index formula (distinct flip-set signatures per cell via
  the S5 `audit_matrix`, constrained=ALL_FAMILIES) on both OS-comparison arms.
  Descriptive only — no verdict attaches; may be authored at analysis time
  because its formula is frozen here and it licenses no claim.
- **`scripts/power_analysis_study4.py --study5`** (ADDITIVE entry point,
  frozen): writes `power_study5.json`; the default Study-4 invocation is
  byte-unchanged (verified: re-run reproduces `power_study4.json`
  byte-identically).

**Exclusions (analysis-time, unchanged lineage rules)**: pilots `{a2, b4}`
excluded from every confirmatory statistic; vacant / non-adjudicated /
null-SMS cells excluded via the shared `_is_excluded`; silent mutants per the
frozen flip machinery. **Seeds**: all bootstraps at 20260708.

### 6c. Multiplicity — Study-5 family map

| Family | Members | Correction | Confirmatory? |
|---|---|---|---|
| XL — Language invariance (external corpus) | H-LANG-2 (delta_XL > 0, gated n ≥ 8) | single test | yes |
| OS — Open-spec source diversity | H2-3 (three-way Delta-delta rule) | single test | yes |
| MR — MR-side diversity | H2-4 (four-step ladder, gated n ≥ 24) | single test | yes |
| (measurement) | full-census shadow kappa | — (no test) | no — reliability measurement |
| X — Exploratory | descriptive re-runs; open-arm H2_1 block; per-vendor battery breakdowns; flip-set diversity index | per-test as labeled | no |

Each confirmatory family holds a single test; no within-family Holm and no
cross-family correction (per-family control under pre-registration; prior
studies' families are closed). Anything discovered after freeze is exploratory
by definition.

---

## 7. One-shot rule, firewalls, deviations

1. **One-shot** (§5c, verbatim discipline of Study-4 §5d): one registered
   generation/elicitation pass per arm; no regeneration, re-elicitation,
   re-certification-after-mutants, cherry-picking, or threshold movement
   after any confirmatory outcome is visible; violations are reported as
   violations.
2. **Pilot/confirmatory firewall** (§2e): pilots are code-fix-only;
   `v8xl_pilot`/`v8open_pilot`/`v8mr_pilot`-tagged artifacts never enter a
   confirmatory statistic; every pilot-triggered fix lands in `PILOT_LOG.md` +
   §10 (P15+) BEFORE the corresponding confirmatory run.
3. **Certification-before-mutants firewall** (§2c): XL pair exclusions happen
   only at certification, pre-mutant, with measurements disclosed; there is no
   post-generation exclusion path.
4. **Battery-blind firewall** (§2d): L batteries are elicited blind to all
   mutants and frozen (hash-pinned) before scoring; V1/V2 certification never
   consults a mutant.
5. **R-side freeze pins** (§2d, §6b): the reused v7 SSOTs are sha256-pinned in
   the frozen analyzer (exit 3 on mismatch).
6. **Amendment protocol**: any post-freeze change is a dated, append-only
   entry in §10, legitimate ONLY while no affected confirmatory outcome
   exists (the Study-4 v1.1/v1.2 standard); Amendment A1 (XL roster freeze) is
   the one scheduled amendment — it executes the frozen §2b protocol and adds
   no discretion.
7. **Gates cannot be moved**: XL `UNDER_CERTIFIED` (n < 8), MR
   `UNDER_RECRUITED` (n < 24), OS `UNDER-RECRUITED` (half-width > 0.14) are
   registered outcomes, not failures to be engineered around.

---

## 8. Disclosure contract and decision matrix

**All four items — the three confirmatory families AND the reliability
census — are reported in the paper regardless of outcome.** No verdict is
demoted to an appendix because it is inconvenient; UNDER-* outcomes are
reported as UNDER-*, with achieved n and intervals, and their gates cannot be
moved.

| Hypothesis | Confirm licenses | Non-confirm licenses |
|---|---|---|
| H-LANG-2 (XL) | "the aligned>cross construct is language-invariant on externally authored code" | lower bound ≤ 0 at achieved n ≥ 8: a genuine falsification on an external corpus (stronger than Study-4's: no authorship confound, power-targeted n); n < 8: UNDER_CERTIFIED, factual |
| H2-3 (OS) | "open-specification source diversity moves Delta-delta by ≥ 0.20" (bounds the same-prompt null's generality) | BOUNDED_NULL: the MR-design-is-the-lever thesis extends to open specifications; UNDER-RECRUITED: factual |
| H2-4 (MR) | "algebra-derived batteries dominate LLM-prompted batteries on identical mutants" — the lever claim confirmed at its sharpest | REVERSED: LLM batteries dominate (counts against the thesis, reported as such); BOUNDED_EQUIVALENCE: battery source bounded-immaterial (also against the strong thesis, reported); UNDER_RECRUITED: factual |
| (census) | — measurement: kappa values + decomposition reported as-is | — |

**What would count against the construct / thesis (registered a priori):**
(i) XL lower bound ≤ 0 at achieved n with primary-DGP power ≥ 0.80 — the
language-invariance claim fails on external code and the paper must say so;
(ii) an OS CONFIRM — the Study-4 BOUNDED_NULL is then a same-prompt artifact,
and the paper's source-diversity conclusion must be narrowed accordingly;
(iii) an MR REVERSED or BOUNDED_EQUIVALENCE — the algebra-derivation lever
claim is respectively refuted or bounded-immaterial, reported as a substantive
finding, not explained away; (iv) census kappa materially lower than the
n = 189 estimates — the single-family-reviewer threat is strengthened and the
threats section must carry it.

---

## 9. Deviations-from-prior-lessons table

| # | Prior lesson | Study-5 closure | Trace |
|---|---|---|---|
| L20 | Certification recorded descriptively is not a gate (c2 admitted at ~1e-2 agreement) | §2c makes the dense-grid differential check a registered ADMISSION rule; failures excluded pre-mutant; the distributional-equivalence loophole is not carried over | §1.2(3), §2c |
| L21 | A knowingly under-powered one-shot leg (H-LANG at 0.6865) cannot separate construct failure from grid smallness | XL n_target is derived from the DEFLATED observed effect on the frozen curve; the floor/target/cap and the UNDER_CERTIFIED gate are registered | §1.2(2), §4a |
| L22 | Self-authored ports leave an authorship confound | P1/P2 (author-directed, §1.6): external corpus; hand-written code confined to the adapter/oracle layer; fallback hand-ports per-program disclosed | §1.2(4), §2b |
| L23 | Same-prompt specs compress the space where source diversity could act | Family OS opens the spec to the stratum level, holding vendors, budget, and protocol fixed; v1.1-verbatim rule | §1.3, §3.2 |
| L24 | Post-hoc sample-based checks invite stratum-size artifacts | the shadow-kappa upgrade is registered as a CENSUS measurement with no verdict attached and frozen labels untouched | §1.5, §3.4 |
| L25 | "Drawn is drawn" — frozen data is reused, never redrawn | MR R-side and the OS comparator are sha256-pinned frozen SSOTs; the analyzer enforces the pin (exit 3) | §2d, §6b |

---

## 10. Amendments log + incident ledger (append-only, dated)

**Registration #1 — 2026-07-10 (this document, Study-5 v1.0).** Registered
three confirmatory families on fresh data that does not yet exist — **Family
XL** (H-LANG-2 on an external cross-language corpus; deterministic selection
protocol §2b under the author-directed principles P1/P2; certification
admission gate §2c; delta_XL > 0 one-sided at B = 10,000/seed 20260708; gates:
UNDER_CERTIFIED below n = 8; power curve frozen at n = 8..28 under the
deflated v7c primary DGP and the Python-arm sensitivity DGP), **Family OS**
(H2-3 open-specification source diversity; open-spec arm vs the sha256-pinned
frozen Study-4 cross arm; v1.1-verbatim three-way rule at 0.20/0.14; flip-set
diversity index registered as descriptive secondary), **Family MR** (H2-4
MR-side diversity on byte-identical frozen v7 pools; R = registered batteries
reused-not-rerun, L = four-vendor LLM-prompted batteries certified V1/V2 and
never tuned; four-step ladder with the n ≥ 24 recruitment gate) — plus the
**full-census reviewer-reliability measurement** (both shadow vendors × 2036
frozen packets; no hypothesis). Pre-froze the analyzer contracts
(`compute_hlang_delta.py --study5-family xl` additive preset with default
byte-identity verified; NEW `compute_mr_diversity_delta.py` with sha256
R-pins, exit-2/exit-3 semantics verified; `compute_dualblind_delta.py`
serves OS as-is) and the power SSOT (`power_study5.json` via the additive
`--study5` entry point; default Study-4 run verified byte-unchanged). One
scheduled amendment: **A1 — XL roster freeze** (executes the frozen §2b
protocol; pre-mutant; no discretion). Disclosed the Study-4 `v8_pilot`
tag-namespace collision (§0.1). All thresholds, gates, seeds, and estimands
fixed in this document before any Study-5 data.

**Incident ledger (continued from P14).** Prior ledger: Incident #1 (Study-1
v3-pool wipe), P4–P9 (Studies 2–3), P13–P14 (Study-4 C-arm pilot). Study 5
opens at **P15+** for pilot-triggered code defects (adapter REPL per new
toolchain, LLM→{C,C++,Java,Go,Rust,Julia} generation + fence-stripping,
open-spec packet blinding, battery-elicitation parsing, census resume logic,
`review_shadow_kappa.py --full` flag addition). Each entry is appended here
and in `PILOT_LOG.md` BEFORE the corresponding confirmatory run, verified
code-level (never protocol-level).

*(No further amendments. Any post-freeze change — a pilot-triggered code fix,
a vendor id remap, the A1 roster freeze — is appended here with date and
rationale before the corresponding confirmatory run.)*

**Amendment A1 — 2026-07-10 (scheduled, pre-mutant): Family-XL roster
freeze.** Executed the frozen §2b selection protocol and the §2c
certification admission gate; full audit trail (enumeration, per-candidate
screening with criteria cited, deterministic Step-4 ranking table, per-pair
certification measurements, declared class-1 exception bands, ambiguity
resolutions D1–D6) in `docs/prereg_v2/STUDY5_XL_ROSTER.md`; machine-readable
roster `configs/xl_roster.json` (schema verified against the frozen
`compute_hlang_delta.load_xl_roster`); certification SSOT
`data/results/study5_xl_certification.json`. Result: achieved certified
n = 21 pairs (floor 12 met, target 20 exceeded, cap 28 respected), 13
external programs, languages C/C++/Java/Rust/Julia; five pairs failed
certification and are excluded-and-disclosed pre-mutant (trapezoid.rs,
simpson.cpp, simpson.rs: defective/float-fragile external Python reference;
invsqrt.go: two-vs-one Newton iterations; besselj0.java: Commons Math
negative-argument domain rejection); read-off power at the frozen §4a
primary curve: n = 20 → 0.8484. Step-6 hand-port fallback NOT invoked.
Adapter layer only (`src/p2/xlport/`); no external program code edited. No
XL mutant, pilot pool, or SMS value existed at this freeze.
