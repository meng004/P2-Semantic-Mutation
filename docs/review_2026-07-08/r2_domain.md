# Domain (MT / mutation testing) — Reviewer 2 — simulated review 2026-07-08

Venue: ACM TOSEM (fast-impact track). Reviewer role: domain expert in mutation
testing, metamorphic testing, and testing of safety-critical / scientific
software. Manuscript: `source/main.tex` (+ `source/supplementary.tex`),
bibliography `source/references.bib`. Prior round: `docs/review_2026-07-07/`.

Every claim below is anchored to `file:line`.

---

## Verdict

**Major revision (light).** The paper has moved substantially since 2026-07-07:
the foundational MT/mutation citations are now real and correctly placed, the
degeneration "theorem" and the undecidability "theorem" are honestly demoted to
characterisations, the LLMorpheus fabrication is gone, and the 34/34 real-defect
face is correctly labelled selection-conditioned. Those were the previous
domain blockers and they are genuinely closed. What remains is **one structural
domain problem that the paper's conceptual spine rests on** — the effect map
`σ` and the aligned-vs-cross partition are only well-defined modulo stratum
purity S5, and S5 is verifiable with the existing AVP machinery but is not
verified — plus a residual internal inconsistency on "structurally unreachable"
HP, two missing 2024–2025 LLM-mutation must-cites, and terminology collisions
that a TOSEM MT audience will trip on. None is desk-reject; all are fixable
without a new experiment except the S5 audit, which is a cheap re-run of code
that already exists.

## Score: 5 / 10

(Up from an effective 3–4 last round. The honesty and infrastructure are a
genuine strength; the residual S5 gap is what keeps this out of minor-revision
territory, because it undermines the fiber reading that is the paper's headline
theoretical contribution.)

---

## 0. Verification of previous-round claimed fixes (ledger audit)

I checked the `synthesis_and_fix_ledger.md` claims against the current source.
The domain-relevant ones are **real**:

- Fix #8 (foundational citations). Confirmed real bib entries: `chen2018metamorphic`
  (CSUR 2018), `segura2016survey` (TSE 2016), `liu2014alleviate` (TSE 2014),
  `kanewala2014scientific` (IST 2014), `demillo1978hints` (Computer 1978),
  `budd1982correctness` (Budd & Angluin, Acta Informatica 1982). All cited in
  `main.tex:303-322`. This closes prior Blocker 8. ✓
