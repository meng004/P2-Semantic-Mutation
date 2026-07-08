# Study-2 Campaign Runbook — cross-source dual-blind mutant generation

**Status:** campaign machinery is READY. All steps below are executable the
moment a valid `.env` is supplied. Nothing here has been run against a live LLM
(no credentials at authoring time). This runbook is the single documented
command sequence for Study-2 data generation.

**Preconditions (all satisfied at authoring):**
- Pre-registration frozen: `docs/prereg_v2/PREREGISTRATION_STUDY2.md` (§5
  dual-blind protocol, §7 SSOT paths, master seed `20260708`, K=3).
- PUT grid expanded 12→30 (`PUT_EXPANSION_IMPLEMENTATION.md`).
- Operator registry expanded 37→91 specs
  (`src/p2/mutators/operator_registry.py`): 37 original + 54 new (18 PUTs ×
  3 ops), authored blind to mutation outcomes.
- Full suite green: `PYTHONPATH=src python3 -m pytest tests/ -q` → 371 passed
  (324 baseline + 24 pre-frozen analysis-script tests `tests/analysis/` + 23
  CF/TF single-stratum filter tests `tests/mutators/test_stratum_filter.py`).
- Offline dry-run proves the pipeline end-to-end minus the API (see §5).

---

## 1. Environment variables (`.env` at repo root)

Copy `.env.example` → `.env` and fill in real values. Required keys
(consumed by `src/p2/mutators/llm_client.py`):

| Var | Role |
|---|---|
| `BLTCY_BASE_URL` / `BLTCY_API_KEY` | OpenAI-compatible proxy — Claude generator + GPT reviewer |
| `DEEPSEEK_BASE_URL` / `DEEPSEEK_API_KEY` | DeepSeek generator + arbiter |

`.env` is gitignored. Never commit real keys. The generator/reviewer family
map is `claude → gpt → deepseek → claude` (ring rotation, §5: generator ≠
reviewer ≠ arbiter on every item).

Sanity-check credentials load before spending tokens:

```bash
PYTHONPATH=src python3 -c "from p2.mutators.llm_client import generator_claude, generator_gpt, generator_deepseek; [f() for f in (generator_claude, generator_gpt, generator_deepseek)]; print('credentials OK')"
```

---

## 2. Command sequence (run in order)

All commands assume repo root and a populated `.env`. Seeds/counts are the
registered ones (seed `20260708`, K=3); do not override them.

### 2.1 Mutant generation — cross-source arm (v4-style, 3 families)

```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --arm cross --review
```

- 91 operators × 3 sources × K=3 = **819 generation trials**, each followed by
  the §5 blind review (reviewer sees only mutant + operator spec + PUT source;
  generator identity, arm label, and SMS are withheld) and arbitration on
  disagreement.
- Output cache: `data/operator_campaign/cache_cross/{op}_{source}_attempt{NN}.py`
  + `_log.json` (per-trial metadata, incl. `review` verdicts).

### 2.2 Mutant generation — same-source arm (v3-style, 1 family)

```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --arm same --review
```

- 91 operators × 1 source × K=3 = **273 generation trials**, identical review
  pipeline. This is the asymmetry fix (L4): both arms score through the *same*
  dual-blind protocol, so any Δδ is attributable to source diversity, not to a
  review-quality drop.

> Both arms write into the same cache dir with distinct source tags; keep the
> arms' outputs separated for Δδ by tagging (the same-source arm uses only the
> `claude` tag). Commit the review labels to
> `data/operator_campaign/cache_cross/` **before** any SMS is computed (§5
> "freeze then score"; analyst blindness).

### 2.3 Build per-PUT mutant pools (dedup / proportional selection + CF/TF filter)

```bash
POOL_VERSION=v4 PYTHONPATH=src python3 scripts/build_pools.py   # cross arm  → data/mutants/{put}_pool_v4/
POOL_VERSION=v3 PYTHONPATH=src python3 scripts/build_pools.py   # same arm   → data/mutants/{put}_pool_v3/
```

`build_pools.py` reads `POOL_VERSION` (v4 = `cache_cross`, v3 = `cache`) and
calls `p2.mutators.pool_builder.select_mutants_for_put` (seed `20260708`) to
select the registered N valid mutants per PUT (v4 = 12, v3 = 30) proportionally
across the operators.

