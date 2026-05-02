# Appendix

This appendix supports the IST main body of *"When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels."* It is organised in seven parts (A-G) mirroring the main-body section ordering. All file paths refer to the reproducibility package (DOI to be assigned at acceptance; see `REPRODUCIBILITY.md`).

---

## A. Notation and Operator Catalogue

### A.1 Complete notation table

```
═══════════════ Paper Domain ═══════════════
Paper identity:   P1, P2, P4, P5

═══════════════ Experimental Objects ═══════════════
PUT set I:        {A1,A2,A3, B1,B2,B3, C1,C2,C3, D1,D2,D3}, |I| = 12
PUT:              S_i  (i ∈ I)
Class mapping:    cls : I → {A, B, C, D}     (open, extensible)
Valid input distribution:    D_S, sampling X_{K_eq} ~ D_S

═══════════════ Metamorphic Testing Side ═══════════════
Meta-Pattern (MP):
  MP = {MP_1, ..., MP_5}, k ∈ {1,...,5}      (open, extensible)
  MP_1 Conservation  MP_2 Monotonicity  MP_3 Convergence
  MP_4 Trajectory    MP_5 Partial-order
Metamorphic Relation:  MR_{i,k} (provided by P1), mr = (r, R) ∈ MR_{i,k}
Automated Verification Pipeline (AVP):
  AVP : Programs × MR_universe × R⁺ → {pass, fail}
  AVP(s, mr, ε_AVP^k)  invokes the verification method per MP_k

═══════════════ Mutation Testing Side ═══════════════
Mutation Operator family (MUT):
  MUT = {mut_1, ..., mut_5}, j ∈ {1,...,5}    (open, extensible)
  mut_1 = mut_C  mut_2 = mut_M  mut_3 = mut_G  mut_4 = mut_T  mut_5 = mut_F
  Signature:  mut_j : Programs → 2^Programs
Mutant:        s' ∈ mut_j(S_i)
Alignment:     align(j) = j

═══════════════ Three-State Decomposition (Fixed) ═══════════════
mut_j(S_i) = equiv_{i,k,j} ⊔ killed_{i,k,j} ⊔ survive_{i,k,j}    (mutually exclusive, exhaustive)

equiv determination (dual conditions):
  (E1) AVP-coherent:  ∀ mr ∈ MR_{i,k}: AVP(S_i, mr) = AVP(s', mr)
  (E2) Output-equiv:  ∀ x ∈ X_{K_eq} ~ D_S: ‖S_i(x) − s'(x)‖ ≤ ε_eq

killed determination:
  killed(s', MR_{i,k}) ⇔ ∃ mr ∈ MR_{i,k}: AVP(S_i, mr) = pass ∧ AVP(s', mr) = fail

═══════════════ Metric (Fixed Classical Structure) ═══════════════
SMS_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
            =  |killed_{i,k,j}| / (|killed_{i,k,j}| + |survive_{i,k,j}|)
            ∈ [0, 1]

═══════════════ LRCA Engineering Attribution Layer (Descriptive, Not in SMS) ═══════════════
Likely root-cause inventory:  C = {C1, ..., C5}      (open, extensible)
  C1 True semantic failure / C2 Tolerance perturbation / C3 OOD
  C4 Statistical-assumption violation / C5 Mutator artefact
LRCA output:    each s' ∈ killed annotated with root_cause(s') ∈ C
Descriptive quantities:    C1_share_{i,k,j}, suspect_share_{i,k,j}

═══════════════ Slicing and Cross-Class ═══════════════
Slicing:         aligned: j = k    cross: j ≠ k
Cross-class:     ΔSMS_c, c ∈ {A, B, C, D}
                 CV(ΔSMS) := std(ΔSMS_c) / |mean(ΔSMS_c)|

═══════════════ Tolerance and Sampling ═══════════════
Tolerance:       ε_AVP^k (MP-dependent), ε_eq (equivalence output tolerance)
Sampling:        K_eq = 1000 (E2 sample size), N = 20 (statistical replicates)
```

The notation skeleton (11 core concepts + three-state decomposition + SMS formula + AVP interface) is **fixed**; the *content* of MUT, MP, C, and cls is open to extension.

### A.2 LRCA decision tree and three-layer diagnostic protocol

**Five likely root causes** (open):

| Code | Meaning |
|---|---|
| C1 | True semantic failure (what P2 seeks) |
| C2 | Numerical tolerance perturbation |
| C3 | Out-of-distribution (OOD) |
| C4 | Statistical-assumption violation |
| C5 | Mutator artefact |

**Three-layer diagnosis with L0 artefact pre-scan:**

```
L0 artefact pre-scan:    double-blind review (§4.2.4 dual-LLM cross-source + 20% manual sampling)
L1 tolerance robustness: N = 20 replicates, fail ratio ≥ 0.80 considered stable
L2 OOD triage:           for C/D classes, distinguish valid D_S^valid from OOD
L3 statistical baseline: for Wilcoxon/DTW, IID/stationarity pre-check on PUT samples
```

**Decision tree:**

```
For each s' ∈ killed_{i,k,j}:
  L1: fail ratio < 0.80 → C2
       otherwise → L2
  L2 (C/D classes): fail only in OOD → C3
       otherwise → L3
  L3 (B/D classes + Wilcoxon/DTW): assumption violation → C4
       otherwise → artefact recheck
  Artefact evidence → C5
       otherwise → C1
```

**Multi-label priority:** C5 > C4 > C3 > C2 > C1.

**LRCA threshold calibration (9-grid scan; `lrca_calibration.json`).** Best ood_band=0.02 with any tolerance_multiplier (3.0 / 10.0 / 30.0) yields mean_C1_share 0.200 / H5 12/60 (20.0%); ood_band=0.05 (default) or 0.10 yields 0.164 / 10/60 (16.7%). `tolerance_multiplier` has zero impact (L1 tolerance rarely triggered); `ood_band` is the only discriminator. Calibration ceiling 12/60 = 20% remains far below 80% — H5 unattainable on this dataset, not a calibration issue (inherent SNR of LLM-mutant pools).

### A.3 AVP protocol specification and equivalence-judgement trade-off

`AVP : Programs × MR_universe × R⁺ → {pass, fail}`. Per-MP verification: MP_1 tolerance equality |LHS − RHS| ≤ ε; MP_2 / MP_5 Wilcoxon signed-rank α=0.05; MP_3 convergence-order + asymptotic residual ratio; MP_4 DTW distance threshold ε_DTW. AVP version = P1 arXiv commit hash; P2 package embeds AVP source.