- Fix #19 (LLMorpheus fabrication). Grep for "cross-MP failure / not listed in
  cited literature" returns **zero hits** in `main.tex`; the surviving mention
  at `main.tex:2090-2095` carries an explicit estimand caveat ("the numerical
  similarity is not substantive support"). ✓
- Fix #20 (degeneration reading). `main.tex:863-868` now reads Theorem 1 as "a
  backward-compatibility characterisation of SMS, not as an independent
  mathematical contribution." ✓
- Fix #21 (undecidability folklore). `main.tex:1005-1008` now states it is "a
  routine consequence of Rice's theorem … not as a novel result." ✓
- Fix #23 (certificate ≠ proof). `main.tex:475-476` defines a certificate as "a
  recorded, budget-stamped piece of test evidence, not a proof object
  (Limitation 9)." ✓
- Fix #25/#26 (family-boundary + S5 disclaimers). `main.tex:2386-2395` now
  carries both the labelling-slack caveat and the S5-purity-unverified
  admission. ✓ (but see §3 — the disclaimer is placed in the discussion, not at
  the definition that needs it).
- Fix #24 (HP "categorically unreachable" softened). **Only partially real** —
  see §4 / §5 below: the figure caption was softened but the table cell and the
  body prose were not.

## 1. Positioning against related work — is the novelty defensible at TOSEM's bar?

The related-work section (`main.tex:299-408`) is now a competent seven-line
bracket and the "closest denominator-oriented comparators" table
(`main.tex:410-417`, `tab:closest-denominator-comparators`) is exactly the right
move for a TOSEM adequacy paper: it separates comparators by *counting object*
(MR obligations vs source-test obligations vs differential-execution coverage vs
syntactic mutants) and then claims SMS is the first to make the denominator the
set of admitted *domain-semantic code mutants*. That framing is defensible.

**The core novelty claim survives scrutiny.** "Semantic mutation as a construct
distinct from syntactic mutation," operationalised as *intensionally semantic,
extensionally syntactic* with membership defined by invariant violation rather
than edit arity (`main.tex:890-897`, `942-955`), is a real specification-relative
distinction and is *not* merely HOM-with-a-label. The SMS-replaces-the-denominator
argument (`main.tex:401-408`) is the paper's strongest positioning sentence.

**Two missing must-cite works (2022–2025), both in the exact lineage the paper
surveys in §(c):**

1. **µBERT** (Degiovanni & Papadakis, "µBERT: Mutation Testing using Pre-Trained
   Language Models"). Grep of `references.bib` for `degiovanni` / `mubert`
   returns **zero hits**. This is arguably the first PLM-driven mutant generator
   and is the direct ancestor of the LLM-mutant lineage the paper cites
   (`tip2025llmorpheus`, `humbatova2021deepcrime`, `dakhel2024llm` at
   `main.tex:329-334`). Omitting it from an MT/mutation TOSEM submission that
   foregrounds "LLM-generated mutants" is a visible gap.
2. **Meta's ACH / LLM-based mutation-guided test generation** (Alshahwan et al.,
   2024–2025). Grep for `alshahwan` / `automated compliance` / `assured llm`
   returns **zero hits**. This is the most prominent *industrial-scale*
   LLM-mutation deployment to date; because the paper carries an "industrial
   arm" and repeatedly invokes real-world relevance (`main.tex:178-187`,
   `2415-2492`), a reviewer will expect it engaged, if only to distinguish
   scope (Meta hardens test suites via LLM faults on general software; this
   paper measures MR adequacy on scientific kernels).

   Neither is fatal, but at TOSEM's currency bar both are "add or the reviewer
   assumes you don't know the 2024–2025 literature."

