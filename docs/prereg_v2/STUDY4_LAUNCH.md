# Study-4 Confirmatory Launch Runbook (pre-data, one-shot)

**Status**: code-level launch readiness. NO confirmatory data exists. Every
command below is copy-paste ready; the coordinator executes them **once** per
the §5d one-shot rule. LIVE steps require the gitignored `.env`
(`BLTCY_BASE_URL` / `BLTCY_API_KEY`). Pre-frozen registration:
`docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md` (+ Amendment v1.1).

Three confirmatory arms → three SSOTs → three verdicts:

| Arm | Family | Roster | Rich x4? | Generation cache | Pool | SMS SSOT | Verdict SSOT |
|---|---|---|---|---|---|---|---|
| Same-source (Python) | — | 28 PUTs | **yes** (C/D) | `cache_study4/same` | `{put}_pool_v7_same` | `sms_track2_v7_same.json` | (feeds H2-2 + H4''') |
| Cross-source (Python) | B (H2-2) | 28 PUTs | **yes** (C/D) | `cache_study4/cross` | `{put}_pool_v7` | `sms_track2_v7.json` | `dualblind_delta_delta_v7.json` |
| C-port (H-LANG) | L | 7 PUTs | **NO** (§2c) | `cache_clang` | `{put}_pool_v7c` | `sms_track2_v7c.json` | `hlang_delta_v7c.json` |

- **28-PUT confirmatory roster** (pilots `{a2,b4}` excluded): `a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8`
- **7-PUT C roster** (a2 RETAINED confirmatory, §0.3 A2): `a1,a2,a3,b1,b2,b3,c2`
- **Rich x4** = the 15 C/D PUTs generate at `attempts × 4` per (operator, slot); A/B at baseline; config-driven (`configs/study4_models.json::rich_multiplier=4`). The C arm is baseline for every PUT.
- **Blinded review is folded into generation** via `--review` (reviewer `claude-fable-5`, arbiter `gpt-5.5`, vendor-blinded packets). SMS is computed only in the *separate* scoring step below → **freeze-then-score** (§5a) is preserved because review completes before any pool/SMS runs.

---

## 1. Generation + blinded review (LIVE, one background command per arm)

Each command runs generation → inline blinded review + arbitration, writing a
per-call token/cost JSONL log. Run the two Python arms as concurrent background
processes; run the C arm after (or concurrently — different cache).

### 1a. Same-source Python arm
```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --study4 --arm same --review \
  --attempts 3 \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8 \
  --cache-dir data/operator_campaign/cache_study4/same \
  --study4-log data/operator_campaign/cache_study4/same/campaign_log.jsonl
```

### 1b. Cross-source Python arm
```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --study4 --arm cross --review \
  --attempts 3 \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8 \
  --cache-dir data/operator_campaign/cache_study4/cross \
  --study4-log data/operator_campaign/cache_study4/cross/campaign_log.jsonl
```

### 1c. C-port (H-LANG) arm — cross-vendor slots, `--lang c`, NO rich multiplier
```bash
PYTHONPATH=src python3 scripts/cross_source_campaign.py --study4 --arm cross --lang c --review \
  --attempts 3 \
  --puts a1,a2,a3,b1,b2,b3,c2 \
  --cache-dir data/operator_campaign/cache_clang \
  --study4-log data/operator_campaign/cache_clang/campaign_log.jsonl
```

On start each arm prints its slot mapping; the Python arms additionally print a
`[rich-x4] … rich=[c1,c2,…,d8]` line confirming the 15 C/D PUTs are at 4×.

**Expected scale / runtime / cost** (projected from the R5 pilots — the reduced
`{a2,b4}` Python pilot and `{a3,b2}` C pilot; see `data/results/study4/`):

| Arm | gen calls (approx) | admission | per-call wall | wall (sequential) | LLM cost (proj.) |
|---|---|---|---|---|---|
| Same Python | ~1,990 (rich x4) | 0.97 (pilot) | ~11 s | ~10–14 h | — |
| Cross Python | ~1,990 (rich x4) | 0.97 (pilot) | ~9–11 s | ~9–13 h | — |
| Both Python (gen+review) | — | — | — | run concurrently | **≈ $150–210** |
| C-port | ~190 | 0.67 (pilot; grok-4.3 weakest at C99) | ~12 s | ~1–2 h | ≈ $5–10 |

The pilot's uniform-K3 projection was $80.6 for both Python arms; the registered
**rich x4** raises Python generation ≈ 2.6× (15/28 PUTs at 4×) with review scaling
proportionally, hence the $150–210 band. Costs are gateway-usage-derived and
approximate (the `claude-fable-5` prompt-token count is inflated/unstable — PILOT
P11 — so `cost_usd` is recorded verbatim but flagged). Gemini runs with the
`max_tokens ≥ 2000` floor; C generation uses a 2048-token budget (P14).

---

## 2. SMS scoring (per arm) — pool (rename) then score to the SSOT

Pools are built with `build_pools.py` (which renames mutants to
`m{idx}_{op}_a{attempt}` so `category_from_filename` parses the operator category
— **required** by the H4''' audit; the raw cache names are not parseable). SMS
then scores the full 5-MP Track-2 matrix into the registered SSOT.