**CF/TF single-stratum admission filter (Study-2, default ON).** When
`single_stratum_filter_enabled()` is true (env `P2_SINGLE_STRATUM_FILTER`,
default `1`) **and** `POOL_VERSION` is a Study-2 version (`v4`/`v5`), each CF/TF
candidate is screened against all five offline AVP checkers **before any SMS is
computed** and admitted iff its invariant-flip count ≤ 1; CE/OS/HP/SI are
admitted unconditionally. The screen is deterministic and identical for both
arms and every PUT. This closes the Study-1 H4 attribution leakage (multi-valued
`sigma`, 35.2% of the off-diagonal kill mass). Full spec, contract, and
audit-mode validation (29/29 recall on Study-1): `docs/prereg_v2/CFTF_CONSTRAINT.md`.
The `build_pools.py` banner prints `single_stratum_filter=ON|OFF`. Study-1
frozen pools (`v2`/`v3`) are never re-screened. To disable (a **disclosed
deviation** from registration): prepend `P2_SINGLE_STRATUM_FILTER=0`.

### 2.4 SMS scoring — Track-2 full 30×5 = 150-cell matrix

```bash
P2_PRIMARY_VERSION=v3 PYTHONPATH=src python3 scripts/sms_campaign.py --track 2 --workers 6 \
    --out data/results/sms_track2_v5.json
```

Runs V1–V4 + AVP/equiv + SMS bookkeeping per cell. `P2_PRIMARY_VERSION=v3` is
mandatory (§4: the deterministic class-indexed primary rule; the v3b path is
prohibited in Study 2).

---

## 3. Cost & runtime estimate (anchored to Study-1 logs)

From `data/operator_campaign/cache_cross/_log.json` (6 ops × 3 × K=3 = 54
trials) and `campaign_log.json` (37 ops, K=10/20):

| Quantity | Study-1 observed | Study-2 projection |
|---|---|---|
| Gen tokens / trial | ~559 prompt + ~338 completion ≈ **900** | same |
| Latency / trial | ~7.2 s (3 sources parallel → ~3.5 s wall) | same |
| Gen trials | 54 (pilot) | **819 (cross) + 273 (same) = 1 092** |
| Review round-trips | n/a (v4 was mechanical-only) | ~1 / passed mutant; pass rate ≈ 35 % → ~**380** reviews + arbiter subset |
| Total tokens | 48 k (pilot) | gen ≈ 1.0 M + review ≈ 0.4 M ≈ **1.4 M** |
| Wall time @ concurrency 20 | 190 s (54 trials) / 999 s (37 ops K≈13) | **~2–4 h** (generation + review dominate) |

Dollar cost depends on the proxied model prices; at ~1.4 M mixed tokens this is
a **small single-digit-dollar to low-tens-of-dollars** campaign, not a large
spend. Budget for retries (transient 429/timeout; `async_llm` retries 3× with
backoff).

---

## 4. Output SSOT paths (registration §7) and downstream analysis

| Artefact | SSOT path |
|---|---|
| SMS pool (30×5) | `data/results/sms_track2_v5.json` |
| Aligned/cross Cliff's δ | `data/results/rq2_cliffs_delta_v5.json` |
| Dual-blind Δδ (both arms) | `data/results/dualblind_delta_delta_v5.json` |
| Industrial per-case (frozen census) | `data/results/industrial_percase_v2.json` |
| Industrial stats | `data/results/industrial_stats_v2.json` |
| Power reference (this registration) | `data/results/power_study2.json` |

Registered analysis scripts that consume the SSOTs (run after generation):

```bash
# H2-1 aligned-vs-cross δ + H2-2 dual-blind Δδ (Families A, B).
# H2-1: one-sided 95% bootstrap lower bound > 0 (seed 20260708).
# H2-2: paired-role bootstrap Δδ = δ(cross-source) − δ(same-source), the two
#       arms block-resampled on the SAME 30 PUTs. Reads both arms' SMS pools.
PYTHONPATH=src python3 scripts/compute_dualblind_delta.py \
    --cross data/results/sms_track2_v5.json \
    --same  data/results/sms_track2_v5_same.json \
    --out   data/results/dualblind_delta_delta_v5.json
# H2-3/H2-4 industrial (Tier-A Wilcoxon Holm-3 + Fisher incidence, Tier-B
#           sensitivity kept separate) on the frozen two-tier census:
PYTHONPATH=src python3 scripts/compute_industrial_stats.py \
    --percase data/results/industrial_percase_v2.json \
    --power   data/results/power_study2.json \
    --out     data/results/industrial_stats_v2.json
PYTHONPATH=src python3 scripts/compute_h2_incidence.py
```

