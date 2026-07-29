"""Decision-Value Experiment (DVE) frozen analysis machinery.

Implements the pre-registered pieces of plan v1.1.1 whose correctness is
checkable before any real holdout exists:

- family_registry: nested (PUT, mechanism/template cluster) family IDs.
- split: SHA-256 commitment + one-shot custodian guard for dev/holdout.
- strategies: S1-S4 greedy portfolio selection over a kill matrix.
- endpoint: FDS family detection score + PUT-level sign-flip test.

Reference: docs/prereg/DVE_prereg_v1.md.
"""
