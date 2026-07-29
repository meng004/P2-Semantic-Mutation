# THM-WIN: Tolerance-Indexed Detection Window (with REM-FPOS and REM-FNEG)

Status: internal-review (awaiting REVIEW CHECKPOINT T3, joint sign-off with
T4)

Normative sources: master plan §0.2–§0.5 (36-symbol closed set) and
[`notation_registry.md`](notation_registry.md). Audited manuscript baseline:
`submission/TOSEM_regular_20260706/main.tex`
(SHA-256 `8c5839319455b3080e5b6915e1ef821b6b931ad5563efa558e891e97a7c7b0f8`).
No symbol outside the registry is introduced. Labels `[THM-WIN]`,
`[REM-FPOS]`, `[REM-FNEG]`, `DEF-10..13` are placeholders replaced by body
numbering in Task T6.1.

## 1. Task T3.1: asset inventory (current Proposition 2 and its anchors)

**Latency window (main.tex:817–822), verbatim:**

> "For a violation-magnitude parameter $\varepsilon$ of an edit template, the
> *latency window* is the interval
> $(\varepsilon_{\mathrm{tol}}, \varepsilon_{\mathrm{crash}})$: above the
> tolerance at which the $\psi$-checker witnesses the violation (S3), below
> the threshold at which the container crashes (S4). An empty window
> certifies non-realizability of the template at that site."

**Strong MR / weak MR / strong boundary (main.tex:884–906), abridged:**

> "…the correct $P$ reproduces the operator's algebraic invariant only up to
> a discretisation residual… Fixing $\varepsilon_{\mathrm{tol}}$, call $r$
> *strong* on $P$ when the correct $P$ satisfies $r$ within
> $\varepsilon_{\mathrm{tol}}$ (its residual stays below
> $\varepsilon_{\mathrm{tol}}$ under refinement)… call $r$ *weak* on $P$ when
> the correct $P$'s residual exceeds $\varepsilon_{\mathrm{tol}}$, so that the
> correct program is itself flagged because the discretisation, not a fault,
> breaks the invariant. The *strong boundary* is the
> $(\varepsilon_{\mathrm{tol}}, \text{resolution})$ locus separating the two
> regimes…"

**Proposition 2 (main.tex:908–934), abridged:**

> "Relative to $(\varepsilon_{\mathrm{tol}}, P)$ the duality of Theorem 2 has
> two failure modes. (i) *False positive (weak MR).* When $r$ is weak the
> correct $P$ violates $r$ and a non-fault is reported… (ii) *False negative
> (surviving non-equivalent mutant).* A semantically active mutant… can leave
> every invariant… satisfied within $\varepsilon_{\mathrm{tol}}$… and so
> survive… when its signature lies below $\varepsilon_{\mathrm{tol}}$ it is a
> *tolerance fault*. The two modes are coupled through
> $\varepsilon_{\mathrm{tol}}$: tightening it shrinks the false-negative set…
> but grows the false-positive set… *Proof.* (i) and (ii) instantiate the
> Definition: weakness places the correct program's residual above
> $\varepsilon_{\mathrm{tol}}$, and coincidental satisfaction places the
> mutant's signature below it; monotonicity of both sets in
> $\varepsilon_{\mathrm{tol}}$ holds because both membership predicates are
> threshold comparisons against the same $\varepsilon_{\mathrm{tol}}$."

Supporting anchors: kill predicate with its pass-on-original conjunct
(main.tex:620–626); semantic-mutant conditions S1–S5, with S4 latency at
main.tex:804–807 (crash-oracle exclusion); empirical boundary study §4.8
(main.tex:1973–2057; PINN false-positive instance 2019–2030 and 2045–2056;
numpy-RNG false-negative instance 2032–2043).

**Informal assumptions Proposition 2 relies on (distilled):**

1. A single scalar tolerance $\varepsilon_{\mathrm{tol}}$ governs both flag
   decisions; both membership predicates are threshold comparisons against
   that same tolerance (stated inside its proof).
2. The correct program carries a well-defined discretisation residual per
   $(\varepsilon_{\mathrm{tol}}, \text{resolution})$ locus — the quantity
   THM-WIN names $\Delta_r$ — but Prop 2 never separates it from the
   mutant's signature quantitatively.
