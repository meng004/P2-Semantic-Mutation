# Contributing

This repository is the P3 Semantic Mutation project. P2 remains
present as a read-only historical reproduction layer.

## Repository Scope

- This **is** the P3 working tree.
- This **is not** a general-purpose mutation-testing framework.
- P3 work lives in `src/p3_v3/`, `tests/p3_v3/`, `scripts/p3_v3/`,
  and later-authorized documentation under `docs/superpowers/`.
- P2 trees are historical. They are not a second active product
  surface.

## P3 Contributions

Welcome through issues and pull requests:

- synthetic tests and documentation for existing P3 v3 modules
- fixes that stay inside a later-authorized writable set
- reports that a documented P3 command failed in a synthetic or
  authorized environment

P3 issues are in scope for this repository. Do not mark them as
belonging to another repository.

## P2 Read-Only Historical Layer

P2 replication-failure reports remain welcome. When opening one,
include the command, the last 50 lines of output, Python and OS
identity, and whether cache replay or re-LLM was used.

Do not accept changes that:

- edit `src/p2/`, P2-only tests, `data/`, `submission/`,
  `replication/`, or P2 manuscripts
- change `data/results/paper_numbers_v4.json` or other P2 SSOT
  files
- reclassify P2 results as P3 results

## Required Design And Review Gates

Implementation of a new P3 behaviour starts only after an
approved design specification and a user-authorized
implementation plan. Design archival is not implementation
authorization.

## Testing Requirements

For P3 qualification and pilot work, run the isolated
`/usr/bin/python3` pytest recipe documented in the active plan.
Report the count the command printed. Do not treat a historical
P2 count as the P3 gate.

P2 historical reproduction, when requested, follows
`REPRODUCIBILITY.md`. This file does not introduce a new P2
pytest total or a new SSOT rebuild command.

## Production Authorization Boundary

Do not run `scripts/p3_v3/qualify_cxx_link.py`, a real compiler,
CMake, or Boost.Math in an ordinary pull request. Those paths
require a separate user authorization. Do not create
`/tmp/p3-cxx-link-qualification` to "try the CLI".

## Code Style

- Python follows the existing style: PEP 8 with 100-character
  lines.
- Commit messages use imperative mood ("add X", "fix Y").
- English for documents that ship as the public repository
  entry. Chinese is acceptable in `docs/theory/`.

## Issue And Pull Request Evidence

A P3 pull request must list:

- the authorization or plan node, if any
- files changed
- the exact pytest command and the printed result
- confirmation that production qualification was not run
