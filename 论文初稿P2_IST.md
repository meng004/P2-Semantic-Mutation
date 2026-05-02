# When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels

## Highlights

- Five semantic mutation operators degenerate to the classical Mutation Score in a proven limit.
- Across 12 Programs Under Test and 60 cells, 292 LLM-generated mutants overlap with 1,250 cosmic-ray syntactic mutants on only 5.14% of abstract syntax trees.
- The Hyperparameter, Structural Injection, and Trajectory Flip classes (54.5% of the mutant pool) are categorically unreachable by first-order syntactic tools.
- Primary v3 Cliff's delta = 0.323 (H2 large-effect threshold not met); cross-source pooling shifts delta by ≤ 0.01 across two MP conditions (v3 → v4-mp5 = −0.009; v3b → v4 = −0.007).
- Stipulated-alternative power at the H2 boundary is 49.1%, so the "not met" verdict is a statement about the point estimate, not about the effect size.

## Abstract

**Context.** Metamorphic Testing (MT) addresses the test-oracle problem in scientific computing, but the classical Mutation Score (MS) is defined over syntactic Abstract Syntax Tree (AST) mutations and so misses domain semantics such as conservation, monotonicity, and convergence order.

**Objective.** We propose the Semantic Mutation Score (SMS), built on five domain-semantic operators — Conservation Erosion, Operator Substitution, Hyperparameter, Trajectory Flip, and Structural Injection. SMS degenerates almost everywhere to MS in a characterised limit, so any SMS-based conclusion remains consistent with prior mutation-testing literature in the classical regime.

**Method.** We instantiate a 12 × 5 matrix of Programs Under Test (PUTs) and meta-patterns (MPs), giving 60 cells with a mean of 24.3 mutants per PUT and N = 20 Automated Verification Pipeline (AVP) repetitions. The PUTs span four single-output `float → float` classes (numeric, probabilistic, surrogate, machine learning; each under 2 KB). A three-layer Layered Root-Cause Analysis (LRCA) classifier separates true semantic faults from tolerance perturbation, out-of-distribution trips, statistical-assumption violation, and mutator artefacts. A three-stage ablation — v3 same-source, v3b data-driven primary MP, v4 cross-source over Claude, GPT, and DeepSeek under an identical prompt — isolates the contribution of metamorphic-relation (MR) design from that of Large Language Model (LLM) source diversity. We compare the 292 v4 mutants against 1,250 cosmic-ray syntactic mutants at the AST-normalised level.

**Results.**
*Primary verdict (v3, pre-registered).* The H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is **not met under the point-estimate criterion**: v3 δ = 0.323 (95% CI [0.017, 0.622]). Stipulated-alternative power at δ_truth = 0.474 is **49.1%**, so "not met" describes the point estimate, not the underlying effect size.
*Robustness (v4-mp5, strips R11).* Holding the c-class primary at the pre-registered MP5 while pooling across LLM sources gives δ_v4-mp5 = 0.314 (95% CI [0.014, 0.622]); the contrast against v3 is Δδ = −0.009 (LLM-source axis under MP5).
*Exploratory (v3b / v4, post-hoc selection).* v3b reaches 0.446† (data-driven c-class primary MP, same source); v4 reaches 0.439† (cross-source, MP1); Δδ(v3b → v4) = −0.007. Across both MP conditions the cross-source axis shifts δ by ≤ 0.01 in magnitude, while the MR-design axis (MP5 ↔ MP1) shifts δ by approximately +0.12.
*Other.* Cross-source pooling raises mean C1\_share from 0.164 to 0.209 and class-c SMS by +91.4%† without moving δ. Friedman χ² = 15.30, p = 0.0041. AST overlap with cosmic-ray is **5.14%**; the Hyperparameter, Structural Injection, and Trajectory Flip classes (159 of 292 mutants) are categorically unreachable by **first-order** syntactic tools (0/0/0). († v3b/v4-derived numbers depend on the §3.4 post-hoc c-class primary-MP shift; permutation null one-sided p = 0.9885.)

**Conclusion.** Within this design, the MR-design axis (c-class primary-MP choice) is the lever on the aligned-vs-cross effect size; the LLM-identity axis (Claude / GPT / DeepSeek under an identical prompt) shifts δ by ≤ 0.01 across two MP conditions. The strong-sense source-diversity test with per-LLM differential prompts is deferred to P4. The §3.5 evidence (5.14% AST overlap, 0/0/0 unreachability for HP / SI / TF under first-order syntactic tools) is independent of this caveat. SMS is a backward-compatible adequacy metric for domain-semantic MR sets.

## Keywords

metamorphic testing; mutation testing; semantic mutation operators; LLM-generated mutants; ablation study; metamorphic relation adequacy; cross-source mutant pool; Cliff's delta; single-output scientific computing kernels

---

## 1. Introduction

### 1.1 Motivation and scope

Metamorphic Testing (MT) addresses the test-oracle problem in scientific computing software: instead of checking outputs against a known-correct reference, MT checks metamorphic relations (MRs) — invariants connecting outputs of related inputs. The adequacy of an MR set, however, has lacked a domain-aware metric. Jia and Harman's (2011) classical Mutation Score (MS) is defined over syntactic Abstract Syntax Tree (AST) mutations and does not capture domain semantics such as conservation laws, monotonicity, convergence order, trajectory shape, or fidelity ordering. Recent work on Large Language Model (LLM) generated mutants (Tip, Bell, and Schäfer 2024; Humbatova, Jahangirova, and Tonella 2021) does generate semantically richer mutants, but does not separate the contribution of LLM source diversity from the contribution of MR design.

Throughout this paper we use the term *four representative classes of single-output scientific computing kernels* (numeric, probabilistic, surrogate, and machine-learning), and avoid the ambiguous software-engineering term *paradigm*. The scope of our claims is strictly bounded to single-output `float → float` kernels: each Program Under Test (PUT) is under 2 KB, and broader industrial transfer is reserved for the P3 and P5 companion papers.

### 1.2 Three-layer methodological framework

We organise the contribution as a three-layer framework around domain-semantic mutation operators.

- **Layer 1, Definitional (§3.2).** A mutation is *semantic* if it satisfies at least one of three necessary conditions: (a) it crosses a function-call or module-import boundary, (b) it depends on domain knowledge for legality, or (c) it changes the algorithmic class. The five meta-operator classes — Conservation Erosion (CE, also written mut_C), Operator Substitution (OS, mut_M), Hyperparameter (HP, mut_G), Trajectory Flip (TF, mut_T), and Structural Injection (SI, mut_F) — specialise these conditions across the four PUT classes.
- **Layer 2, Operational (§2.3, §4.3).** An equivalence judgement E1 ∧ E2, where E1 is Automated Verification Pipeline (AVP) coherence and E2 is output equivalence on K_eq = 1000 samples, gives the conservative instantiation of the Layer-1 conditions. The trade-off against E1-alone and E2-alone variants is in Appendix A.3.
- **Layer 3, Applied (§3.5).** AST-normalised empirical traceability across all 12 PUTs: comparing 292 v4 mutants against 1,250 cosmic-ray syntactic mutants, we show empirically that the v4 pool is not a subset of the syntactic-mutant pool.

The 60-cell empirical audit reported in Section 5 is one demonstration following this backbone, not the paper's main contribution. SMS is positioned as a strict generalisation of classical MS: under the degenerate limit `L = L_equiv ∧ L_killed ∧ L_mut` formalised in §2.6, SMS reduces almost everywhere to MS.

### 1.3 Related work and roadmap

This paper is P2 in a five-paper roadmap. P1 audits MR meta-patterns on the same 12-PUT infrastructure (Meng Li et al., *Progress in Nuclear Energy*, under review). P4 is the unified-theory companion (minimal MR-subset existence and three-pillar coupling). P5 and P2-CN cover regulatory and engineering transfer.

Three lines of prior work bracket the contribution of this paper.

**(i) Classical mutation testing.** Jia and Harman (2011) and Papadakis et al. (2019) survey syntactic mutation. The Coupling Effect Hypothesis (CPH) — that tests detecting simple faults also detect complex faults — underpins the use of MS as a fault proxy (DeMillo, Lipton, and Sayward 1978; Andrews, Briand, and Labiche 2005; Just et al. 2014). We argue in §3.5 that CPH holds within syntactic mutation but does not automatically extend across the syntactic-versus-domain-semantic boundary, even when it couples simple syntactic faults to complex syntactic faults. The §3.5 empirical evidence (5.14% AST overlap on 12 PUTs, with HP, SI, and TF at 0/0/0) is the empirical witness for this boundary.

**(ii) Higher-order mutation.** Jia and Harman (2009) and Kintis et al. (2018) study compositions of first-order syntactic mutants. We explicitly exclude any equivalence claim about Higher-Order Mutation (HOM) and list HOM as residual threat R12 (Appendix F.1).

**(iii) LLM-generated mutants.** Tip, Bell, and Schäfer (2024) introduce LLMorpheus, which uses single-LLM JavaScript mutants. Humbatova, Jahangirova, and Tonella (2021) introduce DeepCrime for deep-learning real-fault mutation. Moradi Dakhel et al. (2024) extend LLM-driven mutation testing to test generation on Java PUTs, providing an *Information and Software Technology* anchor for the LLM-mutant lineage. To our knowledge no prior LLM-mutant work isolates *LLM source diversity* from *MR design* in the contribution to effect size; the three-stage ablation in §4.2 closes this gap. On the equivalent-mutant problem, Delgado-Pérez and Chicano (2020) emphasise the importance of the `equiv` term in the MS denominator; we extend that classical bitwise-equivalence definition to a semantic-class equivalence E1 ∧ E2 in §2.3. Zhang et al. (2021) demonstrate MT validation in class-integration test ordering — a non-scientific-computing domain — and the present paper specialises MT to scientific-computing PUTs and couples it to a domain-semantic mutation operator framework.