Both `compute_dualblind_delta.py` and `compute_industrial_stats.py` are now
present in `scripts/`, **pre-frozen before any Study-2 data exists** (the
gold-standard ordering: analysis code frozen pre-data). Each carries the header
"Pre-frozen under PREREGISTRATION_STUDY2.md before Study-2 data generation; any
post-data modification must be disclosed as a deviation", encodes the registered
decision rules (printing the licensed verdict per hypothesis, not just numbers),
and is covered by offline synthetic-fixture tests in `tests/analysis/` that
exercise every branch (confirm / not-confirmed / under-recruited / bounded-null /
inconclusive). No author-time analysis-script gaps remain.

---

## 5. What the dry-run mocks (offline pipeline proof)

```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --dry-run
```

Runs the FULL pipeline on 2 PUTs (a2 = existing, a4 = new) with **no network**,
and exits cleanly (`324 passed` suite covers it via
`tests/mutators/test_dryrun_campaign.py`). It exercises: mock generation →
fence normalization → V1–V4 validation → blind dual-blind review + role
rotation → proportional pool selection (dedup) → AVP/equiv → SMS bookkeeping.

| Real step | Mocked in dry-run | Everything else |
|---|---|---|
| Generator LLM call (`_generate_one`) | `MockLLMClient` extracts the original program from the prompt and wraps it with a small deterministic perturbation → a guaranteed-valid, non-trivial fixture mutant | REAL: `_strip_fences`, `validate_mutant`, cache write, `pool_builder.select_mutants_for_put`, `sms_campaign.evaluate_cell` (AVP conservation, equiv, SMS) |
| Reviewer / arbiter LLM call (`_live_review_call`) | mock reviewer returns a fixed CONFIRMED JSON | REAL: `build_blind_review_packet` (blinding), `assign_review_roles` (rotation), verdict parse + `classify_mutant` |

The single live-only site is `_live_review_call()` (and the generator's
`client.chat.completions.create`); both are the documented TODO-gates that the
mock bypasses. Nothing else changes between dry-run and live — the same
functions run, only the client is swapped.

Dry-run expected output: 18 generated trials, 18/18 V1–V4 pass, 18/18
blind-review CONFIRMED, SMS A2_MP1 and A4_MP1 pools each `inst=6`. The harness
removes its scratch cache (`data/operator_campaign/cache_dryrun/`) on exit.

---

## 5b. Harness mode — generation/review WITHOUT a network API

When no external LLM credentials exist, the §2 live path (`--review`, the three
family clients) cannot run. Study-2 generation and review are instead served by
**Claude-agent instances orchestrated by the main session** (disclosed in the
v1.1 amendment). The offline pipeline is untouched: normalization, V1–V4, dedup,
AVP/equiv, and SMS bookkeeping remain EXACTLY the registered machinery. Only the
generator/reviewer *transport* changes — from a chat-completion call to a
file-based PACKET exchange. Ingestion re-uses `admit_mutant()`, the SAME
normalization → V1–V4 → admission function the live and mock clients call, so a
packet-ingested mutant is byte-indistinguishable downstream.

### Orchestration sequence

```
1. export generation packets      (once, for the confirmatory run)
2. spawn agents per packet batch   → each writes a response file
3. ingest generation              → per-PUT admitted mutant cache
4. build pools + SMS              (§2.3–§2.4, unchanged; CF/TF filter still applies)
5. export blinded review packets  → spawn reviewer agents → ingest review
6. ingest review → arbitration packets for disagreements → ingest arbitration
7. analysis                       (§4, unchanged)
```

### Commands

