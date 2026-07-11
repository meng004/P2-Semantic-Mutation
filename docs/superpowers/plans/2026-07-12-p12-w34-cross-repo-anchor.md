# P12 W3.4 Cross-Repository Anchor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and publish a machine-verifiable P3 acknowledgment of the P12 W3.4 freeze.

**Architecture:** A small standard-library validator checks canonical hashes and an append-only amendment chain. Tracked JSON/JSONL/Markdown artifacts carry only transport and chronology evidence; the frozen consumer contract is read-only.

**Tech Stack:** Python 3.11 standard library, JSON/JSONL, JSON Schema, pytest.

---

### Task 1: Define failing anchor tests

**Files:**
- Create: `tests/dve/test_p12_anchor.py`
- Create: `src/p2/dve/p12_anchor.py`

- [ ] Write tests for the valid anchor, contract-byte pin, self-hash tampering,
  amendment-chain tampering, scientific-effect rejection, and pre-open chronology.
- [ ] Run the test and confirm failure because the validator is absent.

### Task 2: Implement the validator and evidence artifacts

**Files:**
- Create: `schemas/dve/p12_w3_freeze_anchor_v1.1.2.schema.json`
- Create: `data/dve/p12_w3_freeze_anchor_v1.1.2.json`
- Create: `research/evidence/p12_w3_freeze_anchor_v1.1.2.md`
- Create: `research/evidence/p12_consumer_amendments_v1.1.2.jsonl`
- Modify: `src/p2/dve/p12_anchor.py`

- [ ] Implement canonical hashing and stable validation errors.
- [ ] Add the exact W3.4 and consumer-contract identities.
- [ ] Add P3-A001 with `scientific_impact=false` and
  `changes_confirmatory_interpretation=false`.
- [ ] Run the focused tests and confirm green.

### Task 3: Verify and publish

- [ ] Confirm `data/dve/p12_consumer_contract_v1.1.2.json` is byte-identical to its
  frozen SHA-256.
- [ ] Run the complete DVE test suite and `git diff --check`.
- [ ] Commit only the anchor scope, push the branch, and report the commit and
  artifact hashes for P12 receipt construction.