A numerical-coincidence note. Petrović and Ivanković's (2018) ~20% "productive-mutant" rate at Google is numerically close to our LRCA-calibrated C1\_share of 0.20. The two constructs differ — developer survey (subjective) versus three-layer classifier (output) — so the agreement is a contextual numerical coincidence rather than mechanism validation, as we discuss in §6.1.

The SMS metric is conceptually complementary to the code-verification scope of ASME V&V 20-2009 §3, which targets numerical-solver correctness. SMS targets MR fault-detection adequacy; we make no normative compliance claim (Appendix E.3 records this as a long-term aspiration only).

### 1.4 Research questions

- **RQ1** Distributions of inst_rate, equiv_rate, C1_share, survive_rate over 60 cells.
- **RQ2** SMS difference structure between operator-MP aligned (j=k) and cross (j≠k) slices.
- **RQ3** Cross-class consistency across 4 program classes × 5 operators.
- **RQ4** Empirical relationship between SMS and Pattern Coverage (**descriptive only at n = 12; no formal test**; pre-registered as a P4 hypothesis-generating observation).

### 1.5 Hypotheses

- **H1.** At least 4 of the 5 operators produce ≥ 5 non-equivalent mutants on at least 9 of the 12 PUTs.
- **H2.** The aligned-SMS to cross-SMS odds ratio is ≥ 3.0, and Cliff's δ is ≥ 0.474.
- ~~H3~~ retired before v3 data collection: its bidirectional-threshold formulation collapses on LLM-mutant data because too few cells trigger any non-zero equivalent mutant. The R_sem versus R_kill decoupling phenomenon now appears in §6.2 as descriptive evidence.
- **H4.** A within-class sign test gives 4/4 across the 4 classes, and CV(ΔSMS) < 0.5.
- **H5.** Mean suspect\_share is ≤ 0.20 across the 60 cells.

We keep the numbering H1, H2, H4, H5 (with H3 vacant) for cross-reference consistency.

### 1.6 Boundary between P2 and the companion papers

P2 contributes the tool and the empirical report on 12 PUTs and 60 cells. P4 will contribute formal theorems (minimal MR-subset existence, reachable adequacy, three-pillar coupling). The 12 PUTs are deliberately *Numerical Recipes*–style toy kernels: they provide a verifiable minimum working example for the three-layer backbone, and industrial-scale transfer is reserved for P5.

---

## 2. Notation and Equivalence Judgement

### 2.1 Vocabulary inheritance

Seven classical mutation-testing concepts are inherited verbatim from Jia & Harman (2011) and Ammann & Offutt (2008) - PUT (`S_i`), mutation operator (`mut_j ∈ MUT`), mutant (`s' ∈ mut_j(S_i)`), equivalent mutant (`equiv_{i,k,j}`), killed mutant (`killed_{i,k,j}`), surviving mutant (`survive_{i,k,j}`), and Mutation Score. The SMS formula structure is preserved, with extension applied only to the *internal definitions* of `mut`, `equiv`, and `killed`.

Three-state decomposition (mutually exclusive and exhaustive):

```
mut_j(S_i) = equiv_{i,k,j} ⊔ killed_{i,k,j} ⊔ survive_{i,k,j}
SMS_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)  ∈ [0, 1]
```

The complete notation table is in Appendix A.1; index sets and tolerance parameters (`ε_eq`, `ε_AVP^k`, `K_eq = 1000`, `N = 20`) follow that table.

### 2.2 Operator signatures

Operator family and alignment:

```
MUT = {mut_C, mut_M, mut_G, mut_T, mut_F}     (open, extensible)
mut_j : Programs → 2^Programs
align(j) = j      (design choice, not theorem)
```

| Operator | Failure semantics | Aligned MP |
|---|---|---|
| mut_C | Conservation-breaking | MP_1 Conservation |
| mut_M | Monotonicity-breaking | MP_2 Monotonicity |
| mut_G | Convergence-breaking | MP_3 Convergence |
| mut_T | Trajectory-distorting | MP_4 Trajectory |
| mut_F | Fidelity-order-breaking | MP_5 Partial-order |

Per-PUT specialisation tables (mut_C/M/G/T/F across 12 PUTs and 4 classes) are deferred to **Appendix B.2**.

### 2.3 Equivalence judgement E1 ∧ E2 (Layer 2)

The equivalence judgement is the executable instantiation of the Layer-1 necessary conditions (§3.2.0). For each candidate mutant `s'`:

- **E1 (AVP-coherent):** ∀ mr ∈ MR_{i,k}: AVP(S_i, mr) = AVP(s', mr).
- **E2 (Output-equivalent):** ∀ x in K_eq=1000 samples ~ D_S: ‖S_i(x) − s'(x)‖ ≤ ε_eq.

E1 ∧ E2 is the conservative complete instantiation: false-equiv requires *both* AVP coherence and numerical agreement on K_eq samples to fail simultaneously, which is rare; false-non-equiv requires only one of E1, E2 to fail, biasing SMS slightly high. The trade-off table against E1-alone and E2-alone is in Appendix A.3. Under the §2.6 degenerate limit `L`, E1 ∧ E2 reduces almost everywhere to classical bitwise equivalence (Lemma 9.1).

The killed determination preserves the classical OR-aggregation:

```
killed(s', MR_{i,k}) ⇔ ∃ mr ∈ MR_{i,k}: AVP(S_i, mr) = pass ∧ AVP(s', mr) = fail
```

### 2.4 LRCA engineering attribution layer (descriptive, not in SMS)

LRCA annotates every killed mutant with one of five likely root causes: C1 true semantic failure, C2 numerical-tolerance perturbation, C3 out-of-distribution (OOD) trip, C4 statistical-assumption violation, and C5 mutator artefact. The classifier is a three-layer decision tree. Layer 1 checks tolerance robustness over N = 20 repeats with a fail-ratio cutoff of 0.80. Layer 2 triages OOD on the surrogate and machine-learning classes. Layer 3 checks statistical-assumption baselines on the probabilistic and machine-learning classes using Wilcoxon and Dynamic Time Warping. A final pass rechecks for mutator artefacts. Multiple labels are resolved by priority C5 > C4 > C3 > C2 > C1.

The output quantities are `C1_share` (share of C1 among killed mutants) and `suspect_share := 1 − C1_share`. **LRCA does not modify the SMS formula**: the killed set is never filtered by suspect status. LRCA is a descriptive overlay that tells the reader whether a given kill is likely a true semantic-failure detection or an artefact. Appendix A.2 gives the full decision tree, the 9-grid threshold calibration, and the engineering rationale for the priority ordering.

### 2.5 Backward-compatibility declaration

The seven core concepts (PUT, mutation operator, mutant, equivalent mutant, killed mutant, surviving mutant, mutation score) and the SMS formula `|killed| / (|mut| − |equiv|)` are aligned item-for-item with Jia and Harman (2011). We extend only the internal definitions: `mut` shifts from syntactic to domain-semantic operators, `equiv` shifts from bitwise behavioural equivalence to the semantic-class equivalence E1 ∧ E2, and `killed` shifts from an equality oracle to a meta-pattern AVP. We introduce no new formula terms and no new state classifications.

Under the degenerate limit `L` defined in §2.6, SMS reduces almost everywhere to classical syntactic MS, equivalent mutants degenerate to classical behavioural equivalence, killed mutants degenerate to bitwise difference detection, and the LRCA layer trivialises — C2 through C5 cannot fire when L1 ∧ L2 ∧ L3 hold. Any SMS-based empirical conclusion is therefore structurally consistent with the existing mutation-testing literature in the classical syntactic-mutation regime, so there is no metric-level semantic fragmentation. The skeleton of eleven concepts, the three-state decomposition, the SMS formula, and the AVP interface are fixed; the contents of MUT, MP, C, and `cls` remain open to future extension.

### 2.6 SMS → MS degeneration: formal statement

The §2.5 backward-compatibility claim is formalised as a degeneration theorem. The full notation cross-reference is **Appendix G.1**; the joint conditions and lemma proofs are in **Appendix G.2-G.4**. We state only the main theorem and corollary here. Theorem and lemma labels (Theorem 9.1, Corollary 9.1, Lemma 9.1-9.3) are preserved as stable identifiers for cross-reference with Appendix G.

**Definition (Degenerate limit).** `L = L_equiv ∧ L_killed ∧ L_mut`, where each joint condition is a pair of paired axes acting on one layer of the SMS formula:

- `L_equiv = L1 ∧ L2`: ε_eq → 0 ∧ K_eq → ∞ (controls equiv layer; Lemma 9.1).
- `L_killed = L3 ∧ L4`: ε_AVP → 0 ∧ MP set = {MP_eq} (controls killed layer; Lemma 9.2).
- `L_mut = L5 ∧ L6`: mut_j switches to rule-based syntactic operators (Mothra-style) ∧ PUT class ⊆ imperative deterministic programs (controls mut layer; Lemma 9.3).

**Theorem 9.1 (SMS → MS degeneration).** In the degenerate limit `L`, **almost everywhere** with respect to the input distribution `D_S`,

```
SMS_{i,k,j}  -L→  MS_{i,j} = |killed_{i,j}^classic| / (|mut_j^syntax(S_i)| - |equiv_{i,j}^classic|)
```

where the right-hand side is the classical Mutation Score of Jia & Harman (2011), `killed^classic` is the difference-detection set, `equiv^classic` is the behavioural-equivalence set, and `mut^syntax` is the syntactic-mutant set.

**Proof sketch.** By Lemma 9.1, equiv_{i,k,j} → equiv_{i,j}^classic almost everywhere with respect to D_S; the measure-zero qualifier accommodates floating-point pathological points and Not-a-Number propagation. By Lemma 9.2, killed_{i,k,j} → killed_{i,j}^classic, and the MP index k degenerates because L4 collapses MR_{i,k} to {MP_eq}. By Lemma 9.3, mut_j(S_i) → mut_j^syntax(S_i). Substituting into the SMS formula yields MS_{i,j}. Full lemma proofs are in Appendix G.3 and the full theorem proof in Appendix G.4.

**Corollary 9.1 (LRCA trivialisation).** Under `L`, the likely-root-cause inventory C = {C1, ..., C5} degenerates to {C1}, so suspect_share → 0 and SMS becomes a single-layer metric consistent with the engineering attribution structure of Jia & Harman (2011).

**Empirical consistency.** Theorem 9.1 + Corollary 9.1 jointly guarantee that any SMS-based empirical conclusion (§5 Cliff's delta, Friedman chi^2, Spearman rho) is structurally consistent with existing mutation-testing literature in the classical syntactic-mutation regime, and **does not** constitute metric-level semantic fragmentation.

---

## 3. Experimental Subjects and Operator Framework

### 3.1 PUT selection (12 PUTs, 4 classes)

| Class | PUT | Name | Mathematical structure | LOC |
|---|---|---|---|---|
| **A Numeric** | A1 | Lorenz ODE integration | Nonlinear ODE | ~150 |
| | A2 | LU decomposition | Linear algebra | ~80 |
| | A3 | FDM 1D heat conduction | Parabolic PDE | ~200 |
| **B Probabilistic** | B1 | Beta-Binomial conjugate | Analytic posterior | ~60 |
| | B2 | MCMC Metropolis-Hastings | Markov chain | ~250 |
| | B3 | Monte Carlo integration | Importance sampling | ~100 |
| **C Surrogate** | C1 | Gaussian Process Regression | Kernel methods | ~300 |
| | C2 | Polynomial Chaos Expansion | Orthogonal basis | ~250 |
| | C3 | Neural-net surrogate | MLP substitution | ~400 |
| **D ML** | D1 | Multi-Layer Perceptron | Backpropagation | ~350 |
| | D2 | Support Vector Machine | Convex optimisation | ~200 |
| | D3 | Logistic Regression | Maximum likelihood | ~120 |

The 12 PUTs are inherited from P1 (Meng Li et al., under review) but independently justified along four dimensions: library-stack coverage (numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0); mathematical-structure coverage (8 of 12 chapters of *Numerical Recipes*); overlap with existing mutation-testing benchmarks (DeepCrime, Defects4J, and the mutmut and cosmic-ray demos); and signature-simplification trade-offs. The full coverage argument is in Appendix B.1. The `program(x: float) → float` signature is a substantive constraint (§7) that bounds the upper limit of mutant semantic complexity; transfer to industrial multi-output PUTs is reserved for the P3 and P5 papers.

### 3.2 Necessary conditions for semantic mutation (Layer 1)

**Definition (Semantic mutation criteria).** A mutant `s' = mut_j(S_i)` is a *semantic* mutation if and only if it satisfies at least one of the following three conditions.

(a) **Cross-function-boundary replacement.** The AST node operated on crosses at least one function-call or module-import boundary. For example, `np.linalg.det(M) → np.sum(np.diag(M))`.

(b) **Carries domain knowledge.** The legality of the mutation depends on mathematical, physical, or statistical knowledge of the program's domain, not on purely syntactic type preservation. For example, changing the Gaussian Process Regression `noise_level` from 1e-4 to 1e-1.

(c) **Changes algorithmic class.** The mutation alters the algorithmic class implemented. For example, replacing RK4 with Euler changes the integration order.

A mutation that satisfies none of (a) – (c) is purely *syntactic*: AST-local, domain-agnostic, and class-preserving. The five meta-operator classes (CE, OS, HP, TF, SI) are specialisations of (a) – (c):

| Operator class | (a) | (b) | (c) | Primary condition |
|---|---|---|---|---|
| **CE** Constant perturbation | ✗ | △ | ✗ | partial (b); weakest |
| **OS** API replacement | ✓ | ✓ | △ | (a)+(b) |
| **HP** Hyperparameter | ✗ | ✓ | △ | (b)+partial(c) |
| **TF** Numerical transform | △ | ✓ | ✓ | (b)+(c) |
| **SI / CF** Structural injection | △ | ✓ | ✓ | (b)+(c) |

Only **CE partially satisfies** the necessary conditions (it is a semantic / syntactic boundary class); OS, HP, TF, SI strongly satisfy at least one of (a), (b), (c).

### 3.3 60-cell instantiation matrix

```
              MP_1   MP_2   MP_3    MP_4    MP_5
              cons.  mono.  conv.   traj.   p-ord.
   A1 Lorenz   ●●     ●     ●●     ●●      ○
   A2 LU       ●●     ○     ●      ●       ●●
   A3 FDM      ●●     ●     ●●     ●●      ○
   B1 BetaBin  ●●     ●     ○      ○       ●
   B2 MCMC     ●      ●●    ●●     ●●      ●
   B3 MC       ●●     ○     ●●     ●       ○
   C1 GPR      ●      ●●    ●●     ●       ●●
   C2 PCE      ●●     ●     ●●     ●       ●●
   C3 NN-Surr  ●      ●●    ●●     ●●      ●●
   D1 MLP      ●●     ●●    ●      ●       ●●
   D2 SVM      ●      ●●    ●      ○       ●●
   D3 LR       ●●     ●●    ●      ○       ●●
   ●● substantial 30 / ● moderate 24 / ○ vacant 6 (P1 H6)
```

Each PUT averages 24.3 mutants in the v4 cross-source pool (range 10-30); full 60-cell × N=20 = 292 mutant instantiations × 20 AVP repetitions, with K_eq = 1000 input samples for E2 evaluation. Detailed pool counts and per-class operator specialisations are in **Appendix B.2**.

The cell density notation distinguishes ●● substantial (30 cells; aligned slice + strong off-diagonal cells where MR coverage is dense and mutant detection is expected), ● moderate (24 cells; cross slice with non-trivial expected detection rate), and ○ vacant (6 cells; inherited from P1 H6 — historically empty cells where no MR is exercised). The 12 aligned (j = k) cells are precisely the on-diagonal cells; the 48 cross (j ≠ k) cells partition into the 24 ● moderate + 18 ●● off-diagonal substantive + 6 ○ vacant cells. The ● moderate / ●● substantive distinction does not change SMS computation; it tracks expected MR coverage density per P1 documentation and informs the §6.2 R_sem / R_kill decoupling discussion.

**Per-class operator specialisations (illustrative).** Each meta-operator (mut_C / M / G / T / F = CE / OS / HP / TF / SI in their dual form) requires PUT-class-specific specialisation:

- **mut_C Conservation-breaking:** A1 Lorenz adds ε_drift to RHS (slow Hamiltonian drift); A2 LU decomposition omits the (k+1)-th row multiplier; B1 Beta-Bin posterior omits normalisation; C1 GPR covariance omits positive-definite diagonal term; D1 MLP backprop omits one gradient term.
- **mut_M Monotonicity-breaking:** A3 FDM Δt occasionally negative; B2 MCMC acceptance min(1, r) → min(0.95, r); C2 PCE high-order coefficient sort inserts inversion; D2 SVM decision-function sign flips near boundary.
- **mut_G Convergence-breaking:** A1 Lorenz RK4 → 1.5-order hybrid; A3 FDM 2nd-order difference → 1st-order; B3 MC doubling sample size does not 1/N-reduce variance; C3 NN-Surr training-epoch truncation.
- **mut_T Trajectory-distorting:** A1 Lorenz state-vector y / z swap; B2 MCMC inserts independent-sampling segment; C3 NN-Surr training-target slow phase shift; D1 MLP hidden-layer periodic-mask activation.
- **mut_F Fidelity-order-breaking:** A2 LU partial pivoting degrades to no pivoting; C1 GPR length-scale switches to coarse prior; C2 PCE high-order term randomly retains low-order; D3 LR regularisation occasionally large.

The per-class HP / OS / TF substitution rules give similarly differentiated specialisations across PUT classes (e.g., HP on class a = tolerance / max_iter, on class c = GPR `noise_level` / `length_scale`, on class d = MLP `hidden_dim` / dropout; OS on class a = numerical-linalg API swap `det` ↔ `sum(diag)`, on class b = sampling-API swap, on class c = surrogate-class swap GPR ↔ RBF ↔ NN). The full PUT-class × operator specialisation grid is in Appendix B.2.

### 3.4 Engineering significance — c-class primary MP caveat

The diagonal cells `j = k` form the H2-aligned slice, the off-diagonal cells form the cross slice, and the vacant cells `○` are not formally adjudicated. One methodological honesty point belongs in the main body and cannot be deferred to the appendix.

**Pre-registered v3 (primary).** The c-class primary MP follows the P1 specification (MP5). All H1, H2, H4, and H5 verdicts in this paper are rendered on v3.

**Exploratory v3b (post-hoc).** After observing the v3 data, the per-class Friedman test in §5.5 shows χ² = 4.00 and p = 0.406 for the c-class — no significant MP differentiation. On this non-significance basis we shift the c-class primary to the argmax-mean-SMS choice, which is MP1 (data: `c_class_mp_ranking.json`). This is **selection on the response**: it inflates the H4 sign test from 3/4 to 4/4 and Cliff's δ from 0.323 to 0.446 without applying a max-statistic correction. A permutation null over fully exchangeable c-class (PUT, MP) cell SMS values (10,000 permutations) gives one-sided p = 0.9885 and a Bonferroni-bounded effective α of 0.01 (`c_class_permutation_v4.json`). All v3b and v4 results are reported as exploratory; the H4 and H2 primary verdicts rest on v3. P4 will pre-register the c-class primary-MP rule on a fresh dataset.

**Symbol convention.** Throughout the paper, a dagger (†) on a numeric quantity (δ, SMS percentage, sign-test count) flags that the number is derived under the v3b post-hoc c-class primary-MP shift (MP5 → MP1) and inherits the permutation-null one-sided p = 0.9885 caveat above. Numbers without † stand on the v3 pre-registered configuration.

**Naming convention.** For brevity, we write `v4-mp1` for the v4 cross-source pool with the v3b post-hoc c-class primary MP1 (Round-3 default; the version reaching δ = 0.439†) and `v4-mp5` for the v4 cross-source pool holding the c-class primary at the pre-registered MP5 (Round-3 robustness contrast; the version reaching δ = 0.314). Both share the same v4 mutant pool; only the c-class primary-MP convention differs.

### 3.5 P2 vs syntactic mutants — 12-PUT empirical (Layer 3)

**Experimental design.** For each PUT, P2 v4 cross-source mutants (`data/mutants/${PUT}_pool_v4/`, 292 total) are compared at the AST-normalised level (`ast.dump(annotate_fields=False, include_attributes=False)`) with cosmic-ray default-operator mutants (1,250 total; `scripts/p2_vs_syntactic_ast_diff_batch.py`). Source: `data/results/cosmic_ray_12put_ast_diff.json`.

**Aggregate results.**

| Metric | Value |
|---|---|
| Total P2 mutants (12 PUTs) | 292 |
| Total cosmic-ray syntactic mutants (12 PUTs) | 1,250 |
| AST-normalised overlap | 15 |
| **Overall overlap rate** | **5.14%** |

**Per-operator-class breakdown (12-PUT aggregate).**

| Class | n_p2 | n_overlap | Rate | Interpretation |
|---|---|---|---|---|
| **HP** | 72 | 0 | **0.000** | Structurally unreachable |
| **SI** | 33 | 0 | **0.000** | Structurally unreachable |
| **TF** | 54 | 0 | **0.000** | Structurally unreachable |
| CE | 64 | 5 | 0.078 | Boundary class (§3.2 partial (b)) |
| OS | 60 | 7 | 0.117 | Partial incidental hits |
| CF | 9 | 3 | 0.333 | b2 only, n=9 |

**Interpretation: refuting the "post-classification copy" challenge.**

- HP, SI, and TF (159 of 292 = 54.5% of v4 mutants) are **categorically** unrepresentable by cosmic-ray AST-local operators such as BinOp, Compare, and NumberReplacer. The unreachability is structural; enlarging the syntactic operator set does not help.
- The CE class shows 7.81% incidental overlap, mostly LLM-generated half-step perturbations on a2 and b3 such as `_RHO=28.0 → 27.5`. The remaining 92.19% of CE mutants are AST-disjoint, because the LLMs prefer domain-aware perturbations over integer ±1 changes.
- An earlier draft labelled the OS row "✗ tool-inexpressible". The 12-PUT data refines this categorical claim to "△ 88.33% disjoint, 11.67% incidental hits". The systematic-versus-incidental argument in §3.6 (with details in Appendix B.1.5) clarifies why those incidental hits are stochastic byproducts rather than systematic semantic mutation.
- 94.86% of the v4 mutants cannot be reproduced by cosmic-ray defaults. The two pools occupy systematically distinct mutant spaces.

A multi-tool cross-comparison is reserved for P4: mutpy is incompatible with Python 3.10+, and mutmut's operator set overlaps strongly with cosmic-ray's. The DeepSeek, Claude, and GPT contributions to the 15 overlap files are uneven (DeepSeek 11, Claude 4, GPT 0). Appendix B.3 covers the cosmic-ray a1 single-PUT pre-12-PUT pilot, and Appendix F discusses the LLM-source distributional-shift threat R8.

### 3.6 Preventive-defence framing

**Scope of the claim.** The preventive-defence claim below is conditional on a first-order syntactic baseline; HOM-based syntactic compositions are an open question (R12) and are not refuted by the §3.5 evidence.

The HP, SI, and TF zero-overlap result, combined with the §3.2 necessary-conditions argument, amounts to a *preventive-defence* argument: semantic mutation operators address a class of fault hypotheses that lie categorically beyond the reach of first-order syntactic tools. Three points sharpen this framing.

**(i) Systematic versus incidental.** Satisfying conditions (a), (b), or (c) is sufficient for a single semantic mutation, but only when satisfaction reflects design intent — not stochastic byproduct — does it constitute a *systematic* semantic mutation method. A syntactic tool that occasionally hits (a) or (c) with its 12 default operators does so at a non-zero probability, but the hits are not repeatable and they carry neither of the two engineering goods we want. First, designing a semantic mutator like OS `det → sum(diag)` requires knowing that these expressions are equivalent on diagonal matrices but not on general matrices — a deepening of source-code understanding the syntactic tool does not exhibit. Second, domain-semantic faults — wrong physical constants, unit conversions, boundary conditions, hyperparameter semantics, numerical-method order — are not AST-local; the syntactic-tool design goals (operator typos, off-by-one errors, negation flips) do not target them. Systematic semantic mutation therefore requires (a), (b), or (c) to be design intent. Appendix B.1.5 records this argument in full.

**(ii) HOM caveat.** HOM (Jia and Harman 2009; Kintis et al. 2018) could in principle compose syntactic mutants — for example, an Arithmetic Operator Replacement combined with a Statement Deletion — to partially simulate the effects of OS or HP on some PUTs. The §5 empirics did not run a HOM comparison; we list HOM equivalence testing as residual threat R12 (Appendix F.2) and confine our "tool unreachability" claim to *first-order* syntactic tools (mutmut and cosmic-ray default configurations). A multi-syntactic-tool cross-comparison (mutmut and mutpy) is reserved for P4: mutpy is incompatible with Python 3.10+, and mutmut's operator set strongly overlaps cosmic-ray's.

**(iii) Source distributional shift.** The 15 cosmic-ray AST overlaps are not evenly distributed across the three LLMs (DeepSeek 11/15, Claude 4/15, GPT 0/15; see `cosmic_ray_12put_ast_diff.json`). DeepSeek tends to generate syntactically simpler mutations. This LLM-source bias is discussed as R8 (Appendix F.2) but does **not** affect the systematic-vs-incidental argument, which is based on *categorical* AST-locality, not hit frequency: the HP / SI / TF zero-overlap result is 0/0/0 across all three sources.

---

## 4. Experimental Procedure

### 4.1 Procedure overview

```
[§3.1 PUTs] → [§4.2 Mutant generation] → [LRCA L0 prescreen]
            → [§4.4 Equivalence (E1 ∧ E2)] → [AVP → killed/survive]
            → [LRCA three-layer diagnosis] → [SMS + C1_share report]
```

Each (i, k, j) cell is reported with `inst_count`, `equiv_count`, `killed_count`, `survive_count`, SMS_{i,k,j}, C1_share_{i,k,j}, suspect_share_{i,k,j}, and the three rates `inst_rate / equiv_rate / survive_rate` corresponding to RQ1.

### 4.2 Cross-source v4 protocol (summary)

To isolate the contributions of LLM same-source bias and MR-MP alignment design to Cliff's delta, we ran a three-stage ablation:

| Version | Mutant pool | c-class primary MP | Use |
|---|---|---|---|
| **v3** | Same-source (Claude Opus 4.6) | MP5 (P1 legacy) | H2 baseline (pre-registered primary) |
| **v3b** | Same-source | MP1 (data-driven, §3.4) | Isolate MR-MP design contribution |
| **v4** | **Cross-source** (Claude Opus 4.6 + GPT-5.4 + DeepSeek chat) | MP1 | Isolate LLM-source diversity |

The v4 protocol (`scripts/cross_source_campaign.py`) runs each (PUT, operator) pair on Claude / GPT / DeepSeek with K=3 trials under an identical prompt template (temperature 0.7, V1-V4 mechanical-validation gate). Cross-source pool capacity: 37 operators × 3 sources × 3 trials = 333 attempts, 89% V1-V4 pass, 298 confirmed mutants distributed nearly equally (Claude 101, GPT 98, DeepSeek 99).

**Two declared confounds.**

1. **Protocol asymmetry (R13):** v3 / v3b used the original Phase-1 dual-blind reviewer protocol (Claude generation + GPT-5.4 review + DeepSeek arbitration); v4 passes V1-V4 mechanical gates only and does **not** invoke a reviewer LLM. A fraction of `Delta_delta(v3b → v4) = -0.007` may reflect a slight v4 quality shift rather than LLM-source diversity. P4 will rerun dual-blind on the v4 grid.

2. **Chained-conditioning (R11):** v4 inherits the v3b post-hoc selection on c-class primary MP. `Delta_delta(v3b → v4)` is therefore conditional on v3b selection + identical prompt template; the strong-sense LLM-diversity test (v4-pre × c→MP5 + per-LLM differential prompt) is deferred to P4 (full protocol in Appendix C.1.1).

The two contrasts are **reported separately** rather than combined as a synthetic ratio; full per-LLM token / latency / cost figures, V1-V4 specifications, and the full v4-pre / differential-prompt protocol are in **Appendix C.1**.

### 4.3 Mutant-pool prescreen and equivalence detection

**Pool prescreen (LRCA L0).** Each candidate mutant passes three gates: (i) static lint and type checking; (ii) a unit self-test on simple inputs to confirm that the PUT loads, runs, and returns a finite output; and (iii) a double-blind review sign-off under the Phase-1 protocol. In Phase-1, the generator LLM is Claude Opus and the reviewer LLM is GPT-4o; the two roles are isolated, and the reviewer sees only the PUT and the mutant code and outputs a (syntactic, executable, fault-injected) triple. Inconsistent reviewer outputs go to a manual arbitration queue (no more than 10% of cases); double-confirmed mutants enter the pool. We then randomly sample 20% of the pool for manual review by scientific-computing researchers, and downgrade the entire batch to manual review if manual–reviewer inconsistency exceeds 10%. Each cell yields 30–50 candidates and retains 10–15 mutants. The v4 cross-source pool does **not** invoke the reviewer LLM, for cost and speed reasons; a fraction of Δδ(v3b → v4) = −0.007 may therefore reflect a quality decline rather than a source-diversity contribution. We declare this protocol asymmetry as threat R13 (§6.1; full justification in Appendices C.2 and C.3).

**Equivalence detection (E1 ∧ E2).** For each mutant `s'` in mut_j(S_i):

1. **E2 step.** Sample K_eq = 1000 inputs `x ~ D_S`; compute `‖S_i(x) − s'(x)‖`; if ≤ ε_eq for all samples, mark E2-pass.
2. **E1 step.** For every `mr ∈ MR_{i,k}`, compare `AVP(S_i, mr)` with `AVP(s', mr)`; if all consistent, mark E1-pass.
3. **Conjunction.** E1 ∧ E2 → enter `equiv_{i,k,j}`, exclude from SMS denominator. Otherwise pass to AVP-killed determination.

E2 is run before E1 because E2 is computationally cheaper (K_eq scalar evaluations) and quickly discards numerically distinct mutants; the remaining candidates are screened by AVP for MR-relation equivalence. The joint condition is conservative: false-non-equivalent (E1 ∨ E2 fail) is much easier than false-equivalent (both must mis-pass simultaneously), biasing SMS slightly *high* — an explicit conservative engineering choice (Appendix A.3).

**Killed determination.** With OR-aggregation across mr in MR_{i,k}:

```
killed(s', MR_{i,k}) ⇔ ∃ mr ∈ MR_{i,k}: AVP(S_i, mr) = pass ∧ AVP(s', mr) = fail
```

Each (i, k, j) cell is sampled N = 20 times (statistical replicate) to compute the per-cell SMS, with mutant-level fail ratios feeding the LRCA L1 decision. AVP version is pinned to the P1 commit hash (`<P1-AVP-vX.Y>`); the P2 reproducibility package embeds the complete AVP source so that P2 remains self-consistent under any P1 evolution.

### 4.4 LRCA three-layer diagnosis

For each killed mutant the three-layer decision tree applies in order:

- **L1 tolerance robustness** (all classes). N=20 replicates with a fail-ratio cutoff at 0.80 — a kill that survives less than 80% of the 20 replicates is labelled C2 (numerical-tolerance perturbation) and exits.
- **L2 OOD triage** (C / D classes only). Sample from `D_S^valid`; if the mutant fails *only* in the OOD region, label C3 (out-of-distribution) and exit.
- **L3 statistical-assumption baseline** (B / D + Wilcoxon / DTW only). Pre-check IID / stationarity on the PUT's own repeated samples; if the AVP statistical assumption is itself violated, label C4 and exit.
- **Artefact recheck**. An external reviewer re-examines mutant code + prompt history; if LLM / artefact evidence (e.g., mutator over-injection) is found, label C5; otherwise label C1.

Multi-label priority C5 > C4 > C3 > C2 > C1 takes the earliest confirmed non-semantic cause (decision-tree control flow). Threshold calibration over a 9-grid (`ood_band ∈ {0.02, 0.05, 0.10}` × `tolerance_multiplier ∈ {3.0, 10.0, 30.0}`, repeats fixed at 20) lifts H5 from 10/60 to 12/60 cells; the best combination (`ood_band = 0.02, tolerance_multiplier = 3.0`) is reported as primary, with default-threshold results retained as control (`lrca_60cell_v3.json`). The calibration ceiling (12/60 = 20%) remains far below the 80% pre-registered threshold — H5 is unattainable on this dataset as an intrinsic property of LLM-mutant pools, not a calibration issue. Detailed grid table, L0-L3 sub-protocols, and decision-tree pseudocode are in **Appendix A.2 + C.4**.

---

## 5. Statistical Analysis and Empirical Results

### 5.1 Statistical pipeline

The primary statistical reporting follows a pre-registered hierarchy:

| RQ | Primary statistics | Reporting format |
|---|---|---|
| RQ1 | inst_rate, equiv_rate, C1_share, survive_rate | 60-cell heatmap + 4-class marginals |
| RQ2 | aligned-SMS vs cross-SMS; sparse ○ vs dense ●● equiv_rate | Cliff's delta + odds ratio + 95% bootstrap CI |
| RQ3 | ΔSMS_c (c ∈ {A,B,C,D}); CV(ΔSMS) | sign test (df = 3) + descriptive forest plot |
| RQ4 | Spearman ρ + Kendall τ (SMS vs PC) | scatter + dual-metric ranking comparison |

Cell-level multiple comparisons across the 60 cells use Benjamini-Hochberg FDR control at `alpha_FDR = 0.05`. Bootstrap 95% CIs use 1,000 iterations as default (B = 10,000 for the headline H2 delta CI per R-12 response). Mixed-effects modelling (`sms ~ C(class) * C(operator) + (1 | put)`) failed with Singular matrix at N = 60 (insufficient column rank for the class × operator interaction; 11-d fixed-effects + 12 PUT random intercepts exceed the 60-observation budget). The Friedman test is the non-parametric formal alternative. The five hypotheses are pre-registered: H1 (operator implementability) requires ≥ 4 of 5 operators producing ≥ 5 non-equivalent mutants on ≥ 9/12 PUTs; H2 (aligned-vs-cross) requires odds ratio ≥ 3.0 *and* Cliff's delta ≥ 0.474 (Romano 2006 large-effect threshold); H4 (cross-class consistency) requires sign-test 4/4 across 4 classes plus CV(ΔSMS) < 0.5; H5 (LRCA mass) requires mean suspect_share ≤ 0.20. H3 was formally retired before v3 data collection (its bidirectional threshold structure collapsed on LLM-mutant data because too few cells trigger non-zero equivalent mutants). Numbering H1, H2, H4, H5 is preserved with H3 vacant. SMS variants (SMS, SMS_unfiltered) and construction lemmas are in **Appendix D.1**.

### 5.2 RQ1 — 60-cell distribution

| Metric | Value |
|---|---|
| Number of cells | 60 |
| Mean SMS | 0.104 |
| Median SMS | 0.000 |
| Std SMS | 0.213 |
| Cells with SMS = 0 | 45 / 60 |
| Mean mutants / cell (v4) | 24.3 (range 10-30) |

The **zero-mass dominance** (45/60 = 75%) is concentrated in the cross-MP slice: ~88% (42/48) of cross cells are zero, ~25% (3/12) of aligned cells are zero. Cliff's delta is well-defined under this distribution but its inference is effectively dominated by `n_aligned = 12 + n_cross_nonzero ≈ 6 = 18`, not the surface n=60. Median odds ratio is formally infinite (median(cross) = 0); we report "aligned median > 0 = cross median" as auxiliary qualitative evidence.

**Effective-n note.** The surface n_aligned = 12 and n_cross = 48 mask an effective-n constraint at n_eff ≈ 18, which explains the wide 95% bootstrap CI [0.127, 0.740] (upper/lower ratio ≈ 5.83, consistent with known liberal tendency of percentile bootstrap at small n_eff). The implications for power and the H2 verdict direction are quantified jointly with the stipulated-alternative analysis in §5.4. PUT-class diversification at n ≥ 30 (P4) is a testable route to relaxing the effective-n constraint. Power and effect-size disambiguation are treated jointly with the stipulated-alternative analysis in §5.4 (avoiding repetition).

**Consistency with LLM-mutant literature.** Tip et al. (2024) LLMorpheus reports high cross-MP failure proportions on JavaScript scientific-computing PUTs (specific numbers not listed in cited literature); zero-mass dominance appears to be a shared characteristic of LLM-mutant + existing MR-MP alignment designs, not a quirk of this paper's PUT selection.

### 5.3 RQ2 — Aligned vs cross (Cliff's delta)

| Slice | n | Mean SMS | Median SMS |
|---|---|---|---|
| aligned (j = k, v4 + v3b primary) | 12 | 0.275 | 0.267 |
| cross (j ≠ k) | 48 | 0.061 | 0.000 |

Four delta point-estimates (three planned ablation stages plus one robustness contrast):

- **v3 (primary, pre-registered):** delta = **0.323**, 95% CI [0.017, 0.622]
- v3b (exploratory, c→MP1 post-hoc): delta = 0.446†, CI [0.154, 0.743]
- v4 (exploratory, cross-source under fixed prompt, c→MP1): delta = 0.439†, 95% CI [0.127, 0.740] (B = 10,000)
- **v4 robustness (cross-source, c-class held at v3 MP5):** delta = **0.314**, 95% CI [0.014, 0.622]. This row strips R11 chained conditioning by reverting c-class primary to the pre-registered v3 choice while keeping the cross-source pool. The contrast `δ_v4_mp5 − δ_v3 = −0.009` isolates the LLM-source-diversity axis from MR-design re-selection.

**H2 verdict: not met under the pre-registered point-estimate criterion.** None of the three delta values crosses the Romano (2006) large-effect threshold 0.474. The two contrasts are reported separately:

| Contrast | Delta-delta | CI | Interpretation |
|---|---|---|---|
| v3 → v3b (c-class primary MP shift, same-source) | +0.123 | (data-driven; not applicable, see §3.4) | Single-class post-hoc; reflects primary-MP sensitivity, not generic MR-design contribution |
| v3b → v4 (cross-source, c→MP1, fixed prompt) | −0.007 | covers zero | Three LLMs near-identical under prompt-fixed (49.1% stipulated power) |
| **v3 → v4 (under MP5, cross-source only)** | **−0.009** | **covers zero** | Robustness against R11. Source-axis change under MP5 reproduces the v3b → v4 micro-shift, supporting the source-diversity null reading across two independent MP conditions. |

The "v3 → v4 (under MP5)" robustness contrast was added in response to a methodological-asymmetry concern: the −0.007 v3b → v4 contrast inherits R11 chained conditioning (cross-source pool + post-hoc MP1) and so cannot identify which factor is null. Under MP5, c-class is held at the pre-registered choice, so the only difference between this row and v3 (δ = 0.323) is the LLM-source axis. The reproduced ≤ 0.01 shift across two MP conditions supports finding (iii).

This is consistent with Tip et al. (2024) LLMorpheus's medium-effect range on JavaScript LLM mutants - a contextual literature observation (estimand caveat: their delta compares "LLM vs traditional mutants on fault detection", ours compares "aligned vs cross MP slice within one pool"; the numerical similarity is not substantive support).

### 5.4 RQ2 — Stipulated-alternative power

The §5.2 effective-n constraint motivates an explicit power analysis. A plug-in bootstrap (5,000 replications, seed = 42) samples with replacement from the observed (n = 12, n = 48) v4 SMS distributions. The plug-in power table is:

| Threshold | Interpretation | Power at (12, 48) |
|---|---|---|
| δ > 0.000 | Any effect | **0.997** |
| δ > 0.147 | Small | 0.966 |
| δ > 0.330 | Medium | 0.759 |
| **δ > 0.474** | **Large (H2)** | **0.423** |

The plug-in result answers the question "given the *observed* distribution, how often do we exceed the threshold?" A stipulated-alternative simulation answers a more pointed question: "if the *truth* equals the H2 boundary 0.474, how often does the (12, 48) design return δ̂ ≥ 0.474?" SMS distributions have heavy ties at zero (45 of 60 cells), so a raw shift is discontinuous: any ε > 0 jumps δ from 0.314 to 0.74. We therefore use a mixture, drawing the aligned sample with probability w from (observed_aligned + 0.001) and with probability 1 − w from observed_aligned, calibrating w = 0.094 to realise E[δ] = 0.4746.

| Stipulated truth | Criterion | Power |
|---|---|---|
| 0.474 | δ̂ ≥ 0.474 (point estimate) | **0.491** |
| 0.474 | Lower 95% CI bound > 0 (any effect) | 0.868 |

Even when the truth equals the H2 boundary, this design returns "not met" verdicts in roughly half of replications. This supports the framing in §5.3: the H2 verdict is a factual statement about the point estimate failing to clear the threshold, not a claim that the effect is necessarily smaller than 0.474. Increasing the sample size narrows the confidence interval but cannot lift the point estimate. The plug-in sample-size sweep (n_aligned ∈ {6, 12, ..., 60}; n_cross = 4 × n_aligned; power for δ > 0 reaches 0.974 at n_aligned = 6 and 0.996 at 12, then plateaus) is in Appendix D.3.

**Symmetric reading of the same power.** The 49.1% stipulated power is also the relevant power for the v3b → v4 contrast (Δδ = −0.007, CI covers zero): if the true source-diversity effect on δ were as large as 0.474, this design would correctly reject the null in roughly half of replications. The −0.007 null-shift is therefore consistent with a wide range of true source-diversity effects, and we explicitly do not read it as evidence that source diversity is inert. The strong-sense test is deferred to P4.

**Note on monotone-transformation invariance.** Cliff's δ is rank-based — a function of U / (n₁·n₂) — so applying a logit transform to SMS gives δ_logit ≡ δ_raw by construction (`rq2_cliffs_delta_logit_v4.json` records δ_logit = 0.439 = δ_raw, difference 0.000). This is consistent with the rank-invariance theorem and does **not** constitute additional robustness evidence. The genuine robustness threats to the H2 verdict come from the v3b post-hoc selection (§3.4) and the zero-mass dominance (§5.2), not from any metric-scale choice. See Appendix D.2 for the full sensitivity analysis.

### 5.5 RQ3 — Cross-class consistency and Friedman

| Class | Mean SMS (v3) | Mean SMS (v4) |
|---|---|---|
| a (numeric) | 0.067 | 0.067 |
| b (probabilistic) | 0.156 | 0.148 |
| c (surrogate) | 0.047 | **0.089 (+91.4%)** |
| d (ML) | 0.081 | 0.112 (+38%) |

Sign test (within-class aligned mean − cross mean, sign = +):

- **v3 (primary, pre-registered): 3 / 4 (partial)**.
- v3b (exploratory, c→MP1): 4 / 4†.
- v4 cross-source: 4 / 4† (under v3b condition).

**H4 primary verdict: partial (3/4) under v3.** v3b / v4 4/4† are sensitivity reports inheriting the §3.4 post-hoc selection.

The mixed-effects primary model `sms ~ C(class) * C(operator) + (1 | put)` returned Singular matrix; the fallback `sms ~ C(class) + C(operator) + (1 | put)` had PUT random-intercept variance hit boundary 0 (degenerate). We therefore use Friedman as the non-parametric formal alternative:

- **PUT (n=12) × MP (k=5): chi^2 = 15.30, p = 0.0041** (significant).
- MP rank means: 2.92, 2.58, 2.08, 3.08, 4.33.
- Per-class Friedman with **Bonferroni × 4 correction** (R1 W4 round-2): a 1.000 / b **0.116** / c 1.000 / d 1.000 — no per-class result remains significant after correction. Kendall's W effect sizes: a 0.333 (small) / b 0.898 (large concordance, but caveat: N=3 per class makes this label nominal only) / c 0.333 / d 0.417.

**Caveat.** Friedman tests "are MP rank differences present" (averaged over PUTs); H4 tests "is direction consistent across 4 classes". These are logically independent. H4 stands on the §5.5 sign test; per-class Friedman is descriptive only (small N=3 per class).

### 5.6 RQ4 — SMS vs Pattern Coverage

**Status.** RQ4 is reported as a descriptive observation, not a hypothesis test, because n = 12 places the 95% Spearman CI at roughly [−0.5, +0.6], so the test cannot distinguish zero, moderate-positive, or moderate-negative correlation. The numbers below are recorded so that P4 (n ≥ 30 PUTs) can pre-register a directional hypothesis.

Pattern Coverage (PC) per PUT = #triggered (MP_k, R_outcome) cells / 10. Range [0.500, 1.000], mean 0.733. Pairing with mean SMS over 5 MPs: Spearman rho = **0.163** (p = 0.613); Kendall tau = 0.136 (p = 0.568); n = 12.

**Statistical-power caveat first.** At n = 12, Spearman's 95% CI is approximately [-0.5, +0.6]; the test cannot distinguish "zero correlation" from "moderate positive correlation" or "moderate negative correlation". p = 0.61 / 0.57 does **not** support the strong claim that "SMS is independent of PC" or the strong claim that "SMS is strongly correlated with PC". The conservative finding is *no detectable correlation at n = 12*; orthogonality is a hypothesis for P4 (n ≥ 30 PUTs or refined PC operationalisation; full PC operationalisation in Appendix D.5).

### 5.7 H5 — LRCA mass

| Metric | Value |
|---|---|
| Mean C1_share (default threshold) | 0.164 |
| Mean C1_share (calibrated best, ood_band = 0.02) | **0.209** |
| Mean suspect_share (calibrated best) | 0.791 |
| Cells meeting H5 (calibrated best) | **12 / 60 = 20.0%** |

**H5 was pre-registered before pool characteristics were known**; the dense cutoff sweep below shows the verdict is intrinsic to LLM-mutant pools and not a calibration artefact, which is itself a finding worth reporting.

**H5 verdict: not met.** A dense cutoff sweep (R-14 response, Appendix D.2) shows H5 pass-ratio is flat at 20% over cutoffs ∈ [0.05, 0.40]; no cutoff pushes it past 80%. H5 is **intrinsic data property, independent of cutoff choice**; v4's suspect_share distribution is severely bimodal (median 1.0, with 48 cross cells near 1 and 12 aligned cells near 0; the [0.20, 0.80] interior is nearly empty).

---

## 6. Discussion

### 6.1 Cross-source contributes mutant quality, not effect size

Going from v3b same-source to v4 cross-source changes Cliff's δ by only −0.007 (95% CI covers zero); the v4-mp5 robustness contrast holding the c-class primary at the pre-registered MP5 reproduces this null shift (Δδ(v3 → v4-mp5) = −0.009, 95% CI covers zero), strengthening the source-axis null reading by replicating it under an independent MP condition that strips R11 chained conditioning. Cross-source pooling raises mean C1\_share from 0.164 to 0.209 (a 27%† relative increase), class-c mean SMS by **+91.4%†**, and class-d mean SMS by 38%†. Under an identical prompt template, three LLMs converge on near-identical distributions for the aligned-vs-cross question. This *inversely falsifies* our initial hypothesis that LLM same-source bias is the dominant factor in the H2 ceiling. The v3 → v3b shift of +0.123 attributes to MR design — specifically the c-class primary-MP shift, with the caveats in §3.4 — and the v3b → v4 micro-change attributes to source diversity under prompt-fixed conditions. We report these contrasts separately in §5.3 rather than as a synthetic ratio. The strong-sense source-diversity test, with per-LLM differential prompts (V_persona, V_cot), is deferred to P4. Appendix C.1.1 records the full protocol.

The §3.5 evidence (5.14% AST overlap, HP/SI/TF at 0/0/0) confirms that the medium-effect ceiling is not an artefact of LLM-pool overlap with the syntactic-mutant space. 94.86% of v4 mutants are AST-disjoint from cosmic-ray defaults, and the three categorically-unreachable classes (HP, SI, TF; 159 of 292 mutants) lie outside that space by construction. An effect-size breakthrough therefore requires substantive MR-design refinement (a P4 task), not a larger sample.

**A numerical-coincidence note.** Petrović and Ivanković's (2018) ~20% productive-mutant rate at Google is close to our calibrated C1\_share of 0.20. Their construct is a developer survey (subjective usefulness), and LRCA's C1 is the output of a three-layer classifier; the agreement between the two is contextual, not mechanism validation.

### 6.2 Decoupling between R_sem and R_kill

The operator-level pilot in Appendix C.4.1 reveals a sharp pattern: HP, TF, and OS operators on the c-class (surrogate) and d-class (machine learning) PUTs reach R_sem ≈ 1.0 (semantic feasibility — the LLM successfully produces a syntactically valid, executable, intent-bearing mutant) but R_kill = 0 under the PUT's primary MP (the AVP fails to detect the mutant under that MR). Concretely, six cells show R_sem ≥ 0.9 with R_kill = 0: c1\_CE1 (GPR `noise_level` 1e-4 → 1e-1), c2\_OS1 (polynomial → spline basis), c3\_HP1 (relu → tanh), c3\_TF1 (max_iter 1000 → 5), d1\_HP1 (MLP α 1e-4 → 1.0), and d3\_HP1 (LR C 1.0 → 1e-4). In each, the mutant *is* a valid hyperparameter-semantic injection, but the primary MP — MP5 asymptotic for the c-class and MP2 monotonicity for the d-class — is an asymptotic or statistical relation, and the parameter deviation it tolerates is wide enough to absorb the mutant.

The cell-level evidence in §5.2 reproduces this pattern: 75% of cells are zero, concentrated in the cross slices. Under v4 cross-source, mean C1\_share rises from 0.164 to 0.209 (+27%): among the few killed mutants, the cross-source pool reduces LRCA mislabelling. Source diversity therefore improves the *quality* of the kill set without expanding its *coverage*. **The engineering insight is that operator-MP alignment in MR design is necessary for strong SMS signals; merely enlarging the semantically feasible mutant pool dilutes the C1 proportion without lifting the kill rate.** Two questions follow for P4: can we use SMS to infer which MP class is missing for which PUT class, and can we calibrate LRCA so that the threshold separating true semantic faults from artefacts is class-specific?

This decoupling motivates the caveat in §3.4. The v3 → v3b shift of +0.123 attributes to MR design reselection (single-class, post-hoc), and the v3b → v4 micro-change of −0.007 attributes to source diversity under a fixed prompt. The two contrasts cannot be merged into a single factor-decomposition ratio; each carries independent caveats and lives on a different axis of the methodology space.

### 6.3 H4 — partial under primary, exploratory 4/4

All four class means are positive in v3, v3b, v4. Inter-class balance improves under cross-source (c +91.4%†, d +38%†), confirming that c / d classes have higher mutant-diversity demand than a / b. Mixed-effects unavailability (Singular) is a sample-size constraint at N = 60 / 12 PUTs, not evidence absence. **H4 primary: partial (3/4).** v3b / v4 4/4† are sensitivity-only with §3.4 caveats. The Friedman main effect (chi^2 = 15.30, p = 0.0041) speaks to MP differentiation, not H4 direction.

### 6.4 Stakeholder analysis (single-output kernels scope)

**Scope.** All deployment claims in this subsection are bounded to single-output `float → float` kernels under 2 KB — the 12 PUTs of this paper. They do not apply to industrial-scale, multi-module, or multi-output scientific computing software, which lies in the P5 / P2-CN scope.

**Test engineers** can read SMS as a per-MR scalar adequacy score. When SMS sits well below the aligned baseline of about 0.275 (§5.3), the LRCA labels — C2 tolerance, C3 OOD, C4 statistical — point to specific repair paths. Air-gap incompatibility is a hard limitation: the workflow depends on external LLM API calls and is incompatible with most regulated air-gapped Verification and Validation (V&V) environments (IEC 60880, DO-178C, IEC 62304, ISO 26262). Pre-generated mutant pools can be reproduced offline, but generating new mutant pools requires LLM access. Self-hosted open-weight LLMs and offline-cached pools are P5 mitigations. Appendix E.1 gives the full air-gap justification and the standards catalogue.

**MR designers** can use offline batch SMS runs as a quantifiable design-feedback metric. We recommend a quarterly batch audit (about 0.5 person-day per quarter; detailed cost breakdown in Appendix E.2; estimates based on observed timings during this paper's 12-PUT campaign) rather than per-pull-request gating, because LLM API latency, cost non-determinism, and air-gap incompatibility together rule out the per-pull-request style. An earlier draft included a GitHub Actions per-PR YAML template; we removed it in revision because it hardcoded the v3b post-hoc selection into adopters' pipelines. Appendix E.2 gives the quarterly-audit workflow with resource-cost table.

**V&V documentation** can carry SMS as research-grade supplementary evidence alongside code coverage and MR lists. We make no normative claim toward IEC, ISO, or ASME standards. An earlier draft proposed acceptance thresholds (aligned-cell SMS ≥ 0.20 or 0.30 plus C1\_share ≤ 0.20); we removed them in revision because they have no normative backing and could be misread as enforcement-ready. Appendix E.3 records the conceptual complementarity with the code-verification scope of ASME V&V 20-2009 §3.

All three stakeholder classes consume the same single source of truth (`paper_numbers_v4.json` and `lrca_60cell_v4.json`) to avoid documentation fragmentation.

---

## 7. Threats to Validity

| # | Threat | Class | Mitigation summary | Detail |
|---|---|---|---|---|
| R1 | LLM generation reproducibility | Internal | Reproducibility package; identical prompt + seed → ≥ 90% pool overlap | Appendix F.1 |
| R2 | E2 probabilistic approximation | Construct | K_eq = 1000 + Hoeffding bound; sweep deferred to P4 | Appendix F.1 |
| R3 | Circular dependency P1 ↔ P2 | Internal | AVP version pinned to P1 commit hash; embedded source | Appendix F.1 |
| R4 | LRCA multi-label boundary | Internal | Decision-tree priority + multi-label co-occurrence table | Appendix F.1 |
| R5 | 12-PUT representativeness | External | Inherits P1; Appendix B.1 coverage argument; P3 scaling | Appendix F.2 |
| R6 | Cross-class statistical power | Conclusion | H4 framed exploratory; Friedman fallback; mixed-effects unavailable | Appendix F.2 |
| R7 | LLM homogeneity bias | Construct | 3-LLM rotation + 20% manual sampling | Appendix F.2 |
| R8 | LLM-source distributional shift | External | DeepSeek 11/15 of overlaps; argument is categorical, not frequency | Appendix F.2 |
| R9 | Mutant-pool size | Internal | Pool expanded to 17.4 mean; effect intrinsic, not pool-dilution | Appendix F.1 |
| R10 | LLM non-determinism | Internal | De-dup, K = 10/20 repeats, raw-response store | Appendix F.1 |
| R11 | Selection-on-response chained-conditioning | Internal | All v3b / v4 sign tests downgraded to exploratory; permutation + Bonferroni × 5 | Appendix F.1 |
| R12 | HOM equivalence | External | Confined claim to first-order syntactic tools; HOM testing in P4 | Appendix F.2 |
| R13 | v3 / v3b vs v4 protocol asymmetry | Internal | Quality not down (C1_share 0.164 → 0.209); P4 to rerun dual-blind on v4 | Appendix F.1 |

**Final limitations.** We list eight known limitations.

(1) **Equivalence determination is a probabilistic approximation.** Sampling K_eq = 1000 inputs is an engineering implementation of the undecidable equivalence problem, not a theorem-based decision. We give a Hoeffding-style upper bound on the false-equivalence probability in §2.3, but we did not execute a K_eq sweep over {500, 1000, 2000} for this submission. P4 will run that sweep.

(2) **LLM generation homogeneity bias.** Even with three-LLM cross-source pooling, training-data overlap across Claude, GPT, and DeepSeek may produce similar blind spots. Three-LLM rotation and 20% manual sampling reduce but do not eliminate this risk. Future work should add a fourth, independently-trained LLM family — a self-hosted open-weight model is the natural candidate.

(3) **Limited statistical power for cross-class consistency.** The four-class sign test has df = 3, and the mixed-effects model returns Singular matrix at N = 60 over 12 PUTs. We treat H4 as exploratory and present RQ3 in four pieces: class means, sign test, Friedman, and a forest plot.

(4) **LRCA reports "likely" root causes.** The decision-tree priority C5 > C4 > C3 > C2 > C1 is an engineering choice. The reproducibility package preserves the multi-label co-occurrence table for every killed mutant, not only the priority-winning root cause; `root_cause` is best read as a likely cause rather than a definitive causal attribution.

(5) **The AVP is reused from P1.** The P2 reproducibility package embeds the AVP source code so that P2 stays self-consistent under P1 evolution, but interface semantics may shift if P1 undergoes a major revision.

(6) **Epistemological scope versus engineering scope.** SMS measures semantic detection capability in the epistemological sense; engineering value is the specific subject of P2-CN and P5.

(7) **Signature simplification.** The `float → float` single-output signature is a substantive constraint, not a purely engineering trade-off, and it bounds the upper limit of mutant semantic complexity. P3 and P5 will validate SMS portability on industrial-grade multi-output PUTs.

(8) **Air-gap incompatibility.** The mutant-generation workflow calls external LLM APIs and is incompatible with most regulated air-gapped V&V environments (IEC 60880, DO-178C, IEC 62304, ISO 26262). Pre-generated mutant pools can be reproduced offline, but generating new pools requires LLM access. Self-hosted open-weight LLMs and offline-cached pools are P5 mitigations.

---

## 8. Conclusion

### 8.1 Findings summary

The 60-cell empirical demonstration produces six findings.

(i) The H2 large-effect threshold is **not met under the pre-registered point-estimate criterion** (δ = 0.323 in primary v3); the 49.1% stipulated power at the boundary clarifies that "not met" is a statement about the point estimate, not the effect size.

(ii) Under an identical prompt, three-LLM cross-source diversity does not move δ (Δδ = −0.007, 95% CI covers zero).

(iii) Across two c-class primary-MP conditions (MP5 and MP1), the LLM-source axis shifts Cliff's δ by ≤ 0.01 in magnitude (v3 → v4_mp5 = −0.009; v3b → v4 = −0.007), whereas the MR-design axis (MP5 ↔ MP1) shifts δ by approximately +0.12. Within this design, the c-class primary-MP choice, not LLM identity under an identical prompt, is the lever on the aligned-vs-cross effect size. A strong-sense source-diversity test with per-LLM differential prompts is deferred to P4.

(iv) Cross-source pooling raises mutant *quality* (mean C1\_share +27%, class-c mean SMS +91.4%†) without raising the effect size. († class-c +91.4% is conditional on the §3.4 v3b MP1 selection; permutation null one-sided p = 0.9885.)

(v) The Friedman main effect on MP differentiation is χ² = 15.30, p = 0.0041.

(vi) The Spearman correlation between SMS and Pattern Coverage is 0.163 at n = 12. Orthogonality is a hypothesis, not a finding.

### 8.2 Methodological contributions

This paper contributes a three-layer framework for domain-semantic mutation in single-output scientific computing kernels.

- **Layer 1 (§3.2).** Formal necessary conditions for semantic mutation — cross-function-boundary substitution, dependence on domain knowledge, change in algorithmic class — instantiated as five meta-operator classes: CE, OS, HP, TF, and SI (also written mut_C, mut_M, mut_G, mut_T, mut_F).
- **Layer 2 (§2.3).** The E1 ∧ E2 equivalence judgement, the conservative complete instantiation of the Layer-1 conditions, with an explicit trade-off against E1-alone and E2-alone variants.
- **Layer 3 (§3.5).** AST-normalised empirical traceability across all 12 PUTs: a 5.14% overall AST overlap with cosmic-ray defaults, and HP, SI, and TF categorically unreachable at 0/0/0.

SMS is backward-compatible with the classical MS through §2.6 Theorem 9.1, which establishes almost-everywhere degeneration in the limit `L = L_equiv ∧ L_killed ∧ L_mut`. The 60-cell empirical audit reported in §5 is one demonstration following this backbone, not the paper's main contribution.

### 8.3 Future work and P-series roadmap

We commit six P4 follow-ups.

(a) A pre-registered c-class primary-MP rule on a fresh dataset.

(b) A differential-prompt LLM-diversity test using V_canonical, V_persona, and V_cot (full protocol in Appendix C.1.1).

(c) A scaling study at n ≥ 30 PUTs for SMS-vs-Pattern-Coverage orthogonality and for HOM-equivalence empirics.

(d) A rerun of the dual-blind reviewer protocol on the full v4 grid, to separate protocol asymmetry (R13) from source diversity.

(e) Cross-language portability work (Python → JavaScript and Julia) building on Tip, Bell, and Schäfer (2024).

(f) A self-hosted open-weight LLM pilot for air-gapped industrial deployment (P5 scope).

The companion P-series roadmap is as follows.

- **P1.** MR meta-pattern audit on the same 12-PUT infrastructure (under review at *Progress in Nuclear Energy* and *International Conference on Software Analysis, Evolution and Reengineering* (SANER) 2027).
- **P3.** Industrial-scale Java and C++ port with a second-rater inter-rater κ for LRCA.
- **P4.** Formal theorems on minimal MR-subset existence, reachable adequacy, and three-pillar coupling, targeted at *ACM Transactions on Software Engineering and Methodology*.
- **P5.** Regulatory transfer to IEC 60880, ISO 26262, and DO-178C with the conceptual complementarity argument (Chinese, in submission to *Nuclear Power Engineering*).

---

## References

DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978). Hints on test data selection: Help for the practicing programmer. *Computer*, 11(4), 34-41. https://doi.org/10.1109/C-M.1978.218136

Jia, Y., & Harman, M. (2011). An analysis and survey of the development of mutation testing. *IEEE Transactions on Software Engineering*, 37(5), 649-678. https://doi.org/10.1109/TSE.2010.62

Jia, Y., & Harman, M. (2009). Higher Order Mutation Testing. *Information and Software Technology*, 51(10), 1379-1393. https://doi.org/10.1016/j.infsof.2009.04.016

Andrews, J. H., Briand, L. C., & Labiche, Y. (2005). Is mutation an appropriate tool for testing experiments? In *Proc. ICSE 2005* (pp. 402-411). ACM. https://doi.org/10.1145/1062455.1062530

Just, R., Jalali, D., Inozemtseva, L., Ernst, M. D., Holmes, R., & Fraser, G. (2014). Are mutants a valid substitute for real faults in software testing? In *Proc. FSE 2014* (pp. 654-665). ACM. https://doi.org/10.1145/2635868.2635929

Papadakis, M., Kintis, M., Zhang, J., Jia, Y., Le Traon, Y., & Harman, M. (2019). Mutation testing advances: An analysis and survey. *Advances in Computers*, 112, 275-378. https://doi.org/10.1016/bs.adcom.2018.03.015

Kintis, M., Papadakis, M., Papadopoulos, A., Valvis, E., Malevris, N., & Le Traon, Y. (2018). How effective are mutation testing tools? An empirical analysis of Java mutation testing tools with manual analysis and real faults. *Empirical Software Engineering*, 23(4), 2426-2463. https://doi.org/10.1007/s10664-017-9582-5

Delgado-Pérez, P., & Chicano, F. (2020). An experimental and practical study on the equivalent mutant connection: An evolutionary approach. *Information and Software Technology*, 124, 106317. https://doi.org/10.1016/j.infsof.2020.106317

Moradi Dakhel, A., Nikanjam, A., Majdinasab, V., Khomh, F., & Desmarais, M. C. (2024). Effective test generation using pre-trained Large Language Models and mutation testing. *Information and Software Technology*, 171, 107468. https://doi.org/10.1016/j.infsof.2024.107468

Zhang, M., Keung, J. W., Chen, T. Y., & Xiao, Y. (2021). Validating class integration test order generation systems with Metamorphic Testing. *Information and Software Technology*, 132, 106507. https://doi.org/10.1016/j.infsof.2020.106507

Ammann, P., & Offutt, J. (2008). *Introduction to software testing* (1st ed.). Cambridge University Press.

Petrović, G., & Ivanković, M. (2018). State of mutation testing at Google. In *Proc. ICSE-SEIP 2018* (pp. 163-171). ACM. https://doi.org/10.1145/3183519.3183521

Petrović, G., Ivanković, M., Fraser, G., & Just, R. (2021). Practical mutation testing at scale: A view from Google. *IEEE Transactions on Software Engineering*, 48(10), 3900-3912. https://doi.org/10.1109/TSE.2021.3107634

Tip, F., Bell, J., & Schäfer, M. (2024). LLMorpheus: Mutation testing using large language models. *arXiv preprint* arXiv:2404.09952.

Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. In *Proc. ISSTA 2021* (pp. 67-78). ACM. https://doi.org/10.1145/3460319.3464825

Just, R., Jalali, D., & Ernst, M. D. (2014). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. In *Proc. ISSTA 2014* (pp. 437-440). ACM. https://doi.org/10.1145/2610384.2628055

Romano, J., Kromrey, J. D., Coraggio, J., & Skowronek, J. (2006). Appropriate statistics for ordinal level data. Annual Meeting of the Florida Association of Institutional Research, Cocoa Beach, FL.

Vargha, A., & Delaney, H. D. (2000). A critique and improvement of the CL common language effect size statistics of McGraw and Wong. *Journal of Educational and Behavioral Statistics*, 25(2), 101-132. https://doi.org/10.3102/10769986025002101

Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). *Numerical Recipes: The Art of Scientific Computing* (3rd ed.). Cambridge University Press.

ASME V&V 20 Committee. (2009). *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*. ASME V&V 20-2009.

Hovmöller, A. (2016-). *mutmut*: A Python mutation testing tool. https://github.com/boxed/mutmut

Bingham, A. (2015-). *cosmic-ray*: Python mutation testing. Sixty North. https://github.com/sixty-north/cosmic-ray

Hałas, K. (2012-). *mutpy*: Mutation testing for Python. https://github.com/mutpy/mutpy

Li, M. et al. (under review). Empirical audit of metamorphic-relation meta-patterns in scientific computing software (P1). *Progress in Nuclear Energy* / SANER 2027.

Li, M. et al. (under review). [P2-CN companion]. *Nuclear Power Engineering*.
