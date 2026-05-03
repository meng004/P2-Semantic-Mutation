# Zenodo Upload Metadata (R-25 artifact commitment)

> Draft metadata for archiving the P2 reproducibility bundle on Zenodo.
> Replace `<TBD>` placeholders before upload. After upload, paste the
> minted DOI into `DATASET.md` §9 and the paper §8 (artifact section).

## Upload type

`Software` (with linked dataset)

## Title

When LLM Source Diversity Doesn't Help: A Semantic Mutation Score Audit — Reproducibility Bundle (P2)

## Creators

| Order | Name | ORCID | Affiliation |
|---|---|---|---|
| 1 | Li, Meng | `<TBD>` | `<TBD>` |
| 2 | `<TBD coauthor>` | `<TBD>` | `<TBD>` |

## Description (Zenodo HTML field)

```
This archive contains the complete reproducibility bundle for the paper
"When LLM Source Diversity Doesn't Help: A Semantic Mutation Score
Audit" (under review at Information and Software Technology).

Contents:
- src/      — Python implementation of 12 PUTs, 60 MRs, 37 mutation
              operators, AVP dispatcher, LRCA 3-layer diagnosis,
              SMS computation, RQ1-4 statistical analysis
- scripts/  — end-to-end campaign scripts (build_pools, sms_campaign,
              run_lrca, compute_rq{2,3,4}, build_paper_numbers,
              render_figures)
- data/     — 470 raw LLM trials, 212 confirmed mutants, v4
              cross-source pools, all paper-cited metrics
              (paper_numbers_v4.json is the SSOT)
- figures/  — 5 paper figures (PDF), and v2/ snapshot for lineage
- tests/    — 116 unit tests covering PUT/MR/AVP/LRCA/equiv components
- REPRODUCIBILITY.md — exact command sequence to reproduce all paper
              numbers from cached data in ~20 minutes
- DATASET.md — per-artifact provenance and version lineage

Reproducibility level: any-rerun (deterministic from committed cache).
Path B (re-call all LLMs from scratch) requires API credentials for
Claude (Anthropic), GPT-5.4 (via any OpenAI-compatible proxy), DeepSeek V4 Pro and
~USD $80; non-deterministic by construction.
```

## Keywords

`metamorphic testing`, `mutation testing`, `test adequacy`, `scientific computing`, `large language models`, `LLM-generated mutants`, `reproducibility`, `Python`

## License

- **Software (`src/`, `scripts/`, `tests/`):** MIT
- **Data (`data/`, `figures/`):** CC-BY-4.0

## Related identifiers

| Relation | Identifier | Type |
|---|---|---|
| `isSupplementTo` | `<paper DOI placeholder; populated post-acceptance>` | DOI |
| `isPartOf` | `<series DOI: P1 → P2 → P3 → P4>` | DOI (TBD) |
| `references` | `10.1109/IST.2024.<TBD>` (Tip 2024 LLMorpheus) | DOI |
| `references` | `10.1109/ICSE.2018.<TBD>` (Petrović & Ivanković 2018) | DOI |

## Funding

`<TBD funding source>`

## Version

`1.0.0` — first archival release; corresponds to commit hash recorded
in `git log -1 --format=%H` at upload time.

## Communities

- `mt` (Metamorphic Testing community, if exists)
- `software-citation`

## Pre-upload checklist

- [ ] All paths in `REPRODUCIBILITY.md` resolve from a fresh clone
- [ ] `pytest -q` passes 116/116 on a fresh venv
- [ ] `data/results/paper_numbers_v4.json` matches §6 of REPRODUCIBILITY
- [ ] `.env` is **not** in the bundle (`.gitignore` confirms)
- [ ] LICENSE present (MIT)
- [ ] Authors' ORCIDs filled in
- [ ] Co-author affiliations filled in
- [ ] Funding source filled in (or marked "self-funded")
- [ ] Tag the commit: `git tag -a v1.0.0-zenodo -m "Zenodo archive snapshot"`

## After-upload follow-up

1. Paste DOI into:
   - `DATASET.md` §9 citation block
   - 论文初稿P2.md §8 (artifact availability statement; pending R-25)
2. Add Zenodo DOI badge to `README.md`
3. Update `docs/STATE.md` "Stage" line to reflect artifact archived
