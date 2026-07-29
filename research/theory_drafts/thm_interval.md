# THM-INT: Interval Soundness and Monotonicity (with LEM-WIT)

Status: internal-review — CHECKPOINT T1 passed with amendments A1/A2
(2026-07-28, delegated review; record:
`docs/review_20260728/checkpoint_t1_record.md`)

Normative sources: master plan §0.2–§0.5 (36-symbol closed set) and
[`notation_registry.md`](notation_registry.md). Audited manuscript baseline:
`submission/TOSEM_regular_20260706/main.tex`
(SHA-256 `8c5839319455b3080e5b6915e1ef821b6b931ad5563efa558e891e97a7c7b0f8`).
No symbol outside the registry is introduced. Labels `[LEM-WIT]`, `[THM-INT]`
are placeholders replaced by body numbering in Task T6.1.

## 1. Definitions consumed (registry references)

- DEF-01 (three-state equivalence): `CERTIFIED_EQUIVALENT` (machine-checkable
  certificate \(c\in\mathcal C\) proving \(P'\equiv_{\mathrm{obs}}P\)),
  `CONFIRMED_NON_EQUIVALENT` (witness
  \(x:\ \|\mathrm{obs}(\Phi_P(x))-\mathrm{obs}(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}\)),
  `EQUIVALENCE_UNRESOLVED` (neither; includes candidates whose E1∧E2 sample
  agreement carries no certificate).
- DEF-02 (counts): \(n\) confirmed non-equivalent, \(k\) killed by \(R\),
  \(u\) unresolved survivors, \(u_{\mathrm{neq}}\in[0,u]\) truly non-equivalent
  among the unresolved (unknown).
- DEF-03 (AVP determinism): the MR verdict is a deterministic function of the
  \(\mathrm{obs}\)-observed outputs of the executions in the MR tuple;
  stochastic PUTs are read under the §2.3 N-repeat aggregation semantics.
- DEF-04 (interval readings): \(\mathrm{SMS}_{\mathrm{strict}}=k/n\),
  \(\mathrm{SMS}_{\mathrm{cons}}=k/(n+u)\).
- Manuscript kill predicate (main.tex:620–626):
  \(\mathrm{killed}(P',\mathrm{MR}_{i,k})\iff\exists\,mr\in\mathrm{MR}_{i,k}:
  \mathrm{AVP}(P,mr)=\text{pass}\wedge\mathrm{AVP}(P',mr)=\text{fail}\).

Convention: interval claims are stated for cells with \(n\ge 1\). A cell with
\(n=0\) has an undefined \(\mathrm{SMS}_{\mathrm{strict}}\) and is excluded,
matching the manuscript's denominator guard (`run_cell.py` sets SMS only for a
positive denominator; every v4 cell has \(n\ge 10\)).

## 2. Statements (finalised baseline, master plan Phase T1)

```latex
\textbf{Lemma [LEM-WIT] (kill witness upgrade).} Assume the AVP verdict is a
deterministic function of the $\mathrm{obs}$-observed outputs of the executions
in an MR tuple, and that on the executed tuple the verdict is stable under
pointwise obs-output perturbations of magnitude at most
$\varepsilon_{\mathrm{eq}}$ (non-degenerate tolerance margins; the regime of
Theorem~[THM-WIN](iii)). If $\mathrm{killed}(P',\mathrm{MR}_{i,k})$ holds, then some
execution input $x$ satisfies
$\|\mathrm{obs}(\Phi_{P}(x))-\mathrm{obs}(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}$,
hence $P'$ is CONFIRMED\_NON\_EQUIVALENT. Consequently the unresolved set
contains no killed mutants.

\textbf{Theorem [THM-INT] (interval soundness and monotonicity).} Let $n\ge1$ be the
number of confirmed non-equivalent mutants, $k$ the number killed by $R$,
and $u$ the number of unresolved survivors. Let $u_{\mathrm{neq}}\in[0,u]$ be the
(unknown) number of truly non-equivalent mutants among the unresolved.
Then the ground-truth score $k/(n+u_{\mathrm{neq}})$ satisfies
\[ \mathrm{SMS}_{\mathrm{cons}}=\tfrac{k}{n+u}\;\le\;\tfrac{k}{n+u_{\mathrm{neq}}}\;\le\;\tfrac{k}{n}=\mathrm{SMS}_{\mathrm{strict}}, \]
with width $\mathrm{SMS}_{\mathrm{strict}}\cdot\tfrac{u}{n+u}$. Each
equivalence certificate ($u\!\to\!u\!-\!1$) or divergence witness
($u\!\to\!u\!-\!1$, $n\!\to\!n\!+\!1$) weakly narrows the interval; and for
$R\subseteq R'$, with the three-state classification held fixed (admission and
witness status computed once against the cell's relation universe), both
endpoints are non-decreasing.
```

(Statements carry CHECKPOINT T1 amendments A1/A2, synchronised with the master
plan: A1 hoists the margin-stability clause into LEM-WIT's hypotheses — without
it the lemma admits a threshold-straddling counterexample; A2 adds the
fixed-classification proviso to the \(R\subseteq R'\) clause. Amendment A6
(2026-07-29, T6.2 independent audit) adds \(n\ge1\) to the statement,
hoisting the §1 domain convention into the hypotheses.)

## 3. Proof of LEM-WIT (closes PO-INT-1, PO-INT-2)

**Scope of the determinism hypothesis (PO-INT-1).** In the executable §2.3
semantics the hypothesis holds in the following concrete form. The evaluation
procedure of a relation \(mr\) fixes its executed input tuple (seeded input
generation is part of the procedure), runs the program on that tuple, applies
\(\mathrm{obs}\), and computes the verdict by a fixed threshold functional at
tolerance \(\varepsilon_{\mathrm{AVP}}\) (`src/p2/avp`, `src/p2/lrca/killed.py`).
For deterministic PUTs the verdict is therefore a fixed function
\(V_{mr}\) of the tuple \((\mathrm{obs}(\Phi_Q(x)))_{x\in X_{mr}}\), where
\(X_{mr}\) is the common executed input tuple. For stochastic PUTs the v4
pipeline replaces each AVP call by a strict-majority vote over \(N=20\)
independent repetitions (`src/p2/avp/repeat.py`); the verdict is then a fixed
function of the \(N\)-repeat *aggregated* observation, and every occurrence of
"observed output" below is read at that aggregated level (DEF-03's parenthetical;
footnote F1). The second stated hypothesis (amendment A1) reads concretely:

- **Margin non-degeneracy (stability clause; hypothesis, not proof device).**
  On the executed tuple, no relation residual lies within
  \(\varepsilon_{\mathrm{eq}}\) of its decision threshold, so the verdict
  functional \(V_{mr}\) is invariant under pointwise perturbations of the
  observed outputs of magnitude \(\le\varepsilon_{\mathrm{eq}}\). This is
  clause R2 (\(\varepsilon_{\mathrm{eq}}\)-separation) of the THM-WIN §4
  regime (DEF-13; consumption map in `thm_window.md` §4, repair B2); in the
  v4 pipeline
  \(\varepsilon_{\mathrm{eq}}=\varepsilon_{\mathrm{AVP}}=10^{-6}\) are wired
  equal (`src/p2/equiv/judge.py`), so the clause is the assumption that no
  executed residual straddles the shared tolerance within \(10^{-6}\).
  Necessity: with residuals \(\tau-\delta_1\) (pass on \(P\)) and
  \(\tau+\delta_2\) (fail on \(P'\)), \(\delta_1+\delta_2\) small, a kill can
  arise from pointwise output divergence \(<\varepsilon_{\mathrm{eq}}\); the
  bare determinism hypothesis therefore cannot yield the
  \(>\varepsilon_{\mathrm{eq}}\) witness, and the clause is not removable.

**Witness extraction (PO-INT-2).** Assume
\(\mathrm{killed}(P',\mathrm{MR}_{i,k})\). Fix \(mr\) with
\(\mathrm{AVP}(P,mr)=\text{pass}\) and \(\mathrm{AVP}(P',mr)=\text{fail}\).
Suppose toward a contradiction that every executed input \(x\in X_{mr}\)
satisfies
\(\|\mathrm{obs}(\Phi_P(x))-\mathrm{obs}(\Phi_{P'}(x))\|\le\varepsilon_{\mathrm{eq}}\).
Then the observed-output tuple of \(P'\) is a pointwise
\(\le\varepsilon_{\mathrm{eq}}\) perturbation of that of \(P\), and the margin
non-degeneracy clause forces
\(V_{mr}\big((\mathrm{obs}(\Phi_{P'}(x)))_{x}\big)=V_{mr}\big((\mathrm{obs}(\Phi_{P}(x)))_{x}\big)\),
i.e.\ \(\mathrm{AVP}(P',mr)=\mathrm{AVP}(P,mr)=\text{pass}\), contradicting
fail. Hence some executed \(x\) has
\(\|\mathrm{obs}(\Phi_P(x))-\mathrm{obs}(\Phi_{P'}(x))\|>\varepsilon_{\mathrm{eq}}\).
That is precisely the DEF-01 divergence witness, so \(P'\) is
`CONFIRMED_NON_EQUIVALENT`. Since the three DEF-01 states are mutually
exclusive and `EQUIVALENCE_UNRESOLVED` requires that no witness exists, no
killed mutant is unresolved. ∎

**F1 (stochastic footnote, per Step 3 self-check).** For stochastic PUTs the
witness produced by the argument is a divergence of the \(N\)-repeat aggregated
observations, i.e.\ "beyond tolerance in the AVP verdict semantics"; it is a
`CONFIRMED_NON_EQUIVALENT` verdict relative to the aggregated observable that
the AVP consumes, not a claim about any single random run. Deterministic PUTs
need no such qualification.

## 4. Proof of THM-INT (closes PO-INT-3, PO-INT-4, PO-INT-5)

**Ground-truth denominator.** By LEM-WIT every killed mutant carries a
divergence witness, so the killed count \(k\) sits entirely inside the
confirmed non-equivalent population \(n\); the true non-equivalent universe of
the cell is the confirmed \(n\) plus the unknown \(u_{\mathrm{neq}}\) among the
unresolved, and certified-equivalent candidates contribute nothing. The
ground-truth score is therefore \(k/(n+u_{\mathrm{neq}})\) with the same
numerator \(k\).

**(i) Interval and attainability (PO-INT-3).** For fixed \(k\ge 0,n\ge 1\) the
map \(t\mapsto k/(n+t)\) is non-increasing on \(t\ge 0\) (strictly decreasing
when \(k>0\)). Applying it to \(0\le u_{\mathrm{neq}}\le u\):
\[
\mathrm{SMS}_{\mathrm{cons}}=\frac{k}{n+u}\;\le\;\frac{k}{n+u_{\mathrm{neq}}}\;\le\;\frac{k}{n}=\mathrm{SMS}_{\mathrm{strict}},
\]
and both endpoints are attained: \(u_{\mathrm{neq}}=u\) (every unresolved
survivor truly non-equivalent) gives the left endpoint,
\(u_{\mathrm{neq}}=0\) (every unresolved survivor truly equivalent) gives the
right endpoint. Both extremes are consistent with the available evidence, so
neither endpoint can be excluded without new certificates or witnesses. ∎

**(ii) Width identity (PO-INT-4).**
\[
\frac{k}{n}-\frac{k}{n+u}
=\frac{k(n+u)-kn}{n(n+u)}
=\frac{ku}{n(n+u)}
=\frac{k}{n}\cdot\frac{u}{n+u}
=\mathrm{SMS}_{\mathrm{strict}}\cdot\frac{u}{n+u}. \qquad\square
\]

**(iii) Evidence monotonicity (PO-INT-5; four cases).** Write
\(I(n,k,u)=[\,k/(n+u),\;k/n\,]\).

1. *Equivalence certificate on an unresolved survivor*:
   \((n,k,u)\to(n,k,u-1)\). Upper endpoint \(k/n\) unchanged; lower endpoint
   rises from \(k/(n+u)\) to \(k/(n+u-1)\). Hence
   \(I(n,k,u-1)\subseteq I(n,k,u)\): the interval weakly narrows (strictly when
   \(k>0\), \(u\ge 1\); width ratio
   \((u-1)(n+u)/\big(u(n+u-1)\big)<1\) since \(-n<0\)).
2. *Divergence witness on an unresolved survivor*:
   \((n,k,u)\to(n+1,k,u-1)\). Lower endpoint \(k/(n+1+u-1)=k/(n+u)\) unchanged;
   upper endpoint falls from \(k/n\) to \(k/(n+1)\). Hence
   \(I(n+1,k,u-1)\subseteq I(n,k,u)\): weakly narrows. (Unresolved mutants are
   survivors by LEM-WIT, so the witness turns an unresolved survivor into a
   confirmed non-equivalent survivor; \(k\) is unchanged.)
3. *Unresolved survivor killed by a newly added MR*: the kill supplies the
   LEM-WIT witness, so \((n,k,u)\to(n+1,k+1,u-1)\). This is an instance of MR
   expansion, judged by the endpoint-monotonicity claim of case 4 (with
   \(\Delta=0\), \(j=1\)), not by the narrowing claim.
4. *MR expansion \(R\subseteq R'\), fixed classification (amendment A2)*: the
   three-state classification is computed once against the cell's relation
   universe (the prescreen-once protocol), so enlarging the evaluated set
   changes kills only; OR-aggregation over a superset can only add kills. Let
   \(\Delta\ge 0\) be new kills among confirmed non-equivalent survivors and
   \(j\ge 0\) new kills among unresolved survivors (each of the latter moves
   one unit \(u\to u-1\), \(n\to n+1\), \(k\to k+1\) by LEM-WIT). The updated
   counts are \(n'=n+j\), \(k'=k+\Delta+j\), \(u'=u-j\). Then
   \[
   \mathrm{SMS}_{\mathrm{strict}}'=\frac{k+\Delta+j}{n+j}\;\ge\;\frac{k+j}{n+j}\;\ge\;\frac{k}{n}
   \quad(\text{since } k\le n),
   \qquad
   \mathrm{SMS}_{\mathrm{cons}}'=\frac{k+\Delta+j}{(n+j)+(u-j)}=\frac{k+\Delta+j}{n+u}\;\ge\;\frac{k}{n+u}.
   \]
   Both endpoints are non-decreasing. (The interval need not narrow under
   expansion; the two motions are deliberately separated in the statement.
   Why the proviso is not removable: if the classification were re-run with
   \(R'\), the E1 quantification domain would grow, and a new relation on
   which the verdicts of \(P\) and \(P'\) differ without a kill — fail on
   \(P\), pass on \(P'\) — would convert an unresolved survivor into a
   confirmed one, a case-2 witness motion \((n{+}1,k,u{-}1)\) that lowers the
   strict endpoint; "both endpoints non-decreasing" would then be false for
   the composite update.) ∎

*Remark (uniform lower-endpoint monotonicity).* Across all four motions the
conservative endpoint \(\mathrm{SMS}_{\mathrm{cons}}\) never decreases
(cases 1 and 4 raise or preserve it; cases 2 and 3 preserve and raise it
respectively), so \(\mathrm{SMS}_{\mathrm{cons}}\) is a monotone lower bound
of the ground-truth score under every admissible evidence update.

## 5. Obligations ledger

| PO | Disposition |
|---|---|
| PO-INT-1 | closed — §3 scope paragraph: deterministic PUTs exact; stochastic PUTs via N=20 strict-majority aggregation (F1); stability clause hoisted into the statement (amendment A1) with a necessity counterexample, tied to DEF-13 margins and the pipeline fact \(\varepsilon_{\mathrm{eq}}=\varepsilon_{\mathrm{AVP}}=10^{-6}\) |
| PO-INT-2 | closed — §3 witness extraction (contradiction through the fixed verdict functional) |
| PO-INT-3 | closed — §4(i), monotone map plus attainable endpoints |
| PO-INT-4 | closed — §4(ii), algebraic identity |
| PO-INT-5 | closed — §4(iii), all four evidence motions verified endpoint-by-endpoint; \(R\subseteq R'\) clause carries the fixed-classification proviso (amendment A2) with a non-removability argument |

CHECKPOINT T1 amendments (2026-07-28, delegated review):

- **A1 (validity repair).** Margin-stability clause hoisted from the proof into
  LEM-WIT's stated hypotheses; without it the lemma admits the
  threshold-straddling counterexample recorded in §3.
- **A2 (validity repair).** Fixed-classification proviso added to the
  \(R\subseteq R'\) clause; without it E1's growing quantification domain can
  generate witness-only motions that lower the strict endpoint.

Self-check items (Task T1.1 Step 3):

1. *AVP determinism basis in §2.3*: the manuscript types AVP as a function
   `Programs × MR_universe × R+ → {pass, fail}` (supplementary A.1) and the
   executable pipeline implements the verdict as a fixed threshold functional
   over seeded executions; DEF-03 is therefore grounded in the current text,
   with the stability clause as the one genuinely additional regime condition,
   surfaced explicitly in §3 rather than smuggled.
2. *Does the N=20 repeat semantics break LEM-WIT?* No for the aggregated
   reading: the majority-vote verdict is a deterministic function of the
   N-repeat aggregated observations, and the witness statement is read in the
   AVP verdict semantics per footnote F1. A single-run pointwise witness is
   **not** claimed for stochastic PUTs.
3. *Degenerate denominators*: convention \(n\ge1\) recorded in §1; all 60 v4
   mp-cells satisfy it (min \(n=10\)).

## 6. Empirical instantiation note (development-only)

The v4 legacy ledger (`data/results/sms_track2_v4.json`, 60 mp-cells) judges
equivalence by single-shot E1∧E2 sampling only; the pipeline has no
certificate layer, so every `equiv` verdict is `EQUIVALENCE_UNRESOLVED` under
DEF-01 and \(u=\) the cell's `equiv` count, while every denominator member
failed E1∨E2 and is `CONFIRMED_NON_EQUIVALENT` (E2 failure is a direct DEF-01
witness; E1 failure is a witness through LEM-WIT's argument). In v4 the
recorded `equiv` is 0 in all 60 cells — a true empirical observation
(`data/results/equiv_diagnosis.json`, case B) — so \(u=0\), every interval
degenerates to the point \(\mathrm{SMS}_{\mathrm{strict}}=\mathrm{SMS}_{\mathrm{cons}}=\)
legacy SMS, and the interval reading changes no v4 number retroactively. The
machinery becomes informative exactly when sample-judged equivalence or
certificates appear (planned v5 pipeline). Demo artefact:
`scripts/theory/interval_demo.py` →
`data/results/interval_demo_v4.json` (development-only; §2.10 illustration).