3. The mutant's detectability is decided by comparing a scalar "signature"
   against $\varepsilon_{\mathrm{tol}}$ — the quantity THM-WIN names
   $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$.
4. Execution noise is absent (implicit determinism); repeats, stochastic
   PUTs, and observation error are outside Prop 2's scope.
5. No upper edge: the crash threshold $\varepsilon_{\mathrm{crash}}$ lives in
   the latency-window definition and S4, not in Prop 2 itself.

THM-WIN upgrades Prop 2 in place: it makes (2)–(4) explicit ($\Delta_r$,
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$, $\bar\eta$), turns the two
qualitative failure modes into quantitative two-sided bounds, and attaches
the S4 upper edge.

## 2. Definitions consumed (registry references)

- **DEF-05 (exact checker; presupposed).** $r$ is an exact checker for
  stratum $\psi_j$ ⟺ $\mathrm{flag}(r,P')\iff[\![P']\!]\not\models_\tau\psi_j$,
  with $\mathrm{flag}(r,P')\equiv(J_r=\mathrm{fail})$. Operational reading
  used throughout this draft: the checker computes the relation residual on
  the executed tuple and sets $J_r=\mathrm{fail}$ iff that residual
  **strictly exceeds** $\varepsilon_{\mathrm{tol}}$ (consistent with the
  latency-window prose "above the tolerance", main.tex:819–821, and with the
  pipeline's `|LHS − RHS| ≤ ε ⇒ pass` convention in
  `src/p2/avp/mp1_conservation.py`).
- **DEF-10 (violation magnitude).**
  $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\ge 0$ is the structural
  violation magnitude the edit induces at stratum $\psi$: the noise-free,
  discretisation-free size of the invariant violation, measured on the
  stratum's violation axis. For parametric violation templates it is the
  *realized* magnitude measured by a direct invariant-violation functional
  (argumentation plan F-10 protocol), not the nominal injected parameter.
- **DEF-11 (noise model).** Each program execution's observed output carries
  noise $\eta$ with $|\eta|\le\bar\eta$. Deterministic PUTs:
  $\bar\eta=\eta_{\mathrm{det}}$ (rounding + observation). Stochastic PUTs
  under the §2.3 $N$-repeat aggregation ($N=20$ in the pipeline):
  $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$, where
  $\sigma_{\mathrm{out}}$ is the output standard deviation and $c$ the
  concentration constant of the aggregator. Reading (CHECKPOINT T3 note B3):
  for unbounded noise distributions the bound $|\eta|\le\bar\eta$ is a
  concentration-style model assumption, and the stochastic-case statements
  hold with the confidence level attached to the choice of $c$; "guaranteed"
  in REM-FNEG is guaranteed under the model, i.e. at that confidence.
  Budget correspondence to the MR-validity theory v3.1 §4.3:
  $\eta_{\mathrm{det}}\approx\tau_{\mathrm{round}}+\tau_{\mathrm{obs}}$; the
  stochastic term $c\sigma_{\mathrm{out}}/\sqrt N$ ≙ $\tau_{\mathrm{stat}}$;
  $\Delta_r$ (below) is dominated by $\tau_{\mathrm{disc}}$.
- **DEF-12 (structure-preservation residual and margin).**
  $\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)$, the correct-program
  structure-preservation residual under ideal (noise-free) semantics — the
  instantiation of $\Delta(S,P)$ from the MR-validity theory v3.1 on the
  structure inducing $r$. Margin: $\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r$.
- **DEF-13 (detection window).** The window is
  $(\varepsilon_{\mathrm{lo}},\ \varepsilon_{\mathrm{crash}})$ with lower
  edge $\varepsilon_{\mathrm{lo}}:=\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
  and upper edge the S4 crash threshold $\varepsilon_{\mathrm{crash}}$
  (main.tex:817–822).

Residual-notation convention (no new symbol): $\varepsilon_r(x;Q)$ denotes
the ideal (noise-free) relation residual of $r$ at input $x$ for program
$Q$; when a residual is said to be *computed on the executed tuple*, it means
the ideal residual perturbed by the tuple's aggregate execution noise, which
for a pairwise (source, follow-up) tuple is bounded by $2\bar\eta$ (§5,
H-a).

