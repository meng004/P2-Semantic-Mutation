# R3 Review — Scientific-Computing V&V Practitioner (TOSEM)

**Reviewer role:** Industrial numerical-library / simulation-software quality assurance.
**Central question I judge by:** *Can I use this, and is it worth using?*
**Manuscript:** `submission/TOSEM_regular_20260707/main.tex` (3114 lines) + `supplementary.tex` (1577 lines).
**Review posture:** independent (no other reviewer visible); manuscript NOT modified; claims spot-checked against the repository.

---

## Summary

The paper defines a Semantic Mutation Score (SMS) as an MR-relative adequacy
metric with an explicit degeneration back to classical Mutation Score, instantiates
it on 12 single-output `float→float` scientific-computing kernels (60-cell audit),
and adds an "industrial real-defect arm" of 34 reproduced library defects to test
whether kill-rate, semantic alignment, and real-defect detection separate as
constructs.

From a V&V-practitioner standpoint the manuscript is unusually honest: it repeatedly
states non-claims (Table 1, lines 218-250), reports pre-registered thresholds it
*fails* (H1–H4), and openly declares air-gap incompatibility. That candor is its
biggest strength and it lifts the scope-honesty score. However, the practical payload
for a real numerical-library team is thin: the SMS metric itself is validated only on
sub-2 KB Python kernels; the industrial arm does **not** compute SMS at all (only a
kill-rate/detection contrast); 25% of even the toy kernels yield zero signal; the cost
model exists only at toy scale; and the workflow is blocked in exactly the regulated
domains it name-drops (IEC 60880, DO-178C). A reproducibility spot-check also surfaced
a labelling discrepancy between the manuscript and the repo's own reproduction guide on
the configuration that produces the headline aligned baseline (0.275).

**Reproducibility spot-check performed (path/file existence, no long runs):**
- `data/results/` present, 60+ artefacts incl. `paper_numbers_v4.json`, `lrca_60cell_v4.json`, `sms_track2_v4.json` — all exist. ✓
- `REPRODUCIBILITY.md` §3 smoke command `PYTHONPATH=src .venv/bin/pytest tests/ -q` — `tests/` exists with subpackages (`avp/ equiv/ lrca/ mrs/ mutators/ puts/ stats/ pipeline/ integration/`). ✓
- All scripts referenced in §4 (`build_pools.py`, `sms_campaign.py`, `run_lrca.py`, `compute_rq2.py`, `build_paper_numbers.py`, `render_figures.py`, `cross_source_campaign.py`) exist. ✓
- `requirements-frozen.txt` present. ✓
- Industrial arm verified via `gh api repos/meng004/P12-Defect4MR/contents/README.md`: repo exists, Zenodo DOI 10.5281/zenodo.21203424 matches main.tex line 2400, libraries listed (LAPACK, OpenBLAS, PETSc, SciPy, FFTW, …). ✓ **BUT** the README census reports **35 `verified_full`** defects (E-PETSC-004 upgraded 2026-07-06), whereas the paper freezes the arm at **n=34** (main.tex line 2396/2431). Defensible (census frozen before comparison) but the mismatch is undocumented in the manuscript.

---

## Strengths

1. **Explicit, auditable non-claims and failed-threshold honesty.** Table 1 (lines 218–250) enumerates what is *not* claimed; H1–H4 verdicts are reported as failures used to delimit scope, not buried (Abstract line 101; RQ5 H3 "not met" line 2563). For a practitioner deciding trust, this is exactly the right posture and rare in this literature.

2. **Air-gap incompatibility stated as a hard limitation up front, not hidden.** Main.tex lines 2676–2683 and limitation #8 (lines 2827–2832), with the standards catalogue and mitigation paths in supplementary §E.1 (lines 1014–1055). The paper does not pretend the LLM-dependent workflow is deployable in regulated V&V.

3. **Honest treatment of the industrial arm's selection-conditioning.** The 34/34 real-defect face is explicitly labelled "selection-conditioned rather than evidential" because admission requires MR-detectability (lines 2468–2471, 2479–2487). The non-nesting counterexamples (A-LAPACK-004, E-PETSC-001/004, C-GSL-001, C-SCIPY-002; lines 2492–2532) are a genuine, falsifiable contribution rather than a cherry-picked win.