```bash
# 1. GENERATION packets (one per PUT). Confirmatory run: emit ALL PUTs ONCE.
PYTHONPATH=src python3 scripts/cross_source_campaign.py \
    --export-packets data/study2_packets/gen --arm cross     # (or --puts a2,a4)

# 2–3. Agents fill data/study2_packets/gen/gen_<put>_response.json, then:
PYTHONPATH=src python3 scripts/cross_source_campaign.py \
    --ingest-generation data/study2_packets/gen \
    --cache-dir data/operator_campaign/cache_cross            # SAME admission gate

# 4. pools + SMS exactly as §2.3–§2.4 (build_pools.py, sms_campaign.py).

# 5. BLINDED review packets (one per admitted mutant), agents write verdicts:
PYTHONPATH=src python3 scripts/cross_source_campaign.py \
    --export-review-packets data/study2_packets/review \
    --cache-dir data/operator_campaign/cache_cross
PYTHONPATH=src python3 scripts/cross_source_campaign.py \
    --ingest-review data/study2_packets/review

# 6. Arbitration packets land in data/study2_packets/review/arbitration/;
#    agents write verdicts there, then re-ingest that sub-directory:
PYTHONPATH=src python3 scripts/cross_source_campaign.py \
    --ingest-review data/study2_packets/review/arbitration \
    --packets-dir  data/study2_packets/review/arbitration
```

### What packets contain (and deliberately omit)

- **Generation packet** (`gen_<put>.json`): the registered prompt template
  (pinned by `sha256`; the F2 single-stratum CF/TF clause of §2.3 is folded into
  the rendered prompt when enabled), PUT source, MR definitions, per-operator
  specs (incl. the CF/TF `constraint_flag` integration point), mutant-count
  target, `seed`, and the response schema. **No SMS/outcome field anywhere.**
- **Review packet** (`rev_<blind>.json`): mutant code + PUT + operator context
  only. **Blinded** — no generator identity, no arm label, no cell aggregates,
  no SMS. The blind-id→source map (`_blind_map.json`) is private (audit only,
  never shown to the reviewer agent). Verdicts carry V-checks + an E1∧E2
  equivalence opinion (recorded; the mechanical AVP/equiv pipeline stays
  authoritative for SMS).

### Batch sizes

- **Generation**: batch by PUT (one packet = one PUT = up to ~3 operators ×
  |sources| × K=3 slots). Spawn one agent per packet; ~10–15 packets per wave
  keeps orchestration reviewable. 30 PUTs → 30 generation packets.
- **Review**: batch ~20–40 blinded packets per agent wave (each verdict is
  independent and short). Arbitration is a small tail (only disagreements).

### One-shot rule (confirmatory)

Packets for the confirmatory run are generated **once**. `--export-packets`
writes a manifest (`manifest.json`: per-packet `sha256`, slot counts,
timestamps) and appends a `campaign_log.json` entry; re-exporting the same PUT
overwrites its manifest row rather than silently forking a second draw. The
manifest is the proof of one-shot: any re-generation is visible as a changed
`sha256`/timestamp. Strict ingestion rejects malformed responses (logged with
clear errors) and never applies packet-specific leniency, so the admitted pool
is a pure function of the agent responses + the registered gate.

The round-trip is covered offline by `tests/mutators/test_packet_harness.py`
(export → synthetic well-formed + malformed responses → ingest → pool → SMS
cell appears; malformed rejected with clear errors; review blinding + arbitration).

---

## 6. Integrity notes

- Operator specs (`operator_registry.py`, the 54 new entries) were authored
  from PUT source + registry conventions only; **no `data/results/*`** file was
  read. Existing 37 operators are byte-unchanged (`test_old_put_operators_unchanged`).
- SMS is computed only *after* review labels are frozen (§5). Reviewers never
  see kills; the analyst does not alter review labels.
- Primary-MP is the deterministic class rule (A→MP1, B→MP2, C→MP5, D→MP2);
  run with `P2_PRIMARY_VERSION=v3`. No outcome-conditioned reselection.
- CF/TF single-stratum filter (§2.3) is keyed on the **Study-1** S5 audit only
  (`data/results/s5_purity_v4.json`); no Study-2 data is peeked. It is a
  campaign-config flag, not a registry edit — the 37 Study-1 specs stay
  byte-unchanged and Study-1 pools are never re-screened. See
  `docs/prereg_v2/CFTF_CONSTRAINT.md`.
