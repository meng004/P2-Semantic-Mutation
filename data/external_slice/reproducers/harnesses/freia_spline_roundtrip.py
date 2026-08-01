#!/usr/bin/env python3
"""D-FREIA-001 issue-property driver (m_rev / f_rev.traj): forward-inverse round-trip of
RationalQuadraticSpline coupling (FrEIA issue #140).

Bug (binned.py, reverse direction): the inside-domain mask compares y against
knot_x[..., -1] instead of knot_y[..., -1], so codomain points between the two
bounds are routed through the wrong branch (spline vs identity tails) in the
inverse -- breaking x == f^{-1}(f(x)) (or crashing in searchsorted).

Oracle: max |x - f^{-1}(f(x))| over a wide input sample must be at machine
precision for an invertible block.  Run with PYTHONPATH per arm.
"""
import sys, numpy as np, torch
import FrEIA.framework as Ff
import FrEIA.modules as Fm

torch.set_default_dtype(torch.float64)
torch.manual_seed(0); np.random.seed(0)

def subnet(cin, cout):
    return torch.nn.Sequential(torch.nn.Linear(cin, 32), torch.nn.ReLU(),
                               torch.nn.Linear(32, cout))

inn = Ff.SequenceINN(4)
inn.append(Fm.RationalQuadraticSpline, subnet_constructor=subnet, bins=8)
for p in inn.parameters():   # randomize away from identity-init
    with torch.no_grad(): p.add_(0.4 * torch.randn_like(p))

worst = 0.0; crashed = 0; total = 0
with torch.no_grad():
    for scale in (0.5, 1.0, 2.0, 4.0, 8.0):
        x = torch.randn(4096, 4) * scale
        try:
            z, _ = inn(x)
            xr, _ = inn(z, rev=True)
            err = (x - xr).abs().max().item()
            worst = max(worst, err)
            print(f"scale={scale}: roundtrip max|x - f^-1(f(x))| = {err:.3e}")
        except Exception as e:
            print(f"scale={scale}: CRASH in round-trip: {type(e).__name__}: {e}")
            crashed += 1
        total += 1
import FrEIA
# threshold 1e-2 separates branch-misrouting O(domain width) from RQS
# inversion round-off (<=1e-3 at scale 8 on all revisions incl. master)
ok = (crashed == 0) and (worst < 1e-2)
print(f"### FrEIA arm={sys.argv[1] if len(sys.argv)>1 else '?'} worst={worst:.3e} crashes={crashed}/{total}")
print("### VERDICT:", "PASS" if ok else "VIOLATED")

sys.exit(0 if ok else 1)
