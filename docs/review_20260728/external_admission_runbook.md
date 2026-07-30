# External Admission Adjudication Runbook

## 0. Defect4MR artifact — fixed GitHub source

The Defect4MR artifact is available from the private repository `https://github.com/meng004/P12-Defect4MR` (the supplied lowercase URL redirects to this canonical name). Task 3.1 pins commit `2bf7c2401c846544e715d879eb639e8c3bf44067`; the authoritative 64-row ledger is `data/ledgers/candidates.json`, blob SHA `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`.

Verified census at the pinned commit: 64 total = 35 `verified_full` + 16 `candidate_full` + 12 `rejected` + 1 `candidate_needs_oracle`. The `v1.0.1` tag has a different 34/17 split and is not an acceptable substitute for this execution.

The raw ledger contains `mr_mapping` and `proposed_mr_oracle`, so it must **not** be copied as-is into the admission workspace. A one-time import job must verify repository commit, ledger blob, counts, and schema, then emit a sanitized manifest that excludes those two fields and all mutation/kill information. The import session is retired after this mechanical conversion and may not adjudicate admission. Store only the sanitized manifest plus provenance/hash log under `data/external_slice/defect4mr_import/`.

Readiness support is distributed across `reports/cloud/<case>-verification.md`, `scripts/cloud/<case>-verification/`, `data/registry/cases.{yaml,json}`, `tools/d4mr/`, and `docs/d4mr-CONTRACT.md`. The registry covers all 35 `verified_full` cases, but only 3/35 image entries have a digest; for the other 32, rebuild from the verification report or first publish and pin the image. Do not interpret a registry entry with `digest: null` as an immediately runnable image.

## 1. Authority and current boundary

The governing specification is `research/prereg_v2/external_slice_protocol.md`, especially §§1, 2, and 6. Admission has exactly three criteria. No extra quality, popularity, downstream-detection, or convenience criterion may be introduced.

The 64-pool source is now accessible at the fixed GitHub commit and its re-adjudication is unblocked, but has not yet been executed. The current sheet still contains only the bounded supplementary-mining pilot. The pilot remains supplemental and must not replace the 64-pool adjudication. Two-human annotation and new buggy/fixed build work have not yet been performed.

## 2. Sheet contract

The header must be exactly:

```text
neutral_id,repo,issue_url,buggy_sha,fixed_sha,mechanism_sentence,crit_real_defect,crit_dual_arm_repro,crit_in_scope,decision,exclusion_reason,analysis_id
```

During the mining pilot:

- `crit_real_defect` and `crit_in_scope` are `PASS` or `FAIL`.
- `crit_dual_arm_repro` is `PENDING`.
- `decision` is `ADMIT_PENDING_REPRO` only when the first and third criteria pass; otherwise it is `EXCLUDED`.
- `analysis_id` is empty in every row until the blind category map has been frozen.
- The mechanism field is one sentence describing only the numerical effect of the fix.

## 3. Neutral identity and leakage control

1. Allocate `EXT-<repo>-<NN>` in repository order before any post-admission categorisation.
2. Use a two-digit sequence that is unique within each repository.
3. Do not encode a hypothesised category in the ID, mechanism sentence, exclusion reason, filename, or row order.
4. Do not consult downstream test-relation text, detection outcomes, score values, or later aliases.
5. Keep `analysis_id` blank until the category-map freeze is complete.
6. Run the checks below before every handoff. The hexadecimal escapes deliberately keep the reserved vocabulary out of the runbook itself.

```bash
pattern='(?i)(^|[^[:alnum:]_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)([^[:alnum:]_]|$)'
rg -n "$pattern" \
  data/external_slice/admission_sheet.csv \
  data/external_slice/MINING_LOG.md \
  docs/review_20260728/external_admission_runbook.md
# Expected: no output and rg exit status 1.

python3 - <<'PY'
import csv
from pathlib import Path

path = Path("data/external_slice/admission_sheet.csv")
with path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
bad = [row["neutral_id"] for row in rows if row["analysis_id"].strip()]
assert not bad, f"premature analysis aliases: {bad}"
PY
```

Any match or nonempty alias is a release blocker. Remove the leak, re-read the complete row, and repeat both checks.

## 4. Exactly-three-criteria adjudication

Apply the following steps to every candidate, including candidates that will be excluded.

### Step A1: public real defect

Pass only when both items exist:

1. a public issue or equivalent public tracker entry describing defective behaviour; and
2. an identifiable public fix commit.

