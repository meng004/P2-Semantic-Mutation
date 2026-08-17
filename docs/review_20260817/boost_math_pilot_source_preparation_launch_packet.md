# Boost.Math PILOT_ONLY Source-Preparation Launch Review Packet

- node: `P1SP3A1_BOOST_MATH_PILOT_SOURCE_PREPARATION_AUTHORIZATION_AND_LAUNCH_PACKET`
- request_status: `PILOT_SOURCE_PREPARATION_LAUNCH_REVIEW_CANDIDATE`
- claims=blocked
- This packet is not an independent PASS.
- This packet does not authorize production execution.
- The frozen production command may run only after a later independent launch verdict PASS and a later machine launch authority are both archived.

This packet asks GPT-5.6 Sol High for an independent launch review. It does not create a launch verdict. It does not create machine launch authority. It does not run source preparation.

## 1. Git / authority anchors

| Item | Value |
|---|---|
| Node starting commit | `69f3fda7f4203cc8f6774af5dbaf4941c7cbed08` |
| Authorization A commit | `0da17445389dfb59eba49d03f11e3ee12905208c` |
| Packet parent commit | `0da17445389dfb59eba49d03f11e3ee12905208c` |
| branch | `main` |
| Plan path | `docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md` |
| Plan SHA-256 | `faddb776c5e6704df6708bebe8ab14a0de198f76328d777d7d92091fbe30f60a` |
| Plan verdict path | `docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md` |
| Plan verdict SHA-256 | `a88fd08ef2c6a288e4ff68cab3d1bccfb41ac158a24ccc49f904ef300a137c7e` |
| Capability verdict path | `docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md` |
| Capability verdict SHA-256 | `a73b450dca03db24c7479d263ed1f0dc216d73d884daae042683bce3457c4983` |
| Capability reviewed commit | `e5a92499b2b3495ecd0013b2279438147b203f25` |
| Authorization A path | `data/p3_v3/pilot/boost_math/user-auth-preparation.txt` |
| Authorization A SHA-256 | `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6` |
| Authorization A bytes | 38 |
| Authorization A LF | 1 |
| Authorization A CR | 0 |
| Claim ledger path | `research/evidence/p3_claim_ledger_v1.3.0.yml` |
| Claim ledger SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| claims | blocked |

Formal capability state remains `PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS`. This packet does not change that state.

## 2. Authorization interpretation

The controller archived a user message that was exactly one standalone line:

```
AUTHORIZE_BOOSTMATH_PILOT_PREPARATION
```

Archived bytes are exactly `b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n"`.

- SHA-256: `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- bytes: 38
- LF: 1
- CR: 0

Authorization A only permits the preparation process to continue into this launch review. Authorization A does not replace an independent launch verdict. Authorization A does not replace machine launch authority. Authorization A does not authorize skipping this packet, the later verdict, or the later machine authority. Authorization A does not authorize running the frozen production command.

## 3. Source-content provenance

| Item | Value |
|---|---|
| Upstream repository | `https://github.com/boostorg/math.git` |
| Content type | `DERIVED_PUBLIC_SOURCE_PROJECTION` |
| Official release archive | no |
| Phase 1 original archive | no |
| Common Git root tree | `dc86f3259c84f68ac7c4e2be11a1ed8567011240` |
| Earliest matching ancestor witness | `04c2c248dfc5e35eeb7638152d5bd7c2985feef2` |
| Mainline merge witness | `03ea9c8d7dff1083facd134c8f641e006b68fdae` |
| A/B root-tree relation | A and B share the same Git root tree |
| Full-history total / completed | 10181 |
| Full-history match count | 2 |
| Full-history scan SHA-256 | `ca5ee0617f11dedd550dc34d5bf9df15b7dfdde52af1fbc759839e74af6a7987` |
| Content-equivalence script SHA-256 | `6aeb41d86c5413d6646153fe449e762b2b6a7762c72b92322555814708274659` |
| Content-equivalence result SHA-256 | `072fc700e0c8c87ce8b716c44119cc565538125ed6e6a9ac1111c6af2810e14d` |
| Result artifact self-hash | `bbfe856280f785d6f49216da3358d8eab4468335571da9490b3107bafab18903` |

The diagnostic archive is a derived public-source projection. It is not an official Boost.Math release archive. It is not a recovered Phase 1 original archive. Discovery roles (ancestor witness, mainline merge witness, common root tree) are diagnostic labels only. They are not production authority.

## 4. Projection contract

The frozen projection excludes exactly one public relative path:

- excluded path: `build/Jamfile.v2`
- excluded_path_count: 1
- serialization: canonical-json-array-with-terminal-lf
- hashed bytes textual representation: `b'["build/Jamfile.v2"]\n'`
- digest: `e705bcca7f2afa2f81a869a005a6bcb3a6f606f7ef03b5e580200694a7c448cc`
- retained_file_count: 4396
- materialized_file_count: 4396
- materialized_total_bytes: 95635487
- normalized source tree SHA-256: `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`

The digest is the SHA-256 of the canonical JSON array `["build/Jamfile.v2"]` plus one terminal LF. It is not a newline-joined plain path list.

This projection exists so a later authorized production run can reproduce the already frozen Phase 1 normalized source object. This packet does not claim that Phase 1 originally used the same generation process.

## 5. Archive identity

| Item | Value |
|---|---|
| Archive path | `/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar` |
| SHA-256 | `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392` |
| bytes | 99676160 |
| format | TAR |
| type | regular file, not a symlink |
| mode | 0644 (not group/world writable) |
| three_way_archive_bytes_equal | true |
| production archive reader | verified TAR, SHA and bytes match |

The archive must be re-snapshotted and re-hashed at independent review time and again at any later execution time. Any path, mode, symlink, hash, size, or format drift must BLOCK. The archive must not be silently regenerated and substituted.

## 6. Production paths and exact command

| Binding | Path | Existence at packet time |
|---|---|---|
| ARCHIVE_PATH | `/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar` | present |
| MATERIALIZE_ROOT | `/tmp/p3-boost-math-pilot-production-source` | absent |
| STAGING | `/tmp/p3-boost-math-pilot-production-source.staging` | absent |

Only the archive exists now. MATERIALIZE_ROOT and STAGING must remain absent until a later authorized production node creates them through the reviewed extractor.

Frozen future command, recorded verbatim and not executed here:

```
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src timeout 30m \
  python3 scripts/p3_v3/pilot.py validate-source \
  --archive /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar \
  --materialize-root /tmp/p3-boost-math-pilot-production-source
```

DO NOT EXECUTE IN THIS NODE

## 7. Expected production outputs

Describe only. This node creates none of the following:

- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/source-preparation-result.json`
- `/tmp/p3-boost-math-pilot-production-source`

A later PASS, if one is ever issued after independent verdict and machine authority, must bind all of:

- archive SHA `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392`
- archive bytes `99676160`
- archive format `TAR`
- frozen normalized tree `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- Authorization A hash `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- gate-chain predecessor hashes (plan, plan verdict, capability verdict, launch authority, Authorization A)
- materialized file count `4396`
- materialized total bytes `95635487`
- source-manifest SHA of the created manifest
- execution_class=`PILOT_ONLY`
- denominator=`PILOT_ONLY`
- claims=blocked

## 8. Fail-closed conditions

Any of the following must BLOCK and write zero PASS claims:

- authority, path, hash, or schema drift
- reviewed production byte drift
- archive path unsafe, or archive hash, size, or format drift
- MATERIALIZE_ROOT or STAGING already exists
- extraction unsafe
- materialized tree mismatch against the frozen normalized tree
- manifest, result, or root conflict or residue
- launch verdict missing
- machine launch authority missing
- Authorization A bytes or hash drift

## 9. Required independent review

GPT-5.6 Sol High must independently inspect:

- Authorization A exactness
- DAG predecessor order
- plan, plan-verdict, and capability identities
- archive witness provenance and its limits
- projection serialization correction (`canonical-json-array-with-terminal-lf`)
- exact archive, root, and command bindings
- production outputs and fail-closed boundaries
- claims remain blocked

The independent reviewer may issue only `PASS` or `BLOCK`.

If the verdict is PASS, a later separate archival node may exclusive-create:

`docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md`

That later verdict file must use this exact JSON schema and no other keys:

```json
{
  "reviewed_packet_path": str,
  "reviewed_packet_sha256": str,
  "plan_verdict_sha256": str,
  "capability_verdict_sha256": str,
  "authorization_a_sha256": str,
  "verdict": str,
  "authorized_state": str,
  "claims": str
}
```

PASS values, if later issued, must be:

- verdict=`PASS`
- authorized_state=`PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN`
- claims=blocked

The closed schema above is the complete verdict object. It must not add launch-authority path or launch-authority hash fields.

Machine launch authority may be created only in another node after that verdict is archived. This packet does not create either object.

## 10. Scientific boundary

- formal denominator membership=false
- rq4_supported=false
- Source preparation, even after a later authorized run, is still not a paper experimental result.
- This packet does not change the claim ledger.
- claims=blocked
- Do not write Results or Contributions from this packet.
- This node did not run the production command.

request_status remains `PILOT_SOURCE_PREPARATION_LAUNCH_REVIEW_CANDIDATE`.