**Clark-style homonym still only implicitly disambiguated.** The paper's *title
term* "semantic mutation" collides with Clark/Dan/Hierons semantic mutation
testing (`main.tex:349-353`, `7a6c2809…`, `dan2012smtc`, `derezinska2019uml`),
which perturbs *language / semantic-variation-point interpretations* — a
different construct from domain-invariant-certified code edits. The text now
describes that construct ("perturbing semantic-variation-point interpretations
rather than syntactic structure," `main.tex:352-353`) and asserts its own
first-ness (`main.tex:365-368`), but never states the contrast in one clean
sentence ("their object is the interpretation the developer might have
misunderstood; ours is a certified violation of a declared domain invariant in
code"). This was raised last round and is still owed. One sentence closes it.

## 2. Degeneration-theorem framing — under/over-claimed?

**The current hedged framing is correct and I would not push further.**
`main.tex:837-868` states the limit `L = L_equiv ∧ L_killed ∧ L_mut` (with the
paired axes ε→0 / K→∞ / MP set = {MP_eq} / mut_j → syntactic operators), then
explicitly says "Under the stated substitutions the equality is definitional
once the three layers coincide; the almost-everywhere qualifier concerns only
the bounded E2 classifier on floating-point pathological inputs" and reads it as
"a backward-compatibility characterisation … not an independent mathematical
contribution" (`main.tex:863-868`).

This resolves the two prior domain objections cleanly:
- The prior "a.e. w.r.t. `D_S` is ill-typed because SMS is a ratio of finite
  cardinalities" objection is now answered by re-scoping the a.e. qualifier to
  the E2 *classifier's decision on inputs* (`main.tex:854-855, 864-865`), which
  *is* a function of `D_S`. That is the right rescue.
- The theorem is no longer double-counted as one of three "proofs" answering
  RQ1: `main.tex:501-503` now enumerates undecidability + fiber characterisation
  + duality as the RQ1 formal content, with degeneration cited separately as the
  MS tie-in. Consistent.

One residual under-labelling: it is still *called* a `theorem` environment
(`main.tex:837`) and the corollary "LRCA trivialisation" (`main.tex:870-876`)
inherits the same status. Given the prose now says it is definitional, consider
`\begin{proposition}` or "Characterisation 1." This is cosmetic, not a blocker —
the *claim strength* is now honest.

## 3. S5 purity declaration — does leaving it unverified undermine the stratification? (YES)

This is my principal domain concern and the reason the score is 5 not 7.

The paper's theoretical spine is the **effect map** `σ` (`main.tex:971-985`),
which "sends an applicable edit `e` to *the* semantic-effect class of `P_e`"
valued in `{≡_α, ill-formed, ψ₁-viol, …, ψ₅-viol, active-off-taxonomy}`. `σ` is
presented as a **function** (single-valued): each fiber is a `σ`-preimage, and
the entire RQ2 aligned-vs-cross result (`main.tex:2410-2413`,
`rq2-aligned-vs-cross-cliffs-delta`) is a partition of kill mass by the diagonal
`j = k` vs off-diagonal `j ≠ k` of that fiber structure. The headline empirical
claim of the paper lives on this partition.

**But `σ` is well-defined only if S5 (stratum purity) holds.** S5 is defined at
`main.tex:952-955` as `⟦P'⟧ ⊨ ψ'` for all `ψ' ∈ I \ {ψ}` — i.e. a mutant
declared at stratum `ψ` must violate *no other* invariant. The
`active-off-taxonomy` escape hatch (`main.tex:981-982`) only covers the case
where *no* invariant flips; it does **not** cover the case where *two or more*
flip, which is exactly an S5 violation and exactly the case that makes `σ`
multi-valued. So:

- If any admitted mutant violates ≥2 of the five invariants, `σ` is not a
  function, the "fiber of a class is its σ-preimage" definition
  (`main.tex:982-983`) is not a partition, and the `j = k` vs `j ≠ k`
  decomposition — the paper's headline — is contaminated.
- The paper itself supplies the prima-facie evidence: `main.tex:2391-2395`
  admits "S5 purity … is enforced by generation intent and certificate review,
  not verified against all five invariants, so part of the off-diagonal kill
  mass may reflect multi-stratum effects rather than pure cross-stratum
  detection." That is an admission that the off-diagonal (the *contrast* term in
  RQ2) may be an S5 artifact.
- `S5` is even flagged "(required where stratum labels feed downstream)"
  (`main.tex:952-953`) — and they *do* feed downstream, into the very partition
  that is the result.

**What a domain reviewer demands (and it is cheap):** S5 is *decidable on the
bounded corpus* with the machinery that already exists. The AVP already checks
the target invariant per mutant; run the *other four* invariant checkers on each
of the 292 semantic mutants (and each of the 34 industrial cases) and report,
per mutant, the count of invariants flipped. Then report the **purity rate** =
fraction of admitted mutants that flip exactly one. Concretely:

1. A per-stratum purity table (rows CE/OS/HP/TF/SI, column "% mutants flipping
   exactly one invariant").
2. The off-diagonal kill mass re-attributed: of the `j ≠ k` kills, how many come
   from *pure* cross-stratum mutants vs multi-stratum ones.
3. If purity is high (say ≥ 90%), the fiber partition survives and this is a
   two-paragraph robustness win. If it is low, the RQ2 aligned-vs-cross reading
   must be re-stated as "kill mass by *declared generating* stratum" (a weaker,
   still-publishable claim) rather than "by semantic-effect fiber."

Leaving S5 as a discussion-section disclaimer while the theory section
(`main.tex:971-985`) silently treats `σ` as single-valued is the gap. At
minimum, the effect-map definition must carry an inline "well-defined as a
function only on the S5-pure sub-domain; multi-stratum edits are handled as …"
note *at the definition*, not 1400 lines later in the discussion.

## 4. Industrial arm — does 34 cases convince a domain reviewer of real-world relevance?

**Partially, and the framing is now honest, but three things cap its
persuasiveness.**

What works: the arm spans a credible spread of *widely used* libraries — numpy
2.4.4, scipy 1.17.1, scikit-learn, plus LAPACK, OpenBLAS, PocketFFT,
OrdinaryDiffEq, jax (`supplementary.tex:281-282, 1443-1445, 1495-1499`) — not
author kernels, which is the right rebuttal to "toy PUTs." The 34 cases span
five strata (mono 10 / conv 9 / inv 6 / adj 5 / rev 4, `supplementary.tex:1480-1483`).
The four *non-nesting counterexamples* (A-LAPACK-004, A-OPENBLAS-001,
B-POCKETFFT-002, E-ORDINARYDIFFEQ-001, `main.tex:2478-2487`) with distinct
mechanisms (order-preserving value destruction, symmetry-preserving zeroing,
in-bounds overshoot, stale-read edit) are the strongest qualitative content in
the whole paper — they show construct *separation*, not just a score. Keep and
expand these.

What caps it:

1. **The dataset is self-authored and unpublished.** `defect4mr2026` is
   `howpublished = {Unpublished project design note and artifact specification}`,
   `note = {Project material, University of South China}` (`references.bib`).
   The 34-case evidence therefore rests on an artifact the reviewer cannot
   inspect, produced by the same group — the antithesis of an independent
   community benchmark (Defects4J-style). The paper *does* cite a Zenodo DOI
   (10.5281/zenodo.21203424, `main.tex:2424`), which contradicts the bib's
   "Unpublished" descriptor — reconcile these, and if the DOI resolves, cite it
   as the primary and drop "unpublished."
2. **No per-case table reaches the reader.** The arm reports only "result-level
   facts" (`supplementary.tex:1460-1500`): stratum counts, four-group aggregate,
   and the 34/34 face. A domain reviewer wants, at minimum, a per-case table
   (case ID, library, version, defect one-liner, registered MR stratum,
   T1/B1/B2/A1 detection). Without it the "26/34, 27/34, 19/34 baseline-blind"
   contrast (`main.tex:2460-2463`) is unauditable. Given the paper insists it is
   "not a benchmark article," a *results appendix* table (not mining tooling)
   would not violate that boundary and would materially raise credibility.
3. **The marginal stat is fragile and honestly reported — but thin.** T1 vs B1
   is +0.101, Holm-adjusted p = 0.046, Cliff's δ = +0.247, and the paper itself
   flags the effect narrowed from 30→34 cases (`main.tex:2444-2451`). The other
   two family members are non-significant. A single p just under 0.05 on a
   self-built 34-case corpus is not, on its own, "real-world relevance." The
   evidential weight genuinely lives in the *blindness contrast* and the
   *non-nesting counterexamples*, and the paper should lead with those rather
   than the p-value.

To make it convincing: (a) publish/point to a resolvable per-case table; (b) if
feasible, overlap even a handful of cases with an established scientific-computing
bug corpus so at least part of the arm is independently verifiable; (c) foreground
the mechanistic non-nesting cases as the construct-separation evidence and demote
the marginal aggregate to a supporting role.

## 5. Terminology and construct clarity — SMS/MS, five invariant classes, meta-mutation operators

Three collisions a TOSEM MT reader will trip on:

1. **"meta-operator" vs "meta-pattern."** The five *mutation operator families*
   are called "meta-operator classes" (CE/OS/HP/TF/SI, `main.tex:212, 959, 1232,
   2977`) and the five *MR strata* are called "meta-patterns" (MP,
   `main.tex:625-627, 1262`). Two distinct 5-element sets, both prefixed
   "meta-," put into a load-bearing 1-1 alignment `align(j)=j`. Since RQ2's whole
   result is aligned-operator-vs-cross-operator against meta-patterns, having
   both objects named "meta-X" is a genuine readability hazard. Rename one — e.g.
   operator *families* (drop "meta-") and reserve "meta-pattern" for MR strata.
2. **Dual naming CE = mut_C, OS = mut_M, HP = mut_G, TF = mut_T, SI = mut_F**
   (`main.tex:212-214, 1311, 2977`). The subscript letters do not match the
   abbreviations (OS↔M, HP↔G), so the reader must memorise a second, mnemonic-
   breaking scheme. This was flagged last round and persists. Pick one scheme.
3. **Three interlocked 5-sets.** Five invariant classes `I = {ψ₁…ψ₅}`
   (`main.tex:952-955`), five operator families (`mut_C…mut_F`, `main.tex:959`),
   five meta-patterns — all in tight 1-1-1 correspondence via `align(j)=j`. This
   is elegant but brittle: the family-leakage examples the paper *itself* gives
   (c3_HP1 "relu→tanh" sits at the OS/HP boundary; c3_TF1 "max_iter 1000→5" at
   the HP/TF boundary, `main.tex:2379-2390`) show the operator→stratum identity
   is not crisp exactly where RQ2 needs it. The labelling-slack caveat
   (`main.tex:2386-2390`) is honest but concedes the discriminant is soft.

**Residual "structurally unreachable" inconsistency (partial fix #24).** The
figure-3 caption was softened — `main.tex:1382-1384` now reads "SI and TF are
structurally cross-function, while HP zero overlap reflects the default
first-order value menu." But the very next table, `tab:p2-05`
(`main.tex:1430-1432`), still labels **all three** HP/SI/TF "Structurally
unreachable," and the body prose at `main.tex:1445-1448` says "HP, SI, and TF …
are unrepresentable under default first-order configurations … The unreachability
is structural under first-order operators." So within the *same subsection* HP is
simultaneously "structural" (table + prose) and "a value-menu artifact"
(caption). HP is an AST-local single-literal edit (necessary-conditions table
marks HP "×" on structural condition (a), `main.tex:1207-1237`), so the caption
is the correct reading and the table/prose overstate. Fix the table cell
("value-menu artifact, not structural") and the prose to match the caption.
This is the residual of prior Blocker 6.

---

## Reviewer 2 视角的最严苛审稿意见

Five-dimension ARS scan (methodology / external validity / statistical selection
bias / benchmark fairness / Hawthorne):

- **[致命问题 1 — methodology] The effect map `σ` is not proven well-defined, and
  the paper's headline result depends on it.** `σ` is presented as a function
  (`main.tex:971-985`) but is single-valued only on the S5-pure sub-domain
  (`main.tex:952-955`); S5 is never verified (`main.tex:2391-2395` admits this),
  and the off-diagonal kill mass — the *contrast* term of the RQ2 aligned-vs-cross
  result — is by the authors' own words possibly a multi-stratum artifact. Because
  S5 is *decidable on the bounded corpus* with the existing AVP checkers, a
  reviewer will treat "we didn't run it" as unacceptable rather than a limitation.
  This is a publication blocker until either (a) a per-mutant invariant-flip-count
  / purity audit is reported, or (b) RQ2 is re-stated over *declared generating*
  stratum with `σ`'s partiality made explicit at the definition. **Fixable without
  new data — it is a re-run of code that already exists.**

- **[非致命, benchmark fairness] Industrial-arm evidence rests on a self-authored,
  unpublished dataset with no per-case table reaching the reader.** `defect4mr2026`
  is "Unpublished … Project material, University of South China" (`references.bib`),
  contradicted by a cited Zenodo DOI (`main.tex:2424`); the baseline-blindness
  contrast (26/34, 27/34, 19/34) is unauditable without a results-level per-case
  table (`supplementary.tex:1460-1500`). Not a blocker because the arm is honestly
  framed as selection-conditioned and result-level, but it must be de-risked with
  a resolvable per-case appendix and, ideally, partial overlap with an independent
  corpus. Reconcile the "unpublished" vs DOI descriptor.

- **[非致命, statistical selection bias] The 34/34 real-defect face is correctly
  disclosed as selection-conditioned** (`main.tex:2456-2463`), and the marginal
  aggregate (Holm p = 0.046, narrowed on 30→34) is reported with its fragility
  (`main.tex:2444-2451`). This is exemplary honesty; no residual selective-reporting
  blocker. The only ask is to *lead* with the blindness contrast and non-nesting
  mechanisms rather than the p-value.

- **[非致命, external validity] Scope is honestly bounded** to single-output
  float-to-float kernels < 2 KB (`main.tex:173-176`), with no industrial-transfer
  claim for multi-output software. The industrial arm partially addresses transfer
  via real libraries but on a small n. Acknowledged, not a blocker.

- **[Hawthorne] Not applicable** — no human subjects, no behavioural intervention;
  mutants and MR checks are mechanical. No Hawthorne exposure.

**Bottom line:** one genuine publication blocker (S5 / `σ` well-definedness),
cheaply closable with existing code; everything else is minor-to-major polish.
The paper's honesty infrastructure is a real asset — do not let the S5 gap sit
behind a discussion-section disclaimer while the theory section uses `σ` as a
function.
