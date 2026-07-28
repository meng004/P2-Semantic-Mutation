# THM-GAP: Block Structure and Gap Attribution (with COR-ZERO and ξ)

Status: internal-review (awaiting REVIEW CHECKPOINT T2 — the pre-registration
freeze gate, R-5: the argumentation plan's Phase 1 may start only after this
checkpoint passes)

Normative sources: master plan §0.2–§0.5 (36-symbol closed set) and
[`notation_registry.md`](notation_registry.md). Audited manuscript baseline:
`submission/TOSEM_regular_20260706/main.tex`
(SHA-256 `8c5839319455b3080e5b6915e1ef821b6b931ad5563efa558e891e97a7c7b0f8`).
No symbol outside the registry is introduced. Labels `[THM-GAP]`, `[COR-ZERO]`,
`[LEM-CLO]`, `[THM-WIN]`, `[THM-DUAL]` are placeholders replaced by body
numbering in Task T6.1.

## 1. Definitions consumed (registry references)

- DEF-05 (exact checker): \(r\) is an exact checker for stratum \(\psi_j\)
  ⟺ \(\mathrm{flag}(r,P')\iff[\![P']\!]\not\models_\tau\psi_j\), with
  \(\mathrm{flag}(r,P')\equiv(J_r=\mathrm{fail})\).
- DEF-06 (covered strata): \(\mathrm{Cov}(R)=\{j:\exists r\in R\ \text{an
  exact checker for }\psi_j\}\).
- DEF-07 (fibers, weights, per-stratum score):
  \(M_j=\mathrm{eff}^{-1}(\psi_j\text{-viol})\cap M_{\mathrm{neq}}\);
  \(w_j=|M_j|/|M_{\mathrm{neq}}|\); \(\mathrm{SMS}_j(R)\) = kill rate
  restricted to \(M_j\).
- DEF-08 (gap decomposition):
  \(\mathrm{Gap}_{\mathrm{aln}}(R)=\sum_{j\notin\mathrm{Cov}(R)}w_j\);
  \(\mathrm{Gap}_{\mathrm{str}}(R)=\sum_{j\in\mathrm{Cov}(R)}w_j(1-\mathrm{SMS}_j(R))\).
- DEF-09 (exactness defect): \(\xi(R)\) = block-off-diagonal kill mass /
  total kill mass; model-check statistic, never folded into SMS.
- Manuscript anchors: invariants \(\psi_j\) are predicates over the observable
  behaviour and \([\![P]\!]\models\psi\) reads "the observable behaviour
  satisfies \(\psi\)" (main.tex:766–775); S5 stratum purity
  "\([\![P']\!]\models\psi'\) for all \(\psi'\in\Psi\setminus\{\psi\}\)"
  (main.tex:807–810, family symbol pending the \(I\to\Psi\) migration); kill
  predicate with its pass-on-original conjunct (main.tex:620–626); THM-DUAL =
  manuscript Theorem 2, strong MR = violation set closed under observational
  equivalence (main.tex:862–872).

Scoring convention: \(\mathrm{SMS}(R)\) in this draft is the strict score on
the certified non-equivalent universe \(M_{\mathrm{neq}}\) (THM-INT's
unresolved axis is orthogonal; the decomposition below applies verbatim to
any fixed accounting universe).

## 2. Statements (finalised baseline, master plan Phase T2)

```latex
\textbf{Definition (exact checker).} $r$ is an exact checker for stratum
$\psi_j$ if its violation predicate flags $P'$ iff
$[\![P']\!]\not\models_{\tau}\psi_j$ within the tolerance regime of
Theorem~[THM-WIN]. $\mathrm{Cov}(R)=\{j: R$ contains an exact checker for $\psi_j\}$.

\textbf{Theorem [THM-GAP] (block structure and gap attribution).} Assume (i)
stratum purity S5 for all $m_{\mathrm{mut}}\in M_{\mathrm{neq}}$, (ii) every $r\in R$ is
an exact checker for some stratum, (iii) non-degenerate tolerance margins
(Theorem~[THM-WIN]). Then no $m_{\mathrm{mut}}$ in fiber $M_j$ with $j\notin \mathrm{Cov}(R)$
is killed, the fiber-by-stratum kill matrix is block-diagonal, and
\[ 1-\mathrm{SMS}(R)=\underbrace{\textstyle\sum_{j\notin \mathrm{Cov}(R)} w_j}_{\mathrm{Gap}_{\mathrm{aln}}(R)\ \text{(alignment gap)}}
 +\underbrace{\textstyle\sum_{j\in \mathrm{Cov}(R)} w_j\,(1-\mathrm{SMS}_j(R))}_{\mathrm{Gap}_{\mathrm{str}}(R)\ \text{(strength gap)}},
 \qquad w_j=\tfrac{|M_j|}{|M_{\mathrm{neq}}|}, \]
both computable from the kill matrix and fiber labels alone.

\textbf{Corollary [COR-ZERO] (cross-zero prediction).} If
$\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing$ then $\mathrm{SMS}(R)=0$.

\textbf{Definition (exactness defect).} $\xi(R)=$ block-off-diagonal kill
mass / total kills; $\xi$ measures deviation from (i)-(ii) and is reported
as a model-check statistic, not folded into SMS.
```

## 3. Setup and premise reading

**Premise (i), explicit reading.** "S5 for all
\(m_{\mathrm{mut}}\in M_{\mathrm{neq}}\)" is read as: every admitted
non-equivalent mutant is *stratified* — it violates its unique target stratum
(S3 witness) and satisfies every other declared stratum (S5). Consequently
the fibers \(\{M_j\}\) partition \(M_{\mathrm{neq}}\) and
\(\sum_j w_j=1\). Mutants outside this reading (active-off-taxonomy, or
S5-impure multi-stratum violators) are excluded by the premise; empirically
their kill mass is exactly what \(\xi\) measures (§7). This reading is
flagged for author confirmation at CHECKPOINT T2 (§10, Q1).

**Premise (ii), checker labels.** Every \(r\in R\) carries a stratum label
\(\ell(r)\) with \(r\) an exact checker of \(\psi_{\ell(r)}\). The label is
unique provided declared strata have extensionally distinct tolerance
violation classes (if \(\{\not\models_\tau\psi_j\}=\{\not\models_\tau\psi_l\}\)
as program classes, \(j\) and \(l\) would be indistinguishable to any
checker; the declared family \(\Psi\) is assumed non-redundant in this
sense — one line, recorded).

**Premise (iii), what it licenses.** The manuscript states S5 with plain
\(\models\) (main.tex:807–810) while DEF-05's checker decides
\(\models_\tau\). Non-degenerate margins (the regime defined in THM-WIN;
margin exceeding the noise budget) close this gap: a stratum satisfied
outright is satisfied with margin, so the checker's tolerance decision does
not spuriously flag it, and checkers pass on the original program. Premise
(iii) is therefore not decorative: without it, borderline residuals could
flip tolerance verdicts and break the block structure — the same regime
condition that CHECKPOINT T1's amendment A1 made explicit in LEM-WIT.

## 4. Core lemma: no cross-stratum flag (closes PO-GAP-2, PO-GAP-3)

**Lemma (no cross-stratum flag).** Under (i)–(iii), if \(r\in R\) is an exact
checker of \(\psi_l\) and \(m_{\mathrm{mut}}\in M_j\) with \(l\ne j\), then
\(r\) does not flag \(m_{\mathrm{mut}}\), hence \(r\) does not kill
\(m_{\mathrm{mut}}\).

*Proof.* By (i), \(m_{\mathrm{mut}}\) satisfies every stratum other than
\(\psi_j\); in particular \([\![m_{\mathrm{mut}}]\!]\models\psi_l\). By (iii)
this satisfaction holds with margin, so the tolerance decision agrees:
\([\![m_{\mathrm{mut}}]\!]\models_\tau\psi_l\). By DEF-05,
\(\mathrm{flag}(r,m_{\mathrm{mut}})\iff[\![m_{\mathrm{mut}}]\!]\not\models_\tau\psi_l\),
so \(r\) does not flag \(m_{\mathrm{mut}}\), i.e.
\(J_r(m_{\mathrm{mut}})\ne\mathrm{fail}\). The kill predicate
(main.tex:620–626) requires \(\mathrm{AVP}(P,r)=\mathrm{pass}\) **and**
\(\mathrm{AVP}(m_{\mathrm{mut}},r)=\mathrm{fail}\); the second conjunct
fails. ∎

**PO-GAP-2 (uncovered fibers survive).** If \(j\notin\mathrm{Cov}(R)\), every
\(r\in R\) has \(\ell(r)\ne j\) (by DEF-06), so by the lemma no \(r\in R\)
flags any \(m_{\mathrm{mut}}\in M_j\); OR-aggregation over \(R\) yields no
kill. Hence no mutant of an uncovered fiber is killed. ∎

**PO-GAP-3 (block-diagonal kill matrix, formal statement).** Index rows by
fibers \(j\) and columns by checker strata \(l\in\ell(R)\); let the
\((j,l)\) entry count the members of \(M_j\) killed by exact checkers of
\(\psi_l\) in \(R\). By the lemma every off-diagonal entry (\(l\ne j\)) is
zero: kills are supported on the diagonal \(l=j\). (No new matrix symbol is
introduced; the array is described in prose, keeping the registry closed.) ∎

## 5. Gap decomposition (closes PO-GAP-4)

Under premise (i) the fibers partition \(M_{\mathrm{neq}}\), so
\(\sum_j w_j=1\) and the strict score decomposes fiber-wise:
\(\mathrm{SMS}(R)=\sum_j w_j\,\mathrm{SMS}_j(R)\). By PO-GAP-2,
\(\mathrm{SMS}_j(R)=0\) for \(j\notin\mathrm{Cov}(R)\). Therefore
\[
1-\mathrm{SMS}(R)=\sum_j w_j\bigl(1-\mathrm{SMS}_j(R)\bigr)
=\underbrace{\sum_{j\notin\mathrm{Cov}(R)}w_j}_{\mathrm{Gap}_{\mathrm{aln}}(R)}
+\underbrace{\sum_{j\in\mathrm{Cov}(R)}w_j\bigl(1-\mathrm{SMS}_j(R)\bigr)}_{\mathrm{Gap}_{\mathrm{str}}(R)},
\]
an exact algebraic identity; both terms are non-negative and sum to
\(1-\mathrm{SMS}(R)\le 1\). ∎

## 6. Computability (closes PO-GAP-5)

Inputs required: (a) fiber labels of mutants (generation-time
\(\mathrm{eff}\) labels certifying membership \(m_{\mathrm{mut}}\in M_j\));
(b) checker stratum labels \(\ell(r)\) (premise (ii) attaches one to every
\(r\in R\)); (c) the per-(fiber, checker) kill matrix from execution. Then:
\(w_j\) = label counts over \(|M_{\mathrm{neq}}|\);
\(\mathrm{SMS}_j(R)\) = row-\(j\) kill indicator rate;
\(\mathrm{Cov}(R)=\ell(R)\). Both gaps are finite sums of these quantities —
no equivalence oracle beyond the \(M_{\mathrm{neq}}\) certification already
assumed, and no ground-truth beyond the labels. Constructive and
post-hoc-computable from archived campaign artefacts. ∎

## 7. COR-ZERO (closes PO-GAP-6) and the exactness defect ξ

**COR-ZERO.** If \(\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing\), then by the
decomposition \(\mathrm{SMS}(R)=\sum_{j\in\mathrm{Cov}(R)}w_j\,\mathrm{SMS}_j(R)=0\)
since every covered fiber has zero mass. ∎

**ξ semantics.** Under premises (i)–(iii) the block structure forces
\(\xi(R)=0\); observed \(\xi(R)>0\) therefore *quantifies deviation from the
premises* (S5-impure mutants, non-exact checkers, or degenerate margins) —
a model-check statistic in the sense of a testable implication of the
assumed measurement model. ξ is reported alongside SMS and never folded into
it. Reporting rule (per master §0.3 A-PROV and the argumentation plan): the
pooled ξ is the secondary confirmatory prediction H-XI (prior landmark
0.10, B-1); per-cell ξ distributions remain descriptive; verdicts of
H-ZERO/H-DISC are unconditional on ξ (F-2 dual-channel rule).

## 8. Interface note (Four-Pillar T3; companion, non-load-bearing)

\(\mathrm{Gap}_{\mathrm{aln}}(R)\) corresponds to the selection residual
\(\Omega_{\mathrm{sel}}\) of the Four-Pillar theory's T3 three-layer residual
decomposition: defect mass the *selected* relation set cannot detect although
admissible relations could — eliminable by adding aligned MRs (exact checkers
of the uncovered strata). \(\mathrm{Gap}_{\mathrm{str}}(R)\) is the
within-stratum detection-power gap: survivors inside covered fibers, governed
by the detection window (THM-WIN: realized violation magnitudes below the
window's lower edge) and by finite input search — effects of
\(\Omega_{\mathrm{search}}\) type, not reducible to selection. Notation
bridge: the Four-Pillar adopted relation set \(S\) ≙ this paper's \(R\)
(registry §0.4). The Four-Pillar framework is cited as a companion technical
report; no result in this draft depends on it (non-load-bearing).

## 9. Empirical implications (derivation source for H-ZERO / H-DISC)

- **Prediction.** Under the A-PROV operationalisation (below), COR-ZERO
  predicts \(\mathrm{SMS}=0\) for every cell whose evaluated MR set has no
  aligned provenance with a positive-mass fiber (`PRED_ZERO` labels); cells
  with aligned coverage of positive-mass fibers are predicted nonzero.
- **v4 reading (development-only, F-8/F-9).** In the v4 legacy 60 mp-cell
  partition, the zero-inflation's cross-condition zero mass is the
  *theoretically predicted* component, not a metric failure; this reading is
  development evidence only and feeds no confirmatory verdict.
- **Consumption lines.** The argumentation plan consumes this theorem as the
  derivation source of its hypotheses: master argumentation plan §1.2, row
  "RQ3 构念效度（零部分）| H-ZERO" (prediction labels = COR-ZERO's
  `PRED_ZERO`/`NONZERO`; balanced accuracy ≥ 0.75, McNemar vs majority
  class) and row "RQ3 构念效度（非零部分）| H-DISC" (conditional
  discrimination restricted to predicted-nonzero cells)
  (`docs/superpowers/plans/2026-07-28-p3-argumentation-uplift.md`).
- **A-PROV declaration (methodological bridge, not a theorem premise;
  master §0.3, F-12).** Applying COR-ZERO to empirical data requires
  provenance-as-coverage: aligned-provenance MR sets approximate exact
  checkers of their target stratum, and \(\mathrm{Cov}(R)\) is
  operationalised as applicability matrix × MR provenance. Evidence is
  dual-channel (F-2): the ex-ante channel (construction and provenance
  audit — symmetric checklists, generation-time \(\mathrm{eff}\) labels,
  applicability-matrix hash) decides whether A-PROV is asserted, independent
  of kill outcomes; the ex-post channel is \(\xi(R)\) (§7) as the
  result-side diagnostic with its pre-registered H-XI landmark and the
  H-ZERO × H-XI 2×2 adjudication table. ξ does not change H-ZERO/H-DISC
  verdicts.

REM-IDF (identifiability up to coverage classes) attaches to this theorem's
discussion section; drafted in Phase T4 (`rem_identifiability.md`), merged in
Task T6.1.

## 9b. LEM-CLO and manuscript consistency (Task T2.2)

**Lemma statement.**

```latex
\textbf{Lemma [LEM-CLO] (exact checkers are strong MRs).} Let $r$ be an exact
checker for stratum $\psi_j$ (DEF-05). Then the violation set of $r$ equals
$\{P' : [\![P']\!]\not\models_{\tau}\psi_j\}$ and is closed under
$\equiv_{\mathrm{obs}}$; hence $r$ is a strong MR in the sense of
Theorem~[THM-DUAL], and inherits its duality guarantees (a strong MR detects
no observationally inactive mutant).
```

*Proof (PO-GAP-1).* The violation-set identity is DEF-05 read as a set
equation: \(\mathrm{flag}(r,P')\iff[\![P']\!]\not\models_\tau\psi_j\). Each
\(\psi_j\) is a predicate over the observable behaviour, and satisfaction is
evaluated on the observed behaviour (main.tex:766–775: "each \(\psi\) is a
predicate over the observable behaviour", "\([\![P]\!]\models\psi\) when
\(P\)'s observable behaviour satisfies \(\psi\)"); the tolerance-indexed
relation \(\models_\tau\) evaluates the same predicate with margin
\(\tau\) on the same observable. Membership of
\(\{P':[\![P']\!]\not\models_\tau\psi_j\}\) therefore depends on \(P'\) only
through its observed behaviour. If \(P''\equiv_{\mathrm{obs}}P'\), the two
observed behaviours coincide pointwise on the admitted domain, so
\(P''\) violates iff \(P'\) does: the violation set is a union of
\(\equiv_{\mathrm{obs}}\)-classes, i.e. closed. The manuscript defines a
strong MR exactly by this closure (main.tex:862–863), so \(r\) is strong and
Theorem 2's guarantees apply. ∎

**Properness (one line).** The inclusion is strict in general: a relation
whose violation set is the union of two distinct strata's tolerance-violation
classes is \(\equiv_{\mathrm{obs}}\)-closed (hence strong) but exact for
neither stratum — exactness additionally pins the set to a single stratum's
class.

**S5 manuscript check and elevation note.** Verified wording
(main.tex:807–810): S5 is stated *conditionally* — "stratum purity (required
where stratum labels feed downstream), \([\![P']\!]\models\psi'\) for all
\(\psi'\in I\setminus\{\psi\}\)" (family symbol \(I\) pending the
\(I\to\Psi\) migration). THM-GAP elevates S5 from conditional to premise (i).
Required body note for Task T6.1 integration (recorded here as the
hand-off): "S5-violating mutants route their kill mass into the exactness
defect \(\xi\)" — i.e. the elevation does not silently drop impure mutants;
it prices them into the model-check statistic. The \(\models\) vs
\(\models_\tau\) gap between S5's wording and DEF-05's decision is bridged by
premise (iii) (§3), the same regime that CHECKPOINT T1's amendment A1 made
explicit in LEM-WIT.

## 10. Obligations ledger and CHECKPOINT T2 questions

| PO | Disposition |
|---|---|
| PO-GAP-1 | closed — §9b (LEM-CLO: violation-set identity from DEF-05; closure through the observable-behaviour definition of \(\psi_j\), main.tex:766–775; strongness per Theorem 2's closure definition, main.tex:862–863; properness noted) |
| PO-GAP-2 | closed — §4 (uncovered fibers survive) |
| PO-GAP-3 | closed — §4 (block-diagonal statement, prose array, registry-closed) |
| PO-GAP-4 | closed — §5 (exact algebraic identity from the fiber partition) |
| PO-GAP-5 | closed — §6 (constructive from labels + kill matrix) |
| PO-GAP-6 | closed — §7 (COR-ZERO) |

Questions the author must adjudicate at CHECKPOINT T2:

1. **Premise strength.** (i) is read as "every admitted non-equivalent mutant
   is stratified (S3 target + S5 purity)" — an idealisation of the pool;
   (ii) idealises every evaluated MR as an exact checker. Is the intended
   division — idealised premises in the theorem, A-PROV as the declared
   empirical bridge, ξ as the quantified deviation — the right split, or
   should the theorem itself be weakened (e.g., an approximate-block bound
   with ξ in the statement)? The current draft keeps the clean statement and
   routes all deviation to ξ (recommendation: keep; a perturbed statement
   would duplicate what ξ already measures).
2. **ξ reporting mode.** Confirmed as: pooled ξ = secondary confirmatory
   H-XI (landmark 0.10, B-1); per-cell descriptive; verdict-unconditional
   for H-ZERO/H-DISC (F-2). Any change here must go through the
   argumentation plan's pre-registration text before freeze.
3. **Non-redundancy of Ψ.** §3's one-line assumption that declared strata
   have distinct tolerance-violation classes — acceptable as a standing
   convention of the invariant family, or should it be stated inside the
   theorem?

After this checkpoint passes, the argumentation plan's Phase 1
(pre-registration) is unblocked (R-5).
