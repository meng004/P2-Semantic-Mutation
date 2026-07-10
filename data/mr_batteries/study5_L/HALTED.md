# HALTED — Study-5 Family-MR Arm-L elicitation wave (2026-07-10)

**Status: HALTED mid-draw by author editorial directive (2026-07-10). No
further elicitation call was issued after the halt. Drawn is drawn — nothing
here may be re-elicited, re-rolled, certified, assembled, or scored under the
halted registration.**

## Halt reason (author editorial directive, 2026-07-10)

The author's editorial review determined that the Family-MR design as
registered carries a **battery-size / execution-budget confound**: the Arm-L
cell battery (UNION of up to four vendors' certified MRs, 1-3 MRs per vendor
per cell) is not matched to the registered Arm-R battery (one algebra-derived
MR per cell) in MR count, execution budget, or kill opportunities. Under the
frozen kill rule (killed iff ANY battery MR passes on the PUT and fails on
the mutant), a larger battery mechanically enjoys more kill opportunities, so
an SMS_R − SMS_L difference cannot be attributed to the battery's design
source (algebra-derived vs LLM-prompted). Study-5's families will NOT be
integrated wholesale into the paper. The drawn material below is archived for
a future **budget-matched** redesign.

## What was drawn before the halt (one-shot ledger)

| Slot | Drawn (of 140 cells) | Gateway cost (USD) |
|---|---|---|
| gpt-5.5 (gateway) | 40 | 0.7281 |
| gemini-3.5-flash (gateway) | 40 | 0.1197 |
| grok-4.1 → served grok-4.3 (gateway) | 37 | 0.3229 |
| **confirmatory gateway total** | **117 / 420 (cell, vendor) units** | **1.1708** |

- Cells with all 3 gateway vendors drawn: **37 / 140** (roster order a1 … b1,
  with three grok units outstanding in that range: A7_MP3, A8_MP5, B1_MP4).
- First undrawn units in roster order: A7_MP3/grok-4.1, A8_MP5/grok-4.1,
  B1_MP4/grok-4.1, then B2_MP1 (all three vendors) onward.
- Transport errors: 0. Zero-byte / truncated raw files: 0. Log rows and raw
  files reconcile exactly (117 = 117; no raw-without-log, no log-without-raw).
- claude-fable-5 slot (session harness): all **140** cell responses were
  authored in-session pre-halt under `claude_inbox/` but **never ingested**
  into the raw/draw ledger (ingestion was halted with the wave); zero token
  cost.
- Registered pilot (`v8mr_pilot/`, {a2, b4}, firewall-excluded): fully drawn
  pre-halt (40/40 responses: 30 gateway + 10 claude), certified V1/V2 and
  assembled BEFORE the halt; gateway cost **0.2113 USD**. Pilot-triggered
  code fix P16 (parser binding-syntax; renumbered from a P15 collision with the Study-4 incident) is logged in `PILOT_LOG.md` and §10.
- **Total gateway spend of the wave (pilot + confirmatory): 1.3821 USD.**

## What was deliberately NOT done (per the halt directive)

- NO certification (V1/V2) of any confirmatory response.
- NO battery assembly (`batteries/` for the confirmatory tag does not exist).
- NO SMS-L scoring anywhere in this wave;
  `data/results/sms_track2_v8_mrL{,_same}.json` do not exist and
  `scripts/compute_mr_diversity_delta.py` still exits 2 (verified).
- NO ingestion of the authored claude responses.

## Layout of the archive

```
data/mr_batteries/study5_L/
├── HALTED.md                  # this file
├── elicitation_log.jsonl      # 117 confirmatory draw rows (ts/tokens/cost/served-model)
├── raw/                       # 117 verbatim gateway completions ({put}_MP{k}_{model}.txt)
├── claude_inbox/              # 140 authored-but-never-ingested claude-slot responses
└── v8mr_pilot/                # registered {a2,b4} pilot (complete: raw/records/batteries/summary/log)
```

## Provenance pins

- Elicitation template (Amendment A2, used for every drawn unit):
  `docs/prereg_v2/STUDY5_MR_ELICITATION_PROMPT.md`, sha256
  `67c879d29e42f1f8b6c2cfb45e8a59a6efa70517cd252828488b1fe20192a02c`.
- Serving parameters: temperature 0.7, requested max_tokens 2500 (per-model
  floors), transport-only retries; one call per (PUT, stratum, vendor).
- R-side frozen SSOTs untouched (sha256 pins verified at halt):
  `sms_track2_v7.json` `13c6e0…b22c792`, `sms_track2_v7_same.json`
  `c7931a…38a1b4af`.
- Driver: `scripts/study5_mr_elicit.py` (draw/ingest/certify/assemble/summary;
  only draw and pilot legs were exercised for the confirmatory tag).

## For the future budget-matched redesign

The 117 drawn gateway responses and 140 authored claude responses are frozen
archival material of the HALTED design. A budget-matched redesign (e.g.
per-cell battery size capped to match Arm-R's per-cell MR count, or an
Arm-R execution-budget inflation to the union size) is a NEW registration;
whether this material is admissible there is that registration's decision to
make, not this wave's. Resume point if (and only if) a registration rules the
remaining draws admissible: 303 undrawn (cell, vendor) units starting at
A7_MP3/grok-4.1, then B2_MP1 onward.