## 3. Statements (finalised baseline, master plan Phase T3)

```latex
\textbf{Theorem [THM-WIN] (tolerance-indexed detection window).} Let $m_{\mathrm{mut}}$ carry
violation magnitude $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$ at stratum $\psi$, let $r$ be an exact
checker with tolerance $\varepsilon_{\mathrm{tol}}$, let
$\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)$ be the correct-program
structure-preservation residual (the instantiation of $\Delta(S,P)$ from the
MR-validity theory on the structure inducing $r$; here $P^\star$ is the
cell's original program, assumed correct per S2), and $|\eta|\le\bar\eta$
the execution noise, with the violation functional $L_r$-Lipschitz in
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$. Assume the additive
residual budget H-a, the non-degenerate-margin regime R1, and, for (i),
magnitude realization H-d (Appendix hypotheses). Then
(i) $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})>\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$ implies
$r$ kills $m_{\mathrm{mut}}$; (ii) $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})<\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
implies $r$ does not kill $m_{\mathrm{mut}}$; (iii) with the crash threshold
$\varepsilon_{\mathrm{crash}}$ (S4), the kill region lies within
$(\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta,\ \varepsilon_{\mathrm{crash}})$.

\textbf{Remark [REM-FPOS] (weak-MR false positive).} If
$\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r<0$ the correct program is flagged
whenever validation executes an input whose residual exceeds
$\varepsilon_{\mathrm{tol}}+2\bar\eta$ (such inputs exist since $\Delta_r$
is a supremum; in the band up to $2\bar\eta$ noise can mask the flag), and
$r$ exits the admissible evaluation set (empirically: the PINN case).

\textbf{Remark [REM-FNEG] (stochastic false negative and repeat prescription).}
For stochastic PUTs $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$;
guaranteed detection at target magnitude $\varepsilon^\dagger$ requires
$N\ge\bigl(2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})\bigr)^2$
(empirically: the RNG case).
```

(R-9: the two Remarks live inside the THM-WIN theorem environment with no
independent numbering; their proof obligations PO-WIN-5/6 remain.
Amendments A4/A5 (2026-07-29, T6.2 independent audit): A4 hoists H-a/R1/H-d
into the stated hypotheses and pins $P^\star$ to the cell's original program;
A5 conditions REM-FPOS's flagging on validation executing an
above-threshold-plus-noise input, master-first synced.)

**Scope note (execution multiplicity).** The constant $2\bar\eta$ is the
noise budget of a *pairwise* relation tuple: one source and one follow-up
execution, each contributing $\le\bar\eta$ (triangle inequality twice). This
covers the relations that dominate the manuscript catalogue: the MP\_1
conservation checks, the per-pair residuals of the MP\_2/MP\_5 Wilcoxon
verifiers, and the MP\_4 trajectory comparisons are all pairwise
(`src/p2/avp/mp1_conservation.py`, `mp2_5_wilcoxon.py`, `mp4_dtw.py`). For a
relation whose residual functional consumes $p$ program executions, each
residual 1-Lipschitz in each observed output, the budget generalizes to
$p\bar\eta$ and every occurrence of $2\bar\eta$ in the statement and proofs
is replaced by $p\bar\eta$. The catalogue contains one such family: the
MP\_3 convergence-order relation evaluates the program at $p=4$ grid
resolutions (`src/p2/avp/dispatcher.py:15-16`, `mp3_convergence.py`) and its
verdict is a log–log regression slope, whose noise propagation additionally
carries a design-dependent conditioning constant; its window bounds must be
read with the $p=4$ budget and that constant.

## 4. The non-degenerate-margin regime (H-c; the regime cited by LEM-WIT and THM-GAP)

**Definition (non-degenerate-margin regime; the tolerance regime of
Theorem [THM-WIN](iii); two clauses per CHECKPOINT T3 repair B2).** The pair
$(r, P^\star)$ is in the *non-degenerate-margin regime* iff

- **(R1) margin dominance:**
  $\mu_r \;=\; \varepsilon_{\mathrm{tol}}-\Delta_r \;>\; 2\bar\eta$ (strict;
  for a $p$-execution relation read $2\bar\eta$ as $p\bar\eta$ throughout,
  §3 scope note), and