4. **SSOT-based reproduction discipline.** A single source of truth (`paper_numbers_v4.json`, `lrca_60cell_v4.json`) is declared for all stakeholder classes (lines 2703–2705) and a frozen pre-registration commit hash + Zenodo DOI are given (lines 530–533).

---

## Weaknesses

### W1 — SMS itself has ZERO industrial validation; the industrial arm validates a *different* construct
**Location:** Abstract closing clause line 101 ("its construct separation supported on industrial code"); RQ4 industrial subsection lines 2391–2538; limitation #10 lines 2846–2856.
**Severity: MAJOR**
The industrial arm does not compute SMS on any library defect; it runs a kill-rate/detection contrast (T1/B1/B2/A1) and a per-defect face. Limitation #10 admits "the semantic-mutant SMS instantiation itself is evaluated on the 12 controlled kernels only; extending SMS computation to the industrial cases is registered follow-up work" (lines 2854–2856). Therefore the industrial arm does **not** demonstrate that the paper's headline metric transfers to industrial code — it only shows a related construct separation persists. The Abstract's final sentence ("SMS is therefore a construct-level diagnostic … with its construct separation supported on industrial code") reads, to a practitioner, as if SMS were validated industrially. The title ("… in Scientific Computing Programs") is similarly broad.
**Fix:** Reword the Abstract's closing clause to "the *construct distinction* (kill-rate vs alignment vs real-defect detection) is supported on industrial code, while the SMS metric is validated only on the 12 kernels." Consider a scope qualifier in the title or first Abstract sentence ("single-output kernels, with a construct-level industrial arm").

### W2 — Reproduction-guide vs manuscript disagree on the configuration behind the headline aligned baseline (0.275)
**Location:** main.tex §3.5.1 lines 1319–1335 and §5.4 lines 2008/2022–2026 ("c-class primary … *held at the pre-registered partial-order meta-pattern*"; "data-driven shift … *withdrawn*"); vs `REPRODUCIBILITY.md` lines 51–59, 86 ("`P2_PRIMARY_VERSION=v3b` … picks the *data-driven* c-class primary MP assignment (c1/c2/c3 → MP1) … **REQUIRED** … without it mean_aligned will be ~0.213 instead of the paper's 0.275").
**Severity: MAJOR**
The manuscript says the configuration producing aligned mean 0.275 is the *pre-registered, held* primary MP and that the *data-driven* reselection was *withdrawn* (permutation p=0.989). The repository's own reproduction guide says the paper's 0.275 is only reproduced with the *data-driven* v3b primary, and that the pre-registered/default path gives 0.213/0.275 divergence. A reproducing practitioner cannot tell which label is correct, and the number in question is the aligned baseline that anchors the whole "Practical Interpretation" section (used as the 0.275 repair trigger, lines 2674, 2685–2690). Either the two documents use "pre-registered/data-driven" inconsistently, or the headline aligned baseline depends on a post-hoc primary-MP choice (a garden-of-forking-paths on the number practitioners are told to act on).
**Fix:** Reconcile terminology explicitly. State in the manuscript which env-var configuration (`P2_PRIMARY_VERSION`) yields Table 8's 0.275, confirm it equals the pre-registered partial-order choice, and add a one-line note in §3.5.1 mapping "partial-order meta-pattern" → the exact MP index → the `v3b` flag.

### W3 — Air-gap blocker + no self-hosted evidence guts practical uptake in the named target domains
**Location:** lines 2676–2683; supplementary §E.1 lines 1014–1055 (mitigations "(a) self-hosted open-weight LLMs (Llama …)").
**Severity: MAJOR**
The paper positions itself for scientific-computing V&V and repeatedly cites nuclear/aerospace/medical standards, yet the only demonstrated workflow requires external commercial LLM APIs (Claude/GPT/DeepSeek), which are prohibited in precisely those air-gapped pipelines. The "self-hosted open-weight LLM" mitigation is asserted with **no experiment** showing an open-weight model produces comparable semantic mutants; it is speculation. So for the audience most in need of MR-adequacy tooling, the answer to "can I use this?" is currently *no*, and the paper offers no evidence the future mitigation works.
**Fix:** Either (a) run even a small open-weight-LLM feasibility probe on 2–3 PUTs and report mutant-quality delta, or (b) demote the regulated-domain framing and standards catalogue so the paper does not imply near-term applicability there.

