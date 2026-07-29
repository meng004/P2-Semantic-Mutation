# P12 W3.4 Cross-Repository Anchor Design

## Goal

Create a P3-side, content-addressed acknowledgment of the final P12 W3.4 workflow
freeze without changing the frozen P3 consumer contract or claiming any W4 result.

## Frozen identities

- P12 commit: `223fbadb55a016a76ac7c5bcd0dca37481103f1a`
- P12 contract SHA-256: `ea26e756b7f04831f981fffd19bcdf2070b8e5055fe4914e2b5cbce6c488182e`
- P12 freeze-manifest SHA-256: `8509567d11c4f91508578431448744a54d5f0c400eb5c937f6b91625d2cb236e`
- P3 consumer-contract commit: `2f1088854c284b3af56e34fc6ff4fe8542962920`
- P3 consumer-contract SHA-256: `be201031e738c28c5c0ff15a1048da81891cd8d971d0684ef040d3cd7d6d28b6`

## Architecture

P3 stores an anchor JSON with a canonical self-hash, a human-readable evidence
record, and an append-only amendment ledger. Amendment `P3-A001` changes only the
transport anchor from “remote annotated tag” to “remote tag or cross-repository
content-hash acknowledgment” because the cloud producer credential cannot create
`refs/tags/*`. The frozen consumer-contract bytes and every scientific constant stay
unchanged.

`src/p2/dve/p12_anchor.py` validates the anchor, verifies the P3 contract bytes,
checks the amendment event hash chain, and binds the amendment to the same P12
identities. Stable error codes reject byte drift, stale self-hashes, broken chains,
post-opening acknowledgments, and any amendment that affects scientific
interpretation.

## Evidence boundary

This anchor supports only the chronology and identity of the P12 W3.4 workflow
freeze. It does not support achieved scale, W4 compliance, RFDS results, external
human replication, or any manuscript result claim. `d2_opened` and `w4_executed`
must both be false.

## Verification

Tests cover the valid committed package and negative controls for every frozen hash,
contract-byte drift, amendment-chain tampering, scientific-impact overclaiming,
missing pre-open flags, and an incorrect tag-status representation.