Prefer a merged fix PR. Record its merge commit as `fixed_sha`. If the requested merge-or-head rule is needed for an unmerged PR, record its immutable current head commit. In either case, resolve `buggy_sha` as the first parent of the recorded fix commit. Store full 40-character hashes, not branch names or abbreviated hashes.

Fail when the report is private, no defective behaviour is described, no fix commit can be identified, or the issue-to-fix link cannot be established. Search popularity and labels are not evidence for this criterion.

### Step A2: buggy/fixed dual-arm reproduction

This criterion remains `PENDING` during mining. It passes only after both source versions build in isolated environments and one trigger demonstrates the issue-described behavioural difference on the same input.

If either build fails, the trigger cannot be made deterministic, or the claimed difference cannot be demonstrated, write `REPRO_FAILED` in `crit_dual_arm_repro`, set `decision=EXCLUDED`, and begin `exclusion_reason` with `REPRO_FAILED:` followed by the failing stage. Keep the row in place and do not recruit a replacement.

### Step A3: numerical-kernel scope

Pass only when the defect is in a single-output or few-output numerical kernel and the callable can be adapted to a float-vector input with a float or few-float output.

Fail when the defect is crash-only, build/packaging, API misuse, documentation, performance-only, test infrastructure, or an intended API redesign. Also fail when the changed component is not a numerical kernel or its output contract cannot be reduced to the required few-output form without changing the defect.

### Decision derivation for this pilot

- A1 pass and A3 pass, with A2 pending: `ADMIT_PENDING_REPRO`.
- Any A1 or A3 failure: `EXCLUDED`.
- A2 failure later: `EXCLUDED` with `REPRO_FAILED` retained in its criterion field and reason.

The protocol defines final admission by the conjunction of all three criterion fields. It does not freeze a separate post-reproduction CSV token for a successful row. Until that presentation choice is approved, do not invent another result code; use the three fields as the authoritative final predicate.

## 5. Mechanism-sentence procedure

1. Read the issue, fix PR description, and actual patch.
2. Identify the observable numerical effect repaired by the changed lines.
3. Write one present-tense sentence, with no category hypothesis and no downstream testing language.
4. Prefer statements such as `restores the normalisation constant of the returned density`.
5. Do not state that a later test will detect the defect.
6. Re-run the leakage check in §3.

## 6. Buggy/fixed reproduction recipe

### 6.1 Required files

For each pending row, create:

```text
data/external_slice/reproducers/EXT-<repo>-<NN>.py
data/external_slice/reproduction/EXT-<repo>-<NN>/environment.json
data/external_slice/reproduction/EXT-<repo>-<NN>/buggy.json
data/external_slice/reproduction/EXT-<repo>-<NN>/fixed.json
```

The trigger must accept a deterministic seed where randomness is involved and emit canonical JSON containing the input, observed output, expected property, package version, and exit status. The same trigger file and input fixture must run against both arms.

### 6.2 Environment construction

Use one isolated environment per arm. Record the Python version, platform, compiler, BLAS/LAPACK provider where relevant, package hash, and every build-tool version.

Choose one reproducible installation route:

1. **Pinned release route:** install exact published buggy and fixed package versions with all transitive requirements pinned by `==`.
2. **Exact-source route:** materialise each recorded SHA into a separate source directory, install identical pinned build requirements, and build each source tree independently.

Pinned-release command pattern:

```bash
python<COMPATIBLE_VERSION> -m venv "<CASE_DIR>/venv-buggy"
python<COMPATIBLE_VERSION> -m venv "<CASE_DIR>/venv-fixed"
"<CASE_DIR>/venv-buggy/bin/python" -m pip install --require-hashes -r "<BUGGY_LOCK>"
"<CASE_DIR>/venv-fixed/bin/python" -m pip install --require-hashes -r "<FIXED_LOCK>"
```

Exact-source command pattern:

```bash
curl -L "https://github.com/<OWNER>/<REPO>/archive/<BUGGY_SHA>.tar.gz" -o "<CASE_DIR>/buggy.tar.gz"
curl -L "https://github.com/<OWNER>/<REPO>/archive/<FIXED_SHA>.tar.gz" -o "<CASE_DIR>/fixed.tar.gz"
mkdir "<CASE_DIR>/buggy-src" "<CASE_DIR>/fixed-src"
tar -xzf "<CASE_DIR>/buggy.tar.gz" --strip-components=1 -C "<CASE_DIR>/buggy-src"
tar -xzf "<CASE_DIR>/fixed.tar.gz" --strip-components=1 -C "<CASE_DIR>/fixed-src"
python<COMPATIBLE_VERSION> -m venv "<CASE_DIR>/venv-buggy"
python<COMPATIBLE_VERSION> -m venv "<CASE_DIR>/venv-fixed"
"<CASE_DIR>/venv-buggy/bin/python" -m pip install --require-hashes -r "<BUILD_LOCK>"
"<CASE_DIR>/venv-fixed/bin/python" -m pip install --require-hashes -r "<BUILD_LOCK>"
"<CASE_DIR>/venv-buggy/bin/python" -m pip install --no-deps --no-build-isolation "<CASE_DIR>/buggy-src"
"<CASE_DIR>/venv-fixed/bin/python" -m pip install --no-deps --no-build-isolation "<CASE_DIR>/fixed-src"
```

