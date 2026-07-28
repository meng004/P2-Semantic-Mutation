# REM-IDF: Identifiability from Kill Signatures (THM-GAP Remark) and LRCA Repositioning

Status: internal-review (adjudicated at REVIEW CHECKPOINT T3, joint with T3;
statement carries amendment A3)

Normative sources: master plan §0.2–§0.5 (36-symbol closed set) and
[`notation_registry.md`](notation_registry.md). Attaches to
[`thm_gap.md`](thm_gap.md) as a Remark inside THM-GAP's discussion (R-9: no
independent theorem numbering, no independent proof obligations; audited
under T6 audit item (8)). Labels `[REM-IDF]`, `[THM-GAP]`, `[THM-WIN]` are
placeholders replaced by body numbering in Task T6.1.

## 1. Statement (finalised baseline as amended by A3)

```latex
\textbf{Remark [REM-IDF] (identifiability from kill signatures).} Under the
assumptions of Theorem~[THM-GAP] let $\mathrm{sig}(m_{\mathrm{mut}})=\{r\in R: r\ \text{kills}\ m_{\mathrm{mut}}\}$.
For any killed $m_{\mathrm{mut}}$, all members of $\mathrm{sig}(m_{\mathrm{mut}})$ are checkers of the
same stratum, which identifies the fiber of $m_{\mathrm{mut}}$ exactly; with a
separating family (one exact checker per stratum in $\mathrm{Cov}(R)$) the
killed subpopulations therefore separate every covered stratum. For
survivors the signature is identically empty and carries no fiber
information: an empty signature is consistent with every uncovered fiber and
with the below-window remainder (Theorem~[THM-WIN](ii)) of every covered
fiber, so survivor fiber attribution must come from generation-time labels,
not from kill signatures.
```

**Amendment A3 (why the original survivor clause was replaced).** The
pre-amendment clause claimed survivor fiber membership "identifiable only up
to the partition of strata induced by identical R-coverage", trivial on
\(\mathrm{Cov}(R)\) under a separating family. That is an overclaim: an
empty signature is simultaneously consistent with membership in any
uncovered fiber and in the below-window remainder of any covered fiber, so
no coverage-induced class is determined by the observation. The corrected
clause states exactly what survives scrutiny: kill signatures identify
killed mutants' fibers (block-diagonality) and separate covered strata on
the killed subpopulations; they carry zero information about survivors.

## 2. Justification (two sentences, merged into THM-GAP's discussion at T6.1)

Same-stratum membership of \(\mathrm{sig}(m_{\mathrm{mut}})\) is the
block-diagonal kill matrix of THM-GAP reread row-wise: a killed
\(m_{\mathrm{mut}}\in M_j\) can only be flagged by checkers with label
\(j\), so its nonempty signature both certifies the kill and names the
fiber. Survivor rows of the kill matrix are identically zero, so they are
observationally indistinguishable from one another; the below-window
remainder of every covered fiber (Theorem [THM-WIN](ii)) and every uncovered
fiber produce the same all-pass observation, and survivor attribution is
therefore carried by generation-time \(\mathrm{eff}\) labels — the A-PROV
ex-ante channel — not by execution outcomes.

## 3. LRCA repositioning (replacement text for the manuscript's §2.4 functional description; T6.1 handoff)

Replacement sentence for the current "LRCA is a diagnostic annotation that
tells the reader whether a given kill is more consistent with…" (committed
baseline main.tex:646–649):

> LRCA is a diagnostic annotator of deviations from the block structure of
> Theorem [THM-GAP]: C1 marks kills consistent with the diagonal (the
> declared-stratum detection the metric is designed to count), while C2–C5
> label the kill mass that the exactness defect \(\xi\) aggregates
> (tolerance sensitivity, out-of-distribution behaviour,
> statistical-assumption failure, mutator artefact). LRCA does not modify
> the SMS formula: the killed set is never filtered by suspect status.

Consequences recorded for integration: (a) the existing contribution claim
"C2–C5" reads, post-THM-GAP, as the measurement-model diagnostics of ξ
rather than free-standing engineering labels; (b) the SMS-untouched
invariant of LRCA is unchanged; (c) survivor attribution (this Remark) and
kill-mass attribution (LRCA) are complementary: the former is label-borne,
the latter outcome-borne.

## 4. Ledger

| Item | Disposition |
|---|---|
| Independent PO | none (R-9); justification merged into THM-GAP discussion; audited under T6 audit item (8) |
| Statement fidelity | amendment A3 applied master-first (master plan Phase T4 block, phase T4 file, this draft) |
| Dependencies | THM-GAP (block structure); THM-WIN(ii) (below-window remainder); no cycles introduced |
| CHECKPOINT | adjudicated at REVIEW CHECKPOINT T3 (record: `docs/review_20260728/checkpoint_t3_record.md`) |