### W4 — Cost/effort model exists only at toy scale; no scaling estimate for real libraries
**Location:** §Practical Interpretation lines 2685–2692 ("~0.5 person-day per quarter"); supplementary §E.2 Table (lines 1084–1099): "24-30 × 12 PUTs ≈ 300 mutants, API \$5-15, ~30 min".
**Severity: MINOR**
Every quantitative cost figure is derived from the 12-kernel, ~300-mutant campaign. A practitioner cannot extrapolate to a multi-module library (thousands of functions, non-trivial build/execution harness, multi-output signatures). The "0.5 person-day/quarter" and "\$10/quarter" numbers should not be read as an industrial cost model, but the phrasing invites that reading.
**Fix:** Add one sentence bounding the cost estimate to the 12-kernel scale and stating that industrial-scale cost is unquantified.

### W5 — Threats table omits practitioner-relevant longevity/degrees-of-freedom threats
**Location:** Threats table lines 2744–2777; final limitations lines 2780–2857.
**Severity: MINOR**
Two threats a QA practitioner would want addressed are missing: (i) **LLM model deprecation / API discontinuation** — Path B reproduction and any future pool generation depend on commercial models that get retired; the archival cache protects *this paper's* numbers but not an adopter regenerating pools two years out. (ii) **Primary-MP selection as an analyst degree of freedom** — the aligned/cross grouping (hence 0.275) hinges on the c-class primary-MP convention (W2); this researcher-choice sensitivity is discussed in §3.5.1 but is absent from the threats catalogue. The env-var fragility (`REPRODUCIBILITY.md` line 86: forgetting the flag silently yields 0.213) is itself a reproducibility threat worth listing.
**Fix:** Add both rows to Table (Threats to Validity), each with the mitigation already implied in the text.

### W6 — 25% zero-signal PUT cohort undercuts "usable adequacy metric" for practitioners
**Location:** lines 2876–2889 (A1, A3, C2 all-zero across all five MPs; "for 25% of the PUTs, SMS gives zero signal at every operator-MP cell").
**Severity: MINOR**
This is disclosed honestly (so not a scope-honesty failure), but from a *usability* standpoint it is a first-order concern: on a quarter of even the hand-picked toy kernels the metric cannot rank MR sets at all. The paper attributes this to MR-design adequacy rather than mutant generation (R_sem≈1.0), which is the right diagnosis, but a practitioner needs an ex-ante signal for *when* SMS will be informative before investing the LLM budget.
**Fix:** Add a short "when NOT to use SMS" note to Table (Reading SMS and LRCA together, lines 2650–2670): if a PUT's admitted-mutant pool has R_sem≈1 but zero kills across all MPs, SMS is uninformative and the effort should go to MR discovery first.

---

## Scores (0–10)

| Dimension | Score | Rationale |
|---|---|---|
| **external_validity** | 5 | SMS validated only on 12 sub-2 KB Python kernels; industrial arm tests a *different* construct and does not compute SMS (W1); 25% zero-signal PUTs (W6); n=60 cannot fit the hierarchical model (lines 2859–2874). Honest, but genuinely narrow. |
| **practicality** | 4 | Hard air-gap blocker in the named target domains with only speculative mitigation (W3); LLM-API dependency; cost model toy-scale only (W4). Offline cache-replay path and "diagnostic not deployment" framing keep it off the floor. |
| **scope_honesty** | 7 | Exemplary non-claims table, failed-threshold reporting, and selection-conditioning disclosure. Docked for the broad title, the Abstract's "supported on industrial code" over-read (W1), and the manuscript/repo primary-MP labelling clash (W2). |
| **reproducibility** | 6 | Scripts, tests, SSOT, frozen commit, and Zenodo DOIs all present and verified; industrial repo verified. Docked for the §3.5.1-vs-`REPRODUCIBILITY.md` discrepancy on the headline number (W2) and env-var fragility that silently yields wrong numbers; full run not executed. |

---

## Verdict

**Major revision.** The construction is sound and the honesty is genuinely above field norm, but as an industrial V&V reader I cannot yet act on it: the headline metric is unvalidated outside toy kernels, the industrial arm proves a narrower point than the Abstract implies, and the tool is blocked in the regulated domains it courts.

**Distance to stable acceptance (one sentence):** Reconcile the primary-MP labelling between manuscript and reproduction guide (W2) and re-scope the Abstract/title so the industrial-code claim matches what was actually measured (W1); the remaining air-gap/cost/threats items (W3–W6) can be closed with text plus one small open-weight feasibility probe.