- **(R2) $\varepsilon_{\mathrm{eq}}$-separation:** on the executed tuples,
  no relation residual lies within $\varepsilon_{\mathrm{eq}}$ of the
  decision threshold $\varepsilon_{\mathrm{tol}}$, so the verdict functional
  is invariant under pointwise obs-output perturbations of magnitude
  $\le\varepsilon_{\mathrm{eq}}$.

R1 makes the correct program pass robustly: every residual computed on an
executed tuple of $P^\star$ is at most
$\Delta_r+2\bar\eta<\varepsilon_{\mathrm{tol}}$, so
$J_r(P^\star)=\mathrm{pass}$ on every evaluation. R2 is the verdict-stability
clause; it is logically independent of R1 (R1 bounds residual *levels*, R2
bounds their *distance to the threshold*) and is mild in the pipeline, where
$\varepsilon_{\mathrm{eq}}=\varepsilon_{\mathrm{AVP}}=10^{-6}$ sits far below
the working margins. Consumption map: THM-WIN(i) and (iii) and THM-GAP's
premise (iii) consume R1 (with H-a); LEM-WIT's stability hypothesis
(amendment A1) consumes R2. Both external citations resolve here: THM-GAP's
"non-degenerate tolerance margins (Theorem [THM-WIN])" = R1 imported at
every $r\in R$ together with H-a (`thm_gap.md` §3, repair B1); LEM-WIT's
"stable under pointwise obs-output perturbations … the regime of
Theorem [THM-WIN](iii)" = R2 (`thm_interval.md` §2–§3).

## 5. Hypotheses and proofs

### PO-WIN-1: hypothesis formalization and satisfiability

**H-a (additive residual budget).** On the executed tuple at input $x\in
D_r$, the residual the checker computes for the mutant satisfies

$$\bigl|\varepsilon_r(x;m_{\mathrm{mut}})-\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\bigr|\;\le\;\Delta_r+2\bar\eta,$$

where here $\varepsilon_r(x;m_{\mathrm{mut}})$ is read as the executed
(noise-bearing) residual. Derivation from the decomposition plus the
triangle inequality, applied twice: (1) the ideal mutant residual decomposes
into the structural violation contribution
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$ plus the
structure-preservation residual, and the latter is bounded by $\Delta_r$
because the mutant *inherits the correct program's discretisation residual*
— the edit perturbs the declared structure (the invariant), not the
discretisation, so the non-structural residual sources are those of
$P^\star$, bounded by the sup defining $\Delta_r$; (2) the executed tuple
aggregates two program executions (source and follow-up of the MR tuple),
each observation carrying noise $\le\bar\eta$, so the executed residual
deviates from the ideal one by at most $2\bar\eta$. (For $p$-execution
relations replace $2\bar\eta$ by $p\bar\eta$; §3 scope note.)

**H-b (Lipschitz transfer; division of labour).** The violation functional
is $L_r$-Lipschitz in $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$: a
change of the injected magnitude moves the realized violation-axis value at
a bounded rate. H-b is used **only** for the empirical dose–response
predictions (§6): it guarantees a monotone, bounded-slope transfer between
the nominal-parameter axis and the realized-magnitude axis, so the window
predicted on the realized axis induces a window on the dose ladder. H-b is
**not needed** for bounds (i)–(iii), which are stated directly on the
realized axis $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$. The empirical
protocol measures $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$ on the
realized axis via a direct invariant-violation functional, independent of
the kill-deciding checker (F-10), where the transfer is the identity by
construction; $L_r$ governs the nominal→realized transfer only.

**H-c (non-degenerate margin / admissibility).** $\mu_r>2\bar\eta$ (§4).
Consumed by (i) (the pass-on-original conjunct of the kill predicate) and
named by (iii)'s regime; not needed for (ii).

**H-d (magnitude realization).** The executed tuple realizes the declared
magnitude: the input $x$ at which the checker evaluates satisfies H-a with
the mutant's full $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$. For
uniform/global parametric violation templates — the dose–response operators,
which perturb a global constant of the computation — every admissible input
realizes the declared magnitude, so H-d is automatic. In general a mutant
may express its violation only on part of $D_r$; on tuples that do not
realize it, (i)'s premise does not apply and detection reverts to a
finite-input-search question. This is an honest search-residual caveat, not
a window failure: (ii) and (iii) are unaffected (they bound the residual
from above, and an unrealized magnitude only lowers it).