### 2a. Same-source Python arm → `sms_track2_v7_same.json`
```bash
PYTHONPATH=src python3 scripts/build_pools.py --pool-version v7_same \
  --cache-dir data/operator_campaign/cache_study4/same \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8

PYTHONPATH=src python3 scripts/sms_campaign.py --track 2 --pool-version v7_same --workers 6 \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8 \
  --out data/results/sms_track2_v7_same.json
```

### 2b. Cross-source Python arm → `sms_track2_v7.json`
```bash
PYTHONPATH=src python3 scripts/build_pools.py --pool-version v7 \
  --cache-dir data/operator_campaign/cache_study4/cross \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8

PYTHONPATH=src python3 scripts/sms_campaign.py --track 2 --pool-version v7 --workers 6 \
  --puts a1,a3,a4,a5,a6,a7,a8,b1,b2,b3,b5,b6,b7,c1,c2,c3,c4,c5,c6,c7,d1,d2,d3,d4,d5,d6,d7,d8 \
  --out data/results/sms_track2_v7.json
```

### 2c. C-port arm → `sms_track2_v7c.json` (`--lang c`, gcc adapter)
```bash
PYTHONPATH=src python3 scripts/build_pools.py --pool-version v7c \
  --cache-dir data/operator_campaign/cache_clang \
  --puts a1,a2,a3,b1,b2,b3,c2

PYTHONPATH=src python3 scripts/sms_campaign.py --track 2 --lang c --pool-version v7c --workers 4 \
  --puts a1,a2,a3,b1,b2,b3,c2 \
  --out data/results/sms_track2_v7c.json
```

SMS wall time is minutes (offline AVP/equiv on the compiled/loaded pools).

---

## 3. Analysis (three frozen scorers — the confirmatory verdicts)

All three are pre-frozen (§7b); bootstrap seed 20260708, B = 10,000. They exit 2
if their input SSOT is absent (no data at freeze).

### 3a. H2-2 — cross-vendor dual-blind Delta-delta (Family B)
```bash
PYTHONPATH=src python3 scripts/compute_dualblind_delta.py \
  --cross data/results/sms_track2_v7.json \
  --same  data/results/sms_track2_v7_same.json \
  --out   data/results/dualblind_delta_delta_v7.json
```
Run **without** `--gated-h2-2` (cross-vendor credentials now exist). The frozen
script's defaults are the Study-2 v5 paths and are **unchanged**; Study-4 points
it at the v7 SSOTs with explicit flags exactly as §7b registers. Decision:
CI excludes 0 → CONFIRM; includes 0 ∧ half-width ≤ 0.14 → BOUNDED_NULL; else
UNDER_RECRUITED.

### 3b. H4'''-graded — pooled rich-class attribution (Family H)
```bash
PYTHONPATH=src python3 scripts/compute_h4_graded.py --pooled \
  data/results/sms_track2_v7.json data/results/sms_track2_v7_same.json \
  --out data/results/h4_graded_v7.json
```
Recruitment gate: pooled n_rich ≥ 24 → then boot_lower_95 > 0.15 → CONFIRM, else
MISATTRIBUTION_CONFIRMED; pooled n_rich < 24 → UNDER_RECRUITED (no threshold
moved). Pilots `{a2,b4}` are firewalled inside the scorer.

### 3c. H-LANG — cross-language invariance (Family L)
```bash
PYTHONPATH=src python3 scripts/compute_hlang_delta.py \
  --matrix data/results/sms_track2_v7c.json \
  --out    data/results/hlang_delta_v7c.json
```
Decision: one-sided 95% lower bound on delta_C > 0 → CONFIRM language-invariance,
else a reported falsification. Power 0.6865 @ n=7 (disclosed, below 0.80).

---

## 4. One-shot / firewall reminders (§5d)

- Run each generation command **exactly once**. Regeneration, re-rolling an arm,
  cherry-picking cells/vendors, or moving any threshold after an outcome is
  visible is a protocol violation → report in §10.
- The calibration pilots are the only place live outcomes were seen pre-freeze
  and fixed **code only** (P13/P14). The confirmatory pools are fresh.
- Do not write into the pilot artefacts (`*_pilot*`, `cache_clang_pilot`,
  `cache_study4_pilot`, `data/results/study4/`); the commands above use the
  confirmatory caches/pools/SSOTs only.
- Offline wiring for all three arms + all three scorers was proven pre-data with
  a 2-op mock dry-run (no live calls); see phase-S commit message.
