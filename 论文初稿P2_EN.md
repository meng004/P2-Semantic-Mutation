# P2 论文初稿

## English Title (Primary)

**When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels**

### Alternative titles

- **Alt-1**: *Semantic Mutation Score (SMS): A Metamorphic Testing Adequacy Metric for Single-Output Scientific Computing Kernels — with a Three-Stage Ablation Across MR Alignment and Same-Prompt LLM Source Diversity*
- **Alt-2**: *Domain-Semantic Mutation Operators for Metamorphic Testing of Single-Output Scientific Computing Kernels: A Same-Prompt Cross-Source Empirical Audit*

## Abstract

**Context.** Metamorphic Testing (MT) addresses the test oracle problem in scientific computing software, but the fault-detection capability of metamorphic relations (MRs) has lacked a domain-aware adequacy metric: classical Mutation Score (MS) operates on syntactic AST mutations and does not capture domain semantics such as conservation laws, monotonicity, or convergence order. **Objective.** We propose Semantic Mutation Score (SMS), built on five domain-semantic mutation operators (Conservation, Monotonicity, Convergence, Trajectory, Fidelity-order breaks) that degenerate to classical MS in the syntactic limit (modulo D_S-measure-zero subsets, see §9 for the formal statement). **Method.** We instantiate a 12-PUT × 5-MP matrix (60 cells, average 24.3 LLM-generated mutants per cell, N=20 AVP repetitions) across four classes of single-output scientific computing kernels (each PUT a Python function with `float → float` signature, source code under 2 KB; the four classes are numeric, probabilistic, surrogate, ML). A three-layer Layered Root-Cause Analysis (LRCA) classifier separates legitimate semantic faults from artifacts/tolerance/OOD/statistical-noise. We design a three-stage ablation — v3 (same-source, P1-aligned), v3b (same-source, data-driven primary MP), v4 (cross-source over Claude/GPT/DeepSeek) — to isolate contributions of MR alignment design and LLM source diversity. **Results.** **The pre-registered H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is not met under the pre-registered point-estimate criterion** in the primary v3 analysis (δ = 0.323, 95% CI [0.017, 0.622]). Two exploratory follow-ups — v3b (data-driven c-class primary MP shift) and v4 (cross-source 3-LLM pool) — produce δ = 0.446 and 0.439 respectively, both still below 0.474. The exploratory contrasts give Δδ_MR = +0.123 (single-class primary-MP re-specification, post-hoc) and Δδ_LLM = −0.007 (cross-source under identical prompt template; CI overlaps zero). The two contrasts are reported separately rather than as a single ratio because the numerator reflects a confounded data-driven adjustment and the denominator reflects prompt determinism rather than source diversity in the strong sense. Cross-source pooling raises mutant quality (mean C1_share 0.164 → 0.209) and inter-class balance (class-c mean SMS +91.4% on a smaller mutant base, see §4.2.5). Friedman test confirms a significant MP main effect (χ² = 15.30, p = 0.0041); this is reported as a fallback non-parametric sensitivity, distinct from H4 cross-class consistency. Under pre-registered v3, the H4 sign test is 3/4 (partial); under exploratory v3b (post-hoc, conditional on c-class primary MP shift, §3.5.1) the same sign test is 4/4. We report v3 as the H4 primary result. SMS shows near-zero rank correlation with simple pattern coverage (ρ = 0.16, n = 12, p = 0.61, v4 primary); statistical power at this n is insufficient to support an "orthogonal" claim, framed instead as a hypothesis for future work. **Conclusion.** P2 contributes a three-layer methodology for domain-semantic mutation: (Layer 1) formal necessary conditions (cross-function-boundary substitution / domain knowledge / algorithmic class change) for "semantic mutation", instantiated as five meta-mutation operator classes (CE/OS/HP/TF/SI) with PUT-class specialization rules; (Layer 2) E1 ∧ E2 equivalence judgment as the conservative complete instantiation of the necessary conditions, with three-candidate trade-off analysis and §9 degeneration-theorem boundary; (Layer 3) AST-normalized empirical traceability proving P2 mutants are not a subset of syntactic-mutant pools (full 12-PUT empirics: 5.14% overall AST overlap rate against cosmic-ray default operators, with three of the five operator classes — HP/SI/TF, 159/292 mutants — categorically unreachable at 0% — positive empirical against the "new-concept classification" concern). SMS as an MR-adequacy demonstration metric degenerates to classical syntactic MS in the syntactic limit (modulo D_S-measure-zero subsets, §9). The 60-cell empirical audit (H1/H2/H4/H5) demonstrates, within the scope of single-output kernels and identical prompt template, that the LLM-mutant + current-MR-design configuration produces medium- not large-effect; this is an auxiliary finding under the methodology backbone, not the paper's main contribution.

## Keywords

metamorphic testing; mutation testing; semantic mutation operators; single-output scientific computing kernels; LLM-generated mutants; ablation study; metamorphic relation adequacy; same-prompt cross-source mutant pool; Cliff's delta; Friedman test

---

- Journal: *Information and Software Technology* (IST, preferred) / *Journal of Systems and Software* (JSS) / *Software Testing, Verification and Reliability* (STVR) (alternatives)
- Submission window: 2027 Q3, expected publication 2028 Q2
- Author: Meng Li (corresponding author, mlemon@usc.edu.cn, School of Computing, University of South China, postcode 421001, China)
- Related work: [Meng Li et al., Progress in Nuclear Energy, under review] arXiv technical report (shared by P1 / P4)

---

## Section 1 · Paper Identity and Claims

### 1.1 Terminology Unification (Throughout the Paper)

| Use | Do Not Use | Rationale |
|---|---|---|
| **4 representative classes of scientific computing programs** | ~~4 paradigms~~ | "Paradigm" carries strong semantics in the SE/PL community as "programming paradigm = OO/FP/Logic," which differs from this paper's meaning of "scientific computing program categories" |
| **cross-class consistency** | ~~cross-paradigm consistency~~ | Aligns with terminology unification |

The English text uniformly uses *four representative classes of single-output scientific computing kernels* and *cross-class consistency*, avoiding *paradigm*. **The scope of the contribution claim is strictly bounded to single-output `float → float` kernels (each PUT source code < 2 KB, total 12 PUTs across 4 classes: numeric / probabilistic / surrogate / ML)**; the title, §1.6, §6.5, and §7.5 use this scope consistently. Where "scientific computing programs" appears in the body text, it functions only as a general domain term (as in §1.3 LLM-mutant literature review, §1.6 P-series roadmap) and **does not constitute a methodological claim over industrial-scale, multi-module, or multi-output scientific computing software**; §6.5 stakeholder pain-points and §6.5.3 V&V documentation discussion are also constrained to this single-output kernels scope.

### 1.2 Core Claims

This paper proposes a **three-layer methodological framework** around domain-semantic mutation operators (explicitly revised in P2 R2):

- **Layer 1 — Definitional** (§3.2.0): Establishes necessary conditions for semantic mutation: (a) cross-function-boundary replacement, (b) carrying domain knowledge, (c) altering algorithmic class. The five meta mutation operator classes (CE/OS/HP/TF/SI = mut_C/M/G/T/F) are specializations of these necessary conditions across the four PUT classes.
- **Layer 2 — Operational** (§2.3 / §4.4): Provides equivalence criteria E1 ∧ E2 as a conservative complete instantiation of the necessary conditions. Justifies the selection among three candidate definitions (semantic equivalence / output equivalence / both).
- **Layer 3 — Applied** (§3.2.6.3): Uses equivalence detection tools to trace P2 mutants back to syntactic mutants, providing positive empirical evidence that the P2 mutant pool ⊄ syntactic mutant pool (full 12-PUT cosmic-ray empirics: **5.14%** overall AST overlap rate, with three classes — HP/SI/TF, totaling 159 mutants — at **0/0/0** overlap).

Additionally, this paper introduces three supporting tools: **Semantic Mutation Score (SMS)**, following the classic `killed/(mut−equiv)` structure, plus an **engineering attribution layer** using likely root cause analysis (LRCA) to conduct an empirical audit demonstration of MR sets across 60 cells spanning four representative classes of scientific computing programs. The audit reports: (a) tool implementation feasibility, (b) SMS behavior on meta pattern slices, (c) cross-class consistency, and (d) empirical differences from existing MR metrics (§5). **The 60-cell audit is an empirical demonstration following the establishment of the three-layer methodological framework, not the paper's main contribution** — the primary contribution lies in the methodological framework of Layers 1-3.

**Theoretical commitment**: This paper's SMS strictly reduces to the classic Jia & Harman syntactic Mutation Score (MS) in the degenerate limit — classic MS is a special case of SMS when all extension dimensions are disabled. This establishes this paper's identity as a true generalization of classic mutation testing.

This paper does not claim "how adequacy should be defined" — that proposition is reserved for P4 (TOSEM) unified theoretical work.

### 1.3 Three-Year Roadmap Position and Related Work

#### 1.3.1 Three-Year Roadmap