**Three-candidate equivalence trade-off.**

| Determination | False-positive | False-negative | SMS bias |
|---|---|---|---|
| E1 alone | numerical coincidence + AVP-coherent | E1 false → non-equiv | Low (smaller denominator) |
| E2 alone | output match, MR differs (rare) | K_eq miss, full-space equal | High |
| **E1 ∧ E2** | both fail simultaneously | E1 ∨ E2 false → non-equiv | Slightly high (conservative) |

E1 alone is fooled by insufficient AVP coverage; E2 alone by numerical coincidence on K_eq. E1 ∧ E2 is the conservative complete instantiation; under `L_equiv` it reduces almost-everywhere to classical bitwise equivalence (Lemma 9.1). Counter-examples: E2 passes but E1 does not (rare; mutant coincides at K_eq but deviates at MR trigger points → non-equivalent); E1 passes but E2 does not (common; consistent within MR but numerical drift > ε_eq → non-equivalent).

---

## B. Experimental Subjects and Mutation-Operator Specialisations

### B.1 PUT selection rationale (detailed coverage argument)

**(a) Library-stack coverage.** numpy 2.4.4 (A1-B3 linear algebra / arrays), scipy 1.17.1 (A1 integrate, A2 linalg, B2 stats), scikit-learn 1.8.0 (C1-D3 surrogate / ML) — Python scientific-computing's de facto foundation stack (PyPI top-50, 2026-04). Uncovered: GPU / distributed (JAX, CuPy, dask), domain-specific (BioPython, Astropy, RDKit). Reserved for P3 (R5).

**(b) Mathematical-structure coverage.** ODE/PDE (A1, A3), direct linear algebra (A2), Bayesian analytic + MCMC + Monte Carlo (B1-B3), kernel + orthogonal polynomial + NN surrogate (C1-C3), convex optimisation + backprop + max-likelihood (D1-D3) — covers 8 of 12 chapters in Numerical Recipes (Press et al. 2007). Uncovered: advanced PDE solvers (FEM, FV, spectral); FFT; interior-point/trust-region optimisation; symbolic/CAS. Reserved for P3.

**(c) Comparison with benchmarks.** DeepCrime (Humbatova et al. 2021): P2 class D topical overlap on ML kernels. Defects4J (Just et al. 2014): no overlap, only mutation-as-fault-proxy reference. mutmut / cosmic-ray demos: general Python, P2 extends scientific-computing focus.

**(d) Scale vs representativeness.** Each PUT 50-400 LOC; signature standardised to `program(x: float) → float`. Substantively smaller than industrial code (typically 1-10 KLOC).

**Limitation.** The `float → float` signature is a substantive constraint, not engineering trade-off. Industrial inputs are typically high-dimensional (CFD grids, MD particles, FEM matrices); scalarised PUTs upper-bound mutant semantic complexity and may systematically under-estimate SMS and cross-class differences on industrial PUTs (declared §7 R5; P3 validates on industrial-grade PUTs).

### B.1.5 Systematic vs incidental

Syntactic tools may *occasionally* hit §3.2 (a) (cross-function-boundary) or (c) (algorithm class), but occasionality undermines two engineering functions of semantic mutation. **(i) Deepening source-code understanding.** Designing OS `np.linalg.det(M) → np.sum(np.diag(M))` requires knowing the two are equivalent on diagonal matrices but not on general matrices (`det = ∏ eigvals` vs `sum(diag) = trace = ∑ eigvals`); syntactic tool AST traversal does not require this understanding even when similar replacements appear. **(ii) Revealing deep faults.** Domain-semantic errors (physical-constant, unit conversion, boundary conditions, hyperparameter semantics, numerical-method order) are not AST-local; syntactic mutator design goals (operator typos, off-by-one, negation flips) have hit probability for domain errors much smaller than systematic semantic-mutator triggering, and lack repeatability. **Conclusion.** Syntactic tools occasionally producing mutants satisfying (a)(b)(c) is stochastic byproduct — not repeatable, not carrying engineering value. Systematic semantic mutation requires (a)(b)(c) to be design intent.

### B.2 Per-class operator specialisations

| Operator | Representative specialisations across PUTs |
|---|---|
| **mut_C** Conservation-breaking | A1 Lorenz: add ε_drift to RHS (slow Hamiltonian drift); A2 LU: decomposition omits k+1-th multiplier (breaks det conservation); B1 Beta-Bin: posterior omits normalisation; C1 GPR: covariance omits positive-definite diagonal term; D1 MLP: backprop omits one gradient term. |
| **mut_M** Monotonicity-breaking | A3 FDM: Δt coefficient occasionally negative; B2 MCMC: acceptance min(1, r) → min(0.95, r); C2 PCE: high-order coefficient sort inserts inversion; D2 SVM: decision-function sign flips near boundary. |
| **mut_G** Convergence-breaking | A1 Lorenz: RK4 → 1.5-order hybrid; A3 FDM: 2nd-order difference → 1st-order; B3 MC: doubling sample size does not 1/N-reduce variance; C3 NN-Surr: training-epoch truncation. |
| **mut_T** Trajectory-distorting | A1 Lorenz: state-vector y/z swap; B2 MCMC: insert independent-sampling segment; C3 NN-Surr: training-target slow phase shift; D1 MLP: hidden-layer periodic-mask activation. |
| **mut_F** Fidelity-order-breaking | A2 LU: partial pivoting degrades to no pivoting; C1 GPR: length-scale switches to coarse prior; C2 PCE: high-order term randomly retains low-order; D3 LR: regularisation occasionally large. |

**Per-class HP / OS / TF substitution rules** (illustrative). **HP** on class a: tolerance / max_iter; on class c: GPR `noise_level` / `length_scale`; on class d: MLP `hidden_dim` / dropout. **OS** on class a: numerical-linalg API swaps (`det` ↔ `sum(diag)`); on class b: probability-distribution sampling swaps; on class c: surrogate-class swaps (GPR ↔ RBF ↔ NN). **TF** on class a: integration-order changes (RK4 → Euler); on class b: MC estimator changes.

**Operator-level cross-table with cosmic-ray defaults** (R-15 response). The 12 cosmic-ray default operators are AST-local: `NumberReplacer` (Num/Constant — CE partial, △ literal values only); `ReplaceArithmeticOperator` (BinOp); `ReplaceComparisonOperator` (Compare); `ReplaceLogicalOperator` (BoolOp); `ReplaceUnaryOperator` (UnaryOp); `ReplaceTrueFalse` (NameConstant — CE keyword, △ Bool literal); `BreakContinueReplacer` (Break/Continue); `RemoveDecorator`; `RemoveExceptHandler`; `ZeroIterationForLoop` (For); `ReplaceIfBlock` (If); `MutateSubscript`. None correspond to OS / HP / TF / SI:

| P2 class | Tool support | Coverage |
|---|---|---|
| **OS** API replacement | None | △ 88.33% disjoint (incidental low-complexity hits) |
| **HP** | None | ✗ tool inexpressible (0/72) |
| **TF** numerical-method order | None | ✗ tool inexpressible (0/54) |
| **SI / CF** structural injection | None | ✗ tool inexpressible (0/33) |

**Operator-level conclusion.** All 12 default classes remain AST-local (BinOp / Compare / BoolOp / UnaryOp / NameConstant / Subscript / If / For / Break / Continue / decorator / except). Categorically, no entry recognises sklearn / scipy hyperparameter semantics (HP), numerical-method order (TF), or control-flow intent (SI / CF). For OS, low-complexity sub-expressions can be incidentally hit by BinOp; empirical 11.67% (§3.5) is consistent with 88.33% AST-disjointness lower bound.

### B.3 cosmic-ray a1 single-PUT pilot (pre-12-PUT empirical)

Before the 12-PUT generalisation (§3.5 main), a single-PUT lightweight empirical ran via `scripts/run_cosmic_ray_a1.sh` on a1 (file 934 B, AST-bound). Outcome: mutants_generated ~tens; ≥ 90% belong to BinOp / Compare / 12 default classes; small killed-by-`test_a1.py` ratio (P2 unit tests are output-shape/type sanity checks; most cosmic-ray mutants not killed) — empirical manifestation of the §3.2.6 thesis that syntactic-tool mutants are not aligned with MR-violation detection. The 12-PUT generalisation (§3.5) supersedes this pilot but corroborates the same conclusion at scale.

### B.4 Expected LRCA risk profile

**PUT-class × LRCA-layer risk weights.** A numeric: C2 dominant (★★★ on L1 tolerance). B probabilistic: C4 dominant (★★★ on L3). C surrogate: C3 dominant (★★★ on L2 OOD; ★★ tolerance). D ML: C3 + C4 mixed (★★★ L2; ★★ L3).

**Operator-PUT root-cause hotspots (expected).** A: mut_C/G/F dominantly C2 (numerical tolerance), mut_M/T C1 (true semantic). B: dominantly C4 (statistical-assumption violations). C: mut_C/M dominantly C2/C1 on c1/c2, mut_T/F dominantly C3 on c1/c2; c3 (NN-Surr) row dominantly C5 (artefact). D: d1 row dominantly C5 (training-noise artefact); d2/d3 dominantly C1 / C3 mixed.

**Expected suspect_share thresholds.** A: 0.10-0.20 (acceptance ≤ 0.25); B: 0.20-0.35 (≤ 0.40); C: 0.20-0.30 (≤ 0.35); D: 0.25-0.40 (≤ 0.45). 60-cell average: ≤ 0.20 (= H5; acceptance ≤ 0.25).

### B.5 Engineering-significance mapping

j = k aligned diagonal is the H2 threshold-test slice; j ≠ k off-diagonal is control; 6 vacant cells (○, P1 H6) are not formally adjudicated and are repurposed in §6.2 as descriptive evidence for R_sem / R_kill decoupling. v3 → v3b leap (+0.123) attributes to MR-MP design reselection (single-class, post-hoc; §3.4 caveats); v3b → v4 micro-change (-0.007) attributes to LLM-source diversity under prompt-fixed.

### B.6 Mutmut vs cosmic-ray default-operator overlap

Reviewer-requested manual operator-class cross-reference between cosmic-ray's 13 default operators (cosmic-ray 8.4.6, `cosmic_ray.operators` package) and mutmut's 14 default operators (mutmut current `main`, `src/mutmut/mutation/mutators.py`). Both default-operator sets are first-order AST-local replacements; neither implements a cross-function-boundary, domain-knowledge-dependent, or algorithmic-class-changing mutation (the three §3.2 necessary conditions for semantic mutation).

| Operator class | cosmic-ray default | mutmut default | Reaches §3.2 (a/b/c)? | P2 class reachability |
|---|---|---|---|---|
| Numeric literal ±1 | `number_replacer` | `operator_number` | (a) no, (b) no, (c) no | partial CE only (e.g. `_RHO=28.0 → 27.5`) |
| Binary arithmetic swap (+, −, ×, ÷) | `binary_operator_replacement` | `operator_swap_op` (binary subset) | (a) no, (b) no, (c) no | partial OS only (incidental) |
| Comparison swap (<, ≤, >, ≥, ==, !=) | `comparison_operator_replacement` | `operator_swap_op` (compare subset) | (a) no, (b) no, (c) no | none |
| Boolean swap (and ↔ or) | `boolean_replacer` | `operator_swap_op` (bool subset) | (a) no, (b) no, (c) no | none |
| Unary remove / swap | `unary_operator_replacement` | `operator_remove_unary_ops`, `operator_swap_op` | (a) no, (b) no, (c) no | none |
| Keyword swap (True/False, etc.) | `keyword_replacer` | `operator_keywords`, `operator_name` | (a) no, (b) no, (c) no | none |
| break ↔ continue / return | `break_continue` | `operator_keywords` (subset) | (a) no, (b) no, (c) no | none |
| Exception class swap | `exception_replacer` | (none) | (a) no, (b) no, (c) no | none |
| Decorator removal | `remove_decorator` | (none) | (a) no, (b) no, (c) no | none |
| Variable-binding insert / replace | `variable_inserter`, `variable_replacer` | `operator_arg_removal`, `operator_assignment` | (a) no, (b) no, (c) no | none |
| no_op insertion | `no_op` | (none) | (a) no, (b) no, (c) no | none |
| Zero-iteration `for` loop | `zero_iteration_for_loop` | (none) | (a) no, (b) no, (c) no | none |
| String content tweak (XX prefix, case flip) | (none) | `operator_string` | (a) no, (b) no, (c) no | none |
| Lambda body → `None`/`0` | (none) | `operator_lambda` | (a) no, (b) no, (c) no | none |
| Dict kwarg name (XX prefix) | (none) | `operator_dict_arguments` | (a) no, (b) no, (c) no | none |
| Symmetric/asymmetric string-method swap | (none) | `operator_symmetric_string_methods_swap`, `operator_unsymmetrical_string_methods_swap` | (a) no, (b) no, (c) no | none |
| Augmented → simple assignment | (none) | `operator_augmented_assignment` | (a) no, (b) no, (c) no | none |
| `match` case removal | (none) | `operator_match` | (a) no, (b) no, (c) no | none |