**Per-PUT-class satisfiability (core, 12 lines).**
Class A (numeric/dynamical: Lorenz-63, LU, FDM): H-a holds with
$\Delta_r$ = discretisation residual (v3.1 $\tau_{\mathrm{disc}}$);
$\bar\eta=\eta_{\mathrm{det}}$ (deterministic); H-b smooth on finite
horizons (large constant for chaotic flows); H-d automatic for global
templates.
Class B (statistical: Beta-Binomial, MH, MC): H-a holds on the
$N$-repeat aggregated observable; $\bar\eta$ takes the stochastic form
(DEF-11); H-b holds in expectation; H-d automatic for parameter templates.
Class C (surrogate: GPR, PCE, shallow-NN): H-a holds w.r.t. the trained
model's residual; retraining inside the mutant makes H-b fragile for
non-convex trainers (§8); H-d automatic for global templates.
Class D (ML classification: MLP, SVM, LogReg): outputs are probability
functionals; H-a holds on those observables, but saturation can flatten the
violation axis, degrading H-b (§8); the MP\_2/MP\_5 Wilcoxon aggregation is
a hypothesis test whose reading as a DEF-05 threshold functional is the
exact-checker idealization already declared in THM-GAP premise (ii). ∎

### PO-WIN-2: must-kill bound (i)

Assume H-a, H-c, H-d and
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})>\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$.
By H-a (lower side), the executed residual satisfies
$\varepsilon_r(x;m_{\mathrm{mut}})\ge\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})-\Delta_r-2\bar\eta>\varepsilon_{\mathrm{tol}}$,
so the checker flags: $J_r(m_{\mathrm{mut}})=\mathrm{fail}$ (DEF-05, strict
exceedance). By H-c, every executed residual of $P^\star$ is
$\le\Delta_r+2\bar\eta<\varepsilon_{\mathrm{tol}}$, so
$J_r(P^\star)=\mathrm{pass}$. The kill predicate (main.tex:620–626) requires
exactly these two conjuncts — pass on the original and fail on the mutant —
for some relation in the family; $r$ supplies both, hence
$\mathrm{killed}(m_{\mathrm{mut}})$ holds and $r$ kills $m_{\mathrm{mut}}$. ∎

### PO-WIN-3: must-not-kill bound (ii)

Assume H-a and
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})<\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$.
By H-a (upper side), on every executed tuple
$\varepsilon_r(x;m_{\mathrm{mut}})\le\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})+\Delta_r+2\bar\eta<\varepsilon_{\mathrm{tol}}$,
so the checker never flags the mutant: $J_r(m_{\mathrm{mut}})\ne\mathrm{fail}$
on any evaluation. The kill predicate's second conjunct
($\mathrm{AVP}(m_{\mathrm{mut}},\cdot)=\mathrm{fail}$) therefore fails for
$r$, and $r$ does not kill $m_{\mathrm{mut}}$ — regardless of the verdict on
$P^\star$, so H-c is not needed here. ∎

### PO-WIN-4: window inclusion (iii)

Lower edge: by the contrapositive of (ii), a killed
$m_{\mathrm{mut}}$ has
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\ge\varepsilon_{\mathrm{lo}}:=\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
(DEF-13); at equality H-a gives executed residual
$\le\varepsilon_{\mathrm{tol}}$, which under DEF-05's strict-exceedance
convention still yields no flag, so killed implies the strict inequality
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})>\varepsilon_{\mathrm{lo}}$.
Upper edge: a candidate with magnitude $\ge\varepsilon_{\mathrm{crash}}$
crashes the container, violating S4 latency (main.tex:804–807), and is
excluded from the admitted universe by the crash-oracle exclusion — the
latency window (main.tex:817–822) is exactly this interval. Hence the kill
region, as a subset of admitted, semantically-killed magnitudes, is
contained in $(\varepsilon_{\mathrm{lo}},\ \varepsilon_{\mathrm{crash}})$. ∎

### PO-WIN-5: REM-FPOS

