"""Boundary case PINN (cross-paradigm) — soft vs hard constraint (FP / strong edge).

Captures the PINN soft-constraint boundary (spirit of the DeepXDE PeriodicBC bug,
issue #26: an incomplete/soft constraint -> a wrong-but-plausible field). A PINN
that enforces boundary conditions as a SOFT penalty satisfies the BC invariant
only approximately, so an exact-BC strong MR is violated even by a
"successfully trained" model.

PDE: u'' = -pi^2 sin(pi x) on [0,1], true u = sin(pi x), u(0)=u(1)=0.
  CORRECT = hard BC by construction: u(x) = x(1-x) * NN(x)  -> u(0)=u(1)=0 exact
  WRONG   = soft BC penalty (standard PINN practice): u = NN(x), BC in the loss
            -> u(0) only approximately 0

Strong MR (exact boundary invariant): |u(0)| <= epsilon_tol. Hard passes; soft is
killed. epsilon_tol is the explicit factor.
"""
import math
import torch
import torch.nn as nn

_PI = math.pi


def _mlp():
    torch.manual_seed(0)
    return nn.Sequential(nn.Linear(1, 32), nn.Tanh(),
                         nn.Linear(32, 32), nn.Tanh(), nn.Linear(32, 1))


def _u_fn(net, mode):
    def u(x):
        raw = net(x)
        return x * (1.0 - x) * raw if mode == "hard" else raw
    return u


def _train(mode, steps=2500, lam=0.1):
    torch.manual_seed(0)
    net = _mlp()
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    xc = torch.linspace(0.0, 1.0, 100).reshape(-1, 1).requires_grad_(True)
    u = _u_fn(net, mode)
    x0 = torch.zeros(1, 1)
    x1 = torch.ones(1, 1)
    for _ in range(steps):
        opt.zero_grad()
        uu = u(xc)
        ux = torch.autograd.grad(uu, xc, torch.ones_like(uu), create_graph=True)[0]
        uxx = torch.autograd.grad(ux, xc, torch.ones_like(ux), create_graph=True)[0]
        res = uxx + (_PI ** 2) * torch.sin(_PI * xc)
        loss = (res ** 2).mean()
        if mode == "soft":
            loss = loss + lam * (u(x0) ** 2 + u(x1) ** 2).sum()
        loss.backward()
        opt.step()
    return net, u


def boundary_value(mode):
    net, u = _train(mode)
    with torch.no_grad():
        return abs(float(u(torch.zeros(1, 1)).item()))


CORRECT, WRONG = "hard", "soft"


def verdict(mode, epsilon_tol=1e-4):
    """Strong MR: exact boundary invariant |u(0)|<=eps. 'pass' if satisfied.

    Note the FP<->FN tradeoff: at a loose epsilon (e.g. 1e-3) the soft PINN
    survives (the MR turns blind); at a strict epsilon (1e-4) it is killed.
    """
    return "pass" if boundary_value(mode) <= epsilon_tol else "fail"
