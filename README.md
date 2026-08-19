# P3 Semantic Mutation

This GitHub repository is the P3 Semantic Mutation working tree.
It is not a P2-only replica.

## Status And Claim Ceiling

Formal claims remain blocked. Formal denominator membership is
false. Attempt-2 is not authorized. Nothing in this repository
entry upgrades those invariants.

## Active P3 Work

Current in-tree engineering is:

- P3 v3 evidence infrastructure under `src/p3_v3/` and
  `tests/p3_v3/`
- the Boost.Math pilot, with claims blocked
- the Cursor VM C++ compile-link qualification in
  `src/p3_v3/toolchain_qualification.py` and
  `scripts/p3_v3/qualify_cxx_link.py`

Qualification PASS, if later authorized and obtained, proves only
that one frozen C++14 program compiled, linked, and ran on that
VM. It does not authorize Boost.Math, CMake, attempt-2, or paper
Results.

## Repository Layout

```
.
├── src/p3_v3/           # P3 v3 evidence, pilot, and qualification
├── tests/p3_v3/         # P3 v3 synthetic tests
├── scripts/p3_v3/       # P3 CLIs, including qualify_cxx_link.py
├── docs/superpowers/    # P3 designs and implementation plans
├── src/p2/              # historical P2 implementation, read-only
├── tests/               # includes historical P2 tests
├── scripts/             # includes historical P2 campaign scripts
├── data/                # historical P2 SSOT and caches, read-only
├── submission/          # historical P2 IST bundle, read-only
├── replication/         # historical P2 Zenodo bundle, read-only
└── third_party/p1_avp/  # locked P1 AVP reference
```

## Testing

P3 qualification tests use synthetic `which` and `popen`. They
must not resolve or execute a host `c++`. Do not hard-code a
passing-test total in this file; report the count from the command
that was actually run.

The isolated Cursor VM recipe, when that environment is present,
is `/usr/bin/python3` with `PYTHONPATH` including `src` and the
already-provisioned third-party target. Do not reuse a failed
virtualenv.

## Governance And Production Authorization

Editing this repository does not authorize:

- running `scripts/p3_v3/qualify_cxx_link.py`
- invoking a real compiler, CMake, or Boost.Math
- creating `/tmp/p3-cxx-link-qualification`
- attempt-2
- claim or denominator upgrades

Those actions require a later explicit user authorization.

## Historical P2 Reproduction Layer

P2 is a read-only historical reproduction layer for the IST
Semantic Mutation Score audit. Do not add P2 operators, rewrite
P2 numbers, or edit P2 manuscripts as part of P3 work.

The following historical commands keep their original flags and
environment variables.

### P2 smoke

```bash
git clone <this-repo>.git p2-sms-audit
cd p2-sms-audit
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

PYTHONPATH=src .venv/bin/pytest tests/ -q

PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py
```

Expected historical outcome: `data/results/paper_numbers_v4.json`
is rewritten byte-identically. If
`git diff data/results/paper_numbers_v4.json` is empty, the
historical SSOT is verified.

### P2 cache replay

```bash
PYTHONPATH=src .venv/bin/python scripts/operator_campaign.py \
    --replay-from-cache

PYTHONPATH=src .venv/bin/python scripts/compute_rq2_v4_mp5.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py

PYTHONPATH=src .venv/bin/python scripts/compute_lrca_v4_mp5.py

PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff_batch.py

PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py

PYTHONPATH=src .venv/bin/python scripts/generate_figures.py
```

### P2 re-LLM

```bash
cp .env.example .env

PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py \
    --concurrency 6 --temperature 0
```

See `REPRODUCIBILITY.md` and `DATASET.md` for the historical P2
cost table, licences, and artefact provenance.

## Citation And Legacy Artefacts

P2 citation files remain in `replication/` and `CITATION.cff`.
This file does not mint an arXiv identifier or a DOI.

Historical P2 manuscript and submission files remain under
`submission/` and the P2 manuscript names. They are read-only.