$\mu_r<0\iff\Delta_r>\varepsilon_{\mathrm{tol}}$. Since $\Delta_r$ is a sup
over $D_r$, $\sup_{x\in D_r}\varepsilon_r(x;P^\star)>\varepsilon_{\mathrm{tol}}$
implies some $x\in D_r$ has ideal correct-program residual exceeding
$\varepsilon_{\mathrm{tol}}$ (no sup-attainment needed); whenever validation
executes such an input, the correct program is flagged (guaranteed when the
residual exceeds $\varepsilon_{\mathrm{tol}}+2\bar\eta$; between
$\varepsilon_{\mathrm{tol}}$ and $\varepsilon_{\mathrm{tol}}+2\bar\eta$
noise can mask the flag — and the validation inputs must hit such residuals
at all: a one-sentence sampling caveat, stated honestly). A flagged correct
program breaks the kill predicate's pass-on-original conjunct
(main.tex:620–626), so $r$ can contribute no kills, and under the upstream
MR-validation semantics (§2.9, main.tex:884–906: a weak MR flags the
correct program) $r$ exits the admissible evaluation set. Empirical
instance: the PINN case at $\varepsilon_{\mathrm{tol}}=10^{-4}$ (§4.8,
main.tex:2019–2030). ∎

### PO-WIN-6: REM-FNEG

Substitute $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$
(DEF-11) into the must-kill premise (i) at target magnitude
$\varepsilon^\dagger$:
$\varepsilon^\dagger>\varepsilon_{\mathrm{tol}}+\Delta_r+2(c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}})
\iff 2c\sigma_{\mathrm{out}}/\sqrt N<\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}}
\iff \sqrt N>2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})$,
**provided the denominator is positive**, i.e.
$\varepsilon^\dagger>\varepsilon_{\mathrm{tol}}+\Delta_r+2\eta_{\mathrm{det}}$
(side condition; if it fails, no repeat budget guarantees detection).
Squaring gives the stated bound; "requires $N\ge$" is the necessary-condition
reading, and sufficiency holds with strict inequality — for integer $N$ the
two coincide unless the square is exactly integral. Empirical instance: the
numpy-RNG case (§4.8, main.tex:2032–2043), where on the structural MR axes
the effective $\varepsilon^\dagger$ lies below
$\varepsilon_{\mathrm{tol}}+\Delta_r+2\eta_{\mathrm{det}}$ — the side
condition fails, no $N$ rescues detection, and the fix is a different
observable (the odd-bit-fraction discriminator), not more repeats. ∎

## 6. Empirical predictions (derivation source for EXP-DOSE / H-DOSE / H-DOSE-CTR)

- **Monotone dose–response (H-DOSE).** Along the *realized* axis
  $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$, the kill probability is
  monotone non-decreasing: below $\varepsilon_{\mathrm{lo}}$ it is 0 by (ii),
  above $\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$ it is 1 by (i), and
  in between the flag event is a threshold exceedance whose probability is
  non-decreasing under H-a's location-shift structure with
  magnitude-independent noise. On the nominal-parameter axis the same shape
  follows through H-b's monotone bounded-slope transfer.
- **Transition geometry (H-DOSE-CTR).** The transition region has width
  $O(\Delta_r+\bar\eta)$ — the gap between the two guaranteed regions is
  $2(\Delta_r+2\bar\eta)$ — and is centered at
  $\approx\varepsilon_{\mathrm{tol}}$; the center-containment prediction is
  transition center $\in\varepsilon_{\mathrm{tol}}\pm(\Delta_r+2\bar\eta)$.
- **Consumption line.** These two bullets are the theory-side derivation
  source for the argumentation plan's EXP-DOSE experiment: H-DOSE (headline,
  isotonic-vs-constant permutation test) and H-DOSE-CTR (secondary B-2,
  per-curve center containment in
  $\varepsilon_{\mathrm{tol}}\pm(\Delta_r+2\bar\eta)$), with the horizontal
  axis measured on the realized violation functional (F-10), matching the
  axis on which THM-WIN is stated
  (`docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`, RQ2 row).
