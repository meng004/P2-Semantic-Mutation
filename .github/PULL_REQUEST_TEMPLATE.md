## Summary

<!-- One paragraph: what this PR does and why. -->

Linked issue: # <!-- if any -->

## Type of change

- [ ] Documentation fix
- [ ] Script / test fix (no behaviour change)
- [ ] `requirements-frozen.txt` adjustment for newer Python
- [ ] New test for existing module
- [ ] Other (please describe): …

## Pre-submit checklist

- [ ] `PYTHONPATH=src .venv/bin/pytest -q` reports **116 passed**
- [ ] If `src/p2/stats/` or `scripts/compute_*` was touched:
      `scripts/build_paper_numbers.py` produces a zero diff against
      `data/results/paper_numbers_v4.json`
- [ ] If `submission/` or `论文初稿P2_IST*.md` was touched:
      paper is **not yet in press**, and the maintainer has been
      consulted (paper-locked changes need editorial concurrence)
- [ ] No secrets, API keys, or `.env` content added
- [ ] CHANGELOG.md updated under `[Unreleased]`

## Testing notes

<!-- How can the reviewer verify? Specific commands, expected
     outputs. -->

## Out-of-scope guards

This PR does **not**:

- [ ] Change SSOT outputs in `data/results/` (numbers in the
      published paper are pinned to a commit hash)
- [ ] Add a new mutation operator family (P3 territory)
- [ ] Rewrite the manuscript prose (locked once accepted)
