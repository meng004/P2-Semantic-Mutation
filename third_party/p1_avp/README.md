# P1 AVP Integration

P2 reuses P1's AVP (Automated Verification Pipeline) at a fixed commit.
After P1 is published on arXiv, perform:

```bash
git submodule add https://github.com/<P1-repo>.git third_party/p1_avp
cd third_party/p1_avp
git checkout <P1-AVP-commit-hash>
cd ../..
```

Then update `configs/default.yaml`:
```yaml
p1_avp:
  commit_hash: "<actual hash>"
  source_path: third_party/p1_avp
```

P2 must NOT track P1's HEAD; only the locked commit. This isolates P2 from P1's
ongoing revisions during the SANER review cycle.