- **Boundary cases as Remark instances.** The PINN case is REM-FPOS
  realized: the soft-BC residual $\approx5\times10^{-4}$ *is* a $\Delta_r$
  exceeding $\varepsilon_{\mathrm{tol}}=10^{-4}$ ($\mu_r<0$: legitimately
  trained model flagged), while at $\varepsilon_{\mathrm{tol}}=10^{-3}$ the
  margin turns positive and it survives (§4.8, main.tex:2019–2030,
  2045–2056). The RNG case is REM-FNEG realized: the fault signature on the
  structural observables sits below the detectable threshold, the PO-WIN-6
  side condition fails, and the buggy release survives any repeat budget
  (§4.8, main.tex:2032–2043).

## 7. Structure-fate correspondence (one paragraph)

$\Delta_r$ places each MR on the MR-validity theory v3.1 §4.2 structure-fate
axis: $\Delta_r=0$ ↔ exact preservation (strict MR);
$0<\Delta_r\le\varepsilon_{\mathrm{tol}}$ ↔ approximate preservation (the
manuscript's strong / tolerance MR, main.tex:884–906);
$\Delta_r>\varepsilon_{\mathrm{tol}}$ ↔ structure broken (weak MR — exactly
REM-FPOS's $\mu_r<0$); $\Delta_r(h)\to0$ under refinement ↔ asymptotic
preservation (the "residual stays below $\varepsilon_{\mathrm{tol}}$ under
refinement" clause). THM-WIN is thereby the quantitative refinement of
v3.1's Lemma 1 ($\Delta\le\tau\Rightarrow$ Valid) in the mutation-detection
context: where Lemma 1 certifies only that a preserved structure yields a
valid (non-flagging) relation on the correct program, THM-WIN prices the
same $\Delta_r$ into two-sided detection bounds — how much violation
magnitude a valid relation is guaranteed to convert into a kill, and how
much it is guaranteed to miss.

## 8. $L_r$ estimability per PUT class (Task T3.2 Step 5)

$L_r$ here is the nominal-parameter→realized-magnitude transfer slope (H-b),
estimated by regressing the direct invariant-violation functional against
the dose ladder. Assessment over the twelve kernels (`src/p2/puts/`):

| PUT | Class | $L_r$ estimable? | Rationale (one line) |
|---|---|---|---|
| A1 Lorenz-63 | A | yes (caveat) | finite-horizon ($t_{\mathrm{end}}=1.0$) flow is smooth in parameters; chaotic amplification inflates the constant, so estimate on the realized axis with per-dose repeats |
| A2 LU/determinant | A | yes | analytic polynomial map; slope closed-form |
| A3 FDM heat | A | yes (window) | smooth inside the explicit-Euler stability region; degenerate near the machine-precision error floor (`errors > 1e-15` filter) |
| B1 Beta-Binomial | B | yes | closed-form posterior mean; transfer piecewise-linear and bounded |
| B2 Metropolis-Hastings | B | yes (in expectation) | stationary mean smooth in target parameters; needs $N$-repeat averaging ($c\sigma_{\mathrm{out}}/\sqrt N$) |
| B3 MC integration | B | yes | linear dependence of the integrand on the perturbed constant; fixed seed |
| C1 GPR | C | conditional | posterior closed-form *given* hyperparameters, but kernel hyperparameters are an argmax of a non-convex marginal likelihood (L-BFGS in `c1.py`); freeze hyperparameters on the dose ladder or the transfer can jump between basins |
| C2 PCE | C | yes | fixed polynomial features + linear least squares; smooth closed-form transfer |
| C3 shallow-NN (MLPRegressor) | C | **no** | non-convex Adam training: the trained map responds to parametric perturbation by basin switching even at fixed seed; no stable slope |
| D1 MLP classifier | D | **no** | same non-convex retraining pathology, plus `predict_proba` sigmoid saturation makes the violation functional piecewise-flat over magnitude ranges |
| D2 SVM (SVC + Platt) | D | **no** | discrete support-vector-set changes and Platt scaling's internal cross-validation give a discontinuous, resampling-noisy transfer |
| D3 LogReg | D | yes | convex, deterministic, smooth in the decision-function scale; probabilities smooth |

**$L_r$ 不可估 PUT 清单 (non-estimable list, provisional):** C3
(shallow-NN surrogate), D1 (MLP classifier), D2 (SVM classifier); C1 (GPR)
is conditionally estimable only with kernel hyperparameters frozen during
the dose ladder. Note on the D class: these kernels return `predict_proba`
(continuous), so the outputs are not literally label-thresholded; the
piecewise-constant risk enters through probability saturation and retraining
discontinuity, which is why D1/D2 are listed and D3 is not. The final
empirical call happens in the argumentation line Phase 2 (Task 2.3,
dose-response object-list replacement); the plan's POOL-DOSE kernels
(Lorenz, MC integration, GPR, LogReg) are consistent with this assessment
except that GPR carries the freeze-hyperparameters condition, which Task 2.3
must implement or substitute (e.g., PCE).

## 9. Obligations ledger and CHECKPOINT T3 questions

| PO | Disposition |
|---|---|
| PO-WIN-1 | closed — §5 H-a..H-d formalized (H-a from decomposition + triangle inequality twice; H-b confined to dose–response transfer, explicitly not load-bearing for (i)–(iii); H-c = §4 regime; H-d with the search-residual caveat) + 12-line per-class satisfiability |
| PO-WIN-2 | closed — §5 must-kill: H-a lower side ⇒ flag on mutant; H-c ⇒ pass on original; both kill-predicate conjuncts (main.tex:620–626) |
| PO-WIN-3 | closed — §5 must-not-kill: H-a upper side ⇒ no flag ⇒ second conjunct fails; H-c not needed |
| PO-WIN-4 | closed — §5 window inclusion: lower edge from (ii)'s contrapositive + strict-exceedance convention at equality; upper edge from S4 crash-oracle exclusion (main.tex:804–807, 817–822) |
| PO-WIN-5 | closed — §5 REM-FPOS: $\mu_r<0\iff\Delta_r>\varepsilon_{\mathrm{tol}}$; sup argument needs no attainment; sampling/noise caveat stated; exits admissible set via pass-on-original conjunct + §2.9 weak-MR semantics |
| PO-WIN-6 | closed — §5 REM-FNEG: algebraic $N$ bound with the explicit positive-denominator side condition; RNG case as the side-condition-failure instance |

**Open questions for REVIEW CHECKPOINT T3 (joint with T4):**

1. **H-a additivity.** H-a is stated as a two-sided additive bound
   $|\varepsilon_r-\varepsilon_{\mathrm{viol}}|\le\Delta_r+2\bar\eta$. Only
   the two one-sided inequalities are consumed, so the statement could be
   weakened to exactly those (a sub-additivity form) without touching any
   proof. Kept as-is for readability; note that a *multiplicative*
   violation–discretisation interaction would violate H-a and is empirically
   testable as dose–response residual curvature. Author call: keep additive
   H-a, or weaken to the one-sided pair?
2. **$2\bar\eta$ vs $p\bar\eta$.** MP\_3 convergence relations execute
   $p=4$ resolutions (found in `src/p2/avp/dispatcher.py`), so the frozen
   statement's $2\bar\eta$ does not cover them literally; §3's scope note
   states the $p\bar\eta$ generalization plus MP\_3's regression-conditioning
   caveat. Author call: keep the frozen $2\bar\eta$ statement + scope note
   (recommended), or re-freeze with $p\bar\eta$ in the statement?
3. **Strict-exceedance flag convention.** PO-WIN-4's open lower edge relies
   on $J_r=\mathrm{fail}\iff$ residual $>\varepsilon_{\mathrm{tol}}$
   (verified against `mp1_conservation.py`'s `≤ ε ⇒ pass`). Confirm this
   convention is recorded in DEF-05's T6 integration text.
4. **GPR conditional estimability.** Whether POOL-DOSE freezes GPR kernel
   hyperparameters or substitutes the kernel (PCE) is an argumentation-line
   Phase 2 (Task 2.3) decision; flagged here so the freeze predates the
   dose-ladder pre-registration.
5. **REM-FPOS caveat placement.** The guaranteed-flag caveat (sampling must
   hit residuals above $\varepsilon_{\mathrm{tol}}$; noise can mask flags in
   the $2\bar\eta$ band) currently lives in the proof. Author call: keep
   proof-level (recommended; the Remark stays clean) or lift one clause into
   the Remark text at T6.1.