**Aggregate.** Cosmic-ray ∩ mutmut: ~9 of 13 cosmic-ray operators have a near-equivalent in mutmut (numeric, binary, compare, boolean, unary, keyword, break-continue, variable, plus partial overlap on string-prefix vs `XX`); 4 cosmic-ray operators are unique (exception, decorator, no_op, zero-iteration-for); 6 mutmut operators are unique (string content, lambda, dict-kwarg, string-method swap, aug-assignment, match-case). The union is approximately 21 distinct first-order AST-local operator classes. None of the 21 can:

- (a) Cross a function-call or module-import boundary (e.g. replace `det(M)` with `sum(np.diag(M))` requires knowing the equivalence on diagonal matrices — outside any default-operator scope);
- (b) Depend on domain knowledge for legality (e.g. a hyperparameter swap that knows `noise_level=1e-4` is the load-bearing knob in a Gaussian Process Regression PUT requires PUT-class awareness);
- (c) Change the algorithmic class (e.g. swap `polynomial → spline basis` rewrites the surrogate's mathematical structure).

The mutmut / cosmic-ray null intersection on §3.5's HP/SI/TF classes (zero overlap) therefore reflects a **structural property of first-order AST-local mutation** rather than a tool-specific limitation, supporting the §3.6 preventive-defence framing.

---

## C. Experimental Procedure Details

### C.1 Cross-source v4 protocol — full specification

**Three-stage ablation.**

| Version | Mutant pool | c-class primary MP | Use |
|---|---|---|---|
| v3 | Single-source (Claude Opus 4.6) | MP5 (P1 legacy) | H2 baseline (pre-registered) |
| v3b | Single-source (same as v3) | **MP1 (data-driven, §3.4)** | Isolate MR-MP design contribution |
| v4 | **Cross-source** (Claude Opus 4.6 + GPT-5.4 + DeepSeek chat) | MP1 | Isolate LLM-source diversity |

**Protocol** (`scripts/cross_source_campaign.py`). (a) For each (PUT, operator), Claude / GPT / DeepSeek run K = 3 trials with identical prompt (§4.2.2), temperature 0.7; `source_tag` propagated to filenames. (b) **V1-V4 mechanical validation** (`src/p2/mutators/validation.py`): V1 syntax (`ast.parse`), V2 executability, V3 non-triviality (`|y_mutant - y_original| > 1e-6`), V4 signature consistency. (c) **DeepSeek model:** `deepseek-chat` (113 tokens/call, 1.8 s), not `deepseek-v4-pro` (340 tokens/call, 11 s) — quality-equivalent on a2_OS1 dry-run. (d) **Pool capacity:** 37 ops × 3 sources × 3 trials = 333 attempts; V1-V4 pass rate 89%; 298 confirmed mutants. Sources contribute nearly equally: Claude 101 / GPT 98 / DeepSeek 99 (Phase A engineering finding). (e) **Sampling** (`scripts/build_pools.py`, POOL_VERSION = v4): per-PUT 30 max, measured mean 24.3, range 10-30. c1 (GPR) yields only 10 because c1_HP1 / c1_CE1 have V1-V4 near-zero pass (WhiteKernel noise_level 1e-4 → 1e-1 perturbation has minimal output impact, triggers V3 non-trivial failure — itself §6.2 evidence).

**Protocol-asymmetry (R13).** v4 does not invoke reviewer LLM (cost / speed priority; P4 will rerun dual-blind on v4 grid, ~$5-8 USD); v3 / v3b used the original Phase-1 dual-blind (Claude gen + GPT-5.4 review + DeepSeek arbitration). A fraction of Delta_delta(v3b → v4) = -0.007 may be slight v4 quality decline rather than LLM-source diversity.

**Chained-conditioning (R11).** v4 inherits v3b post-hoc c-class primary MP selection. Delta_delta(v3b → v4) is conditional on v3b selection + identical prompt — not neutral-condition LLM-diversity test. v4-pre (cross-source × c→MP5 pre-shift) not run because (i) it answers the same question as the differential-prompt experiment more economically in P4, (ii) cost is asymmetric to narrative benefit already exposed (~$20-30, 2-3 days wall time).

### C.1.1 Differential prompt protocol (R-16 future-work commitment)

R-16 concern: v3b → v4 micro-change of -0.007 may reflect "three LLMs under identical prompt" rather than "true upper bound of LLM diversity". Separation requires *one tailored differential prompt per LLM* (skeleton: `scripts/run_differential_prompt.py`).

**Design (2×3 factorial, within-(PUT, operator)).** Factor A — prompt template, 3 levels: **V_canonical** (control, identical to v4), **V_persona** (per-LLM identity: Claude "numerical-analysis editor"; GPT "scientific-software refactorer"; DeepSeek "library-API substitution specialist"), **V_cot** (Claude `<thinking>` tags; GPT "step by step"; DeepSeek stepped-reasoning). Factor B — LLM source (Claude / GPT-5.4 / DeepSeek chat). K = 3 per cell; total 37 × 3 × 3 × 3 = **999 trials**.

**Exit criteria.** If max(delta) − min(delta) < 0.05: v3b → v4 -0.007 robust. If ≥ 0.05 with prompt variant pushing delta past 0.474: H2 revised from "not met" to "prompt-conditional met" (`paper_numbers_v5.json`). If ≥ 0.05 but all delta < 0.474: prompt sensitivity exists but H2 unchanged.

**Resources.** API ~$18-30 USD; wall 3-4 h at concurrency 4; V1-V4 only, no reviewer LLM.

### C.2 Manual pilot lineage, LLM-client configuration, and L0 prescreen

The original §4.2 protocol used 60% multi-LLM consensus (Claude Opus 4.6 + GPT-5.4 + DeepSeek chat unanimous) plus 40% manual injection by scientific-computing researchers. Each (mut_j, S_i) pair carried one prompt template containing PUT source, semantic intent of mut_j, prohibition against revealing specific MRs (avoids prompt leakage), and output requirements (syntactically correct, executable, single-point modification, diff < 10 lines). Reproducibility parameters: temperature 0.3 in manual-pilot stage (v4 cross-source uses 0.7 per §C.1); fixed seed; 5 candidates per prompt with 2-3 retained.

**Double-blind review (Scheme C).** Generator LLM-G (Claude Opus) and reviewer LLM-R (GPT-4o) are cross-source with strict role separation. LLM-R sees only PUT original + mutant code, unaware of mut_j category / MR content / generator identity, outputting a triple (syntactic, executable, semantic-fault-injected). Double-confirmed mutants enter pool; inconsistencies enter manual arbitration (≤ 10%). From the double-confirmed pool, 20% is sampled for manual review; manual-vs-LLM-R inconsistency > 10% triggers full manual downgrade. Same-source bias mitigation stratifies LLM-R by PUT class. Prompt-injection mitigation disables RAG / web search on the API path.

**L0 pool prescreen.** Each mutant passes static syntax (linters / type checkers), a unit self-test (simple inputs produce finite output), and double-blind sign-off. Target: 30-50 candidates per cell → 10-15 retained after prescreen.

### C.4 LRCA three-layer execution (full)

Decision tree, multi-label priority (C5 > C4 > C3 > C2 > C1), and output (`C1_share`, `suspect_share`) are stated in §A.2; the full pseudocode is reproduced there. LRCA does **not** modify SMS; killed set is not filtered. §5.7 H5 numbers use best calibrated combination (`ood_band = 0.02, tolerance_multiplier = 3.0, repeats = 20`); default-threshold results retained in `lrca_60cell_v3.json` as control. Interface with §3.6 risk profile: L0 prescan ↔ §C.2 dual-LLM double-blind; L1 tolerance ↔ N = 20 repetition subprocess; L2 OOD ↔ input-distribution definition; L3 statistical baseline ↔ pre-check protocol.

### C.4.1 Pilot calibration (37 operators, K = 10/20)

A 2026 Q3 operator-level pilot ran 12 PUTs × 37 operators (12 `is_key=True` at K=20, 25 at K=10; 470 trials total). Pilot precursor quantities: R_sem (V1-V6 ∧ operator_match pass rate), D_impl (median pairwise AST + literal + identifier Jaccard distance among confirmed mutants), R_kill (proportion of confirmed mutants killed by AVP under that PUT's primary MP). Aggregate (N=37): R_sem median 0.50 mean 0.468 (0/37 with R_sem=0); D_impl median 0.42 mean 0.392 (1/37 with D_impl ≈ 0); R_kill median 0.00 mean 0.189. All 37 operators produced ≥ 1 V1-V6 passing mutant (verifying H1).

**Key R_sem / R_kill decoupling pattern.** R_sem ≥ 0.9 ∧ R_kill = 0 combinations all on HP / TF / OS operators in c / d classes (e.g., c1_CE1 noise 1e-4→1e-1 with R_sem 1.00, R_kill 0.00; c3_HP1 relu→tanh, c3_TF1 max_iter 1000→5, d1_HP1 MLP α, d3_HP1 LR C). R_sem-high ∧ R_kill = 1 combinations all on CE / OS operators in a / b classes (a2_CE1 LU det, a2_OS1 prod→sum, b1_OS1 α/β swap, d1_TF1 label flip). This is empirical evidence for §6.2 R_sem / R_kill decoupling at cell level.

---

## D. Statistical Analysis Details

### D.1 SMS variants and construction lemmas

**SMS_unfiltered (reviewer comparison metric):**

```
SMS_unfiltered_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
                          (same form as primary; killed does not distinguish C1 vs C2-C5)
```

The appendix of the reproducibility package provides cell-by-cell difference between SMS_unfiltered and SMS; if relative difference < 5%, this confirms LRCA does not affect robustness of primary conclusions.

**Primary-table construction.**

| RQ | Primary statistics | Reporting format |
|---|---|---|
| RQ1 | inst_rate, equiv_rate, C1_share, survive_rate | 60-cell heatmap + 4-class marginals |
| RQ2 | aligned-SMS vs cross-SMS; sparse ○ vs dense ●● equiv_rate | Cliff's delta + odds ratio + 95% bootstrap CI |
| RQ3 | ΔSMS_c (c ∈ {A,B,C,D}); CV(ΔSMS) | sign test (df=3) + descriptive forest plot |
| RQ4 | Spearman ρ + Kendall τ for SMS vs PC | scatter + dual-metric ranking comparison |

**Multiple comparisons.** Cell-level claims across 60 cells use Benjamini-Hochberg FDR, alpha_FDR = 0.05. N = 20 bootstrap intervals: 1,000-iteration 95% CI (B = 10,000 for the headline H2 delta CI).

### D.2 Cliff's delta cutoff sensitivity and logit-transformation invariance

**H5 cutoff sensitivity (R-14 response).** Dense grid scan (cutoff ∈ {0.05, 0.10, ..., 0.50}, step 0.05) on v4 data (`scripts/h5_sensitivity.py`, `data/results/h5_sensitivity_v4.json`):

| cutoff | h5_cells_pass | h5_pass_ratio |
|---|---|---|
| 0.05 | 12 / 60 | 20.0% |
| 0.10 | 12 / 60 | 20.0% |
| 0.15 | 12 / 60 | 20.0% |
| **0.20 (paper)** | **12 / 60** | **20.0%** |
| 0.25 | 12 / 60 | 20.0% |
| 0.30 | 12 / 60 | 20.0% |
| 0.35 | 12 / 60 | 20.0% |
| 0.40 | 12 / 60 | 20.0% |
| 0.45 | 13 / 60 | 21.7% |
| 0.50 | 13 / 60 | 21.7% |

**Conclusion.** H5 verdict (not met) is intrinsic data property, independent of cutoff choice. v4 suspect_share distribution is severely bimodal: median 1.0, mean 0.79; 48 cross cells at suspect_share ≈ 1, 12 aligned cells in low end; the [0.20, 0.80] interior is nearly empty. Specific value 0.20 is **not load-bearing**.

**Logit-transformation invariance.** Cliff's delta is rank-based (function of U / (n1·n2)), mathematically invariant under any strictly monotone transformation (Romano 2006). Logit is strictly monotone on (0, 1), so delta_logit ≡ delta_raw is a construction result. `data/results/rq2_cliffs_delta_logit_v4.json` shows delta_logit = 0.439 = delta_raw (difference 0.000), consistent with rank-invariance theorem. **Not additional robustness evidence**; H2 robustness threats come from §3.4 v3b post-hoc selection and §5.2 zero-mass dominance, not metric-scale choice.

### D.3 Power analysis — plug-in and stipulated-alternative

**Plug-in bootstrap.** With-replacement sample from observed aligned (n=12) and cross (n=48) v4 SMS pools; N_sim = 5,000, seed = 42 (`scripts/compute_rq2_power.py`, `rq2_power_v4.json`):

| Threshold | Interpretation | Power |
|---|---|---|
| delta > 0.000 | Any-effect | **0.997** |
| delta > 0.147 | Small | 0.966 |
| delta > 0.330 | Medium | 0.759 |
| **delta > 0.474** | **Large (H2)** | **0.423** |

Sample-size sweep (n_aligned ∈ {6, 12, ..., 60}, n_cross = 4×): power for delta > 0 reaches 0.974 at n=6, 0.996 at 12, plateaus thereafter. RQ2 primary analysis has very low sample-size requirement; the bottleneck is the effect-size boundary itself, not sampling noise. Even at delta_truth ≈ 0.474, sample has only ~42% chance of detecting under plug-in; but this does **not** mean "insufficient power is the cause of H2 not being met" — observed delta = 0.439 < 0.474; increasing sample only narrows CI.

**Stipulated-alternative (R1 W1 round-2).** Implementation via mixture-weight (`scripts/compute_rq2_power_stipulated.py`, N_sim = 2,000): SMS has heavy ties at zero (45/60 = 0), raw shifting is discontinuous (any ε > 0 jumps delta from 0.314 to 0.74). Mixture: aligned' = (probability w) sample from (observed_aligned + 0.001) + (probability 1−w) sample from observed_aligned, calibrate w so E[delta] ≈ 0.474. Calibrated w = 0.094, realised E[delta] = 0.4746.

| Stipulated truth | Criterion | Power |
|---|---|---|
| 0.474 | delta_hat ≥ 0.474 (point-estimate) | **0.491** |
| 0.474 | 95% CI lower > 0 (any-effect) | 0.868 |

Even at delta_truth = 0.474, the (12, 48) design returns delta_hat ≥ 0.474 in only ~49% of replications — this *supports* the §5.3 framing that "not met" is point-estimate, not effect-size.

### D.4 Friedman per-class — discussion of small-N concordance

Per-class Friedman (3 PUTs × 5 MPs) with Bonferroni × 4: a chi^2=4.00 raw 0.406 adj 1.000, W=0.333; b chi^2=10.78 raw **0.029** adj **0.116**, W=**0.898**; c chi^2=4.00 raw 0.406 adj 1.000, W=0.333; d chi^2=5.00 raw 0.287 adj 1.000, W=0.417. After correction, no per-class result remains significant at family-wise alpha = 0.05. Even b-class W = 0.898 (Cohen 1988 large concordance) is insufficient at N = 3 per class. **H4 verdict rests on §5.5 sign test**; per-class Friedman is sensitivity / descriptive only. Friedman main effect on full 60 cells (chi^2 = 15.30, p = 0.0041) confirms MP rank differences but is logically independent from H4 cross-class consistency.

**Mixed-effects unavailability.** Primary `sms ~ C(class) + C(operator) + C(class):C(operator) + (1 | put)` returned Singular (insufficient column rank for class × operator interaction; N=60 too small for 11-d fixed-effects + 12 PUT random intercepts). Fallback `sms ~ C(class) + C(operator) + (1 | put)` had PUT random-intercept variance hit boundary 0 (degenerates to OLS). Fallback class p-values (descriptive only): b vs a 0.275 / c vs a 0.892 / d vs a 0.991. RQ3 conclusion shifts to four-piece presentation (class means + sign test + Friedman + forest plot).

### D.5 Pattern-coverage operationalisation

Per PUT, (MP_k, R_outcome ∈ {True, False}) binary-tuple coverage: 5 MPs × 2 outcomes = 10 cells, PC = #triggered / 10. Simplest baseline (per-PUT granularity, not distinguishing mutants). PC range over 12 PUTs: [0.500, 1.000], mean 0.733 (`paper_numbers_v4.json`). Pairing per PUT: Spearman rho = 0.163 (p = 0.613); Kendall tau = 0.136 (p = 0.568).

**Power caveat.** At n = 12, Spearman 95% CI ≈ [-0.5, +0.6]; cannot distinguish "zero correlation" from "moderate positive" or "moderate negative". p = 0.61 / 0.57 means "no correlation detected at n = 12", not "correlation does not exist".

**Within-class descriptive.** b2 PC = 1.0 with mean SMS = 0.067; b1 PC = 0.7 with mean SMS = 0.20. c3 PC = 1.0 with mean SMS = 0.14; c1 / c2 PC = 0.7-0.8 with mean SMS = 0.0. Within the same class, higher-PC PUT has lower SMS — contradicts naive "more PC kills more mutants" assumption. Suggestive of orthogonality but n = 12 cannot confirm. P4: expand to n ≥ 30 + refine PC to incorporate mutant dimension.

---

## E. Stakeholder Deployment Considerations (Single-Output Kernels Scope)

### E.1 Air-gap incompatibility — full justification

The §6.4 workflow depends on external LLM API calls (Claude / GPT / DeepSeek), incompatible with most regulated air-gapped V&V workflows:

| Domain | Standard | Air-gap requirement |
|---|---|---|
| Nuclear | IEC 60880 | Air-gapped build for safety-critical software |
| Aerospace | DO-178C | Tool-qualified offline build for DAL-A/B; LLM API outside qualified-tool envelope |
| Medical | IEC 62304 | Class C software lifecycle requires offline reproducible build |
| Automotive | ISO 26262 | ASIL-D requires offline tool chain; cloud LLM non-compliant |

**Mitigation paths (P5).** (i) Self-hosted open-weight LLMs (Llama / DeepSeek local inference) — capability gap vs API-served frontier models; quantitative impact on SMS untested. (ii) Offline-cached pre-generated mutant pools with commit-hash + raw-response signature locking — adopters reproduce a published pool offline (this paper's package supports this), but generating new pools requires external LLM access. SMS for air-gapped industrial deployment is a P5 research direction.

### E.2 Quarterly batch audit workflow

The original §6.5.2 per-PR GitHub Actions YAML was removed in R3 round-2 because it hardcoded `SMS_VERSION=v4` + `P2_PRIMARY_VERSION=v3b` (exploratory post-hoc) into stakeholder-facing CI, propagating selection-on-response into adopters' pipelines; PR-CI threshold 0.10 contradicted §6.5.3 audit threshold 0.20.

**Replacement: quarterly batch audit:**

| Step | Description | Cost |
|---|---|---|
| 1 | Offline mutant-pool generation (per PUT 24-30 × 12 PUTs ≈ 300) | LLM API $5-15; ~30 min |
| 2 | `sms_campaign.py --track 2` | 4-core laptop ~10-20 min |
| 3 | `run_lrca.py` | < 1 min |
| 4 | MR-design team review of MRs with aligned-cell SMS significantly below historical median (0.275) | 1-2 h meeting |

Quarterly: API ~$10 + automation 30 min + manual 1-2 h ≈ 0.5 person-day. Affordable. Per-PR gating not recommended (LLM latency 5-30 s + cost + non-determinism + air-gap incompatibility); adopters needing per-PR should use coverage / unit-test gates. SMS does not replace domain-expert MR physical-reasonableness judgement nor product-requirements review.

### E.3 V&V documentation — conceptual complementarity with ASME V&V 20-2009

§6.5.3 was retitled from "Auditors / certification bodies" in R3 round-2: this subsection makes **no normative claim** toward NRC, FDA, or ISO 26262 review teams. Within single-output kernels scope, no traceable mapping exists to current IEC 60880 / ISO 26262 / DO-178C / ASME V&V 20-2009 normative bodies.

V&V documentation for scientific computing software (per ASME V&V 20-2009 §3 and similar guides) requires quantifiable test-adequacy evidence; current documentation often relies on code coverage + MR lists + SME signatures. SMS may appear as **research-grade supplementary evidence** alongside coverage and MR lists: (a) aligned-cell SMS per critical PUT; (b) LRCA three-layer diagnosis (C1 readout / C2-C5 attribution); (c) 60-cell matrix visualisation. Reviewers can independently run `REPRODUCIBILITY.md`.

**R3 round-2 deletion** of original threshold recommendations (aligned-cell SMS ≥ 0.20 / 0.30 + C1_share ≤ 0.20): no normative backing in IEC / ISO / ASME; misreads as enforce-ready; §3.4 declares 0.275 baseline influenced by v3b post-hoc selection. **SMS reported as descriptive supplementary evidence**, with adequacy judgements left to V&V reviewers case-by-case.

Conceptually complementary to ASME V&V 20-2009 §3 code verification (numerical-solver correctness) vs SMS (MR-set fault-detection adequacy). Substantial scale gap to multi-module CFD codes; incorporation into V&V standards body would require P5 large-scale empirics + multi-year dialogue with ASME V&V 20 / IEEE 1012 / IEC 60880 committees. **No advocacy that SMS enter any normative certification system in 2027.** SMS does not replace SME signatures, FMECA, PIRT, system-level V&V, or ASME V&V 20 §3 numerical-solver verification — it is one link in the evidence chain, not a single-point qualification.

---

## F. Threats to Validity — Detailed Mitigation

### F.1 Internal threats

| ID | Threat | Mitigation | Residual |
|---|---|---|---|
| R1 | LLM generation reproducibility | §C.2 reproducibility parameters in package; dual-LLM cross-source + 20% manual; identical prompt+seed should yield ≥ 90% pool overlap | LLM training data may be updated post-submission |
| R2 | Probabilistic equiv (K_eq=1000) | §2.3 declares probabilistic approximation; Hoeffding-style false-equiv bound | K_eq sweep ∈ {500,1000,2000} deferred to P4 (R1 W3 round-2) |
| R3 | P1 ↔ P2 circular dependency | AVP version pinned to P1 commit hash; package embeds AVP source; §1.6 declares P1 as arXiv technical report | None within scope |
| R4 | LRCA multi-label boundary | §A.2 priority C5>C4>C3>C2>C1; multi-label co-occurrence table in package; root_cause is "likely root cause" not definitive | C2-C5 may multi-trigger on B/D classes |
| R9 | Mutant-pool size | Pool expanded to mean 17.4: delta moved 0.321 → 0.323, CI narrowed; **effect size is intrinsic ceiling, not pool dilution** | Some PUTs < 30 (cache-bound) |
| R10 | LLM non-determinism | Multi-turn de-dup; K=10/20 repetitions; raw prompt+response committed for direct reuse | Claude Opus subscription lacks seed control |
| **R11** | **Chained-conditioning (NEW, P0-5)** | Abstract / §5.5 / §6.3 downgraded v3b/v4 sign tests to exploratory; §3.4 permutation p = 0.9885; Bonferroni alpha_eff = 0.01 | Cannot be fully eliminated within this paper — needs v4-pre rerun or P4 differential prompt |
| **R13** | **Protocol-implementation gap v3/v3b vs v4 (NEW, P1-7)** | v4 used 3 providers (Claude 101 / GPT 98 / DeepSeek 99); v4 C1_share 0.209 > v3b 0.164 weakly opposes "v4 quality decline" | Complete separation requires P4 dual-blind rerun on v4 grid |

R11 and R13 are non-overlapping: R11 = *selection* asymmetry (c-class primary MP inheritance); R13 = *protocol* asymmetry (dual-blind vs V1-V4 only). Both contribute to the explanation space of Delta_delta(v3b → v4) and cannot be merged as a single signal.

### F.2 External / construct / conclusion threats

| ID | Threat | Class | Mitigation |
|---|---|---|---|
| R5 | 12-PUT representativeness | External | Follows P1 site selection; §1.6 P-II open principle (cls extensible); P3 scaling to MD/QC/CFD |
| R6 | Cross-class statistical power | Conclusion | H4 framed exploratory; mixed-effects unavailable (Singular at N=60); shifted to class means + sign test + Friedman + forest plot |
| R7 | LLM homogeneity bias | Construct | §C.2 three-LLM rotation + PUT-class subdivision + 20% manual sampling; third-party LLM family validation deferred |
| R8 | LLM-source distributional shift | External | Hit distribution DeepSeek 11/15, Claude 4/15, GPT 0/15; §3.5 argument is categorical AST-locality, not hit frequency; HP/SI/TF zero-overlap across all 3 sources unaffected |
| R12 | HOM equivalence | External | Tool-unreachability claim confined to first-order syntactic tools; HOM empirical testing listed as P4 future work |

Conclusion threats: multiple comparisons handled by BH-FDR at alpha_FDR=0.05 (§D.1); N=20 stability handled by 1,000-iteration bootstrap CI (§D.3). Construct threat — SMS measures epistemological semantic detection, not production engineering value (P2-CN scope).

---

## G. SMS → MS Degeneration Theorem — Full Proof

### G.1 Notation cross-reference (with §2.1)

PUT `S_i`, mutation operator family mut (syntactic or semantic), mutant set mut(S_i), MP set, equivalence tolerance ε_eq, equivalence sample size K_eq, AVP tolerance ε_AVP. Three-state decomposition: `mut(S) = killed ∪ equiv ∪ survive` (disjoint). SMS formula:

```
SMS_{i,k,j} = |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
```

### G.2 Degenerate-limit definition (R-8 + P1-3 revision: 3 joint conditions)

The degenerate limit `L = L_equiv ∧ L_killed ∧ L_mut` consists of three **joint conditions** (paired axes), each controlling one layer of the SMS formula. L1-L6 are not 6 independent axes; the pairing responds to dependency queries (R0 W8 / R1 §4 / R2 W3 / DA-MAJOR-3).

| Joint condition | Component axes | Pairing rationale |
|---|---|---|
| **L_equiv** (Lemma 9.1) | L1: ε_eq → 0; L2: K_eq → ∞ | L1 alone: equiv stays probabilistic (K_eq cannot cover D_S). L2 alone: bitwise equality diluted by ε_eq. Both simultaneously degenerate equiv to classical behavioural equivalence outside a D_S-measure-zero set. |
| **L_killed** (Lemma 9.2) | L3: ε_AVP^k → 0; L4: MP = {MP_eq}, R(y,y') ≡ y = y' | L3 alone: ε_AVP → 0 still allows non-trivial MP (monotonicity, convergence). L4 alone: equality still carries ε_AVP tolerance. Both simultaneously degenerate killed to classical difference detection. |
| **L_mut** (Lemma 9.3) | L5: mut_j → rule-based syntactic (Mothra AOR/ROR/SDL/CRP); L6: cls(I) ⊆ {imperative deterministic} | L5 alone: syntactic ops on probabilistic/ML may still trigger domain-semantic subsets. L6 alone: imperative programs still mutable by OS/HP/TF/SI. Both simultaneously degenerate mut(S) to Jia & Harman syntactic mutant set. |

### G.3 Lemmas — Three-state decomposition degenerates under L

**Lemma 9.1 (equiv degeneration; P1-3 revision with measure-zero qualification).** Under L_equiv (L1 ∧ L2), semantic-class equivalence (E1 ∧ E2) degenerates to classical behavioural equivalence **almost everywhere** w.r.t. measure D_S.

*Proof.* E1 (type consistency) holds trivially under ε_eq → 0 (L6 makes imperative output spaces scalar/vector with static types). E2 (|S_i(x) − s'(x)| < ε_eq for K_eq samples) under L1 (ε_eq → 0) ∧ L2 (K_eq → ∞ with measure-equivalent sampling) is almost-everywhere equivalent to ∀ x ∈ D_S \ N: S_i(x) = s'(x), where N is a D_S-measure-zero set (continuous D_S: floating-point pathological points / NaN propagation; discrete D_S: N = ∅). This matches Jia & Harman (2011) §3 classical equivalent-mutant definition under measure-zero equivalence classes. ∎

**Lemma 9.2 (killed degeneration).** Under L3 ∧ L4, killed degenerates to classical difference detection.

*Proof.* L4 restricts MP to {MP_eq} with R(y, y') ≡ y = y'. For mr = (r, R) and mutant s', the MP_eq violation condition ∃ x: S_i(x) ≠ s'(r(x)) under L3 (ε_AVP → 0) becomes exact inequality. With r = id, violation is S_i(x) ≠ s'(x) — classical difference detection. With r ≠ id, MP_eq still requires S_i(x) = s'(r(x)) as reference oracle from original program; no new state classifications introduced. ∎

**Lemma 9.3 (mut degeneration).** Under L5 ∧ L6, mut_j(S_i) degenerates to the syntactic mutant set of Jia & Harman (2011).

*Proof.* L5 switches mut_j to rule-based syntactic operators (AOR, ROR, SDL, CRP, UOI — standard Mothra/Proteum sets); L6 restricts PUTs to imperative deterministic programs, excluding triggering conditions for semantic operators on probabilistic/ML programs. Under this configuration, mut_j(S_i) is the literature-defined syntactic mutant set, independent of domain semantics. ∎

### G.4 Theorem 9.1 — Detailed proof

**Theorem 9.1 (SMS → MS degeneration).** In the degenerate limit `L = L_equiv ∧ L_killed ∧ L_mut`, almost everywhere w.r.t. D_S,

```
SMS_{i,k,j}  -L→  MS_{i,j} := |killed_{i,j}^classic| / (|mut_j^syntax(S_i)| − |equiv_{i,j}^classic|)
```

*Proof.* Combine Lemmas 9.1-9.3:

- Numerator: under L3 ∧ L4, killed_{i,k,j} → killed_{i,j}^classic (Lemma 9.2); L4 makes MR_{i,k} trivial over k (only MP_eq remains), so subscript k degenerates.
- Denominator |mut_j(S_i)|: under L5 ∧ L6 → |mut_j^syntax(S_i)| (Lemma 9.3).
- Denominator |equiv_{i,k,j}|: under L1 ∧ L2 → |equiv_{i,j}^classic| (Lemma 9.1; almost-everywhere w.r.t. D_S).

Substituting into the SMS formula yields MS_{i,j}. ∎

**Corollary 9.1 (LRCA trivialisation).** Under L = L1 ∧ L2 ∧ L3, C = {C1, ..., C5} degenerates to {C1}.

*Sketch.* Each of C2-C5's triggering precondition depends on at least one L_j being violated. When L1 ∧ L2 ∧ L3 hold simultaneously, every non-trivial-space dimension (MP non-triviality, AVP tolerance non-zero, non-empty equiv set, MR-design DOF, class-mapping openness) closes; C2-C5 triggering set becomes empty (read off from §A.2 decision tree). The per-C_k to per-L_j minimum-sufficient mapping depends on §4.6 LRCA-classifier engineering thresholds; we do not claim one-to-one correspondence at formal level — readers can trace via §A.2 + §C.4. Under L, suspect_share → 0, LRCA reports only C1 — SMS degenerates to single-layer metric consistent with Jia & Harman (2011) MS engineering structure. ∎

**Empirical consistency.** Theorem 9.1 + Corollary 9.1 jointly guarantee any SMS-based empirical conclusion (Cliff's delta §5.3, Friedman chi^2 §5.5, Spearman rho §5.6) is structurally consistent with existing Jia & Harman (2011) literature in classical syntactic-mutation scenarios — no metric-level semantic fragmentation.