Each lock file must contain exact versions and hashes. Save the lock files with the reproduction record.

Do not let one arm reuse the other arm's build directory or compiled objects. Do not upgrade a dependency in only one arm. If a historical source cannot build on the current interpreter, select and record a compatible interpreter for both arms before declaring failure.

### 6.3 Execution and coding

1. Run the trigger once as an environment smoke check.
2. Run enough seeded repetitions to establish deterministic issue behaviour; use the same seeds and inputs on both arms.
3. Require the buggy arm to exhibit the issue-described behaviour.
4. Require the fixed arm to remove that behaviour without a trigger exception.
5. Save stdout, stderr, return code, and canonical JSON separately.
6. Set `crit_dual_arm_repro=PASS` only if both builds and the behavioural contrast succeed.
7. Otherwise apply `REPRO_FAILED` exactly as described in §4. Do not substitute another candidate.

Execution pattern:

```bash
"<CASE_DIR>/venv-buggy/bin/python" "data/external_slice/reproducers/<NEUTRAL_ID>.py" \
  --seed "<SEED>" --json-out "<CASE_DIR>/buggy.json"
"<CASE_DIR>/venv-fixed/bin/python" "data/external_slice/reproducers/<NEUTRAL_ID>.py" \
  --seed "<SEED>" --json-out "<CASE_DIR>/fixed.json"
```

No downstream detection experiment is permitted during this step.

## 7. Defect4MR v1.0.0 re-adjudication when the artifact arrives

1. Verify the release identity and manifest against DOI `10.5281/zenodo.21203424`.
2. Confirm the artifact itself contains 64 candidate records before creating rows. If the count or manifest differs, stop and document the discrepancy; do not infer missing members.
3. Preserve the release manifest identifier for traceability in a private working crosswalk. The public admission sheet receives only neutral IDs.
4. Within each repository, sort candidates lexicographically by the release manifest ID and assign the next unused two-digit neutral sequence. Record this neutral ordering rule before adjudication.
5. For every manifest member, extract the public issue URL, recorded buggy SHA, recorded fixed SHA, and reproducer location from the artifact.
6. Re-check A1 from the public issue and repository rather than trusting the historical status label.
7. Read the fix diff and independently adjudicate A3. The historical downstream-oracle status is not an admission condition and must not be copied into the sheet.
8. Port or wrap the supplied reproducer to the convention in §6, then run A2 on both exact SHAs.
9. Retain every failed build or trigger as `REPRO_FAILED`; never replace it to preserve a target count.
10. Keep the 10 seeded training cases out of the confirmatory pool by applying `MAPPING_TRAIN` only after the manifest-based draw described in `data/external_slice/annotation/README.md`.
11. Re-run the schema, blank-alias, full-hash, duplicate-ID, row-count, and leakage checks before any slice freeze.

## 8. Integrity checks before handoff

```bash
python3 - <<'PY'
import csv
import re
from pathlib import Path

expected = [
    "neutral_id", "repo", "issue_url", "buggy_sha", "fixed_sha",
    "mechanism_sentence", "crit_real_defect", "crit_dual_arm_repro",
    "crit_in_scope", "decision", "exclusion_reason", "analysis_id",
]
path = Path("data/external_slice/admission_sheet.csv")
with path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    assert reader.fieldnames == expected, reader.fieldnames
    rows = list(reader)

ids = [row["neutral_id"] for row in rows]
assert len(ids) == len(set(ids)), "duplicate neutral ID"
for row in rows:
    assert re.fullmatch(r"[0-9a-f]{40}", row["buggy_sha"])
    assert re.fullmatch(r"[0-9a-f]{40}", row["fixed_sha"])
    assert row["analysis_id"] == ""
    assert row["crit_dual_arm_repro"] in {"PENDING", "PASS", "REPRO_FAILED"}
    assert row["decision"] in {"ADMIT_PENDING_REPRO", "EXCLUDED"}
PY
```

For the current supplementary pilot, the expected row count is 9. Do not use that pilot count as the expected count after the unavailable 64-case artifact is added.