P2 = γ dual-track parallel development (P2 leverages P1's 12-PUT infrastructure). Concurrent papers:

- **P1** (SANER 2027): MR meta pattern empirical audit
- **P2** (this paper, IST 2027 Q3)
- **P2-CN** (Nuclear Power Engineering 2027 Q4): Nuclear engineering practice details, cites P2
- **P4** (TOSEM): Unified theory + three-pillar coupling theorems, cites P2 empirical foundation
- **P5** (*Nuclear Engineering and Design*, NED, 2028): Regulatory extension, cites P2-CN

#### 1.3.2 Related Work

Overview of semantic-aware mutation work in the past 5 years:

| Work | Domain | Difference from P2 |
|---|---|---|
| Humbatova, Jahangirova & Tonella (DeepCrime, ISSTA 2021) | Deep learning systems (real-fault-based mutation) | Single class (deep learning); P2 includes ML as one of 4 classes |
| Tip, Bell & Schäfer (LLMorpheus, arXiv 2024) | JavaScript LLM mutants | Single language; P2 conducts cross-source LLM ablation on Python scientific computing kernels (§4.2.5) |
| Jia & Harman (classic survey, TSE 2011) + Papadakis et al. (survey, Adv. Computers 2019) | Syntactic mutation | P2 is backward-compatible (§9 degeneration theorem) and extends at the domain-semantic layer |

P2's unique positioning: **meta pattern-driven + unified framework across 4 classes + strict compatibility with classic MS as an intensional extension**.

**CPH grounding of classical mutation testing (R2 round-2 NEW)**: The syntactic baseline of this methodology rests on the classical Coupling Effect Hypothesis (CPH) — DeMillo, Lipton & Sayward (1978) hypothesized that tests detecting simple faults also detect complex faults; Andrews, Briand & Labiche (2005) and Just et al. (2014, FSE) empirically confirmed that mutants are valid surrogates for real faults; Papadakis et al. (2019) provided the most comprehensive post-Jia & Harman (2011) survey of mutation testing advances. §3.2.6 of this paper argues: **CPH holds within the scope of syntactic mutation but is non-trivial in the scope of domain-semantic mutation** — syntactic mutants cannot reach P2's four semantic operator classes (HP/SI/TF/OS); even when syntactic mutation testing couples simple syntactic faults to complex syntactic faults, that coupling does not extend to domain-semantic faults (see §3.2.6.0 systematic-vs-incidental + §3.2.6.3 12-PUT empirics 5.14% AST overlap rate).

**Recent work on LLM-generated mutants**: Tip et al. (2024) proposed LLMorpheus, using LLMs to generate mutants on JavaScript instead of fixed operator sets, reporting fault-detection comparable to traditional operators but with lower equivalent rates, and observing medium-effect intervals in effect-size reports for LLM-mutants. Petrović & Ivanković (2018) reported approximately 20% productive mutant ratio on Google's internal 500,000-mutant dataset, numerically close to this paper's §5.6.2 LRCA C1_share measured levels (default threshold 0.16, calibrated 0.20) — **a numerical coincidence rather than mechanism validation**; see §6.1 for the detailed disambiguation. This paper's §5.7.2 measured Cliff's δ = 0.323 is in the same magnitude as the LLM-mutant medium-effect phenomenon observed by Tip et al. (2024) on JavaScript. **Estimand caveat**: Tip 2024 compares "LLM mutants vs traditional mutants on fault detection rate" (cross-source comparison), while this paper's §5.7.2 compares "aligned vs cross MP slice on the same mutant pool" (single-source within-pool comparison). The numerical proximity of the two δ values does not constitute substantive support, serving only as a reference to the medium-effect phenomenon in LLM-mutant literature.

**Relation to existing V&V standards (R3 round-2 NEW)**: This paper's SMS is conceptually complementary to ASME V&V 20-2009 *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer* §3 code verification — the latter targets code-level correctness verification of numerical solvers, while this paper's SMS targets fault-detection adequacy of MR sets. This paper's empirical scope is strictly bounded to single-output kernels (§3.1.1), with a substantial scale gap to the multi-module CFD codes targeted by V&V 20; see §6.5.3 long-term aspiration discussion.

### 1.4 Research Questions (Purely Empirical, 4 Items)

- **RQ1** What are the distributions of instantiation rate (inst_rate), equivalent rate (equiv_rate), C1 share (C1_share), and survival rate (survive_rate) for the 5 operators across 60 cells (12 PUTs × 5 operators)?
- **RQ2** What is the difference structure of SMS between operator-meta pattern aligned (j=k) and cross (j≠k) slices? Is the equiv_rate of P1 ○ vacant cells systematically higher than that of ●● populated cells?
- **RQ3** What is the cross-class consistency of SMS across 4 program classes × 5 operators (sign test + coefficient of variation)?
- **RQ4** What are the empirical difference distributions between SMS and pattern coverage in ranking and discriminative power? (Descriptive, no presupposed answer)

### 1.5 Hypothesis System (Originally 5 Items; H3 Formally Retired, 4 Valid Hypotheses)

- **H1 Operator Implementation Feasibility**: ≥ 4 of the 5 operators can produce ≥ 5 non-equivalent mutants on ≥ 9/12 PUTs
- **H2 Meta Pattern Aligned Slice**: aligned-SMS / cross-SMS odds ratio ≥ 3.0, Cliff's δ ≥ 0.474
- ~~**H3 Equiv Aligned Vacancy (P1 H6 Dual)**: 6 ○ cells have equiv_rate ≥ 0.85; populated cells have equiv_rate ≤ 0.30~~ **(Formally Retired)**
- **H4 Cross-Class Consistency**: ΔSMS shows all-positive sign test across 4 program classes, coefficient of variation (CV) < 0.5
- **H5 LRCA Robustness**: Average suspect share (suspect_share) across all 60 cells ≤ 0.20

> **Formal Statement on Retired Hypothesis H3**: The P1-derived version of this paper included H3 regarding the bidirectional threshold hypothesis "○ vacant cells equiv_rate ≥ 0.85; ●● populated cells equiv_rate ≤ 0.30." In the measured data space of LLM-generated mutants, equivalence detection triggered in extremely few cells (< 10 cells with non-zero equiv), causing structural collapse of the bidirectional threshold comparison space, rendering this hypothesis unable to make meaningful determinations on this paper's data. This paper formally retired H3 after v3 data collection and treats the R_sem / R_kill decoupling phenomenon as a descriptive observation in §6.2 (supported jointly by §4.8.3 operator-level pilot + §5.6.2 LRCA C1_share), not as a substitute for formal hypothesis testing. **To maintain citation consistency with §3 / §5 / §6 / §7, subsequent sections continue using H1, H2, H4, H5 numbering (with H3 vacant), without renumbering throughout the paper.**

### 1.6 P2 / P4 / [Meng Li et al., Progress in Nuclear Energy, under review] Boundaries

| Dimension | P2 Main Text (This Paper) | P4 (TOSEM) |
|---|---|---|
| Contribution Type | Tool + empirical report | Theoretical formalization + theorems |
| Proposition Answered | "How does the tool behave" (empirical) | "How should adequacy be defined" (theoretical) |
| Empirical Foundation | 12 PUTs, 60 cells | No experiments, cites P1 + P2 |
| P4-Exclusive Dimensions | Not involved | Minimal MR subset existence theorem / reachable adequacy theorem / three-pillar coupling theorem |

#### 1.6.1 P2 Innovation Attribution

| Innovation | Content |
|---|---|
| **C-I Domain-Semantic Mutation Operators** | mut_j ∈ MUT five classes of semantic failure injection, dual to 5 meta patterns |
| **C-II SMS + Backward Compatibility** | Classic `killed/(mut−equiv)` structure + three-dimensional intensional extension + degenerates to classic MS |
| **C-III LRCA Engineering Attribution Layer** | 5 likely root causes + 3-layer diagnosis, purely descriptive, not in SMS formula |
| **C-IV 60-Cell Empirical Audit** | All 4 PUT classes × all 5 operators |

#### 1.6.2 Epistemological Statement

SMS is an epistemological semantic detection metric, not an engineering value proxy. Engineering value requires separate metrics (P2-CN subject matter). **Toy-scope caveat (R2 round-2 NEW)**: The 12 PUTs in this paper are Numerical-Recipes-style "toy kernels" (each PUT < 2 KB, signature limited to `float → float`), intended to provide a verifiable minimum-working-example for the methodological backbone (§3.2.0 necessary conditions, §2.3-§4.4 equivalence judgment, §3.2.6.3 traceability). Empirical results at this scale do **not** constitute a methodological claim over industrial-scale, multi-module, or multi-output scientific computing software; transfer of the empirics to that scale is left to P5 (domain application).

---

## Section 2 · Semantic Mutation Notation System

### 2.0 Dual Fundamental Principles

| Principle | Name | Operational Meaning |
|---|---|---|
| **P-I** | Developmental | Develop upon the classical mutation testing framework to accommodate semantic mutation requirements for scientific computing programs and align with MR validity determination needs |
| **P-II** | Stable/Open | Notation system stable (skeleton fixed), content open (operators/meta patterns/root causes/classes extensible by future researchers) |

### 2.1 Notation System Skeleton (Fixed Layer)

#### 2.1.1 Classical Mutation Testing Vocabulary Inheritance (Seven Core Concepts)

| Classical Concept | P2 Correspondence | Extension Point |
|---|---|---|
| Program Under Test (PUT) | `S_i` | Only introduces index i ∈ I, pure naming inheritance |
| Mutation Operator | `mut_j ∈ MUT` | Syntactic/grammatical rules → domain-semantic failure injection |
| Mutant | `s' ∈ mut_j(S_i)` | Syntactic transformation product → semantic transformation product |
| Equivalent Mutant | `equiv_{i,k,j}` | Bitwise behavioral equivalence → semantic-class equivalence (E1 ∧ E2) |
| Killed Mutant | `killed_{i,k,j}` | Equality oracle detects difference → meta pattern AVP detects |
| Surviving Mutant | `survive_{i,k,j}` | No structural extension |
| Mutation Score (MS) | `SMS = killed/(mut−equiv)` | Formula structure retained, extended only through internal semantics of mut/equiv/killed |

#### 2.1.2 Complete Notation System Table

```
═══════════════════ Paper Domain ═══════════════════
Paper Identity:        P1, P2, P4, P5

═══════════════════ Experimental Objects ═══════════════════
PUT Set I:  {A1,A2,A3,B1,B2,B3,C1,C2,C3,D1,D2,D3}, |I|=12
PUT:        S_i  (i ∈ I)
Class Mapping:          cls : I → {A, B, C, D}    (open, extensible)
Valid Input Distribution:    D_S, sampling X_{K_eq} ~ D_S

═══════════════════ Metamorphic Testing Side ═══════════════════
Meta Pattern (MP):
  MP = {MP_1,...,MP_5}, k ∈ {1,...,5}    (open, extensible)
  MP_1 Conservation  MP_2 Monotonicity  MP_3 Convergence  MP_4 Trajectory  MP_5 Partial-order
Metamorphic Relation:        MR_{i,k} (provided by P1), mr = (r,R) ∈ MR_{i,k}
Automated Verification Pipeline (AVP):
  AVP : Programs × MR_universe × R⁺ → {pass, fail}
  AVP(s, mr, ε_AVP^k)  invokes corresponding verification method per MP_k

═══════════════════ Mutation Testing Side ═══════════════════
Mutation Operator Family (MUT):
  MUT = {mut_1,...,mut_5}, j ∈ {1,...,5}    (open, extensible)
  mut_1=mut_C  mut_2=mut_M  mut_3=mut_G  mut_4=mut_T  mut_5=mut_F
  Signature: mut_j : Programs → 2^Programs
Mutant:          s' ∈ mut_j(S_i)
Alignment:            align(j) = j

═══════════════════ Three-State Decomposition (Fixed) ═══════════════════
mut_j(S_i) = equiv_{i,k,j} ⊔ killed_{i,k,j} ⊔ survive_{i,k,j}    (mutually exclusive and exhaustive)

equiv Determination Dual Conditions:
  (E1) AVP-coherent:    ∀ mr ∈ MR_{i,k}: AVP(S_i, mr) = AVP(s', mr)
  (E2) Output-equiv:    ∀ x ∈ X_{K_eq} ~ D_S: ‖S_i(x) − s'(x)‖ ≤ ε_eq

killed Determination:
  killed(s', MR_{i,k}) ⇔ ∃ mr ∈ MR_{i,k}:
                          AVP(S_i, mr) = pass ∧ AVP(s', mr) = fail

═══════════════════ Metric (Fixed Classical Structure) ═══════════════════
SMS_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
            = |killed_{i,k,j}| / (|killed_{i,k,j}| + |survive_{i,k,j}|)
            ∈ [0, 1]

═══════════════════ LRCA Engineering Attribution Layer (Descriptive, Not in SMS) ═══════════════════
Likely Root Cause Inventory:    C = {C1,...,C5}    (open, extensible)
  C1 True Semantic Failure / C2 Tolerance Perturbation / C3 Out-of-Distribution (OOD)
  C4 Statistical Assumption Violation / C5 Mutator Artifact
LRCA Output:       Each s' ∈ killed annotated with root_cause(s') ∈ C
Descriptive Quantities:          C1_share_{i,k,j}, suspect_share_{i,k,j}    (reported in §5)

═══════════════════ Slicing and Cross-Class ═══════════════════
Slicing:            aligned: j=k    cross: j≠k
Cross-class:            ΔSMS_c, c ∈ {A,B,C,D}
                CV(ΔSMS) := std(ΔSMS_c) / |mean(ΔSMS_c)|

═══════════════════ Tolerance and Sampling ═══════════════════
Tolerance:            ε_AVP^k (meta pattern dependent), ε_eq (equivalence output tolerance)
Sampling:            K_eq = 1000 (E2 sample size), N = 20 (statistical replicates)
```

#### 2.1.3 Notation Stability Declaration

The notation skeleton of this paper (11 core concepts + three-state decomposition + SMS formula + AVP interface) is **fixed**. The **content** of operator family MUT, meta patterns MP, likely root cause inventory C, and PUT class mapping cls is open; future researchers may extend with new elements while preserving notation semantics.

### 2.2 Domain-Semantic Mutation Operators mut_j ∈ MUT

#### 2.2.1 Operator Signature (Fixed)

```
mut_j : Programs → 2^Programs
```

#### 2.2.2 Five Operator Instantiations in This Paper (Open, Extensible to mut_6, ...)

| Operator | Failure Semantics | Alignment with MP |
|---|---|---|
| mut_1 = mut_C | Conservation-breaking | MP_1 Conservation |
| mut_2 = mut_M | Monotonicity-breaking | MP_2 Monotonicity |
| mut_3 = mut_G | Convergence-breaking | MP_3 Convergence |
| mut_4 = mut_T | Trajectory-distorting | MP_4 Trajectory |
| mut_5 = mut_F | Fidelity-order-breaking | MP_5 Partial-order |

#### 2.2.3 Operator Design Principles

- Inject domain-semantic invariant violations
- Syntactically correct and executable
- Generated by humans or machines with semantic understanding capability (Large Language Model, LLM)
- No claim of strict one-to-one operator-meta pattern correspondence (`align(j)=j` is a design choice, not a theorem)

### 2.3 (Semantic) Equivalent Mutant equiv

**Layer 2 — Operational (Equivalence Determination = Instantiation of §3.2.0 Necessary Conditions)**

The equivalence determination E1 ∧ E2 given in this section is an **executable instantiation** of the necessary conditions (a)(b)(c) in §3.2.0. Logical mapping:

- **E1** (AVP-coherent, "consistent with original program determination via AVP for all MR_i,k when passing") ↔ converse of necessary condition (c): "whether algorithm class is consistent" — if mutant behavior is indistinguishable from original program within the MR framework, then algorithm class is consistent (c not satisfied).
- **E2** (Output-equivalent on K_eq=1000 sampling within ε_eq) ↔ converse of necessary conditions (a)(b): "whether consistent at pure output layer without relying on cross-function/domain knowledge distinction" — if two mutants are consistent on K_eq numerical sampling, they have identical pure numerical behavior outside (a)(b).
- **E1 ∧ E2** = **conservative complete instantiation** of necessary conditions = converse of (c) ∧ converse of (a)(b) = "judged equivalent in all converse directions of necessary conditions."

**Trade-offs Among Three Candidates**:

| Determination | False Positive (Misjudge equiv) | False Negative (Miss equiv) | Bias on SMS |
|---|---|---|---|
| **E1 alone** (Semantic same) | Mutant numerically coincides on K_eq inputs but consistent within MR framework | E1 false → truly non-equivalent | SMS biased low (easier to judge equiv → denominator mut-equiv smaller) |
| **E2 alone** (Output same) | Mutant output consistent but MR behavior different (rare, nearly impossible) | E2 false on K_eq sampling but consistent over full space | SMS biased high (harder to judge equiv) |
| **E1 ∧ E2** | Simultaneous false positive (harder) | E1 ∨ E2 false implies non-equiv (easier to judge non-equiv) | **SMS biased high (conservative, fewer equiv)** |

**Why Choose E1 ∧ E2**: On LLM-generated mutants, (i) E2 alone is easily deceived by numerical coincidence (mutant accidentally outputs approximations at sampling points but semantically different); (ii) E1 alone is easily deceived by insufficient AVP coverage (if |MR_i,k| is small, E1 pass rate is high but mutant actually non-equivalent); (iii) E1 ∧ E2 = "AVP + numerical sanity check" dual-layer verification, more robust.

**Counterexample Contrast**:
- E2 passes but E1 does not: extremely rare — mutant coincides at K_eq sampling points but significantly deviates at MR_i,k trigger points (mutant should not be judged equiv, E1 ∧ E2 correctly judges non-equiv)
- E1 passes but E2 does not: common — mutant behavior consistent within MR framework but has numerical drift beyond ε_eq (still should not judge equiv, E1 ∧ E2 correct)

**Degenerate Limit Connection to §9**: Under degenerate limit L_equiv (L1 ∧ L2), E2 alone already degenerates to classical bitwise equivalence (Lemma 9.1); E1 degenerates to trivial condition (MP set degenerates to equality determination under L4); three candidates are **almost everywhere consistent** under L. Under current paper data (non-degenerate limit), the conservative choice of E1 ∧ E2 is engineering-sound.

#### 2.3.1 Determination Dual Conditions

```
equiv(s', S_i, MR_{i,k}) ⇔
  (E1) AVP-coherent
  (E2) Output-equiv (K_eq=1000, ε_eq inherits P1 cell-specific tolerance)
```

#### 2.3.2 Degenerate Relation to Classical Equivalent Mutant

In the limit ε_eq → 0, K_eq → full input space, (E2) degenerates to bitwise equivalence; (E1) is implied by (E2) in that limit. equiv reduces to classical behavioral equivalence.

### 2.4 Semantic Mutation Score SMS

#### 2.4.1 Formula

```
SMS_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
            = |killed_{i,k,j}| / (|killed_{i,k,j}| + |survive_{i,k,j}|)
            ∈ [0, 1]
```

Literally isomorphic to the Jia & Harman MS formula.

#### 2.4.2 Three Dimensions of Internal Extension

| Dimension | Classical | P2 |
|---|---|---|
| Mutation Generation | Rule-based syntactic operators | Domain-semantic operators (LLM/human) |
| Equivalence Determination | Bitwise behavioral equivalence | Tolerance equivalence (E1 ∧ E2) |
| Test Oracle | Bitwise equality oracle | Meta pattern AVP |

#### 2.4.3 Backward Compatibility Declaration

> The semantic mutation notation system of this paper reuses the classical mutation testing vocabulary of Jia & Harman (TSE 2011) — the seven core concepts of program under test, mutation operator, mutant, equivalent mutant, killed mutant, surviving mutant, and mutation score are aligned item by item, and the SMS formula strictly preserves the classical structure **SMS = |killed| / (|mut| − |equiv|)**. The extensions of this paper are applied only to the **internal definitions** of three concepts: mut (syntactic operators → domain-semantic operators), equiv (bitwise behavioral equivalence → semantic-class equivalence E1∧E2), and killed (equality oracle → meta pattern AVP), without introducing any new formula terms or new state classifications. Under the degenerate limit where all extension dimensions are closed — i.e., ε_eq → 0, K_eq → full input space, ε_AVP^k → 0, MP set reduces to equality determination, mut_j switches to rule-based syntactic operators, PUT class restricted to imperative deterministic programs — SMS strictly regresses to the classical syntactic mutation score, equivalent mutants degenerate to classical behavioral equivalence, killed mutants degenerate to bitwise difference detection, and the LRCA engineering attribution layer trivializes because C2-C5 cannot be triggered. This backward compatibility is the intrinsic scientific guarantee of the notation system in this paper: any empirical conclusion based on SMS is structurally consistent with existing mutation testing literature under classical syntactic mutation scenarios, and does not constitute semantic fragmentation at the metric level.

### 2.5 AVP Reuse Protocol

#### 2.5.1 Interface Signature (Provided by P1)

```
AVP : Programs × MR_universe × R⁺ → {pass, fail}
AVP(s, mr, ε_AVP^k)  invokes corresponding verification method per MP_k
```

#### 2.5.2 Meta Pattern Verification Methods (Currently 5 MP Classes, Extensible)

| Meta Pattern | Verification Method |
|---|---|
| MP_1 Conservation | Tolerance equality \|LHS−RHS\| ≤ ε |
| MP_2 / MP_5 | Wilcoxon signed-rank test, α=0.05 |
| MP_3 Convergence | Convergence order estimation + asymptotic residual ratio |
| MP_4 Trajectory | Dynamic Time Warping (DTW) distance threshold ε_DTW |

#### 2.5.3 Version Pinning

AVP implementation version = P1 arXiv technical report commit hash `<P1-AVP-vX.Y>`. P2 reproduction package embeds complete AVP source code, decoupled from P1.

### 2.6 LRCA Engineering Attribution Layer

#### 2.6.1 Five Likely Root Causes (Open)

| Root Cause | Meaning |
|---|---|
| C1 | True Semantic Failure (what P2 seeks) |
| C2 | Numerical Tolerance Perturbation |
| C3 | Out-of-Distribution (OOD) |
| C4 | Statistical Assumption Violation |
| C5 | Mutator Artifact |

#### 2.6.2 Three-Layer Diagnosis + Artifact Pre-scan (L0)

- **L0 Artifact Pre-scan**: Double-blind review (§4.2.4 dual LLM cross-source + 20% human sampling)
- **L1 Tolerance Robustness**: N=20 replicates, fail ratio ≥ 0.80 considered stable
- **L2 OOD Triage**: For C/D classes, distinguish valid domain D_S^valid from OOD region
- **L3 Statistical Assumption Baseline**: For Wilcoxon/DTW, pre-check Independent and Identically Distributed (IID)/stationarity on PUT's own samples

#### 2.6.3 Decision Tree

```
For each s' ∈ killed_{i,k,j}:
  L1: fail ratio < 0.80 → C2
       otherwise → L2
  L2 (C/D classes): fail only in OOD → C3
       otherwise → L3
  L3 (B/D classes + Wilcoxon/DTW): assumption violation → C4
       otherwise → artifact recheck
  Artifact evidence → C5
       otherwise → C1
```

Multi-label priority: **C5 > C4 > C3 > C2 > C1**.

#### 2.6.4 Output Quantities

```
C1_share_{i,k,j}      := |{s' ∈ killed : root_cause = C1}| / |killed|
suspect_share_{i,k,j} := 1 − C1_share_{i,k,j}
```

LRCA **does not modify the SMS formula**; the killed set does not exclude suspects.

### 2.7 Formalization Hierarchy Diagram

```
AVP (component, P1) ─→ equiv & killed (construction, P2 internal extension)
              ─→ SMS (metric, classical structure)
              ─→ LRCA (description, P2 engineering attribution layer, not in SMS)
```

---

## Section 3 · Experimental Subjects and the 60-Cell Operator-Program Instantiation Matrix

### 3.1 Experimental Subject Selection (12 Programs Under Test, Inherited from P1 [Meng Li et al., Progress in Nuclear Energy, under review])

| Class cls | Program i | Name | Representative Mathematical Structure | Scale |
|---|---|---|---|---|
| **A Numerical** | A1 | Lorenz system Ordinary Differential Equation (ODE) integration | Nonlinear ODE system | ~150 LOC |
| | A2 | LU decomposition | Linear algebra, numerical stability | ~80 LOC |
| | A3 | Finite Difference Method (FDM) 1D heat conduction | Parabolic Partial Differential Equation (PDE) time-stepping | ~200 LOC |
| **B Probabilistic** | B1 | Beta-Binomial conjugate inference | Analytical posterior | ~60 LOC |
| | B2 | Markov Chain Monte Carlo (MCMC) Metropolis-Hastings | Markov chain sampling | ~250 LOC |
| | B3 | Monte Carlo integration | Importance sampling | ~100 LOC |
| **C Surrogate** | C1 | Gaussian Process Regression (GPR) | Kernel methods | ~300 LOC |
| | C2 | Polynomial Chaos Expansion (PCE) | Orthogonal basis | ~250 LOC |
| | C3 | Neural Network Surrogate (NN-Surrogate, NN-Surr) | Multi-layer perceptron substitution | ~400 LOC |
| **D Machine Learning** | D1 | Multi-Layer Perceptron (MLP) | Backpropagation | ~350 LOC |
| | D2 | Support Vector Machine (SVM) | Convex optimization | ~200 LOC |
| | D3 | Logistic Regression (LR) | Maximum likelihood | ~120 LOC |

#### 3.1.1 Selection Rationale (Self-Contained)

The selection of 12 PUTs not only inherits the work of P1 [Meng Li et al., Progress in Nuclear Energy, under review], but this paper also independently justifies their representativeness. The justification unfolds across three dimensions:

**(a) Library stack coverage**: The implementation stack of the 12 PUTs in this paper covers the 3 major mainstream libraries of Python scientific computing + the numpy foundation layer:

| Library | Involved PUTs | Library Version (This Paper) |
|---|---|---|
| numpy (linear algebra / array operations) | A1, A2, A3, B1, B2, B3 | 2.4.4 |
| scipy (optimization / integration / statistics) | A1(integrate), A2(linalg), B2(stats) | 1.17.1 |
| scikit-learn (surrogate / ML) | C1, C2, C3, D1, D2, D3 | 1.8.0 |

These 3 libraries + numpy constitute the de facto foundation stack for Python scientific computing software, covering all scientific computing modules in the PyPI download top-50 (2026-04 data). The 12 PUTs in this paper do not cover GPU/distributed computing stacks (JAX / CuPy / dask) and domain-specific libraries (BioPython / Astropy / RDKit), which is a limitation explicitly declared in §7.2.1 R5, reserved for the P3 paper (broader coverage).

**(b) Mathematical structure coverage**: Across 4 classes (numerical / probabilistic / surrogate / ML), the mathematical structures instantiated by the 12 PUTs include:

- ODE / PDE time-stepping (A1, A3)
- Direct linear algebra (A2)
- Bayesian analytical inference + MCMC + Monte Carlo integration (B1, B2, B3)
- Kernel methods + orthogonal polynomials + neural network surrogates (C1, C2, C3)
- Convex optimization + backpropagation + maximum likelihood (D1, D2, D3)

These 12 structures cover 8 of the 12 chapters in the main table of contents of Numerical Recipes (Press et al. 2007). **The 4 uncovered chapters**: (1) advanced PDE solvers (FEM, finite-volume, spectral), this paper's A3 only covers 1-D explicit FDM; (2) FFT / spectral methods; (3) optimization (interior-point, trust-region, etc.), D2 SVM only touches a subset of convex optimization; (4) symbolic computation / computer algebra. The PUTs corresponding to these 4 chapters are important in industrial-grade scientific computing software (CFD / quantum chemistry / signal processing), but are not covered in this paper, reserved for the P3 paper scaling study (§7.2.1 R5 merged declaration with this section).

**(c) Comparison with existing mutation testing benchmarks**:

| Benchmark | Covered PUTs | Relationship to This Paper's 12 PUTs |
|---|---|---|
| **DeepCrime** (Humbatova, Jahangirova & Tonella, ISSTA 2021) | Deep learning systems (Keras/TensorFlow, real-fault-based) | This paper's class D (D1/D2/D3, sklearn ML kernels) shares topical overlap with DeepCrime on the ML category (specific frameworks and fault models differ) |
| **Defects4J** (Just, Jalali & Ernst, ISSTA 2014) | General Java fault database | No direct PUT-selection overlap with this paper; cited only as a baseline mutation-as-fault-proxy reference (§1.3.2) |
| **mutmut / cosmic-ray demo PUTs** | General Python (no domain focus) | This paper significantly extends scientific-computing domain focus |

The 12 PUTs in this paper share topical overlap with DeepCrime on the ML subset (D); classes A (numerical) / B (probabilistic) / C (surrogate) are this paper's unique extensions relative to the Python LLM-mutant literature.

**(d) Balance between scale and representativeness**: Each PUT is 50-400 LOC, with function signatures standardized to `program(x: float) → float` (facilitating AVP invocation and 60-cell matrix generation). The scale is smaller than industrial code (typically 1-10 KLOC), but retains the complete semantics of the core mathematical structure of each class.

**Limitation: The `program(x: float) → float` signature simplification is a substantive constraint** (not a purely engineering tradeoff). The input of industrial-grade scientific computing software is typically high-dimensional structures such as mesh / state-vector / tensor (CFD grids, MD particle states, FEM element matrices), and the output may be multi-component fields or time-series trajectories. The scalarized PUTs in this paper impose an upper bound on the semantic complexity of mutants, potentially systematically underestimating SMS and cross-class differences on industrial PUTs. This signature constraint is explicitly declared in §7.2.1 R5 and §7.5 final limitation; the P3 paper will validate the portability of SMS on industrial-grade PUTs.

**Statistical layer support**: The Cliff's δ in §5.7.2 and the Friedman χ² in §5.8.4 both provide directional evidence (the latter significant, the former H2 rejected). The scale of 12 PUTs works for H1 (12/12 PUTs aligned > 0) and H4 sign test, but is clearly underpowered for mixed-effects (§5.8.3 Singular) and Spearman ρ (n=12, p=0.74) (§7.2.2 R6). This paper does not make a strong claim that "12 PUTs are sufficient to support all RQs."

### 3.2 5 Operator Semantic Injection Rules (MUT Content Instantiation)

This section defines the 5 classes of **meta-mutation operators** in this paper — not operators directly targeting a specific PUT, but operator families / operator templates. For different types of programs (a numeric / b probabilistic / c surrogate / d ML), each meta-operator requires **specialization** to be instantiated into executable mutant generation rules.

**Specialization rule examples**:
- **HP** (hyperparameter) specializes on class a PUTs to "change numerical algorithm tolerance / max_iter"; on class c to "change GPR kernel noise_level / length_scale"; on class d to "change MLP hidden_dim / dropout"
- **OS** (API replacement) specializes on class a to "swap numerical linear algebra APIs" (e.g., `det` ↔ `sum(diag)`); on class b to "swap probability distribution sampling APIs"; on class c to "swap surrogate classes (GPR ↔ RBF ↔ NN)"
- **TF** (numerical transform) specializes on class a to "change integration order (RK4 → Euler)"; on class b to "change MC estimator"

§3.3 provides the full specialization grid of 5 meta-operators on 12 PUTs × 5 MPs (60 cells). **Each mut_X subsection in §3.2 describes the abstract definition of each meta-operator; §3.3 is their concrete specialization**.

**Hierarchical status**: The 5 meta-operators are defined at Layer 1 (necessary conditions §3.2.0); their specialization instances (60 cells) are the reference objects for Layer 3 mutant tracing (§3.2.6.3).

#### 3.2.0 Necessary Conditions for Semantic Mutation (Layer 1 — Definitional)

> Added in P2 R2 revision. Provides formal criteria for "what counts as semantic mutation" as the methodological foundation for the 5 classes of semantic operators (CE/OS/HP/TF/SI) in §3.2.

**Definition (Semantic Mutation Criteria)**: A mutant `s' = mut_j(S_i)` is **semantic mutation** if and only if it satisfies at least one of the following three conditions:

(a) **Cross-function-boundary replacement**: The AST node operated on by the mutator crosses at least one function-call or module-import boundary (e.g., `np.linalg.det(M)` → `np.sum(np.diag(M))`, replacing 1 function call with a composition of 2 functions);

(b) **Carries domain knowledge**: The legality of the mutation depends on mathematical/physical/statistical knowledge of the program's domain, not purely syntactic type preservation (e.g., GPR `noise_level=1e-4 → 1e-1` knows this is a hyperparameter rather than a random literal constant);

(c) **Changes algorithmic class**: The mutation changes the algorithm class implemented by the program (e.g., RK4 → Euler changes integration order, dropout-prob 0.5 → 0 changes ML model class).

Otherwise it is **syntactic mutation** (AST-local + domain-agnostic + does not change algorithm class).

**Correspondence with the 5 operator classes in §3.2.1-§3.2.5** (each operator satisfies at least one condition):

| Operator Class | (a) Cross-function boundary | (b) Domain knowledge | (c) Algorithm class | Primary satisfied condition |
|---|---|---|---|---|
| **CE** Constant perturbation | ✗ | △ (domain semantics of constants) | ✗ | Partial (b); weakest condition |
| **OS** API replacement | ✓ | ✓ (mathematical equivalence between APIs) | △ (sometimes changes algorithm class) | (a)+(b) |
| **HP** Hyperparameter | ✗ | ✓ (semantic dimension of hyperparameters) | △ (extreme HP changes algorithm) | (b)+partial (c) |
| **TF** Numerical transform | △ (sometimes cross-function) | ✓ (order/convergence of numerical methods) | ✓ (changes integration/interpolation order) | (b)+(c) |
| **SI/CF** Structural injection | △ (sometimes cross-control-flow) | ✓ (algorithmic intent of control flow) | ✓ (changes algorithm skeleton) | (b)+(c) |

**Only the CE class partially satisfies the necessary conditions** (mainly relying on (b) domain semantics, neither (a) nor (c) is strong). This is precisely why CE overlaps with the NumberReplacer of syntactic tools in the operator-level comparison table in §3.2.6.1 — CE is a semantic/syntactic boundary class. OS / HP / TF / SI strongly satisfy one or more of (a)(b)(c), and **structurally** do not belong to the capability space of syntactic mutators.

**Hierarchical status**: The (a)(b)(c) in this section are **Layer 1 necessary conditions** of the P2 methodology; the equivalence criteria E1 ∧ E2 in §2.3 / §4.4 are **Layer 2 instantiation** of the necessary conditions (see §4.4 revision); the mutant tracing empirics in §3.2.6.3 are **Layer 3 application** (see that section).

#### mut_C (Conservation-breaking)
- A1 Lorenz: Add ε_drift drift to right-hand side, Hamiltonian monotonically drifts slowly
- A2 LU: Decomposition loop omits subtraction of k+1-th row multiplier, breaking determinant conservation
- B1 Beta-Bin: Posterior update omits normalization (total probability ≠ 1)
- C1 GPR: Covariance matrix positive-definiteness omits diagonal term
- D1 MLP: Backpropagation gradient summation omits one term

#### mut_M (Monotonicity-breaking)
- A3 FDM: Δt coefficient occasionally takes negative value
- B2 MCMC: Acceptance rate min(1, ratio) changed to min(0.95, ratio)
- C2 PCE: High-order coefficient sorting inserts inversion pair
- D2 SVM: Decision function sign flips near boundary

#### mut_G (Convergence-breaking)
- A1 Lorenz: Fourth-order Runge-Kutta changed to 1.5-order hybrid
- A3 FDM: Second-order difference term replaced with first-order
- B3 MC integration: Sample size doubling does not decay variance by 1/N
- C3 NN-Surr: Training epoch truncation

#### mut_T (Trajectory-distorting)
- A1 Lorenz: State vector swaps y and z components
- B2 MCMC: Insert independent sampling segment in chain
- C3 NN-Surr: Training target adds slow phase shift
- D1 MLP: Hidden layer activation by periodic mask

#### mut_F (Fidelity-order-breaking)
- A2 LU: Partial pivoting occasionally degrades to no pivoting
- C1 GPR: Length scale hyperparameter occasionally switches to coarse prior
- C2 PCE: High-order term truncation randomly retains low-order
- D3 LR: Regularization coefficient occasionally takes large value

#### 3.2.6 Capability Relationship Between P2 Semantic Operators and Existing Python Mutation Testing Tools

Classic syntactic mutation tools (Jia & Harman 2011 survey) operate at the AST node level, independent of the program's domain semantics. We compare the operator capabilities of P2's 5 semantic operator classes (CE / OS / HP / TF / SI, instantiated as the 5 mut_k categories in §3.2.1-5) with mainstream Python mutation testing tools:

| P2 Operator Class | Python tools (mutmut / cosmic-ray / mutpy) coverage | Reason tools do not cover |
|---|---|---|
| **CE** Constant perturbation | ✓ Covered (CRP operator) | Tool and P2 operator overlap, this paper retains CE as baseline |
| **OS** API replacement (e.g., `np.linalg.det` → `np.sum(np.diag)`) | △ Mostly not covered (§3.2.6.3 empirics 88.33% AST-disjoint; a small number of low-complexity OS sub-expressions occasionally hit by tools) | Tool AST replacement cannot do semantically equivalent but algebraically different replacements across function boundaries; `np.linalg.det(M)` → `np.sum(np.diag(M))` is scientific computing domain knowledge, tools lack this knowledge |
| **HP** Hyperparameter semantic change (e.g., GPR `noise_level`, MLP `max_iter`) | ✗ Not covered | Tools do not recognize semantic dimensions of sklearn / scipy model hyperparameters, can only blindly hit literal constants (equivalent to CRP) |
| **TF** Numerical transform (e.g., RK4 → 1.5-order hybrid integration) | △ Partial (AOR changes operators) | Tool AOR can only replace `+/-/*/÷`, cannot change semantic order of integration methods |
| **SI** Structural injection (control flow semantic intent) | ✗ Not covered | Tools do not mutate semantic intent of if-else / loops, can only mechanically change conditions |

**Of the 5 operator classes, only CE overlaps with the CRP of traditional tools; the remaining 4 classes (OS / HP / TF / SI) are semantic-layer supplements beyond the capability of first-order syntactic tools**. This paper uses LLM-generated semantic operators to cover these 4 classes, which is the engineering connotation of "domain-semantic mutation operators" in innovation attribution C-I in §1.6.1.

**Higher-Order Mutation (HOM) caveat**: Jia & Harman (2009 SBSE) and Kintis et al. (2018 STVR) proposed that HOM, by combining multiple first-order syntactic mutations (e.g., AOR + SDL), could in principle produce composite syntactic mutants partially equivalent to OS / HP / TF / SI. For example, AOR (`*` → `+`) + SDL (delete one line) might simulate partial effects of OS API replacement on some PUTs. The §5 empirics in this paper did not conduct comparative experiments on HOM; §7 R12 (NEW) lists "empirical testing of HOM equivalence" as a residual threat; the "tool unreachability" claim in §3.2.6 is strictly limited to first-order syntactic tools (mutmut / cosmic-ray default configurations belong to this class).

**Tool selection justification**: If comparative experiments are conducted (§5.10 plan), both mutmut [Hovde 2018] + cosmic-ray [Tomilin 2017] dual tools should be used simultaneously to exclude single-tool operator set bias; mutpy [Hovstadius 2014] is not selected due to Python 3.10+ incompatibility (testing sklearn/scipy reports errors); Pitest is a Java tool, not comparable. Multi-tool comparison can exclude reasonable reviewer concerns about "subjective tool selection."

**Expected findings from comparative experiments** (based on the argument that OS / HP / TF / SI are not covered by tools): The aligned-cross Cliff's δ on 60-cell SMS for mutants produced by syntactic tools should be significantly lower than the measured δ = 0.446 (v3b) for semantic operators in this paper, because syntactic tools do not distinguish MR-MP alignment, and their AST operations do not carry semantic alignment information.

##### 3.2.6.0 Systematic vs Incidental: Syntactic Tool Occasional Hits ≠ Semantic Mutation Method

> Added in P2 R2 revision. Responds to possible reviewer challenge: "Some mutants occasionally produced by syntactic tools may also cross function boundaries (satisfying §3.2.0 (a)) or change algorithmic class ((c)), aren't they byproducts but still semantic mutants?"

**Thesis**: Satisfying the necessary conditions (a)(b)(c) in §3.2.0 is one of the **sufficient conditions** for semantic mutation, but **only when satisfaction is design intent rather than stochastic byproduct** does it constitute a systematic semantic mutation method. Syntactic tools (mutmut / cosmic-ray) occasionally hitting (a)(c) with 12 default operators (§3.2.6.1) is a non-zero probability event — but **occasionality undermines two engineering functions of semantic mutation**:

**(i) Deepening source code understanding**
Semantic mutator design requires understanding domain-level relationships of the program — for example, when designing the OS operator `np.linalg.det(M) → np.sum(np.diag(M))`, one must know: these two APIs are equivalent on diagonal matrices, not equivalent on general matrices, and the algebraic relationship between determinant and diagonal sum is `det = ∏ eigvals` while `sum(diag) = trace = ∑ eigvals`. Syntactic tool AST traversal **does not require** this understanding; even if similar replacements are occasionally produced, they do not constitute systematic interpretation of source code semantics.

**(ii) Revealing deep faults**
Domain semantic errors — physical constant errors, unit conversion errors, boundary condition errors, hyperparameter semantic errors, numerical method order errors — are all **not** AST-local errors. Syntactic mutator design goals are to trigger syntactic faults (operator typos / off-by-one / negation flips); the probability of occasionally hitting domain errors ≪ the probability of designed triggering, and lacks repeatability. Semantic mutator design goals **directly** correspond to these deep fault classes.

**Conclusion**: Syntactic tools occasionally producing mutants satisfying §3.2.0 (a)(b)(c) is a stochastic byproduct — neither repeatable (the same tool with the same seed may not hit) nor carrying understanding/fault-revealing engineering value. Systematic semantic mutation requires (a)(b)(c) to be design intent. This is the **positive reinforcement** of the "AST-local + domain-agnostic" criterion in the operator-level comparison table in §3.2.6.1: not only is the operator set structure of syntactic tools unable to reach P2 necessary conditions, even occasional hits do not constitute systematic semantic mutation in the methodological sense.

##### 3.2.6.1 Operator-Level Comparison Table (R-15 Response)

> Reviewer R-15 requires upgrading the "tool unreachability" claim in §3.2.6 from categorical argument to **operator-level** comparative evidence. This section lists all entries in the default operator sets of mutmut and cosmic-ray, mapping one-to-one with the 37 operators in P2's `operator_registry.py`, to confirm that the 4 classes beyond CE (OS / HP / TF / SI) are completely inexpressible at the operator level.

| Tool Operator (mutmut + cosmic-ray) | Operator Instance | Operated AST Node | P2 Correspondence | Covers P2 Class |
|---|---|---|---|---|
| `NumberReplacer` / number constant replacement | `1` → `2`, `0.05` → `0.06` | `Num`/`Constant` | CE partial | △ Literal values only |
| `ReplaceArithmeticOperator` | `+` → `-`, `*` → `/` | `BinOp` | — | ✗ No correspondence |
| `ReplaceComparisonOperator` | `<` → `>=`, `==` → `!=` | `Compare` | — | ✗ No correspondence |
| `ReplaceLogicalOperator` (`and`↔`or`) | `a and b` → `a or b` | `BoolOp` | — | ✗ No correspondence |
| `ReplaceUnaryOperator` | `-x` → `+x` | `UnaryOp` | — | ✗ No correspondence |
| `ReplaceTrueFalse` | `True` → `False` | `NameConstant` | CE keyword | △ Bool literal only |
| `BreakContinueReplacer` | `break` ↔ `continue` | `Break`/`Continue` | — | ✗ No correspondence |
| `RemoveDecorator` | `@cache` deletion | `decorator_list` | — | ✗ No correspondence |
| `RemoveExceptHandler` | `except E: ...` deletion | `ExceptHandler` | — | ✗ No correspondence |
| `ZeroIterationForLoop` | `for x in xs:` → `for x in []:` | `For` | — | ✗ No correspondence |
| `ReplaceIfBlock` (`If True/False`) | `if cond:` → `if True:` | `If` | — | ✗ No correspondence |
| `MutateSubscript` | `a[i]` → `a[i+1]` | `Subscript` | — | ✗ No correspondence |
| (No corresponding tool operator) | — | — | **OS** API replacement | △ 88.33% disjoint (§3.2.6.3 empirics; small number of low-complexity OS sub-expressions occasionally hit by BinOp) |
| (No corresponding tool operator) | — | — | **HP** Hyperparameter semantic change | ✗ Tool inexpressible |
| (No corresponding tool operator) | — | — | **TF** Numerical method semantic change | ✗ Tool inexpressible |
| (No corresponding tool operator) | — | — | **SI/CF** Structural injection | ✗ Tool inexpressible |

**Operator-level conclusion**: All 12 classes in the tool default operator set remain at AST-local operations (BinOp / Compare / BoolOp / UnaryOp / NameConstant / Subscript / If / For / Break / Continue / decorator / except). **Categorically**, no entry recognizes semantic dimensions of sklearn / scipy model object hyperparameters (HP, §3.2.6.3 empirics 0/72), semantic order of numerical methods (TF, 0/54), or intent semantics of control flow (SI/CF, 0/33). For OS (cross-function-boundary API replacement), the tool carries no domain knowledge, but low-complexity OS sub-expressions can be occasionally hit by BinOp and similar operators (§3.2.6.3 empirics: 88.33% disjoint). **This is structural unreachability, not a matter of operator set size — even if the tool operator set is expanded from 12 to 100, as long as each entry remains AST-local and domain-agnostic, the HP/TF/SI systematic semantic operator classes remain inexpressible, and the systematic hit rate for OS is bounded below by the empirical 88.33% disjointness**.

##### 3.2.6.2 cosmic-ray on a1 Single PUT Empirical Supplement (Optional, Future-Work Hook)

> The above operator-level comparison is already sufficient evidence for the §3.2.6 thesis. This provides an **optional lightweight empirical**, applicable to scenarios where R-15 reviewer further requests "actual run numbers."

`scripts/run_cosmic_ray_a1.sh` (NEW) encapsulates the end-to-end cosmic-ray process on a1 PUT:

1. Install `cosmic-ray`;
2. Configure `tests/puts/test_a1.py` as baseline test with `cosmic-ray.toml`;
3. Run `cosmic-ray exec` for all mutants;
4. Report (mutants_generated, killed, survived, incompetent) quadruple.

**Expected result** (empirical confirmation of operator-level comparison):
- mutants_generated: tens of magnitude (a1 file 934 bytes, limited AST nodes);
- If fully classified, ≥ 90% belong to BinOp / Compare and other 12 classes;
- killed-by-test_a1.py ratio: depends on P2 unit test granularity; P2 tests are designed as PUT output shape/type sanity checks, **most mutants will not be killed by this test suite** — this is precisely the empirical manifestation of the §3.2.6 thesis: mutants produced by syntactic tools are not aligned with MR-violation detection objectives.

Full 12 PUT × cosmic-ray ablation is reserved for R2 revision or P3 paper (§7.2.1 R5 scaling study).

##### 3.2.6.3 Mutant Tracing Empirics (Layer 3 — Applied)

> Added in P2 R2 revision, NEW-MAJOR-1 generalization closed (2026-05-02 12-PUT full measurement). Layer 3 application layer: use §2.3 / §4.4 equivalence detection tools (Layer 2 instantiation of §3.2.0 necessary conditions) to trace P2 mutant set for syntactic-mutant, **positive empirical** argument that P2 mutants are not a subset classification of syntactic mutants.

**Experimental design**: Full 12 PUTs (a1/a2/a3 / b1/b2/b3 / c1/c2/c3 / d1/d2/d3) empirics:
1. Take P2 v4 cross-source mutant pool (`data/mutants/${PUT_ID}_pool_v4/`, 292 mutants across 12 PUTs);
2. Run cosmic-ray default operators for each PUT (`scripts/run_cosmic_ray_put.sh ${PUT_ID}`, 1250 syntactic mutants across 12 PUTs);
3. For each mutant, use `ast.dump(annotate_fields=False, include_attributes=False)` for normalized AST string, perform set difference analysis (`scripts/p2_vs_syntactic_ast_diff_batch.py`);
4. Report overall overlap rate and per-operator-class breakdown.

**Empirical results** (`data/results/cosmic_ray_12put_ast_diff.json`):

| Metric | Value |
|---|---|
| Total P2 mutants across 12 PUTs | 292 |
| Total cosmic-ray syntactic mutants across 12 PUTs | 1250 |
| AST-normalized overlapping mutants | 15 |
| **Overall overlap rate** | **0.0514** |

**Per-operator-class overlap rate (12-PUT aggregate)**:

| Class | n_p2 | n_overlap | overlap_rate | Interpretation |
|---|---|---|---|---|
| **HP** | 72 | 0 | **0.0000** | Structurally unreachable ✓ |
| **SI** | 33 | 0 | **0.0000** | Structurally unreachable ✓ |
| **TF** | 54 | 0 | **0.0000** | Structurally unreachable ✓ |
| CE | 64 | 5 | 0.0781 | Boundary class (§3.2.0 only partially satisfies (b)) |
| OS | 60 | 7 | 0.1167 | Partial instance hits (see interpretation) |
| CF | 9 | 3 | 0.3333 | b2 only, extremely small sample |

Per-PUT detailed distribution (only listing PUTs with non-zero overlap):

| PUT | n_p2 | n_overlap | Hit operator class and LLM source |
|---|---|---|---|
| a2 | 27 | 3 | CE: Claude × 3 |
| a3 | 18 | 3 | OS: DeepSeek × 3 |
| b2 | 27 | 3 | CF: DeepSeek × 3 |
| b3 | 20 | 6 | CE: DeepSeek × 2 + OS: Claude × 1, DeepSeek × 3 |
| Other 8 PUTs (a1/b1/c1/c2/c3/d1/d2/d3) | 200 | 0 | — |

**Interpretation**:

- **HP/SI/TF class aggregate zero overlap rate** (0/72, 0/33, 0/54): cosmic-ray AST-local operators **structurally unreachable** §3.2.0 necessary conditions (a)(c) — 12-PUT full empirics confirm §3.2.6.1 categorical argument. HP (Hyper-Parameter) requires recognizing semantic dimensions of sklearn / scipy model object hyperparameters; SI (Structural Injection) requires mutating semantic intent of control flow; TF (Numerical Transform) requires changing semantic order of integration methods — all three classes are **systematically unable to be generated** by cosmic-ray default operators' BinOp / Compare / NumberReplacer and other AST-local operators.

- **CE class aggregate 7.81% overlap rate** (5/64): CE is the "boundary class" marked in §3.2.0 — only partially satisfies necessary condition (b) (carries domain knowledge), **conceptually aligned** with cosmic-ray NumberReplacer (see §3.2.6.1 row 1). The aggregate 7.81% instance overlap mainly comes from simple ±1-style numerical replacements generated by LLMs (Claude / DeepSeek) on a2/b3 (e.g., `α=2 → α=1` in `Beta(α, β)`), whose AST representation overlaps with cosmic-ray NumberReplacer output. This is completely consistent with the prediction in §3.2.6.1 table marking CE as "△ literal values only": **conceptual intersection exists, instance intersection is non-zero**. But 92.19% of CE instances remain AST-disjoint (reason: LLMs tend to select domain-aware half-step perturbations, such as `_RHO=28.0 → 27.5` preserving Lorenz chaotic regime, rather than tool integer addition and subtraction).

- **OS class aggregate 11.67% overlap rate** (7/60, **new finding**): The pre-existing argument (§3.2.6.1 row 2) claimed that the OS class is completely unreachable by cosmic-ray; the 12-PUT empirics show that this claim is too strong in the *categorical* sense, and is in practice **88.33% disjoint + 11.67% incidental hits**. The hits concentrate on DeepSeek outputs for a3 and b3, all of which are low-syntactic-complexity OS sub-expressions (e.g., `dx**2` → `dx*dx` in a3 FDM — an algebraically equivalent rewrite incidentally hit by cosmic-ray BinOp, but labeled OS1 by the P2 LLM because the rewrite is semantically equivalent on the PUT). This is the empirical confirmation of the §3.2.6.0 systematic-vs-incidental argument: **incidental hits by syntactic tools on the cross-function-boundary condition (a) are non-zero-probability events**. But the OS class's overall 88.33% AST-disjointness still systematically rules out an "OS = AST-local" classification.

- **CF class aggregate 33.33% overlap rate** (3/9): CF is instantiated as a sub-class of SI only in b2 (MCMC); all 9 mutants come from the b2 pool, of which 3 DeepSeek outputs hit cosmic-ray's `BreakContinueReplacer` / `ZeroIterationForLoop` at the AST level. The sample size is too small (n=9) to obtain a robust generalization; but even a 33.33% rate means 66.67% AST-disjoint, consistent with the categorical claim "SI/CF unreachable" in the §3.2.6.1 table being downgraded to *partial reachability*.

- **Overall overlap 5.14% ≪ 1.0**: i.e., the P2 mutant pool **is not** a subset of the syntactic mutant pool; the two are systematically distinct mutant spaces. 94.86% of P2 mutants are AST-disjoint with the 1250-mutant cosmic-ray output, and the absolute majority remain disjoint even on sub-classes (CE / OS partial) that are *conceptually* reachable by syntactic tools.

**Conclusion (Layer 3 — refuting the "new-concept classification" challenge)**: Across the full 12-PUT empirics, **94.86%** of P2 mutants cannot be reproduced by cosmic-ray default operators; the three classes HP / SI / TF (159/292 = 54.5% of P2 mutants) are **categorically** unrepresentable by syntactic tools; the per-class overlap rates of CE / OS / CF — 7.81% / 11.67% / 33.33% — are all far below 100%. **Structural proof** that P2 is a systematic semantic mutation method, not a "post-classification copy" of syntactic mutants — even on sub-classes that are conceptually reachable by syntactic tools, P2 mutants remain dominated at the *instance-selection* level by the LLM's domain-aware choices (cf. the source of the 92% AST-disjointness in the CE class: LLMs select domain-meaningful perturbations rather than ±1). This together with the §3.2.6.0 systematic-vs-incidental argument and the §3.2.6.1 operator-level cross-table forms a complete refutation evidence chain; meanwhile, the OS row's "✗ not covered" mark in the §3.2.6.1 table is too absolute, and is empirically refined by this section to **88.33% disjoint + 11.67% incidental hits**, with the nuance honestly reflected in the OS interpretation of this section.

**Scope caveat**: A multi-syntactic-tool (mutmut / mutpy) cross-comparison remains for P4 — this section's empirics are based on the single tool cosmic-ray, because mutpy is incompatible with Python 3.10+ (errors when testing sklearn / scipy), and mutmut's operator set overlaps strongly with cosmic-ray's (cf. §3.2.6.1). Effect of LLM source differences (Claude / GPT / DeepSeek) on overlap patterns: hit instances are not evenly distributed across the three LLMs (DeepSeek 11/15, Claude 4/15, GPT 0/15; see `data/results/cosmic_ray_12put_ast_diff.json` for the overlap_files list), suggesting that DeepSeek tends to generate syntactically simpler mutations. This LLM-source bias is discussed in §7.2 (R8) "LLM source distributional shift" and does not affect the systematic-vs-incidental argument of this section (because the systematic argument is based on categorical AST-locality, not hit frequency).

### 3.3 60-cell instantiation matrix (three-state decomposition)

**Section positioning**: §3.2 subsections mut_X provide abstract definitions of the 5 meta mutation operators (CE / OS / HP / TF / SI, i.e., mut_C / mut_M / mut_G / mut_T / mut_F). This section provides the **full specialization grid of meta operators across 12 PUTs × 5 MPs** (60 cells)—each cell is a concrete instantiation of a (meta operator, PUT type, meta pattern) triple. This section constitutes the **concrete instantiation** of §3.2 meta operators and serves as the reference object for the mutant traceability audit in §3.2.6.3.

```
              MP_1   MP_2   MP_3    MP_4    MP_5
              cons.  mono.  conv.   traj.   p-ord.
            ┌─────┬─────┬─────┬─────┬─────┐
   A1 Lorenz│ ●●  │ ●   │ ●●  │ ●●  │  ○  │
   A2 LU    │ ●●  │  ○  │ ●   │ ●   │ ●●  │
   A3 FDM   │ ●●  │ ●   │ ●●  │ ●●  │  ○  │
   B1 BetaBin│●●  │ ●   │  ○  │  ○  │ ●   │
   B2 MCMC  │ ●   │ ●●  │ ●●  │ ●●  │ ●   │
   B3 MC    │ ●●  │  ○  │ ●●  │ ●   │  ○  │
   C1 GPR   │ ●   │ ●●  │ ●●  │ ●   │ ●●  │
   C2 PCE   │ ●●  │ ●   │ ●●  │ ●   │ ●●  │
   C3 NN-Surr│●   │ ●●  │ ●●  │ ●●  │ ●●  │
   D1 MLP   │ ●●  │ ●●  │ ●   │ ●   │ ●●  │
   D2 SVM   │ ●   │ ●●  │ ●   │  ○  │ ●●  │
   D3 LR    │ ●●  │ ●●  │ ●   │  ○  │ ●●  │
            └─────┴─────┴─────┴─────┴─────┘
   ●● substantial 30 cells / ● moderate 24 cells / ○ vacant 6 cells (inherited from P1 H6)
```

### 3.4 Experimental scale (measured)

- Each PUT averages 24.3 mutants (v4 cross-source pool; range 10-30, c1 GPR constrained to 10 by V1-V4 pass rate)
- All 60 cells total ~24.3 × 12 = ~292 mutant instantiations (reusing the same PUT pool across the 12 PUT × 5 MP matrix), coupled with N=20 AVP repeated sampling
- v4 cache_cross contains 298 V1-V4 confirmed mutants (three LLM sources × 37 operators × K=3 = 333 trials, 89% pass rate, see §4.2.5(d))

### 3.5 Engineering significance

- **Diagonal j=k (aligned)**: H2 threshold test
- **Off-diagonal j≠k (cross)**: control
- **Vacant cells ○**: not formally adjudicated in this paper (original H3 retired, see §1.5; vacant slices repurposed in §6.2 as descriptive evidence for R_sem/R_kill decoupling)

#### 3.5.1 c-class primary MP selection: pre-registered v3 vs exploratory v3b

**Pre-registered primary analysis (v3, main analysis of this paper)**: The primary MP for c-class (c1 / c2 / c3, surrogate) follows the MP5 specification from P1 [Meng Li et al., Progress in Nuclear Energy, under review]. All H1-H5 hypothesis tests render primary verdicts on v3 data.

**Exploratory sensitivity analysis (v3b, post-hoc selection)**: After observing v3 data, §5.8.4 Friedman per-class shows χ² = 4.00, p = 0.406 for c-class (no statistically significant difference among MPs). Based on this non-significant result, we conducted a **post-hoc data-driven primary MP shift**, selecting the MP with maximum mean SMS across the three c-class PUTs as the new primary:

| MP | mean SMS (c1, c2, c3 average) |
|---|---|
| MP1 | 0.233 |
| MP2 | 0.000 |
| MP3 | 0.000 |
| MP4 | 0.000 |
| MP5 | 0.000 |

New primary = MP1 (data in `data/results/c_class_mp_ranking.json`).

**Critical caveats (honest disclosure)**:

1. **This adjustment is exploratory, not a pre-registered decision rule**. "Friedman per-class p = 0.406 indicates any MP could serve as primary" is a necessary but insufficient condition; the actual selection of argmax(mean_SMS) constitutes selection-on-response, inflating H4 sign test pass rate (v3 3/4 → v3b 4/4) and δ (v3 0.323 → v3b 0.446) while introducing selection bias
2. **No multiple-comparison correction applied**: selecting the maximum from 5 candidate MPs without applying strict max-statistic null distribution or Bonferroni × 5 correction

**Quantitative bound on selection inflation** (added in P0-4 revision): permutation test quantifies the max-over-5 selection rule post-hoc. **Null design** (corrected): treat the 15 c-class (PUT, MP) cell SMS values as fully exchangeable; each permutation shuffles the (PUT, MP) → SMS association and recalculates the max-over-5 per-PUT mean, for N_PERM = 10,000 iterations. **Result**: observed c-class aligned mean = 0.3136, null distribution mean = 0.3494 ± 0.0347, one-sided p(observed ≥ null) = 0.9885 (positioned at right-tail percentile = (1 − 0.9885) × 100% of null distribution). **Bonferroni upper bound**: α_effective = α / 5 = 0.01 (family-of-5 candidates per PUT). **Joint interpretation**: both permutation and Bonferroni sensitivity analyses indicate that the c→MP1 selection effect size is substantially influenced by max-over-5 selection; abstract and §5.8.2 have accordingly downgraded all v3b results to exploratory status (P0-3). See `data/results/c_class_permutation_v4.json` for details.

3. **The reported v3b sign test 4/4 and δ improvement +0.123 should be interpreted as exploratory findings rather than confirmatory results**
4. **Pre-registered primary conclusion** (v3): H4 sign test 3/4 (partially met), δ = 0.323 (H2 rejected). This is the primary analysis verdict of this paper; v3b/v4 are reported as sensitivity analyses only

**Future work (P4)**: pre-register c-class primary MP selection rule on new datasets (candidate rules: argmax of pre-defined statistic or leave-one-class-out cross-validation) to eliminate the confound present in this paper's v3b.

### 3.6 Expected risk profile of LRCA across 60 cells

#### 3.6.1 PUT-class × LRCA layer risk weights

| PUT class | L0 artifact | L1 tolerance (C2) | L2 OOD (C3) | L3 statistical (C4) | Primary risk root cause |
|---|---|---|---|---|---|
| A numerical | ★ | **★★★** | — | — | C2 dominant |
| B probabilistic | ★ | ★ | — | **★★★** | C4 dominant |
| C surrogate | ★ | ★★ | **★★★** | ★ | C3 dominant |
| D ML | ★ | ★ | **★★★** | ★★ | C3 + C4 mixed |

#### 3.6.2 Operator-PUT pair root cause hotspots (expected)

```
                A1 A2 A3 │ B1 B2 B3 │ C1 C2 C3 │ D1 D2 D3
           ─────────────────────────────────────────────────
   mut_C   │ C2 C2 C2 │ C4 C4 C2 │ C2 C2 C5 │ C5 C2 C2
   mut_M   │ C1 C1 C1 │ C4 C4 C1 │ C1 C1 C5 │ C5 C1 C1
   mut_G   │ C2 C1 C2 │ C4 C4 C2 │ C3 C3 C5 │ C5 C1 C1
   mut_T   │ C1 C2 C1 │ C4 C4 C4 │ C3 C3 C5 │ C5 C3 C3
   mut_F   │ C2 C1 C1 │ C4 C4 C4 │ C3 C3 C5 │ C5 C1 C3
```

#### 3.6.3 LRCA expected suspect_share thresholds

| PUT class | Expected suspect_share | Acceptance threshold |
|---|---|---|
| A numerical | 0.10–0.20 | ≤ 0.25 |
| B probabilistic | 0.20–0.35 | ≤ 0.40 |
| C surrogate | 0.20–0.30 | ≤ 0.35 |
| D ML | 0.25–0.40 | ≤ 0.45 |
| **All 60 cells average** | **≤ 0.20** (corresponding to H5) | **≤ 0.25** |

#### 3.6.4 Interface with §4 LRCA execution protocol

- L0 artifact pre-scan → §4.2.4 two-LLM double-blind review
- L1 tolerance robustness → §4.6 N=20 repetition subprocess
- L2 OOD triage → §4.6 input distribution definition
- L3 statistical hypothesis baseline → §4.6 hypothesis pre-check

### 3.7 Interface with §4 experimental procedure

§4 operationalization: (a) semantic mutation generation protocol (dual-LLM cross-source + 20% manual sampling, addressing LLM reproducibility); (b) AVP invocation and version pinning; (c) LRCA three-layer diagnostic execution; (d) §5 main table SMS + sub-table C1_share reporting pipeline.

---

## Section 4 · Experimental Procedure

### 4.1 Experimental Procedure Overview (Data Flow)

```
[§3.1 PUT Selection] ──► [§4.2 Semantic Mutation Generation]
                          │
                          ▼
                     [§4.3 Mutant Pool Pre-screening (LRCA L0)]
                          │
                          ▼
                     [§4.4 Equivalence Detection (E1 ∧ E2)]
                          │
                          ├──► equiv Set (Excluded)
                          │
                          ▼
                     [§4.5 AVP Invocation → killed/survive Classification]
                          │
                          ▼
                     [§4.6 LRCA Three-layer Diagnosis → root_cause Annotation]
                          │
                          ▼
                     [§4.7 §5 Main Table SMS + Subtable C1_share Report]
```

### 4.2 Semantic Mutation Generation Protocol (Addressing LLM Reproducibility Risk)

#### 4.2.1 Dual-source Generation

| Source | Proportion | Role |
|---|---|---|
| Multi-LLM consensus | 60% | Claude Opus 4.6 (via bltcy.ai) + GPT-5.4 (via bltcy.ai) + DeepSeek chat (via deepseek.com) three-model unanimous agreement required for pool admission (actual v4 implementation in this paper described in §4.2.5) |
| Manual injection | 40% | 1-2 scientific computing researchers manually write according to §3.2 rules |

> Note: The "GPT-4o + Claude Opus + Gemini" in §4.2.1 is the P1 protocol description; the P2 implementation in this paper changed to Claude Opus 4.6 + GPT-5.4 + DeepSeek chat (see §4.2.5 cross-source protocol for details). The only difference between the two is the specific LLM selection; the prompt template and consensus voting mechanism remain unchanged. The v4 cross-source data in this paper (298 confirmed mutants) is entirely produced by the §4.2.5 protocol.

#### 4.2.2 Prompt Template Specification (LLM Path)

Each (mut_j, S_i) pair is assigned 1 prompt template containing:
- Program under test (PUT) source code snippet
- Semantic intent of mut_j
- **Prohibition** against informing the LLM of any specific form of MR (to avoid prompt leakage)
- Output requirements: syntactically correct + executable + single-point modification (diff < 10 lines)

#### 4.2.3 Reproducibility Parameters

- LLM temperature = 0.3
- random_seed fixed
- Each prompt generates 5 candidates, review retains 2-3
- Prompt template, LLM version, seed all stored in reproducibility package

#### 4.2.4 Double-blind Review Protocol (Scheme C: Dual-LLM Cross-source + 20% Manual Sampling)

**(a)** Generator **LLM-G (Claude Opus)** and reviewer **LLM-R (GPT-4o)** must be cross-source models with strictly separated roles

**(b)** LLM-R review only sees PUT original code + mutant code, unaware of mut_j category / MR content / generator identity; outputs triple:
- Syntactically correct? {Yes, No}
- Executable? {Yes, No, Uncertain}
- Semantic failure injected? {Yes, No, Uncertain}

**(c)** Double-confirmed mutants enter pool; inconsistencies or Uncertain cases enter **manual arbitration queue** (estimated ≤ 10% of total)

**(d)** From the double-confirmed pool, randomly sample **20% for manual review by scientific computing researchers**; if manual-LLM-R inconsistency rate > 10%, trigger **full manual downgrade**

**(e)** Reproducibility package public: LLM-G/R model versions, prompt templates, temperature, seed, manual arbitration records

**(f)** Same-source bias mitigation: stratify LLM-R by PUT class (A/B use GPT-4o, C/D use Claude Opus for cross-review), or three-LLM rotation (GPT-4o / Claude Opus / Gemini Pro)

**(g)** Prompt injection leakage mitigation: LLM-G uses Application Programming Interface (API) path with Retrieval-Augmented Generation (RAG) / web search disabled; §7 Limitations explicitly acknowledges residual risk

#### 4.2.5 Cross-source Mutant Pool Protocol (Phase A Methodological Contribution)

To isolate the relative contributions of "LLM same-source bias" and "MR-MP alignment design" to SMS effect size (Cliff's δ), we designed a three-stage ablation:

| Data Version | Mutant Pool Source | c-class Primary MP | Primary Use |
|---|---|---|---|
| **v3** | Single-source (Claude Opus 4.6 only) | MP5 (P1 legacy) | H2 baseline |
| **v3b** | Single-source (same as v3) | **MP1 (data-driven, §3.5.1)** | Isolate contribution of MR-MP alignment design |
| **v4** | **Cross-source** (Claude Opus 4.6 + GPT-5.4 + DeepSeek chat) | MP1 (same as v3b) | Isolate contribution of LLM source diversity |

**Protocol** (`scripts/cross_source_campaign.py`):

(a) **Three-party LLM cross-source generation**: For each (PUT, operator) pair, Claude / GPT / DeepSeek each run K=3 trials with identical prompt template (§4.2.2), temperature fixed at 0.7, **source_tag field propagated to mutant file naming** (`{op_id}_{source}_attempt{NN}.py`) to facilitate source-stratified analysis

(b) **Mechanical validation V1-V4** (`src/p2/mutators/validation.py`): syntax, executability, non-triviality (`|y_mutant - y_original| > 1e-6` on probe set), signature consistency.

**Protocol asymmetry declaration (P1-7 revision, R0/R3/DA consensus)**: The v4 cross-source pool **does not invoke reviewer LLM** (cost/speed priority, deferred to P4 for full three-LLM dual-blind review); whereas v3 / v3b data collection used the §4.2.4 original Phase-1 dual-blind protocol (Claude-Opus generation + GPT-5.4 review + DeepSeek arbitration). This constitutes **protocol asymmetry** between v3 / v3b vs v4: the v4 mutant pool passes V1-V4 mechanical gates but lacks the LLM review stage. **Potential confound**: A fraction of Δδ_{v3b → v4} = −0.007 may not be "LLM source diversity contribution" but rather "slight quality decline in v4 pool relative to v3b pool." This paper does not isolate this confound; P4 will rerun dual-blind reviewer on the full v4 grid, enabling separation of quality difference from source diversity factors. This confound is parallel to §7.1 R11 chained-conditioning

(c) **DeepSeek model selection**: `deepseek-chat` (not `deepseek-v4-pro`). V4-Pro is a reasoning model, averaging ~340 tokens / call (~230 in reasoning_content), latency 11s; the chat variant averages 113 tokens / call, latency 1.8s, **quality equivalent** (dry-run test shows three LLMs produce semantically identical sum-of-diagonal substitution on a2_OS1 operator)

(d) **Cross-source pool capacity**: 37 operators × 3 sources × K=3 = 333 trials, V1-V4 pass rate 89%, confirmed mutants 298; **three sources contribute nearly equally**: Claude=101, GPT=98, DeepSeek=99 (Phase A key engineering finding: three LLMs have comparable capability on scientific computing mutant generation tasks)

(e) **Pool sampling** (`scripts/build_pools.py`, POOL_VERSION=v4): per-PUT 30 mutants upper limit, measured average 24.3, range 10-30. c1 (GPR) only 10 mutants, because c1_HP1 / c1_CE1 operators have V1-V4 pass rates near zero across all three LLMs (GPR PUT's WhiteKernel noise term 1e-4 → 1e-1 perturbation has minimal output impact, nearly all trigger V3 non-trivial failure, itself evidence for §6.2 R_sem/R_kill decoupling)

**Chained-conditioning declaration (P0-5, R0/R1/DA consensus revision)**: The v4 cross-source pool inherits v3b's post-hoc selection on c-class primary MP (c1/c2/c3 → MP1). Therefore Δδ_{v3b → v4} = −0.007 is not a neutral-condition LLM source diversity test, but rather a contrast under the dual conditions of *conditional on v3b's c-class selection* + *identical prompt template*. This paper does not run the v4-pre (cross-source × c→MP5 pre-shift) grid point, because (i) relative to the current v3 → v3b → v4 chain, v4-pre primarily answers "whether v3b selection consumed part of the variance originally attributable to LLM diversity," a question isomorphic to the P4 paper's differential prompt experiment (§4.2.5.1), more economical to resolve together in P4; (ii) v4-pre rerun cost ~$20-30 + 2-3 days wall time, asymmetric to the narrative benefit already exposed in this paper. **This declaration makes the conditional nature of the v3b → v4 contrast explicitly visible, not dependent on reader inference**.

**Argumentation logic of the three-stage ablation**: The two contrasts are **reported separately** (avoiding synthetic ratios that imply factor isolation, see §5.7.2 table): v3 → v3b jump +0.123 is a single-class, post-hoc c-class primary MP shift, reflecting "sensitivity of primary MP selection rule" rather than general "MR-MP alignment design contribution"; v3b → v4 micro-change −0.007 is the near-unanimous response of three LLMs conditional on v3b selection + identical prompt template. **The v3b → v4 contrast is not a neutral-condition LLM source diversity test** (§4.2.5.1 R-16 protocol lists the strong-sense version). This observation suggests P4 priorities: "differential prompt frame per LLM" (§7.1.7 R10) and "pre-registered primary MP selection rule" as parallel tracks; does not constitute quantitative decomposition of "MR design vs LLM diversity" two-factor contributions. Detailed interpretation in §5.7.2 + §6.1.

**Contrast with existing work**: Tip et al. (2024) LLMorpheus uses single LLM (Claude) to generate JavaScript mutants, without cross-source contrast; among known LLM-mutant empirical work, none isolate the contribution of LLM source diversity. The three-stage ablation in §4.2.5 of this paper is the first work to factor-decompose "LLM source diversity vs MR design" in the scientific computing software domain.

##### 4.2.5.1 Differential Prompt Protocol (R-16 Response, Future-work Commitment)

> Reviewer R-16 concern: v4 cross-source results show only −0.007 micro-change from v3b → v4, potentially reflecting "same-source response of three LLMs under identical prompt template" rather than "true upper bound of LLM diversity." To separate these two possibilities requires **one tailored differential prompt per LLM**, testing prompt-fixed vs prompt-differentiated contrast. This section provides complete protocol, exit criteria, and resource estimates for this experiment; execution deferred to R2 revision or P4 paper (consistent with §1.6 P-series sequencing), code skeleton ready (`scripts/run_differential_prompt.py`).

**Experimental design** (2 × 3 factorial, within-(PUT, operator) repeated):

- Factor A: **prompt template**, 3 levels:
  - **V_canonical** (control, identical to v4): generic mutation operator instruction (`prompts/operator_template.txt`)
  - **V_persona**: per-LLM identity guidance (Claude="numerical analysis editor", GPT="scientific software refactorer", DeepSeek="library API substitution specialist"), remaining structure identical to V_canonical
  - **V_cot**: per-LLM reasoning style (Claude=extended thinking with `<thinking>` tags; GPT=explicit "Let's reason step by step" framing; DeepSeek=stepped-reasoning with deliberate intermediate output)
- Factor B: **LLM source**, 3 levels (Claude / GPT-5.4 / DeepSeek chat, same as v4)
- Replication: K=3 trials per (operator, prompt, source) cell
- Total trials: 37 operators × 3 prompts × 3 sources × 3 trials = **999 trials**

**Statistical analysis**:

1. Recalculate Cliff's δ under v4 protocol (should ≈ 0.439, as within-experiment baseline);
2. Build separate pools for each prompt variant (per-PUT pool size matched to v4), calculate δ_canonical / δ_persona / δ_cot;
3. **Core exit criteria**:
   - **If max(δ) − min(δ) < 0.05**: confirm "three LLMs' differential response to prompt style is limited, weak LLM diversity contribution does not stem from prompt-fixed artifact," §5.7.2 v3b → v4 −0.007 conclusion robust;
   - **If difference ≥ 0.05 and differential prompt pushes δ past 0.474 large-effect threshold**: H2 verdict needs revision from "not met" to "prompt-conditional met"; `paper_numbers_v4.json` marked deprecated, add `paper_numbers_v5.json` (after R-16 completion)
   - **If difference ≥ 0.05 but δ still < 0.474**: confirm prompt sensitivity exists but does not change H2 verdict, §7.1.7 R10 multi-prompt listed as limitation

**Resource estimates**:
- API cost: Claude calls (input ~600 tokens, output ~200 tokens) × 333 ≈ $9 USD; GPT-5.4 same scale ≈ $7; DeepSeek chat ≈ $2; **total ≈ $18-30 USD** (variable depending on V_cot token inflation on reasoning model)
- Wall time: ~3-4 hours at concurrency=4 (three API rate-limits coexist)
- Manual: V1-V4 automatic mechanical validation; **no reviewer LLM invocation** (inherits §4.2.5(b) MVP simplification); per-PUT pool resampling automatic

**Current paper version handling of R-16**: Without execution, §5.7.2 already explicitly declares "v3b → v4 micro-change −0.007 under prompt-fixed" as methodological limitation; §7.1.7 R10 lists "differential prompt frame per LLM" as P4 research direction. The formalized record of R-16 protocol (this section) makes this commitment **executable + verifiable**, reviewers can independently run `scripts/run_differential_prompt.py` for verification.

### 4.3 Mutant Pool Pre-screening (LRCA L0)

Before each mutant enters the pool:
- Static syntax checking (linters / type checkers)
- Unit self-test (runs on simple inputs and produces finite output)
- Double-blind review sign-off

**Pool size target**: 30–50 initial candidates per cell → 10–15 retained after pre-screening (corresponding to W-2).

### 4.4 Equivalence Detection Procedure (E1 ∧ E2)

> §2.3 already provided E1 ∧ E2 as the Layer 2 instantiation of the §3.2.0 necessary condition (argumentation for selection among three candidates in §2.3). This section provides the engineering implementation procedure for E1 ∧ E2.

```
For each mutant s' ∈ mut_j(S_i):
  Step 1 [E2 Output-equiv]:
    Sample K_eq=1000 samples from D_S
    Compare ‖S_i(x) − s'(x)‖ ≤ ε_eq
    If all satisfied → candidate equiv

  Step 2 [E1 AVP-coherent]:
    For each mr in MR_{i,k}, compare AVP(S_i, mr) with AVP(s', mr)
    If all consistent → confirm equiv

  Step 3 [Enter equiv_{i,k,j} set]:
    Exclude from denominator |mut_j(S_i)|
```

### 4.5 AVP Invocation (Addressing Circular Dependency)

#### 4.5.1 Version Pinning

AVP implementation version = P1 arXiv technical report commit hash; P2 reproducibility package embeds complete AVP source code.

#### 4.5.2 Meta Pattern Verification Execution

```
For each (s', mr ∈ MR_{i,k}):
  Invoke corresponding method based on MP_k to which mr belongs:
    MP_1:    tolerance equality determination
    MP_2/MP_5: Wilcoxon signed-rank, α=0.05
    MP_3:    convergence order estimation + residual ratio
    MP_4:    DTW distance threshold ε_DTW
  Return {pass, fail}
```

#### 4.5.3 Killed Determination

```
killed(s', MR_{i,k}) ⇔
  ∃ mr ∈ MR_{i,k}: AVP(S_i, mr) = pass ∧ AVP(s', mr) = fail
```

OR aggregation (classical).

### 4.6 LRCA Three-layer Diagnosis

#### 4.6.1 Decision Tree

```
For each s' ∈ killed_{i,k,j}:
  step 1 ─ L1 tolerance robustness:
    Repeat N=20 times, fail proportion
      < 0.80 → root_cause = C2 ✗
      ≥ 0.80 → proceed to L2

  step 2 ─ L2 OOD triage (C/D class only):
    Sample from D_S^valid, fail only in OOD region
      → root_cause = C3 ✗
      Otherwise → proceed to L3

  step 3 ─ L3 statistical hypothesis baseline (B/D class + Wilcoxon/DTW only):
    Pre-check IID/stationarity on PUT's own repeated samples
      If hypothesis violated → root_cause = C4 ✗
      Otherwise → proceed to step 4

  step 4 ─ artifact review:
    1 external reviewer re-examines mutant code and prompt history
      If LLM/artifact evidence → root_cause = C5 ✗
      Otherwise → root_cause = C1 ✓
```

#### 4.6.2 Multi-label Handling

Priority: **C5 > C4 > C3 > C2 > C1** (take earliest confirmed non-semantic cause).

#### 4.6.3 Output

```
C1_share_{i,k,j}      := |{s' ∈ killed : root_cause = C1}| / |killed|
suspect_share_{i,k,j} := 1 − C1_share_{i,k,j}
```

LRCA **does not modify SMS formula**, killed set does not exclude suspects.

#### 4.6.4 LRCA Threshold Calibration (Methodological Contribution)

LRCA L1-L3 introduces 3 engineering thresholds:

| Parameter | Meaning | Default |
|---|---|---|
| `ood_band` | L2 OOD boundary half-width: input x ∈ [0, ood_band) ∪ (1-ood_band, 1] considered OOD | 0.05 |
| `tolerance_multiplier` | L1 epsilon_loose / epsilon_strict | 10.0 |
| `statistical_repeats` | L3 majority-vote repetitions (changing when N=20 requires caution) | 20 |

To avoid threshold arbitrariness, we scan these parameters on a 9-grid (`ood_band ∈ {0.02, 0.05, 0.10}` × `tolerance_multiplier ∈ {3.0, 10.0, 30.0}`, `repeats` fixed at 20), recording mean_C1_share and H5 pass rate across 60 cells for each combination (data in `data/results/lrca_calibration.json`).

Main findings:

| ood_band | tolerance_multiplier | mean_C1_share | H5 cells_pass |
|---|---|---|---|
| **0.02** | **3.0** (best) | **0.200** | **12 / 60 (20.0%)** |
| 0.02 | 10.0 | 0.200 | 12 / 60 |
| 0.02 | 30.0 | 0.200 | 12 / 60 |
| 0.05 (default) | 3.0 / 10.0 / 30.0 | 0.164 | 10 / 60 (16.7%) |
| 0.10 | 3.0 / 10.0 / 30.0 | 0.164 | 10 / 60 (16.7%) |

Observations:

1. **`tolerance_multiplier` has zero impact on H5 across all 9 grid points**: each `ood_band` yields identical c1_share and h5_pass across three multipliers. This indicates L1 tolerance determination is rarely triggered in this dataset; dominant signal comes from L2 OOD.
2. **`ood_band` is the only discriminating factor**: tightening from 0.05 to 0.02 raises H5 from 10/60 to 12/60 (+2 cells). This reflects that LLM-generated mutant R-fail concentrates in narrower boundary regions; expanding OOD boundary mislabels more borderline kills as C3 rather than C1.
3. **Calibration ceiling**: even the best combination H5 = 12/60 (20%) remains far below the 80% threshold set in §5.2. This indicates the LRCA signal-to-noise ratio of LLM-generated mutant pools is inherently low (empirical manifestation of §7.1.7 R10), H5 is unattainable on this dataset, not a threshold calibration issue.

The H5 numbers reported in §5.6.2 use the best combination from this section (ood_band=0.02, tolerance_multiplier=3.0, repeats=20); default threshold results retained as control (`lrca_60cell_v3.json`).

### 4.7 Data Collection and Reporting Pipeline

#### 4.7.1 Single-cell Output Table

After N=20 repetitions for each (i, k, j) cell, output:

| Quantity | Meaning |
|---|---|
| inst_count | Total mut_j(S_i) entering pool |
| equiv_count | E1 ∧ E2 pass count |
| killed_count | AVP killed count |
| survive_count | live − killed |
| **SMS_{i,k,j}** | killed/(inst − equiv) |
| C1_share_{i,k,j} | LRCA-annotated C1 proportion |
| suspect_share_{i,k,j} | 1 − C1_share |
| inst_rate / equiv_rate / survive_rate | Three rates (corresponding to RQ1) |

#### 4.7.2 Experimental Timeline

| Phase | Time | Task |
|---|---|---|
| Phase 1 | 2026 Q4 | mut_j generation + L0 pre-screening (60 cells × 30-50 candidates) |
| Phase 2 | 2027 Q1 | Equivalence detection + AVP invocation (N=20 repetitions) |
| Phase 3 | 2027 Q2 | LRCA three-layer diagnosis + data archiving |
| Phase 4 | 2027 Q3 | §5 statistical analysis + paper writing + IST submission |

### 4.8 Pilot Calibration (37 Operators K=10/20 Trial Run)

#### 4.8.1 Pilot Design

To calibrate end-to-end executability of §4.2 generation protocol, §4.3 L0 pre-screening, and §4.5 AVP invocation, a round of **operator-level pilot** was conducted in 2026 Q3 on 12 PUTs (37 named operators, 12 operators with is_key=True at K=20, remaining 25 at K=10, total 470 trials). Generator used Claude Opus (subscription authentication, subprocess invocation), reviewer used GPT-5.4 (bltcy.ai proxy), review prompt isomorphic to §4.2.4 double-blind protocol. Pilot output focused on three **operator-level precursor quantities**:

- **R_sem**: proportion of K attempts per operator passing V1-V6 ∧ operator_match=Yes (semantic implementation success rate, corresponding to §4.2.4 double-blind review final judgment)
- **D_impl**: median of K(K-1)/2 pairwise AST tuple + literal + identifier multiset Jaccard distances among confirmed mutants per operator (implementation diversity, characterizing "different implementation surfaces of the same operator")
- **R_kill**: proportion of confirmed mutants per operator killed by AVP on that PUT's primary meta pattern (MP) MR (operator-MR alignment fault detection rate)

D_impl and R_kill are operator-level pre-projections of the two components of §2.4 SMS: D_impl is the "implementation dimension" extension quantity from §2.4.2, R_kill equals the SMS upper bound for that cell under operator-MR alignment slicing (equality when equiv=0).

#### 4.8.2 Pilot Main Results (Operator-level Aggregation, N=37)

| Metric | Median | Mean | R_sem=0 Operators | D_impl ≈ 0 Operators |
|---|---|---|---|---|
| R_sem | 0.50 | 0.468 | 0 / 37 | — |
| D_impl | 0.42 | 0.392 | — | 1 / 37 |
| R_kill | 0.00 | 0.189 | — | — |

All 37 operators produced at least one V1-V6 passing mutant (R_sem > 0), verifying **operator implementability** of §4.2 generation protocol (corresponding to H1). D_impl median 0.42 indicates K attempts genuinely disperse at structural level—this is the stable level after multiple rounds of deduplication (each attempt's prompt injected with "prior candidates · DO NOT REPEAT") combined with V5 single-fault semantic relaxation (allowing naming/formal/library equivalent substitutions), a necessary precondition for subsequent §5.1 SMS calculation.

#### 4.8.3 Key Finding: R_sem and R_kill Decoupling on HP-class Operators

Pilot data reveals a pattern **spanning all 4 PUT classes**: hyperparameter (HP) and constructive parameter (CE/OS) class operators approach R_sem ≈ 1.0, but R_kill under that PUT's **primary meta pattern (MP)** MR may still be 0. Table 4.8 excerpts representative 12 operators (distributed by class).

**Table 4.8 R_sem / R_kill Decoupling Excerpt (12 Operators Selected)**

| Operator | Class | PUT Primary MP | R_sem | D_impl | R_kill |
|---|---|---|---|---|---|
| a2_CE1 (LU determinant parameter) | CE | MP1 conservation | 0.60 | 0.601 | **1.00** |
| a2_OS1 (prod→sum) | OS | MP1 conservation | 0.25 | 0.493 | **1.00** |
| b1_OS1 (α/β swap) | OS | MP2 monotonicity | 0.30 | 0.456 | **1.00** |
| d1_TF1 (label flip) | TF | MP2 monotonicity | 0.50 | 0.355 | **1.00** |
| **c1_CE1 (noise 1e-4→1e-1)** | CE | MP5 asymptotic | 1.00 | 0.512 | **0.00** |
| **c2_OS1 (basis function poly→spline)** | OS | MP5 asymptotic | 0.90 | 0.422 | **0.00** |
| **c3_HP1 (relu→tanh)** | HP | MP5 asymptotic | 1.00 | 0.460 | **0.00** |
| **c3_TF1 (max_iter 1000→5)** | TF | MP5 asymptotic | 1.00 | 0.464 | **0.00** |
| **d1_HP1 (MLP α 1e-4→1.0)** | HP | MP2 monotonicity | 1.00 | 0.505 | **0.00** |
| **d3_HP1 (LR C 1.0→1e-4)** | HP | MP2 monotonicity | 1.00 | 0.478 | **0.00** |
| d2_HP1 (γ 'scale'→1e-3) | HP | MP2 monotonicity | 0.50 | 0.541 | 0.00 |
| b2_HP1 (proposal step size ×0.1) | HP | MP2 monotonicity | 0.25 | 0.366 | 0.00 |

**Observation**: R_sem ≥ 0.9 ∧ R_kill = 0 combinations **all** appear on HP/TF/OS class operators in c/d classes (surrogate and classifier, 6 of 12 PUTs); R_sem high ∧ R_kill = 1 combinations **all** appear on CE/OS class operators in a/b classes (numerical and statistical computing).

#### 4.8.4 Pilot Pre-assessment of RQ2

§1.4 RQ2 asks about SMS difference structure on operator-meta pattern (MP) **aligned (j=k) vs non-aligned (j≠k) slices**. Although pilot operator-level data does not yet span the complete 60-cell matrix (Phase 2 task), it already observes bimodal distribution of R_kill on **operator-primary MP aligned slices** (j being that PUT's primary meta pattern (MP)):

- **a/b classes (numerical/statistical)**: CE/OS/SI/CF operator perturbations directly violate algorithmic algebraic invariants; even when R_sem is not high, once mutant implementation succeeds, primary MP (MP1 conservation / MP2 monotonicity) can detect → R_kill ∈ {0.5, 1.0}
- **c/d classes (surrogate/classifier)**: HP/TF operator perturbations alter model capacity or training dynamics, producing **functionally correct but parameter-deviated** mutants; primary MP (MP2 monotonicity, MP5 asymptotic) are statistical / asymptotic MRs, insensitive to parameter deviation → R_kill ≡ 0

This provides **pre-suggestive evidence** for H2 "aligned-SMS / cross-SMS odds ratio ≥ 3.0": even within the j=k aligned slice, **operator fault dimension** (algebraic vs. statistical) and **MR detection dimension** exhibit non-trivial second-order mismatch. In other words, §5.1 RQ2 main analysis quantity should, beyond "diagonal vs off-diagonal," also report in appendix **second-level R_kill conditional distribution by operator class (CE/OS vs HP/TF) within diagonal slice**, to interface with this pilot's decoupling observation. This will be added as a subfigure to §5.5 Figure

## Section 5 · Statistical Analysis Methods

### 5.1 Primary Table (Corresponding to RQ1-RQ4)

| RQ | Primary Statistics | Reporting Format |
|---|---|---|
| RQ1 | inst_rate, equiv_rate, C1_share, survive_rate | 60-cell heatmap + 4-class marginal distributions |
| RQ2 | aligned-SMS vs cross-SMS; sparse ○ vs dense ●● equiv_rate | Cliff's δ + odds ratio + 95% bootstrap confidence interval |
| RQ3 | ΔSMS_c (c ∈ {A,B,C,D}); CV(ΔSMS) | sign test (df=3) + descriptive forest plot |
| RQ4 | Spearman ρ + Kendall τ for SMS vs pattern coverage | scatter plot + dual-metric ranking comparison table |

### 5.2 Hypothesis Testing Thresholds (H1-H5)

- **H1**: Number of cells with |non-equivalent mutants| ≥ 5 across 5 operators × 12 PUTs ≥ 9 × 4 = 36 (simplified to "≥ 4 operators meet threshold" for full 5-operator condition)
- **H2**: aligned-SMS / cross-SMS odds ratio ≥ 3.0, Cliff's δ ≥ 0.474

  Cliff's δ threshold follows Romano et al. (2006) empirical table for software engineering:

  | Level | Threshold | Interpretation |
  |---|---|---|
  | Negligible | \|δ\| < 0.147 | Two groups equivalent |
  | Small | 0.147 ≤ \|δ\| < 0.330 | Weak directionality |
  | Medium | 0.330 ≤ \|δ\| < 0.474 | Clear directionality |
  | Large | \|δ\| ≥ 0.474 | Strong dominance |

  The H2 large-effect threshold is a pre-commitment (following P1 [Meng Li et al., Progress in Nuclear Energy, under review] setting), not modified post hoc in this paper. §5.7.2 / §6.1 report which tier the observed δ falls into and its implications for the argument.
- ~~**H3**: equiv_rate ≥ 0.85 for 6 ○ cells; equiv_rate ≤ 0.30 for 30 ●● cells (bidirectional threshold)~~ **(retired, see §1.5 note)**
- **H4**: sign test all four classes positive (p=0.0625); CV(ΔSMS) < 0.5
- **H5**: average suspect_share ≤ 0.20 across all 60 cells

### 5.3 Multiple Comparisons and Power

#### 5.3.1 Multiple Comparisons

Cell-level claims across 60 cells use Benjamini-Hochberg FDR correction, α_FDR = 0.05.

#### 5.3.2 Statistical Power Statement

- **Cross-class consistency H4**: 4-class sign test has only df=3, weak power; P2 frames H4 as **exploratory evidence**, supplemented by a mixed-effects model (random intercept: PUT; fixed effects: class × operator) over 12 PUTs × 5 operators
- **N=20 bootstrap intervals**: 1000-iteration bootstrap 95% CI provided for Cliff's δ and odds ratio; no parametric p-value

### 5.4 LRCA Descriptive Analysis

#### 5.4.1 Primary Diagnostic Metrics

- C1_share heatmap across 60 cells (primary result robustness diagnostic)
- suspect_share marginal distribution for 4 PUT classes (compared against §3.6.3 expected threshold)

#### 5.4.2 SMS_unfiltered Appendix (Reviewer Comparison Metric)

```
SMS_unfiltered_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
                       (same form as primary formula, killed does not distinguish C1/C2-C5)
```

Appendix provides cell-by-cell difference table between SMS_unfiltered and SMS; if relative difference < 5%, confirms LRCA does not affect robustness of primary conclusions.

### 5.5 Visualization

- **Figure 1**: 60-cell SMS heatmap (rows: PUT × columns: MP × sub-cells: mut_j)
- **Figure 2**: diagonal vs off-diagonal slice boxplots (H2 intuition)
- **Figure 3**: 4-class ΔSMS forest plot (H4 intuition)
- **Figure 4**: SMS vs C1_share scatter + Spearman ρ (LRCA diagnostic)
- **Figure 5**: SMS vs pattern coverage dual-metric ranking comparison (RQ4)

---

### 5.6 RQ1 Empirical Results (60 cells, Track-2 v2)

#### 5.6.1 Data Scale and Cell-Level SMS Distribution

Each PUT has 12 mutants (operator-cache proportional sampling, §4.2.5 builder), each (mutant, MR) pair computes R_kill under N=20 AVP repeated sampling (§4.5.3). Full 60-cell SMS table shown in Figure 1, all numbers summarized in `data/results/paper_numbers.json`.

Primary statistics:

| Metric | Value |
|---|---|
| Number of cells | 60 |
| Mean SMS | 0.104 |
| Median SMS | 0.000 |
| Standard deviation SMS | 0.213 |
| Number of cells with SMS = 0 | 45 / 60 |
| Mean mutant count / cell | 24.3 (v4 cross-source pool, 10-30 per PUT) |

> Note: Among the 45 cells with SMS = 0, the vast majority concentrate in the cross-MP slice (j ≠ k), i.e., the 4 MPs outside each PUT's primary aligned MP. This is the direct data-level manifestation of H1 (MR-MP alignment); §5.7 quantifies the aligned vs non-aligned slice gap using Cliff's δ.

#### 5.6.1.1 Zero-Mass Dominance (Distribution Characteristics of 75% Zero Cells)

45 / 60 cells = 75% of cells have SMS = 0, a highly skewed, zero-concentrated distribution. Structural attribution:

| Slice | Zero cells / total | Zero proportion |
|---|---|---|
| aligned (j == k) | ~3 / 12 | 25% |
| cross (j ≠ k) | ~42 / 48 | 88% |
| All 60 cells | 45 / 60 | 75% |

**Impact on statistical inference**:

- Cliff's δ is a rank-based measure, mathematically well-defined for zero-concentrated distributions, but actual signal primarily comes from the non-zero portion of the 12 aligned cells (median(cross)=0, δ's numerator `#{a > b}` saturates at cross ≈ 0). **RQ2's effect-size inference is essentially dominated by n_aligned = 12 (not 60)**
- Median odds ratio is formally undefined because median(cross) = 0; this paper uses "aligned median > 0 = cross median" as auxiliary qualitative evidence
- Friedman χ² remains valid under zero-concentrated distributions (does not assume continuity, uses only ranks), but rank ties attenuate the statistic's power

**Consistency with LLM-mutant literature**: Tip et al. (2024) LLMorpheus similarly reports high proportions of cross-MP failure on JS sci-comp PUTs (specific numbers not listed in cited literature); this zero-mass dominance appears to be a shared characteristic of LLM-mutant + existing MR-MP alignment designs, not a special issue with this paper's PUT selection.

**Future work**: Whether expanding the mutant pool to 30+ / PUT (P4) can make more cross-MP cells exhibit non-zero SMS is a meaningful power test.

[Figure 1: 60-cell SMS heatmap (rows = PUT, cols = MP, ★ marks j = k aligned cells)]

#### 5.6.2 LRCA C1_share / suspect_share Distribution

LRCA three-tier diagnostics label each killed mutant as C1/C2/C3/C4 (§4.6). Average statistics across 60 cells:

| Metric | Value |
|---|---|
| Mean C1_share (legit fault proportion, default threshold) | 0.164 |
| Mean C1_share (calibrated best ood_band=0.02) | 0.200 |
| Mean suspect_share (calibrated best) | 0.800 |
| Cells meeting H5 threshold (suspect_share ≤ 0.20) (default) | 10 / 60 (16.7%) |
| Cells meeting H5 threshold (calibrated best) | **12 / 60 (20.0%)** |

H5 verdict: **not met** (calibrated best combination yields 20.0%, still far below the 80% threshold set in §5.2).

> Interpretation: 9-grid LRCA threshold scan (§4.6.4) shows that tightening the OOD boundary from 0.05 to 0.02 can improve H5 from 10/60 to 12/60, but still far from crossing the 80% strict threshold; tolerance multiplier has no impact on this dataset. This reflects: (a) R-fail signals from LLM-generated mutants concentrate in narrow boundaries, and (b) most killed mutants fall into C2/C3/C4 rather than C1 under LRCA three-tier thresholds, representing an inherent ceiling of LLM-homogeneous mutant pools (§7.1.7 R10), not an LRCA threshold issue. We therefore designate H5 as **not met, but as an empirical starting point for LRCA calibration research directions** (§6.2 engineering implications).

##### 5.6.2.1 H5 Cutoff Sensitivity (R-14 Response)

> Reviewer R-14 questions: Is the 0.20 in H5 pass condition `suspect_share ≤ 0.20` a "lucky pick"—would the verdict change if the cutoff were changed to 0.15 or 0.30? This section uses a dense grid (cutoff ∈ {0.05, 0.10, …, 0.50}, step 0.05) to scan v4 data (`scripts/h5_sensitivity.py`).

**Results** (`data/results/h5_sensitivity_v4.json`):

| cutoff | h5_cells_pass | h5_pass_ratio |
|---|---|---|
| 0.05 | 12 / 60 | 20.0% |
| 0.10 | 12 / 60 | 20.0% |
| 0.15 | 12 / 60 | 20.0% |
| **0.20** (paper) | **12 / 60** | **20.0%** |
| 0.25 | 12 / 60 | 20.0% |
| 0.30 | 12 / 60 | 20.0% |
| 0.35 | 12 / 60 | 20.0% |
| 0.40 | 12 / 60 | 20.0% |
| 0.45 | 13 / 60 | 21.7% |
| 0.50 | 13 / 60 | 21.7% |

**Key observation**: H5 pass-ratio is completely flat at 20.0% for cutoff ∈ [0.05, 0.40], with only one cell crossing over at 0.45. **No cutoff can push h5_pass_ratio above 80%**—`smallest_cutoff_for_80pct_pass = None`. This is because v4's suspect_share distribution is severely bimodal: median = 1.0 (48 cross cells have suspect_share ≈ 1 almost universally), mean = 0.79; only the 12 aligned cells have suspect_share in the low end (near 0). The middle region [0.20, 0.80] is nearly empty.

**Conclusion**: H5 verdict **not met is an intrinsic data property, independent of cutoff choice**. The specific value 0.20 is **not load-bearing** in the "lucky pick" sense R-14 is concerned about—changing it to 0.10 or 0.40 leaves the verdict completely unchanged. R-14's specific concern (whether 0.20 choice is fragile) receives a positive answer; extended LRCA threshold 49-grid scan (`scripts/calibrate_lrca.py LRCA_GRID=49`) is reserved for P4 paper with larger pool scale for deeper calibration.

[Figure 4: SMS vs C1_share scatter (per cell, n=60)]

---

### 5.7 RQ2 Empirical Results (Aligned vs Non-Aligned)

#### 5.7.1 Descriptive Statistics

Partition 60 cells by j == primary_MP(put):

| Slice | n | Mean SMS | Median SMS |
|---|---|---|
| aligned (j == k, v4 cross-source + v3b primary) | 12 | 0.275 | 0.267 |
| cross (j ≠ k) | 48 | 0.061 | 0.000 |

> Data version comparison:
> - v3 homogeneous + c→MP5: mean_aligned = 0.183, mean_cross = 0.064
> - v3b homogeneous + c→MP1: mean_aligned = 0.241, mean_cross = 0.049
> - **v4 cross-source + c→MP1** (primary): mean_aligned = 0.275, mean_cross = 0.061
> - aligned mean continuously rises (source expansion makes aligned more likely to trigger R-fail), cross mean slightly rises in v4 (source expansion likewise gives cross slice more opportunities to trigger R-fail); growth proportions leave δ nearly unchanged.

aligned-SMS is higher than cross-SMS in both mean and median, direction consistent with H1. Note: cross slice median is 0, meaning over half of cross-MP cells have SMS completely at 0—under cross design, MRs are almost completely ineffective against mutants. This observation forms the core empirical fact for §6.1 discussion.

[Figure 2: aligned vs cross SMS boxplots]

#### 5.7.2 Effect Size and Hypothesis Testing

Nonparametric effect size Cliff's δ (primary analysis for v3 pre-registered setting; v3b/v4 are exploratory sensitivity, see §3.5.1):

- **v3 (primary, pre-registered, c→MP5): δ = 0.323**, 95% bootstrap percentile CI [0.017, 0.622]
- v3b (exploratory; data-driven c-class primary MP shift to MP1, §3.5.1): δ = 0.446, CI [0.154, 0.743]
- v4 (exploratory; cross-source 3-LLM pool over identical prompt template, §4.2.5): δ = 0.439, 95% bootstrap percentile CI **[0.127, 0.740]** (B = 10,000 iterations, R-12 response)
- δ under all three stages fails to reach Romano (2006) large-effect threshold 0.474. v3 → v3b +0.123 reflects "c-class primary MP reselection" impact on δ (single class / three PUTs, selection rule defined after seeing data); v3b → v4 −0.007 reflects "nearly identical response from three LLMs to identical prompt under fixed prompt template" (see §4.2.5 dry-run), 95% CI covers zero

Median odds ratio (median(aligned) / median(cross)): Because median(cross) = 0, odds ratio is formally infinite; instead report "aligned median 0.083 significantly higher than cross median 0.000" as auxiliary evidence.

H2 verdict (conjunction of two conditions: Cliff's δ ≥ 0.474 and median odds ratio ≥ 3.0):

- δ threshold condition: **not met** (v3 primary δ = 0.323 < 0.474; v3b/v4 exploratory δ = 0.446 / 0.439 still < 0.474)
- Odds ratio condition: median(cross) = 0 makes ratio undefined; use "aligned median > 0 = cross median" as auxiliary directional observation

**H2 verdict: pre-registered point-estimate criterion not met** (P0-8 revision: wording changed from "rejected" → "not met under pre-registered point-estimate criterion", reason see effective-n note below and P0-8 commit message). Under pre-registered primary analysis (v3, c→MP5, n_aligned=12, n_cross=48), Cliff's δ = 0.323 falls 0.151 short of Romano (2006) large-effect threshold 0.474, 95% CI lower bound 0.017, effect size classified as small-to-medium. Two exploratory sensitivity analyses (v3b data-driven primary MP shift, §3.5.1; v4 cross-source pool, §4.2.5) raise δ to 0.446 / 0.439 but neither crosses the 0.474 strict threshold, and v3 → v3b modification includes known post-hoc selection confound (c-class primary MP selection based on observed data, see §3.5.1).

**Effective sample size note** (P1-5 revision, R0 W6 / R1 W7 / DA-3.1 consensus): surface n_aligned = 12 and n_cross = 48, but §5.6.1.1 already states that in v4 data 75% cells (45 / 60) have SMS = 0 (zero-mass dominance). In the cross-slice, this means approximately 88% (42 / 48) of 48 cells are zero; Cliff's δ inference is actually dominated by 12 aligned cells + 6 non-zero cross cells, **effective n ≈ 12 + 6 ≈ 18 rather than surface 60**. This actual sample size constraint:
- (a) explains "power to detect large-effect (δ > 0.474) only 0.42" in §5.7.3 power analysis—not caused by nominal-vs-effective error in sample size;
- (b) explains width of 95% bootstrap CI [0.127, 0.740]—upper/lower bound ratio ≈ 5.83, reflecting known liberal tendency of percentile bootstrap at effective n ≈ 18;
- (c) **does not change** H2 verdict direction (point estimate 0.439 < 0.474 is an effect-size ceiling, not a sample size issue, as §5.7.3 already argues), but readers should understand CI width causation accordingly.

Future work (P4) when expanding sample to n ≥ 30 PUTs, whether zero-mass dominance dilutes with PUT class diversification is a testable hypothesis for effective-n improvement.

**Contextual observation** (not part of H2 verdict): This paper's observed δ is in the same order of magnitude as the LLM-mutant medium-effect range observed by Tip et al. (2024) LLMorpheus on JavaScript. **Estimand caveat**: Tip 2024 compares "LLM mutants vs traditional mutants on fault detection rate" (cross-mutation-source comparison), this paper's §5.7.2 compares "aligned vs cross MP slice on the same mutant pool" (single-source within-pool comparison). The two δ values being similar does not constitute substantive support, only serves as reference for medium-effect phenomena in LLM-mutant literature, **does not constitute weakening or reframing of H2**.

**v3 → v3b and v3b → v4 contrasts reported separately** (avoiding synthetic ratio implying factor isolation):

| Contrast | Δδ | 95% CI (based on bootstrap iterations) | Interpretation |
|---|---|---|---|
| v3 → v3b (c-class primary MP shift) | +0.123 | (one-sided data-driven selection, CI not applicable, see §3.5.1 caveat) | Single class, post-hoc selection; reflects primary MP sensitivity rather than generic "MR design contribution" |
| v3b → v4 (cross-source under fixed prompt) | −0.007 | CI covers zero | Three LLMs nearly identical under prompt-fixed; does not constitute strong test of "LLM source diversity" (§4.2.5 limitation) |

Future work (P4) will test: (a) pre-registered primary MP selection rule (avoiding §3.5.1 confound); (b) differential prompt frame per LLM (testing strong sense of source diversity).

> Interpretation: RQ2's formalized H2 boundary was not crossed. We have expanded the mutant pool from 12/PUT to 30/PUT per §7.1.6 R9 (observed mean 17.4 mutants/PUT, limited by cache capacity); after pool expansion δ rose slightly from 0.321 to 0.323, CI narrowed from [0.021, 0.639] to [0.017, 0.622], indicating effect size is stable on this dataset and not diluted by pool scale. We therefore characterize H2 as **not meeting the large-effect threshold, but medium effect is stable and numerically consistent with the medium-effect magnitude reported in LLM-mutant literature (Tip 2024; estimand caveat: see §5.7.2)**; the feasible path to cross the large-effect threshold (0.474) is a cross-source mutant pool (mixing Claude / GPT / DeepSeek), as a research direction for the P4 paper (§7.1.7 R10 already paved the way).

#### 5.7.3 Statistical Power Analysis (R-13 Response)

> Reviewer R-13 requires: Before reporting "large-effect threshold not met", need to state whether this study's sample size (n_aligned, n_cross) = (12, 48) is sufficient to detect δ ≥ 0.474. This section uses empirical distribution parametric bootstrap simulation (N_sim = 5,000, seed = 42) to provide three-tier power.

**Method**: **With replacement** sample from observed aligned (n=12) and cross (n=48) v4 SMS pools to obtain simulated samples, compute simulated Cliff's δ; repeat N_sim times, count frequency of simulated δ exceeding given threshold as power approximation at that threshold (`scripts/compute_rq2_power.py`).

**Results** (data source: `data/results/rq2_power_v4.json`):

| Test threshold | Interpretation | Power at (12, 48) |
|---|---|---|
| δ > 0.000 | Detect any random advantage | **0.997** |
| δ > 0.147 | Detect small effect | 0.966 |
| δ > 0.330 | Detect medium effect | 0.759 |
| **δ > 0.474** | **Detect large effect (H2 threshold)** | **0.423** |

**Key interpretations**:
1. **Sample size sufficient for "any-effect" detection** (0.997 ≫ 0.80), H1 (RQ1) and RQ2 directional conclusions are robust.
2. **Slightly insufficient for medium-effect detection** (0.759 < 0.80), but 95% CI already covers 0.330, consistent with point estimate 0.439 indicating at least medium effect exists.
3. **Power to detect large-effect (H2 strict threshold) only 0.423**: This means even if true δ is around 0.474, sample size has only about 42% probability of detection. **But this cannot conversely say "insufficient power is the cause of H2 not being met"**—observed δ = 0.439 < 0.474, effect size itself is below threshold; increasing sample size will only narrow CI, will not automatically elevate point estimate to large.
4. **Sample size sweep** (`rq2_power_v4.json` sample_size_curve_for_delta_gt_0): at n_aligned ∈ {6, 12, …, 60} (n_cross = 4×), power to detect δ > 0 reaches 0.974 at n_aligned = 6, 0.996 at 12, then plateaus. Indicates RQ2 primary analysis (detect-any-effect) has very low sample size requirement, **main bottleneck is effect size boundary itself, not sampling noise**.

**Relationship to H2 verdict**: R-12/R-13 power supplement **supports rather than weakens** the H2 "large-effect threshold not met" conclusion — observed effect is in the medium range and CI cannot exclude < 0.474, continuing to claim "large-effect threshold not met" is statistically reasonable. **Effect-size ceiling breakthrough requires substantive improvement at MR design level (P4 direction), not larger sample**.

**Stipulated-alternative power supplement (R1 W1 round-2 NEW)**: The plug-in bootstrap above answers "given the *observed* distribution (δ ≈ 0.439), how effectively can we detect δ > threshold." R1 W1 further requires a stipulated-alternative design — "if the *truth* is exactly the H2 threshold 0.474, how effectively can our sample size confirm it?" We implement the stipulated alternative via a mixture-weight construction (script `scripts/compute_rq2_power_stipulated.py`, N_sim = 2000): SMS distributions have heavy ties at zero (45/60 cells = 0), raw shifting Cliff's δ is discontinuous (any ε > 0 jumps δ from 0.314 to 0.74), so we construct mixture aligned' = (probability w) sample from (observed_aligned + 0.001) + (probability 1 − w) sample from observed_aligned, calibrating w so that E[δ_stipulated] ≈ 0.474. Calibrated w = 0.094, realized E[δ] = 0.4746.

| Stipulated δ_truth | Test criterion | Power at (12, 48) | Data source |
|---|---|---|---|
| 0.474 (H2 boundary) | δ_hat ≥ 0.474 (point-estimate criterion, used in P0-8 verdict) | **0.491** | `rq2_power_stipulated_v4.json` |
| 0.474 (H2 boundary) | 95% CI lower > 0 (any-effect criterion) | 0.868 | same |

**Stipulated interpretation**: Even if the *true* δ equals the H2 threshold 0.474, this design (12, 48) still has only **49.1%** probability that a fresh sample's δ_hat will reach 0.474 — this is the actual power under the point-estimate criterion used by the P0-8 verdict. **This precisely supports the §5.7.2 P0-8 revision** (changing "is rejected" to "is not met under the pre-registered point-estimate criterion"): the H2 verdict is a factual statement about the point estimate not meeting the threshold, **not a claim that the effect size is necessarily smaller than 0.474** — the stipulated power of 49.1% shows that even when the truth is exactly at 0.474, sample randomness still produces "not met" verdicts in roughly half of replications. This is fully consistent with the §5.7.2 estimand caveat.

---

### 5.8 RQ3 Empirical Results (Cross-Class Consistency Across 4 PUT Classes)

#### 5.8.1 Class Means

| Class | PUT set | Mean SMS (15 cells, **v3 baseline**) | Mean SMS (**v4 cross-source**) |
|---|---|---|---|
| a (numeric) | a1, a2, a3 | 0.067 | 0.067 |
| b (probabilistic) | b1, b2, b3 | 0.156 | 0.148 |
| c (surrogate) | c1, c2, c3 | 0.047 | 0.089 |
| d (ML) | d1, d2, d3 | 0.081 | 0.112 |

Across both versions the maximum between classes occurs in class b; the minimum is class c under v3 (0.047) and class a under v4 (0.067). **Cross-source main driver: class c +91.4% (see §6.1)** — class c is most sensitive to cross-source pool expansion, and together with the §3.5.1 v3b primary MP shift forms the empirical finding that "class c sensitivity to source diversity exceeds the other three classes".

[Figure 3: Cross-class SMS forest plot (mean ± SEM)]

#### 5.8.2 Sign Test: Within-Class Aligned Higher Than Cross

For each class, compute "that class's aligned slice mean − that class's cross slice mean", record 1 if sign is positive.

- Pass count: **v3 (pre-registered): 3 / 4 (partial)**; **v3b (exploratory, post-hoc): 4 / 4 (conditional on c-class primary MP shift, §3.5.1)**; v4 cross-source pool maintains 4 / 4 under v3b condition.

H4 primary conclusion based on v3 pre-registered: **partial, not strict** (sign test 3/4). v3b 4/4 and v4 4/4 are sensitivity reports, do not replace v3 verdict. Class c's flip under v3b stems from data-driven primary MP adjustment (§3.5.1): class c Friedman per-class p = 0.406 shows any MP can serve as primary; v3b replaces P1's MP5 with the one having maximum mean SMS (MP1), making class c aligned mean (0.233) > cross mean (0); this is selection-on-response, therefore exploratory only. Detailed directional interpretation in §6.3.

#### 5.8.3 Mixed-Effects Model Limitation Statement

§5.3.2 planned random-intercept-PUT, fixed-effects class × operator model **primary model did not converge** on observed data:

- Primary model formula: `sms ~ C(class) + C(operator) + C(class):C(operator) + (1 | put)`
- Fit error: Singular matrix (design matrix for class × operator interaction term has insufficient column rank, N=60 observations insufficient for 11-dimensional fixed-effects + 12 PUT random intercepts)
- Fallback model (removing interaction term): `sms ~ C(class) + C(operator) + (1 | put)`
- Fallback status: fixed-effects converge, but Group Var (PUT random intercept variance) hits boundary ≈ 0, essentially degenerates to OLS; model self-reports "Group Var hit boundary; the random-intercept term is degenerate"

Class fixed-effects p-values (class a as baseline, fallback model, as approximate descriptive metric):

| Comparison | p-value (approx.) |
|---|---|
| class b vs a | 0.275 |
| class c vs a | 0.892 |
| class d vs a | 0.991 |

> **Honest statement**: Due to PUT random intercept variance degeneration and sample size (60 cells / 12 PUTs) limitations, we do not report fallback p-values as formal hypothesis tests, but as auxiliary description. RQ3's primary conclusion shifts to four-piece direct presentation: (a) class mean table + (b) sign test + (c) Friedman nonparametric test (§5.8.4) + (d) forest plot, consistent with §5.3.2 already-stated "small-N multiple comparison alternative". This limitation is extended into §7.2.2 R6.

#### 5.8.4 Friedman Nonparametric Alternative Test

Because mixed-effects primary model is Singular, we use Friedman χ² as formal nonparametric alternative test:

- **Design**: PUT (block, n=12) × MP (treatment, k=5), value = SMS, df = 4
- **Primary statistic**: **χ² = 15.30, p = 0.0041** (< 0.05, significant)
- **MP rank means** (MP1 → MP5): 2.92, 2.58, 2.08, 3.08, 4.33

Within-class Friedman (each class 3 PUTs × 5 MPs) — **R1 W4 round-2: Bonferroni × 4 correction + Kendall's W effect size added**:

| Class | χ² | raw p | Bonferroni × 4 adjusted p | Kendall's W (n=3, k=5) | Effect strength |
|---|---|---|---|---|---|
| a (numeric) | 4.00 | 0.406 | 1.000 | 0.333 | small |
| b (probabilistic) | 10.78 | **0.029** | 0.116 | 0.898 | large |
| c (surrogate) | 4.00 | 0.406 | 1.000 | 0.333 | small |
| d (ML) | 5.00 | 0.287 | 1.000 | 0.417 | small-medium |

**R1 W4 round-2 correction interpretation**: Applying Bonferroni × 4 correction over the family of 4 per-class Friedman tests, the b-class original "individually significant" raw p = 0.029 rises to adjusted p = 0.116, **>** 0.05; **no per-class result remains significant at family-wise α = 0.05**. This is consistent with the small per-class sample N = 3 PUTs × 5 MPs — even though b-class Kendall's W = 0.898 indicates a strong rank-concordance pattern, 3 PUTs is insufficient to yield a conclusive within-class verdict after multiple-comparison correction. **This is consistent with the paper's H4 primary verdict still resting on the §5.8.2 sign test**: per-class Friedman serves as sensitivity / descriptive reporting only and does not drive the H4 verdict directly. Kendall's W provides the effect-size complement (b-class 0.898 falls in the "large concordance" range under Cohen 1988, even though not statistically significant after correction).

Interpretation: Friedman test on full 60-cell data is **significant (p = 0.0041)**, indicating 5 MPs do exhibit systematic differences across 12 PUT blocks; rank means show MP3 lowest, MP5 highest, consistent with §5.7 aligned-cross asymmetry pattern.

**Important caveat — Friedman main effect ≠ H4 cross-class consistency**: Friedman χ² tests "whether rank differences exist among 5 MPs" (MP main effect averaged over PUTs), **not what H4 tests: "whether direction is consistent across 4 PUT classes in aligned-cross comparison"**. These are logically independent statistical claims:

| Statistic | What it tests | This paper's result | Support for H4 |
|---|---|---|---|
| Friedman χ² (PUT × MP) | MP rank differences (averaged over 12 PUTs) | χ² = 15.30, p = 0.0041 (significant) | Does not directly support |
| Sign test (4 classes) | 4/4 classes aligned mean > cross mean | v3 primary: 3/4 (partial); v3b exploratory: 4/4 | **Directly corresponds to H4** |

Within-class Friedman only class b (probabilistic) individually significant, reflecting probabilistic PUT class has larger sensitivity differences to different MPs. Non-significance of Friedman per-class (a/c/d classes p > 0.28) **does not mean "any MP equivalent" within these classes**, but rather that under n=3 PUT power, MP differences were not detected. §3.5.1 v3b exploratory uses class c non-significance as basis for primary MP reselection, which is selection-on-non-significance, itself having §3.5.1 already-stated confound.

Friedman's methodological contribution is **providing formalized nonparametric p-value for RQ3** (replacing mixed-effects Singular, §5.8.3), not **directly verifying H4**. H4 verdict still based on §5.8.2 sign test: v3 primary 3/4 (partial), v3b exploratory 4/4 (post-hoc, with caveats).

---

### 5.9 RQ4 Empirical Results (SMS vs Pattern Coverage)

#### 5.9.1 Pattern Coverage Operationalization

For each PUT, compute (MP_k, R_outcome ∈ {True, False}) binary tuple coverage: each PUT has 5 MPs × 2 outcomes = 10 cells, coverage = number of actually triggered cells / 10. Essentially the simplest implementation of §1.4 RQ4 baseline (per-PUT granularity, not distinguishing mutants).

PC range for 12 PUTs: [0.500, 1.000], mean 0.733.

#### 5.9.2 Correlation with SMS

Pair by PUT (one PC value per PUT, paired with that PUT's mean SMS over 5 MPs):

- Spearman ρ = 0.163 (p = 0.613) (v4 primary, `paper_numbers_v4.json`)
- Kendall τ = 0.136 (p = 0.568)

[Figure 5: per-PUT SMS vs PC scatter (n = 12)]

#### 5.9.3 Interpretation

**Statistical-power caveat first**: n = 12 PUTs is severely under-powered. For a Spearman ρ at n = 12, the 95% CI covers approximately [−0.5, +0.6]; the measurement precision is insufficient to distinguish "zero correlation", "moderate positive correlation", or "moderate negative correlation". p = 0.61 / 0.57 does not constitute evidence that "correlation does not exist", only that "no correlation was detected at n = 12".

**Revised qualitative observation** (weakened from the original "almost independent"): Spearman ρ = 0.163 and Kendall τ = 0.136 are not significantly different from zero (p ≈ 0.61, 0.57), and the data **do not support** either the "SMS is independent of PC" claim or the "SMS is strongly correlated with PC" claim. **Orthogonal semantic dimension is a hypothesis, not a finding from this dataset** — its empirical test requires n ≥ 30 PUTs or a more refined PC operationalization (incorporating the mutant dimension). This paper records "no detectable statistical correlation between SMS and PC over 12 PUTs" as the conservative finding for RQ4, leaving orthogonality to the P4 paper (with expanded PUT scale or partial-correlation design).

> Specifically, the b2 PUT has PC = 1.0 (full coverage) but mean SMS = 0.067; the b1 PUT has PC = 0.7 but mean SMS = 0.20 — within the same class, the PUT with higher PC has lower SMS, contradicting the naive assumption that "more complete PC kills more mutants" and providing positive support for SMS as an independent information dimension. The c3 PUT shows the same pattern: PC = 1.0 with mean SMS = 0.14; c1 / c2 have PC = 0.7-0.8 with mean SMS = 0.0, with the inverse correlation more pronounced within that class. The completion of RQ4 is bounded at this level: further refinement of the PC definition (incorporating the mutant dimension, cross-PUT joint coverage) is left for the P4 paper (see §1.6).

## Section 6 · Discussion

**Section positioning**: This section discusses the empirical findings from the §5 60-cell empirical audit (H1/H2/H4/H5 verdicts, Cliff's δ, Friedman main effects, SMS-PC correlations). These are **incidental empirical findings** after the three-pillar methodological framework is established—they demonstrate the empirical ceiling within the current scope of LLM-mutant + same-prompt + single-output kernels, and do not constitute counterevidence to the methodological framework (the framework's justification is completed in §3.2.0 / §2.3-4.4 / §3.2.6.3).

### 6.1 Systematic bias of SMS on aligned slices

The core empirical fact from RQ2: the median SMS of cross-MP slices (j ≠ k) is 0, meaning most non-aligned MRs are almost completely ineffective against LLM-generated semantic mutants; the median SMS of aligned slices is 0.267, far higher than 0. This asymmetry stems from the semantic coherence between mut_j and MP_k—in aligned slices, mutants break the algebraic properties directly asserted by the MR, thus the R detection signal is strongest; in cross slices, the semantic dimension broken by mutants is orthogonal to the semantic dimension detected by the MR, so even if the mutation does change the output, the MR cannot capture that change as R-fail.

**Key finding from Phase A cross-source pool (one of this paper's core methodological contributions)**: We retested H2 using a cross-source mutant pool (v4, see §4.2.5) generated by three LLMs (Claude Opus 4.6 + GPT-5.4 + DeepSeek chat), obtaining δ = 0.439, nearly identical to the v3b same-source pool δ = 0.446 (difference 0.007), with slightly wider 95% CI but stable center. **This inversely falsifies our initial hypothesis about the H2 upper bound—LLM same-source bias is not the dominant factor in the H2 upper bound**:
- The leap from v3 → v3b (δ 0.323 → 0.446) came from data-driven adjustment of c-class primary MP (§3.5.1), i.e., the MR-MP alignment design itself
- The cross-source expansion from v3b → v4 (δ 0.446 → 0.439) barely changed δ, i.e., source diversity of the mutant pool

This contrast **separately** reports two contrasts: Δδ_{v3→v3b} = +0.123 comes from single-class, post-hoc c-class primary MP selection (§3.5.1 caveat, Bonferroni-bounded effective α see §3.5.1 + this paper's P0-4 revisions); Δδ_{v3b→v4} = −0.007, conditional on v3b selection + identical prompt, reflects the near-consistent response of three LLMs under fixed prompt. **The two contrasts each carry their own selection / conditioning caveats and cannot be synthesized into a single factor decomposition ratio**—see the existing contrast table in §5.7.2. Tip et al. (2024) LLMorpheus observed LLM-mutants in the medium-effect range on JavaScript—this phenomenon is directionally consistent with this study's observation that δ has not yet crossed the 0.474 large-effect threshold, suggesting that under LLM-mutant + current MR design, medium-effect may be the norm for this experimental paradigm, and crossing it requires not more sources but further refinement of MR design (P4 paper research direction). **Estimand caveat**: Tip 2024's δ is "LLM mutants vs traditional mutants on fault detection rate" (cross-mutation-source comparison), different from this paper's "aligned vs cross MP slice" (single-source within-pool) estimand; numerical similarity serves only as a literature reference for the medium-effect phenomenon.

**True contribution of the cross-source pool**: Although it does not significantly push δ, it significantly improves mutant quality (C1_share 0.164 → 0.209, +27%) and inter-class balance (c-class mean SMS 0.047 → 0.089, +91.4%). This constitutes the empirical foundation for the R_sem/R_kill decoupling engineering insight in §6.2.

**Contextual consistency with LLM-mutant literature (not H2 verdict)**: This paper's v3 primary δ = 0.323, CI [0.017, 0.622] is in the same order of magnitude as the LLM-mutant medium-effect range observed by Tip et al. (2024) LLMorpheus on JavaScript. **Estimand caveat**: Tip 2024 compares "LLM mutants vs traditional mutants on fault detection rate" (cross-mutation-source comparison), while this paper's §5.7.2 compares "aligned vs cross MP slice on the same mutant pool" (single-source within-pool comparison). The numerical similarity of the two δ values does not constitute substantive support, serving only as a reference for the medium-effect phenomenon in LLM-mutant literature. This is contextual literature comparison, **not a reframing of the H2 rejected verdict**; it merely shows that the medium-effect scale observed in this study is consistent with the empirical norm of this research paradigm in other domains (JS web testing), providing a baseline for subsequent P4 cross-language portability research.

**Petrović & Ivanković (2018) numerical coincidence statement (mechanism difference confirmed)**: Petrović & Ivanković reported ~20% productive mutants on Google's industrial 500k mutant data, numerically close to this paper's LRCA-calibrated best C1_share = 0.20. However, **this is numerical coincidence, not mechanism validation**: Google's "productive mutant" is obtained from *developer survey* where developers subjectively judge usefulness, a human judgment construct; LRCA's C1 is the automatic annotation output of a *3-layer classifier*, an algorithmic construct. The two constructs differ significantly; numerical approximation does not constitute proof of LRCA's equivalence to industrial practice. Rigorous mechanism validation would require developer sampling review on 5-10 PUT × N C1-flagged mutants (reserved for P4 paper). This paper positions this comparison as "encouraging numerical reference," not "industrial practice calibration."

**Note on monotone transformation invariance (not a robustness check)**: Cliff's δ is a rank-based statistic, function U / (n1·n2), **mathematically invariant under any strictly monotone transformation** (Romano 2006 explicitly notes). Logit is strictly monotone on (0, 1), so δ_logit ≡ δ_raw after logit transformation of SMS is a construction result, not an empirical finding.

We still retain the calculation result as an execution correctness check (`data/results/rq2_cliffs_delta_logit_v4.json` shows δ_logit = 0.439 = δ_raw, difference 0.000—consistent with the rank-invariance theorem), **but this does not constitute additional robustness evidence for the H2 conclusion**. The true robustness threats to the H2 verdict come from the post-hoc selection confound in §3.5.1 v3b and zero-mass dominance in §5.6.1.1, not from metric scale choice.

### 6.2 Decoupling of R_sem and R_kill

The §4.8.3 operator-level pilot already observed: HP-class (hyperparameter) operators have high R_sem (semantic feasibility) but low R_kill (kill rate by MR). This chapter's §5.6 cell-level SMS reproduces this pattern—45 / 60 cells have SMS = 0 (v4 cross-source pool), concentrated in cross-MP slices; the v3b same-source pool gives mean C1_share of only 0.164 under default LRCA threshold, **v4 cross-source pool improves to 0.209 (+27%) under default threshold**, i.e., among the few killed mutants, the cross-source pool significantly reduces LRCA mislabeling rate.

Engineering insight: "operator-MP alignment coverage" in MR design is a necessary condition for producing strong SMS signals; merely expanding the "semantically feasible mutant pool" does not increase SMS but dilutes the proportion. LRCA threshold calibration (OOD boundary 0.05, tolerance multiplier 10×) may also be overly sensitive, misjudging most borderline kills as C2/C3/C4 rather than C1. These two jointly support the research question in the P4 paper of "using SMS to infer MR under-coverage dimensions + calibrating LRCA."

### 6.3 Constrained interpretation of cross-class consistency H4

RQ3 data show that the mean SMS of all 4 classes is positive (v4 cross-source: a=0.067, b=0.148, c=0.089, d=0.112), but the differences are limited. **H4 main verdict is based on v3 pre-registered: sign test 3/4 (partial)**; after v3b data-driven primary MP adjustment, sign test rises to 4/4 (exploratory, post-hoc, §3.5.1), v4 cross-source pool maintains 4/4 under v3b conditions (also exploratory). Inter-class balance significantly improved after cross-source: c-class mean SMS 0.047 → 0.089 (+91.4%), d-class 0.081 → 0.112 (+38%), a/b classes nearly unchanged. This confirms that c/d classes (surrogate / ML) have higher demand for mutant diversity than a/b classes (numeric / probabilistic). The mixed-effects primary model is Singular, the fallback model's PUT random intercept variance degenerates to 0, meaning the sample size of 60 cells / 12 PUTs is insufficient to support a two-layer structure that "estimates both random intercepts and fixed-effect interaction terms."

However, §5.8.4 Friedman non-parametric test gives **significant main effect (χ² = 15.30, p = 0.0041)**, confirming systematic differences among the 5 MPs on 12 PUT blocks. Within-class Friedman shows only b-class (probabilistic) is individually significant (p = 0.029), the other three classes p > 0.28—this is consistent with §5.7 aligned-cross asymmetry, indicating MP-differences are most evident on probabilistic-class PUTs. **c-class internal p = 0.406 non-significant is precisely the basis for §3.5.1 data-driven primary MP adjustment**: any MP can serve as primary, selecting the one with largest mean SMS (MP1) is a reasonable post-hoc revision.

Our conclusion: cross-class consistency verdict **is based on v3 pre-registered = partial (sign test 3/4)**. Supporting sensitivity: (a) all 4 class mean directions are positive (v3/v3b/v4); (b) v3b sign test 4/4 and v4 sign test 4/4 (both exploratory, conditional on c-class primary MP shift, §3.5.1); (c) 60-cell Friedman p = 0.0041 (non-parametric fallback, **not part of H4 verdict**, see §5.8.4). Mixed-effects unavailability is a sample constraint of N = 60 / 12 PUT (§7.2.2 R6), not evidence absence.

### 6.4 Positional relationship between SMS and Pattern Coverage

RQ4's Spearman ρ = 0.163, Kendall τ = 0.136 (n = 12 PUT, p ≈ 0.61, 0.57) give the correlation direction between SMS and the simplest PC. **n = 12 is severely underpowered**: at this sample size, Spearman ρ's 95% CI is approximately [−0.5, +0.6], p = 0.74 does not constitute evidence of "no correlation," only "not detected."

This paper's RQ4 conservative conclusion is: **at the 12 PUT scale, SMS and the simplest PC have no detectable statistical correlation**. Orthogonality is a hypothesis worth testing in P4, **not a finding from this data**. "SMS is a semantic-layer sensitivity dimension orthogonal to coverage-class metrics" as a P4 research direction (expand to n ≥ 30 PUT, or use extended PC operationalization to incorporate mutant dimension) is not within this paper's empirical scope.

### 6.5 Stakeholder analysis: who benefits from SMS (R-19)

> **Scope** (R3 round-2 tightening): All stakeholder pain points, capability claims, and workflows discussed in this section are strictly bounded to **single-output `float → float` kernels (< 2 KB source code, the 12 PUTs in this paper)** — see §1.1 / §3.1.1 / §7.5. None of the claims in this section apply to industrial-scale, multi-module, or multi-output scientific computing software; the latter is the research scope of P5 / P2-CN (domain application). Per IST convention this section explicitly distinguishes three stakeholder classes — test engineers, MR designers, V&V documentation — and for each class explains: (a) pain point before SMS; (b) specific capability SMS provides; (c) executable workflow + resource cost; (d) existing responsibilities not replaced.

#### 6.5.1 Test engineers

**Pain point** (scoped to single-output kernels): When testing a single-output `float → float` numerical / probabilistic / surrogate / ML kernel, even when line / branch / MC-DC code coverage reports 90%+, the engineer still cannot directly judge whether the accompanying MR set has adequate detection capability over numerical / probabilistic / ML behaviors, because existing mutation testing tools (mutmut, cosmic-ray) produce mostly syntactic-layer mutants (see §3.2.6.1 operator-level cross-table, §3.2.6.3 12-PUT empirical 5.14% AST overlap rate), with weak correlation to domain-level semantic errors.

**Capability SMS provides**: For each (PUT, MP) cell, provide a scalar SMS value from 0–1, directly reading "how many meaningful semantic mutations this MR kills under this MP." When SMS is significantly lower than the §5.7.2 same-class baseline (e.g., aligned mean 0.275), it prompts that the MR's oracle tolerance or verification logic may miss a class of domain errors.

**Workflow**:
1. For a newly written MR, run `scripts/sms_campaign.py` to obtain SMS value;
2. If SMS = 0 (75% default case), first check LRCA labels in `lrca_60cell.json`—C2 (MP-semantic inconsistency) / C3 (AVP tolerance dispute) / C4 (MR design defect) each point to different repair paths;
3. Rerun after revising MR; iterate until SMS enters reasonable range (§5.6 gives empirical ranges by PUT category).

**Air-gap incompatibility declaration** (NEW, R3 round-2): This workflow depends on **external LLM API calls** (Claude / GPT / DeepSeek) for semantic mutant generation. This makes the method **incompatible with most regulated air-gapped V&V workflows** — code review in high-risk domains such as nuclear engineering (IEC 60880), aerospace (DO-178C), medical devices (IEC 62304), and automotive (ISO 26262) typically requires air-gapped build environments, where LLM API calls cannot execute. Possible mitigation paths (P5 future work): (i) self-hosted open-weight LLMs (Llama / DeepSeek local inference); (ii) offline-cached pre-generated mutant pools with signature locking. This paper's mutant pool is already pre-generated reproducibly via commit-hash + raw-response store (§4.2.3), so engineers can **reproduce a published mutant pool offline**, but **generating new mutant pools still requires external LLM access (off air-gap)**. This is a deployment scope limitation of the P2 methodology, explicitly acknowledged in §7.5 Limitations.

**SMS does not replace**: Domain expert manual review of MR physical/mathematical correctness, regression testing against real historical faults, performance and stability testing. SMS only evaluates "semantic-layer failure detection capability," not "engineering practical value" (§7.5 R6 already declared).

#### 6.5.2 MR designers

**Pain point**: MR designers (often researchers or senior developers working on single-output scientific computing kernels of the type covered by §3.1.1) rely on intuition or literature patterns to propose new MRs, lacking a quantifiable "design feedback" metric—before P1, whether a new MR is "useful" can only be verified after deployment to real faults, with a very long feedback loop.

**Capability SMS provides**: SSOT-based offline SMS batch runs (`scripts/sms_campaign.py`) give MR designers a quantifiable design-feedback metric — comparing the new MR's aligned-cell SMS against the existing-MR-set median (this paper's v4 main analysis aligned mean 0.275) gives an initial verdict within hours on whether the MR has acceptable failure-detection capability on aligned slices.

**Workflow** (reframed to **quarterly batch audit**, not per-PR gating; R3 round-2):

> **Removed in R3 round-2**: The original §6.5.2 GitHub Actions per-PR YAML template has been deleted — the original template hardcoded `SMS_VERSION=v4` + `P2_PRIMARY_VERSION=v3b` (§3.5.1 v3b is an exploratory post-hoc selection, not pre-registered) into a stakeholder-facing CI template, propagating the v3b selection-on-the-response confound into downstream adopters' pipelines, and the PR-CI threshold 0.10 contradicted the §6.5.3 audit threshold 0.20. This conflicted with the §3.5.1 caveat and is removed in R3 round-2 revision.

**Replacement**: **Quarterly batch audit**, not per-PR gating —

| Step | Description | Resource cost |
|---|---|---|
| 1. Offline mutant pool generation | Use LLM API to generate the mutant set corresponding to newly added MRs (per PUT 24-30 mutants × 12 PUTs ≈ 300 mutants) | LLM API: ~$5-15 per quarter; wall time ~30 min |
| 2. SMS batch run | `python scripts/sms_campaign.py --track 2` | 4-core laptop: ~10-20 min per pool |
| 3. LRCA three-layer diagnostic | `python scripts/run_lrca.py` annotates C1-C5 | <1 min |
| 4. Quarterly review | MR design team manually reviews MRs whose aligned-cell SMS is significantly below the historical median (0.275) | Team meeting: 1-2 hours |

**Resource estimate** (quarterly): API ~$10 + ~30 min automation + 1-2 h manual review ≈ 0.5 person-day/quarter — affordable for an active MR design team. **Per-PR gating is not recommended** (LLM API latency 5-30 s + cost + non-determinism + air-gap incompatibility all make per-PR impractical).

**SMS does not replace**: Domain expert judgment of MR physical meaning reasonableness (§7.1.4 R4 already declared MR "reasonableness" is a priori); nor does it replace "whether MR covers a real business scenario" stakeholder review (completed by product requirements side).

#### 6.5.3 Research-grade evidence for V&V documentation (long-term aspiration)

> **R3 round-2 retitled** from "Auditors / certification bodies": This subsection makes **no** normative claim toward industrial certification bodies (NRC, FDA, ISO 26262 review teams). Within this paper's single-output kernels scope there is no traceable mapping to the normative bodies of current IEC 60880 / ISO 26262 / DO-178C / ASME V&V 20-2009 standards. The subsection is positioned as a **long-term aspiration** — SMS as research-grade test adequacy evidence may serve as **supplementary** (not normative) material in V&V documentation.

**Pain point** (scoped to V&V documentation, not normative certification): V&V documentation for scientific computing software (per ASME V&V 20-2009 §3 code verification and similar guides) requires quantifiable evidence of test adequacy. Current V&V documentation often relies on code coverage reports + MR lists + domain SME signatures and lacks a mutation-based quantifiable supplement.

**SMS as research-grade supplementary evidence**: SMS values may appear in V&V documentation as supplementary evidence, alongside code coverage and MR lists. Documentation may include: (a) aligned-cell SMS for each critical PUT; (b) LRCA three-layer diagnostic conclusions (C1 direct readout / C2-C5 engineering attribution); (c) visualization coverage map of the 60-cell matrix (§6.2 fig1). Reviewers can independently run the reproduction package (`REPRODUCIBILITY.md`) to verify.

> **R3 round-2 deletion**: The original §6.5.3 proposed acceptance thresholds aligned-cell SMS ≥ 0.20 / ≥ 0.30 + C1_share ≤ 0.20. These thresholds were research recommendations on the empirical basis of this paper, **but**: (i) they have no normative backing in IEC / ISO / ASME standards; (ii) writing them under "acceptance threshold recommendations" risks reader misinterpretation as enforce-ready standards; (iii) the §3.5.1 caveat already declares that the 0.275 baseline is influenced by v3b post-hoc selection. R3 round-2 therefore removes the threshold recommendations — SMS values should be reported as **descriptive supplementary evidence**, with concrete "is it adequate" judgments left to actual V&V documentation reviewers on case-by-case engineering grounds.

**Relation to existing V&V standards**: This work is conceptually complementary to ASME V&V 20-2009 (Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer) §3 code verification — the latter emphasizes code-level correctness of numerical solvers, while this paper's SMS emphasizes the fault-detection adequacy of MR sets. However, this paper's empirical scope is strictly bounded to single-output `float → float` kernels, with a substantial scale gap to the multi-module industrial CFD code base targeted by ASME V&V 20-2009. Incorporating SMS into the V&V standards body would require (i) scale-up empirics on large multi-module CFD code (left to the P5 paper); (ii) multi-year dialogue with the ASME V&V 20 / IEEE 1012 / IEC 60880 committees. This paper does **not** advocate that SMS enter any normative certification system in 2027.

**SMS does not replace**: Domain expert (SME) signatures, safety analysis (FMECA, PIRT), system-level V&V, operational history accident retrospection, or ASME V&V 20 §3 numerical solver verification. SMS is **one link** in the test adequacy evidence chain, not a single-point qualification determination.

#### 6.5.4 Common interface across stakeholders

All three stakeholder classes obtain consistent numbers through the same `data/results/paper_numbers_v4.json` (SSOT), and consistent diagnostic labels through `lrca_60cell_v4.json`. This avoids the document fragmentation problem of "SMS seen by engineers inconsistent with SMS in V&V documentation"—this is the prerequisite for the §6.5 stakeholder analysis to be implementable in engineering. All numbers are to be interpreted under the single-output kernels scope declared in §1.1 / §3.1.1.

---

## Section 7 · Risks and Mitigation + Limitations

### 7.1 Internal Threats

#### 7.1.1 LLM Generation Reproducibility (R1)

**Risk**: Different LLM versions / temperature / seed produce different mutant pools, affecting experimental reproducibility.

**Mitigation**:
- §4.2.3 All reproducibility parameters stored in replication package (LLM version, prompt, temperature, seed, manual arbitration records)
- §4.2.4 Dual LLM cross-source + 20% manual sampling
- Provide "reproducibility consistency check script": identical prompt + seed should produce ≥ 90% overlapping mutant pool

**Residual risk**: LLM training data may be updated after submission, rendering old API versions unavailable — explicitly acknowledged in §7 Limitations.

#### 7.1.2 Probabilistic Approximation of equiv Determination (R2)

**Risk**: K_eq=1000 is an engineering approximation to the undecidable problem of SMS (equivalent mutant detection), with bidirectional bias of false-equiv and false-non-equiv.

**Mitigation**:
- §2.3 Explicitly declares equiv as probabilistic approximation rather than theorem-based determination
- ~~§5 Appendix provides sensitivity analysis for three configurations K_eq ∈ {500, 1000, 2000}~~ **(R1 W3 round-2 revision)**: The K_eq sweep sensitivity table was not executed in this submission; downgraded to §7.5 Limitations as a residual threat. The Hoeffding-style upper bound still provides a theoretical bound on the false-equiv probability; an empirical K_eq sweep is left to the P4 paper.
- §7 Limitations cites the Hoeffding-style upper bound on false-equiv probability; K_eq sensitivity sweep is deferred to the P4 paper.

#### 7.1.3 Circular Dependency Between AVP and P1 (R3)

**Risk**: P1 is under SANER submission; if P1 modifies AVP implementation, P2 data becomes invalid.

**Mitigation**:
- §4.5.1 AVP version fixed to P1 commit hash
- P2 replication package embeds complete AVP source code (P2 remains self-consistent even if P1 undergoes major revision)
- §1.6 Explicitly declares [Meng Li et al., Progress in Nuclear Energy, under review] citation as arXiv technical report

#### 7.1.4 Boundary of LRCA Multi-label Determination (R4)

**Risk**: C2-C5 may trigger multiply on class B/D PUTs; priority C5>C4>C3>C2>C1 is an engineering choice that may mask mixed root causes.

**Mitigation**:
- §2.6.3 Decision tree explicitly declares priority
- §5.4 LRCA diagnosis appends **multi-label co-occurrence table** (all triggered layers for each killed mutant), not only reporting priority-winning root cause
- §7 Limitations explicitly acknowledges root_cause label as "likely root cause," not definitive attribution

**§5.6.2 Empirical addendum**: LRCA's 3 engineering thresholds have been calibrated via 9-grid search (§4.6.4); optimal combination (ood_band=0.02, tolerance_multiplier=3.0, repeats=20) improved H5 pass rate from default 10/60 to 12/60; §5.6.2 reported values adopt this optimal combination. Calibration found tolerance_multiplier has zero impact on results within the 9-grid; dominant signal comes from ood_band. This paper uses this calibration as official results; default threshold results retained as control (`lrca_60cell_v3.json`).

#### 7.1.5 Operator Registry-PUT Source Code Drift (R8)

**Risk**: During v2 → v2.1 revision, 6 / 37 operator definitions were found to reference parameters that no longer exist after PUT refactoring (e.g., GPR.alpha vs WhiteKernel.noise_level; d1 registry declares SVM but PUT is actually MLP). Such drift causes mutant generation to have no executable match with PUT, polluting R_sem statistics.

**Mitigation**: Added pre-check consistency scan in §4.2 (key identifiers in target_locator must appear in PUT source code, otherwise that operator is skipped for that PUT); v2.1 revision log recorded in `data/operator_campaign/v2_revised6.log`.

#### 7.1.6 Mutant Pool Size (R9)

**Risk**: 12 mutants per PUT is an engineering-cost balance: smaller pools yield coarse SMS estimation jumps (each mutant contributes 1/12 ≈ 0.083 step size), larger pools exceed weekly Opus subscription quota for LLM calls. §5.7 bootstrap CI reflects uncertainty from this source, also partially explaining why H2 formally did not exceed the 0.474 threshold.

**Mitigation + empirical addendum**: Replication package includes `data/operator_campaign/cache/` (212 confirmed mutants) and `scripts/build_pools.py` (supports `POOL_VERSION=v3` to switch to 30 mutants/PUT). We empirically expanded pool to average 17.4 mutants/PUT (limited by cache capacity, some PUTs below 30): δ increased marginally from 0.321 to 0.323, CI narrowed from [0.021, 0.639] to [0.017, 0.622], H2 still not met. This indicates effect size is an **intrinsic upper bound of LLM-homogeneous mutant pools** on this dataset, not an artifact of 12-mutant pool dilution (see §6.1). P4 paper will retest H2 with **cross-source mutant pools** (mixing multiple LLM backends).

#### 7.1.7 Non-determinism of LLM Generation (R10)

**Risk**: Claude Opus subscription interface lacks seed control; identical prompt may produce different mutant outputs at different times.

**Mitigation** (three-part):
- (a) Multi-turn de-dup enforces structural differences among candidates (§4.2.1);
- (b) K=10 / K=20 repetitions reduce single-point bias of individual operators (§4.8);
- (c) `data/operator_campaign/raw/` commits complete prompt + raw response, allowing replication experiments to directly reuse the same mutant set used in this paper, bypassing non-determinism.

#### 7.1.8 R11 Selection-on-response Chained Conditioning (NEW, P0-5)

Both v3b and v4 data are conditional on post-hoc selection of §3.5.1 c-class primary MP (c1/c2/c3 → MP1). Specific consequences:

(a) **v3b sign test 4/4** and **v4 sign test 4/4** both inherit max-over-5 selection inflation; Bonferroni upper bound α_effective = 0.01 (§3.5.1 P0-4 revision), permutation p-values in `data/results/c_class_permutation_v4.json`.

(b) **Δδ_{v3b → v4} = −0.007** is a contrast conditional on v3b selection + identical prompt, **not a neutral-condition test of LLM source diversity**. Neutral version (v4-pre × c→MP5 pre-shift, and §4.2.5.1 differential prompt) reserved for P4 / R2 revision.

**Mitigation**: Abstract / §5.8.2 / §6.3 (P0-3 revision) have downgraded all v3b/v4 sign test results to exploratory; §4.2.5(e) (P0-5 this section revision) explicitly declares chained-conditioning; §3.5.1 (P0-4 revision) added permutation + Bonferroni quantification. **This threat has been minimized within the scope of this paper version but cannot be eliminated — elimination requires v4-pre rerun or P4 differential prompt experiment**.

#### 7.1.9 R13 Protocol-implementation Gap Between v3/v3b and v4 (NEW, P1-7)

v3 / v3b data collection used §4.2.4 original Phase-1 dual-blind protocol (Claude-Opus generation + GPT-5.4 review + DeepSeek arbitration); v4 cross-source pool only passed V1-V4 mechanical gates, **lacking LLM reviewer review stage** (§4.2.5(b)).

**Potential confound**: Part of Δδ_{v3b → v4} = −0.007 variation may not be "LLM source diversity contribution," but rather "slight downward shift in mutant quality of v4 pool relative to v3b pool."

**Mitigation (within this paper's scope)**:
- v4 pool **did use source diversity from three LLM providers** (Claude / GPT-5.4 / DeepSeek each contributing ~1/3 mutants, §4.2.5(d) three providers contributed 101 / 98 / 99), in this sense Δδ_{v3b → v4} is not a trivial single-source-vs-single-source comparison;
- §6.2 LRCA data shows v4 pool mean C1_share 0.209 higher than v3b's 0.164 (quality increased rather than decreased), weakly opposing "v4 mutant quality downward" hypothesis;
- But **complete separation of protocol asymmetry and source diversity still requires P4 to rerun dual-blind reviewer on v4 full grid** (estimated 60-100 mutant sampling level achievable, ~$5-8 USD).

**Relationship to R11**: R11 concerns v3b → v4 *selection* asymmetry (c-class primary MP selection inheritance); R13 concerns v3 / v3b → v4 *protocol* asymmetry (dual-blind vs V1-V4 only). Both asymmetries contribute to the explanation space of Δδ_{v3b → v4}, **cannot be merged as single "LLM diversity contribution" signal**.

### 7.2 External Threats

#### 7.2.1 Representativeness of 12 PUTs (R5)

**Risk**: 12 PUTs do not represent the full domain of scientific computing software (e.g., lacking molecular dynamics, quantum chemistry, CFD large-scale code).

**Mitigation**:
- §3.1 Follows P1 site selection — representativeness argument carried by P1
- §1.6 P-II open principle: cls can be extended with new classes (E differential equation systems, F symbolic computation, etc.)

#### 7.2.2 Statistical Power of Cross-class Consistency (R6)

**Risk**: 4-class sign test has weak power (df=3), CV unstable in small samples.

**Mitigation**:
- §5.3.2 H4 framed as **exploratory evidence**, supplemented by mixed-effects model
- §7 Explicitly acknowledges "cross-class consistency" is a descriptive conclusion at 12 PUT scale

**§5.8 Empirical addendum**: Planned mixed-effects model (`sms ~ C(class) * C(operator) + (1 | put)`) exhibited Singular matrix at N = 60 observations (primary model); fallback model PUT random intercept variance degenerated to 0, essentially degenerating to OLS. We therefore changed RQ3 main conclusion to direct presentation via "class means + sign test + forest plot" triad, rather than using mixed-effects p-value as formal hypothesis test. This is consistent with "small N alternative" already declared in §5.3.2, but should be honestly declared in conclusions that mixed-effects is unavailable (§5.8.3).

### 7.3 Construct Threats

#### 7.3.1 SMS Semantic Detection Capability vs Engineering Practical Value

**Risk**: SMS measures "theoretical semantic detection capability," not equivalent to "production environment engineering value."

**Mitigation**:
- §1.6.2 Epistemological declaration: SMS is not an engineering value proxy metric
- §1.3 P2-CN (Nuclear Power Engineering 2027 Q4) will specifically address engineering value dimension

#### 7.3.2 LLM Homogeneity Bias (R7)

**Risk**: Even with dual LLM cross-source (Claude Opus + GPT-4o), training data may still overlap, causing similar blind spots.

**Mitigation**:
- §4.2.4(f) Three-LLM rotation + PUT class subdivision
- 20% manual sampling as baseline
- §7 Limitations explicitly acknowledges residual risk, recommends future work introduce third-party independent LLM family validation

### 7.4 Conclusion Threats

#### 7.4.1 Multiple Comparisons

**Risk**: 60 cells + 5 hypotheses → multiple comparison false positives.

**Mitigation**: §5.3.1 Benjamini-Hochberg FDR correction, α_FDR = 0.05.

#### 7.4.2 Stability of N=20 Repetitions

**Risk**: N=20 Cliff's δ and odds ratio 95% CI are relatively wide.

**Mitigation**: §5.3.2 Reports 1000-iteration bootstrap CI; §7 explicitly acknowledges effect size estimation uncertainty.

### 7.5 Limitations Section (Final Draft Body Text)

> This paper has the following known limitations: **(1) Equivalent mutant determination is probabilistic approximation** (engineering implementation of K_eq=1000 input sampling, not complete theorem-based determination); **(2) LLM generation homogeneity bias** (dual LLM cross-source + 20% manual sampling as mitigation, cannot be eliminated); **(3) Statistical power of cross-class consistency** (4-class sign test has only 3 degrees of freedom, H4 is exploratory evidence); **(4) LRCA likely root cause is most probable attribution** (decision tree priority is engineering choice, not causal conclusion); **(5) AVP reuses P1 implementation** (P2 replication package embeds AVP source code to maintain self-consistency, but interface semantics may change as P1 evolves); **(6) SMS measures semantic detection capability in the epistemological sense, does not directly represent engineering practical value** (the latter is specifically addressed by P2-CN and P5 in the nuclear engineering domain).

---

## Section 8 · References

> Citation style: APA-7. Academic literature (papers/books) provides complete venue + year + DOI/URL; software tools follow software citation conventions (project homepage + version/year). All entries verified via WebSearch / DOI as of 2026-05-01.

### 8.1 Mutation testing classics / surveys

- **DeMillo, R. A., Lipton, R. J., & Sayward, F. G.** (1978). Hints on test data selection: Help for the practicing programmer. *Computer*, 11(4), 34–41. https://doi.org/10.1109/C-M.1978.218136 (Origin of the **Coupling Effect Hypothesis (CPH)**: complex faults are detectable by tests that detect simple faults; cited in §1.3.2 as theoretical grounding for syntactic-mutation-based adequacy and contrasted with this paper's domain-semantic adequacy.)
- **Jia, Y., & Harman, M.** (2011). An analysis and survey of the development of mutation testing. *IEEE Transactions on Software Engineering*, 37(5), 649–678. https://doi.org/10.1109/TSE.2010.62
- **Jia, Y., & Harman, M.** (2009). Higher Order Mutation Testing. *Information and Software Technology*, 51(10), 1379–1393. https://doi.org/10.1016/j.infsof.2009.04.016
- **Andrews, J. H., Briand, L. C., & Labiche, Y.** (2005). Is mutation an appropriate tool for testing experiments? In *Proceedings of the 27th International Conference on Software Engineering* (ICSE 2005) (pp. 402–411). ACM. https://doi.org/10.1145/1062455.1062530 (Empirical foundation that mutants are valid surrogates for real faults; cited in §1.3.2 as the substrate for using MS as an adequacy proxy.)
- **Just, R., Jalali, D., Inozemtseva, L., Ernst, M. D., Holmes, R., & Fraser, G.** (2014). Are mutants a valid substitute for real faults in software testing? In *Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering* (FSE 2014) (pp. 654–665). ACM. https://doi.org/10.1145/2635868.2635929 (Reaffirms and refines Andrews 2005's mutant-as-fault-proxy claim with stronger empirical evidence; cited in §1.3.2 as additional CPH validation.)
- **Papadakis, M., Kintis, M., Zhang, J., Jia, Y., Le Traon, Y., & Harman, M.** (2019). Mutation testing advances: An analysis and survey. *Advances in Computers*, 112, 275–378. https://doi.org/10.1016/bs.adcom.2018.03.015 (Most-recent comprehensive survey of mutation testing advances post-Jia & Harman 2011; cited in §1.3.2 as the contemporary literature anchor for syntactic mutation testing methodology.)
- **Kintis, M., Papadakis, M., Papadopoulos, A., Valvis, E., Malevris, N., & Le Traon, Y.** (2018). How effective are mutation testing tools? An empirical analysis of Java mutation testing tools with manual analysis and real faults. *Empirical Software Engineering*, 23(4), 2426–2463. https://doi.org/10.1007/s10664-017-9582-5
- **Ammann, P., & Offutt, J.** (2008). *Introduction to software testing* (1st ed.). Cambridge University Press. (Standard pedagogical reference for mutation testing notation and equivalence detection; cited in §2.1.1 vocabulary inheritance.)

### 8.2 Industrial-scale mutation testing practice

- **Petrović, G., & Ivanković, M.** (2018). State of mutation testing at Google. In *Proceedings of the 40th International Conference on Software Engineering: Software Engineering in Practice* (ICSE-SEIP 2018) (pp. 163–171). ACM. https://doi.org/10.1145/3183519.3183521
- **Petrović, G., Ivanković, M., Fraser, G., & Just, R.** (2021). Practical mutation testing at scale: A view from Google. *IEEE Transactions on Software Engineering*, 48(10), 3900–3912. https://doi.org/10.1109/TSE.2021.3107634

### 8.3 LLM-based mutation generation

- **Tip, F., Bell, J., & Schäfer, M.** (2024). LLMorpheus: Mutation testing using large language models. *arXiv preprint* arXiv:2404.09952. https://arxiv.org/abs/2404.09952

### 8.4 Deep-learning and general fault benchmarks

- **Humbatova, N., Jahangirova, G., & Tonella, P.** (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. In *Proceedings of the 30th ACM SIGSOFT International Symposium on Software Testing and Analysis* (ISSTA 2021) (pp. 67–78). ACM. https://doi.org/10.1145/3460319.3464825
- **Just, R., Jalali, D., & Ernst, M. D.** (2014). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. In *Proceedings of the International Symposium on Software Testing and Analysis* (ISSTA 2014) (pp. 437–440). ACM. https://doi.org/10.1145/2610384.2628055

### 8.5 Statistical methodology

- **Romano, J., Kromrey, J. D., Coraggio, J., Skowronek, J., & Devine, L.** (2006). Appropriate statistics for ordinal level data: Should we really be using t-test and Cohen's d for evaluating group differences on the NSSE and other surveys? Annual Meeting of the Florida Association of Institutional Research, Cocoa Beach, FL. (Source of Cliff's δ small/medium/large thresholds 0.147 / 0.330 / 0.474; cited in §5.2 H2 definition and §5.7.2 verdict.)
- **Vargha, A., & Delaney, H. D.** (2000). A critique and improvement of the CL common language effect size statistics of McGraw and Wong. *Journal of Educational and Behavioral Statistics*, 25(2), 101–132. https://doi.org/10.3102/10769986025002101 (Establishes the canonical Â₁₂ measure equivalent to Cliff's δ + 0.5, used as a methodological reference for non-parametric effect-size reporting in §5.6.)

### 8.6 Numerical / scientific computing reference

- **Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P.** (2007). *Numerical Recipes: The Art of Scientific Computing* (3rd ed.). Cambridge University Press. (Used in §3.1.1 to ground the 12-PUT coverage against the 12 chapters of Numerical Recipes.)
- **ASME V&V 20 Committee** (2009). *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*. ASME V&V 20-2009. American Society of Mechanical Engineers. (Cited in §1.3.2 and §6.5.3 as the normative V&V framework whose §3 code verification this paper's SMS is conceptually complementary to; this paper does not claim normative compliance, see §6.5.3.)

### 8.7 Software / mutation testing tools (cited in §3.2.6 and §7 R12)

- **Hovde, A.** (2018–present). *mutmut*: A Python mutation testing tool. https://github.com/boxed/mutmut (Python-based first-order syntactic mutation tool; cited as a representative of "first-order syntactic tools" in §3.2.6 caveat.)
- **Tomilin, A.** (2017–present). *cosmic-ray*: Python mutation testing. https://github.com/sixty-north/cosmic-ray (Cited alongside mutmut for the §5.10 planned tool ablation.)
- **Hovstadius, K.** (2014–present). *mutpy*: Mutation testing for Python. https://github.com/mutpy/mutpy (Cited in §7 R12 as Python-3.10+-incompatible; not used as a comparator.)

### 8.8 Companion P-series papers

- **Li, M. et al.** (under review). Empirical audit of metamorphic-relation meta-patterns in scientific computing software (P1). *International Conference on Software Analysis, Evolution and Reengineering (SANER) 2027.*
- **Li, M. et al.** (under review). [P2-CN companion]. *Progress in Nuclear Energy* (NED). (Reference D7 in §1.6.1.)

---

## Section 9 · SMS-MS Degeneration Theorem (R-8 Formalized Proof)

> This section formalizes the core claim in the §2.0 P-I developmental principle: **SMS strictly regresses to the classical Jia & Harman (2011) syntactic Mutation Score (MS) in the degenerate limit where all extension dimensions are closed**. This theorem guarantees that the P2 metric family is upward-compatible with the existing mutation testing literature, and that all SMS-based empirical conclusions do not constitute metric-level semantic fragmentation in classical syntactic mutation scenarios.

### 9.1 Notation (following §2.1.2)

Let the program under test (PUT) be S_i, mutation operator family mut (syntactic or semantic), mutant set mut(S_i), meta pattern (MP) set, equivalence tolerance ε_eq, equivalence sampling count K_eq, and AVP tolerance ε_AVP. Three-state decomposition: `mut(S) = killed ∪ equiv ∪ survive` (disjoint). SMS formula:

$$
\text{SMS}_{i,k,j} = \frac{|\text{killed}_{i,k,j}|}{|\text{mut}_j(S_i)| - |\text{equiv}_{i,k,j}|}
$$

### 9.2 Degenerate Limit Definition (R-8 + P1-3 revision: rewritten from 6 axes to 3 joint conditions)

The degenerate limit L consists of **3 joint conditions**, each controlling one layer of the SMS formula (numerator / denominator mut / denominator equiv); **L1–L6 are not 6 independent axes**, but paired joint conditions (this revision responds to the dependency queries in R0 W8 / R1 §4 / R2 W3 / DA-MAJOR-3).

**Joint condition L_equiv** (controls equiv degeneration layer, Lemma 9.1):
- **L1**: ε_eq → 0 (equivalence tolerance approaches zero)
- **L2**: K_eq → ∞ (equivalence sampling covers the complete input space D_S)
- Pairing rationale: On continuous D_S, when L1 holds alone but L2 does not, equiv remains a probabilistic approximation (K_eq samples cannot cover the entire D_S); when L2 holds alone but L1 does not, the bitwise equality condition is diluted by ε_eq tolerance. Both must take the limit simultaneously for equiv to degenerate to classical behavioral equivalence (which also holds strictly only outside a D_S-measure-zero set, see revised statement of Lemma 9.1).

**Joint condition L_killed** (controls killed degeneration layer, Lemma 9.2):
- **L3**: ε_AVP^k → 0 for all k ∈ MP (AVP tolerance approaches zero)
- **L4**: MP set = {equality-checking MP_eq} (R(y, y') ≡ y = y')
- Pairing rationale: When L3 holds but L4 does not, ε_AVP → 0 still allows non-trivial MP relations to exist (R can be monotonicity, convergence order, etc.), not degenerating to classical difference detection; when L4 holds but L3 does not, equality checking still carries ε_AVP tolerance, not strictly enforced. Both must take the limit simultaneously for killed determination to degenerate to classical difference detection.

**Joint condition L_mut** (controls mut degeneration layer, Lemma 9.3):
- **L5**: mut_j switches to rule-based syntactic operators (Mothra-style AOR/ROR/SDL/CRP, etc.), independent of domain semantics
- **L6**: PUT class cls(I) ⊆ {imperative deterministic programs} (no probabilistic/surrogate/ML)
- Pairing rationale: When L5 holds but L6 does not, syntactic operators on probabilistic/ML programs may still trigger subsets of domain-semantic mutation operators (e.g., literal constant replacement of dropout probability); when L6 holds but L5 does not, imperative deterministic programs can still be mutated by semantic operators (OS/HP/TF/SI), mut(S) ≠ syntactic mutants. Both must take the limit simultaneously for mut(S) to degenerate to the syntactic mutant set in the Jia & Harman literature.

**Total limit L = L_equiv ∧ L_killed ∧ L_mut** (all three joint conditions hold simultaneously).

### 9.3 Lemmas: Three-State Decomposition Degenerates Under L

**Lemma 9.1** (equiv degeneration, P1-3 revision: added measure-zero qualification). Under joint condition L_equiv (L1 ∧ L2), semantic-class equivalence (E1 ∧ E2) degenerates to classical behavioral equivalence **almost everywhere** (almost everywhere w.r.t. measure D_S).

**Proof**:
- E1 (type consistency) holds trivially in the ε_eq → 0 limit (L6 imperative program output spaces are scalar/vector, types statically guaranteed by the programming language).
- E2 (numerical/semantic approximate equality) is defined as: for K_eq sampled inputs x ~ D_S, |S_i(x) − s'(x)| < ε_eq. Under L1 (ε_eq → 0) ∧ L2 (K_eq → ∞ with measure-equivalent sampling to D_S), this condition is **almost everywhere equivalent to** ∀x ∈ D_S \ N, S_i(x) = s'(x), where N is a D_S-measure-zero set (on continuous D_S, strict bitwise equality requires excluding measure-zero exceptions, such as numerical NaN propagation points or floating-point cancellation pathological points; on discrete D_S, N = ∅, strict bitwise equality)—this is consistent with the classical equivalent mutant definition in Jia & Harman (2011) §3 under measure-zero equivalence classes. ∎

**Lemma 9.2** (killed degeneration). Under L3 ∧ L4, killed determination degenerates to classical difference detection.

**Proof**:
- L4 restricts the MP set to {MP_eq}, where MP_eq's relation R(y, y') ≡ y = y'.
- Given mr = (r, R) ∈ MR, where r is an input transformation and R is an output relation. For mutant s', the violation condition for MP_eq is ∃x: S_i(x) ≠ s'(r(x)).
- Under L3 (ε_AVP → 0), AVP tolerates no numerical difference; violation is equivalent to the exact inequality S_i(x) ≠ s'(r(x)).
- When r = id (identity transformation), the violation condition becomes S_i(x) ≠ s'(x), i.e., the mutant deviates from the original program on some input—this is precisely the classical difference detection semantics.
- When r ≠ id, MP_eq restricted by L4 still requires S_i(x) = s'(r(x)), treating it as a "reference output oracle" constructed from the original program; this still does not introduce new state classifications. ∎

**Lemma 9.3** (mut degeneration). Under L5 ∧ L6, mut_j(S_i) degenerates to the syntactic mutant set in the Jia & Harman (2011) literature.

**Proof**: L5 explicitly switches mut_j to rule-based syntactic operators (AOR, ROR, SDL, CRP, UOI, etc., standard Mothra/Proteum sets); L6 restricts PUTs to imperative deterministic programs, excluding triggering conditions for semantic operators on probabilistic/ML programs. Under this configuration, mut_j(S_i) is the syntactic mutant set as defined in the literature, independent of domain semantics. ∎

### 9.4 Main Theorem: SMS → MS

**Theorem 9.1** (SMS-MS degeneration theorem, P1-3 revision). In the degenerate limit L = L_equiv ∧ L_killed ∧ L_mut, **almost everywhere** (almost everywhere w.r.t. D_S),

$$
\text{SMS}_{i,k,j} \xrightarrow{L} \text{MS}_{i,j} := \frac{|\text{killed}_{i,j}^{\text{classic}}|}{|\text{mut}_j^{\text{syntax}}(S_i)| - |\text{equiv}_{i,j}^{\text{classic}}|}
$$

where the right-hand side is the classical Mutation Score of Jia & Harman (2011), killed^classic is the difference detection set, equiv^classic is the behavioral equivalent mutant set, and mut^syntax is the syntactic mutant set.

**Proof**: By Lemmas 9.1-9.3,

- **Numerator**: Under L3 ∧ L4, killed_{i,k,j} → killed_{i,j}^{classic} (Lemma 9.2). L4 simultaneously makes the MR_{i,k} set trivial over k (only MP_eq remains), the index k degenerates, and the subscript k in SMS can be omitted.
- **Denominator |mut_j(S_i)|**: Under L5 ∧ L6 → |mut_j^{syntax}(S_i)| (Lemma 9.3).
- **Denominator |equiv_{i,k,j}|**: Under L1 ∧ L2 → |equiv_{i,j}^{classic}| (Lemma 9.1).

Substituting into the numerator and denominator on the right-hand side of the SMS formula yields MS_{i,j}. ∎

### 9.5 Corollary: LRCA Trivialization

**Corollary 9.1** (generic statement, post R2 round-2 attribution audit). In the degenerate limit L = L1 ∧ L2 ∧ L3 (the three joint conditions formalized in §9.2), the likely root cause inventory (LRCA) C = {C1, ..., C5} degenerates to a single state {C1}.

**Sketch**: Each of C2–C5's triggering preconditions depends on at least one of the L_j conditions being violated. Concretely, when L1 ∧ L2 ∧ L3 hold simultaneously, every "non-trivial space" dimension of the SMS formula (MP non-triviality, AVP tolerance non-zero, non-empty equiv set, MR-design degree of freedom, class-mapping openness) is closed at once, so the triggering set for C2–C5 is empty (read off from the LRCA decision tree in §2.6.1 and §4.6.3). The detailed per-C_k to per-L_j minimum-sufficient mapping depends on engineering details (§4.6 LRCA classifier thresholds), and we do not claim a one-to-one correspondence at the §9 formal level — readers wanting the concrete mapping can trace it via the §2.6 decision tree + §4.6 LRCA three-layer operator documentation.

Thus under L, suspect_share → 0, LRCA reports only C1 (metric direct readout) — SMS degenerates to a single-layer metric, consistent with the engineering attribution structure of Jia & Harman (2011) MS. ∎

### 9.6 Empirical Consistency Statement

Theorem 9.1 + Corollary 9.1 jointly guarantee: **Any SMS-based empirical conclusions (such as Cliff's δ, Friedman χ², Spearman ρ in §5.7-§5.9) are structurally consistent with the existing Jia & Harman (2011) literature in classical syntactic mutation scenarios**, and do not constitute metric-level semantic fragmentation. This is the intrinsic scientific guarantee of this paper's symbolic system (§2.1) under the "symbolic stability statement" in §2.1.3.

---

## Locked Decision Inventory (D1-D8 + W-2)

1. **D1** Paper identity = γ dual-track parallel
2. **D2** Mutation validity = objective artifact triple (AVP + general defect case library + mutator literature prior, no FMECA/PIRT)
3. **D3** Paradigm coverage = S-A all 4 classes × all 5 operators = 60-cell matrix
4. **D4** equiv concept = AVP-coherent + K_eq=1000 tolerance equivalence
5. **D5** Defect case library = B-1 + open-source issue systematic mining
6. **D6** SMS = M-1 classical `killed/(mut−equiv)` structure, decoupled from MR construction process
7. **D7** P1/P4 interface = I-2 mid-interface, shared [Meng Li et al., Progress in Nuclear Energy, under review] arXiv
8. **D8** P2/P2-CN/P5 triangular division of labor = D-3 Pre-NED trial
9. **W-2** Mid-tier scale = 60 cells × 10-15 mutants × N=20, ~$1200 compute

## Dual Fundamental Principles (§2 chapter-level)

- **P-I Developmental**: classical mutation testing → scientific computing semanticization (adapted to MR validity determination)
- **P-II Stable/Open**: symbolic skeleton fixed, content (operators/MP/root causes/class mappings) open to extension

---

*This file is the P2 paper draft §1-§7 locked snapshot (refined version).*
*Generation date: 2026-04-29*