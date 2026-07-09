# Cover Letter

Dear Editor,

We submit "A Semantic Mutation Metric for Metamorphic-Relation Adequacy in
Scientific Computing Programs" as a Journal-First Paper for ACM Transactions on
Software Engineering and Methodology (TOSEM). The manuscript is submitted to
the Fast-Impact Track, whose 45-page text limit (excluding the bibliography)
the manuscript satisfies: the body text runs to 42 pages before the References
section, leaving headroom within the cap.

The manuscript contributes Semantic Mutation Score (SMS), a
backward-compatible adequacy metric that preserves the denominator logic of
classical mutation testing while making the observed semantic effect explicit
for metamorphic-relation sets. The empirical evidence combines a 12-program
stress test, an AST-normalized syntactic-overlap audit, boundary and adjoint
arms, and an industrial real-defect arm: result-level statistics over
reproduced, MR-detectable defects from widely used scientific-computing
libraries, used to support the paper's construct separation among aggregate
kill-rate, semantic alignment, and real-defect detection.

Related-work disclosure. The industrial arm draws its result-level statistics
from a defect dataset curated and archived by the authors (Zenodo DOI
10.5281/zenodo.21203424). Benchmark construction, curation protocol, and
governance are not claimed as contributions of this manuscript and are
intended for a separate benchmark/artifact paper; the two manuscripts do not
overlap in claimed contributions (metric and construct validation here;
dataset construction methodology there). To keep the industrial arm
checkable inside this manuscript's own artifact, the per-case
34-case kill matrix and real-defect face are now mirrored in-repo as a
single-source-of-truth file (data/results/industrial_percase_v1.json,
with dataset DOI and archive SHA-256 recorded), from which every RQ4
number is re-derived.

Companion-citation blinding asymmetry. This manuscript adopts the MetaPattern
terminology of a companion theory paper, NOETHER, at the presentation layer,
and cites it (noether2026). Because NOETHER is itself under double-blind
review, we cite it anonymously (author byline withheld, "companion manuscript
under review, 2026") to avoid compromising that process. The other P-series
companions (li2026sms, li2026minmrcomplete, defect4mr2026) are cited by author
name because they are not under blind review. We flag this deliberate
asymmetry for transparency; the anonymous NOETHER citation will be
de-anonymised at camera-ready. No claim, threshold, dataset key, or
pre-registration in this manuscript depends on NOETHER: the alignment is
narrative naming only, and all registered artifacts retain their original
MPk labels.

An earlier version is available on arXiv as arXiv:2605.17437. The current
submission substantially sharpens the semantic-mutation framework, adds
formal terminology and argument-evidence mapping, clarifies non-claims, and uses
real-defect evidence only to support the paper's argument. The work is not
under simultaneous archival review elsewhere.

The replication package is archived on Zenodo under DOI
10.5281/zenodo.20250664. Extended proofs, protocol details, sensitivity
analyses, and the result-level real-defect evidence summary is provided as
supplementary material.

Journal-first novelty statement. This submission reports a new archival
contribution rather than an extension of any prior archival publication. The
work is available as arXiv:2605.17437, and that preprint is disclosed here for
transparency; it has not appeared in a conference, journal, or workshop
proceedings. Relative to the public preprint and to the closest
mutation-testing and metamorphic-testing literature, the TOSEM submission is
novel in five respects. First, it makes the adequacy object an MR set and makes
the denominator an admitted universe of nonequivalent domain-semantic mutants,
rather than syntactic mutants, MR obligations, or execution coverage. Second,
it introduces an explicit semantic-certificate and equivalence discipline and
establishes the degeneration of SMS to classical mutation score under the syntactic
limit. Third, it instantiates five semantic operator families for
scientific-computing kernels and audits their first-order syntactic
reachability. Fourth, it separates MR alignment, aggregate kill rate, and
real-defect detection using boundary and adjoint arms plus an industrial
real-defect arm with a four-group mutation comparison pre-registered in the
dataset protocol over reproduced library defects. Fifth, it narrows the claim from benchmark construction to construct
validation, with supplementary material and artifacts separating
reproducibility details from the main argument.

Length statement. In the ACM manuscript-review format, the body text is 42
pages excluding the bibliography (the References section begins on page 43),
so the manuscript is within the Fast-Impact Track 45-page text limit. The full
PDF is 45 pages including references, and the online supplementary material is
34 pages. Length was reduced from an earlier 52-page draft by demoting extended
protocol prose, theorem proofs, the higher-order-mutation analysis, and the
full threats and program-selection tables to the supplementary appendices
(Appendix K), and by consolidating the three per-study scoreboards and the
inference-permissions table into a single cross-study verdict ledger; no result,
verdict, or number was removed, only relocated with pointers.

Sincerely,

Meng Li
