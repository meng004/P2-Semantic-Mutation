"""End-to-end DVE dry-run (I4 rehearsal) — machinery validation, definitive version.

Plan v1.1.1 §3.1 (I4). Purpose: certify that the full frozen pipeline
(split -> S1 selection -> holdout FDS -> PUT-level sign-flip) has correct
operating characteristics BEFORE any real holdout is opened. Nothing here is a
result about SMS; it validates the instrument.

Two earlier iterations produced genuine design findings, preserved and reported
in docs/dve/M_infra_dry_run.md:

  v0 (dry_run_pipeline_v0_confounded.py.bak): comparing S1 to S2/S3 baselines
     built from holdout-INDEPENDENT signals gave apparent S1 superiority ~0.44
     that was insensitive to transfer -> a POTENCY CONFOUND (S1 intrinsically
     picks broadly-potent MRs; a coverage baseline that ignores kills loses for
     a reason unrelated to signal transfer).

  v1 (label-permutation null): delta==0 because coverage-greedy is degree-
     invariant under label permutation, and MR potency (profile breadth) is a
     global property that family reshuffling does not remove. This showed
     "transfer" decomposes into (i) stable MR-level potency (a legitimate value
     source) and (ii) mechanism-specific alignment.

Definitive minimal model (this file) removes the potency confound BY
CONSTRUCTION so that `transfer` purely controls signal informativeness:

  * MRs are EQUIPOTENT: each MR detects exactly one mechanism class (a partition
    of classes over MRs). No MR is intrinsically broader than another.
  * A holdout family is detected by a portfolio iff the portfolio contains the
    MR for the family's HOLDOUT mechanism class.
  * transfer = P(family's holdout class == its dev class). At transfer=0 the dev
    signal is independent of holdout detectability; at transfer=1 it is perfect.
  * Comparator = potency-matched random selection of k MRs.

Predictions the machinery MUST satisfy:
  transfer=0 -> E[FDS(S1)-FDS(rand)]=0 -> sign-flip rejects at ~alpha (type-I).
  transfer high -> S1 aligns with holdout classes -> power.

Reproducibility: fully seeded; n_put=12 (2^12 exact sign-flip).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from p2.dve import endpoint as ep
from p2.dve import strategies as st


def run_one_world(rng, cfg):
    """Clean isolation of TRANSFER.

    Confounds removed by construction (learned from v0/v1/v2 iterations):
      * potency: MRs are equipotent single-class detectors;
      * R0-redundancy / coverage diversification: BOTH S1 and the comparator
        pick k MRs for DISTINCT non-R0 classes (the comparator is coverage-
        matched, not naive random).
    The only remaining difference is WHICH non-R0 classes are chosen. Class
    frequencies are non-uniform, so choosing the classes that are frequent in
    the HOLDOUT raises FDS. S1 targets classes frequent in DEV residuals; those
    coincide with holdout-frequent classes only through `transfer`.
    """
    n_put, n_fam, n_mech = cfg["n_put"], cfg["n_fam"], cfg["n_mech"]
    n_mr, transfer, k, k0 = cfg["n_mr"], cfg["transfer"], cfg["k"], cfg["k0"]

    classes = [f"mc{c}" for c in range(n_mech)]
    mrs = [f"mr{j}" for j in range(n_mech)]     # exactly one MR per class
    mr_class = {mrs[j]: classes[j] for j in range(n_mech)}
    class_mr = {classes[j]: mrs[j] for j in range(n_mech)}

    # non-uniform class frequency (Zipf-like), independent draws for dev & holdout
    w = 1.0 / (1.0 + np.arange(n_mech))
    dev_p = w / w.sum()
    # holdout frequency equals dev freq w.p. transfer (per family, below), else an
    # independent shuffle of the same weights.
    hold_perm = rng.permutation(n_mech)
    hold_p_indep = (w[hold_perm] / w.sum())

    fams = []  # (put, fid, dev_class_idx, hold_class_idx)
    for p in range(n_put):
        for f in range(n_fam):
            dci = rng.choice(n_mech, p=dev_p)
            if rng.random() < transfer:
                hci = dci
            else:
                hci = rng.choice(n_mech, p=hold_p_indep)
            fams.append((f"P{p}", f"P{p}::fam{f}", int(dci), int(hci)))

    dev, hold = [], []
    for p in range(n_put):
        pf = [f for f in fams if f[0] == f"P{p}"]
        idx = rng.permutation(len(pf)); h = len(pf) // 2
        for j, i in enumerate(idx):
            (hold if j < h else dev).append(pf[i])

    r0_classes = set(range(k0))                    # R0 covers the k0 commonest classes
    non_r0 = [c for c in range(n_mech) if c not in r0_classes]
    from collections import Counter

    # PER-PUT selection (plan §3.5: R_valid(P), R_0(P) are per-PUT). This is what
    # makes PUTs independent replicates and keeps the PUT-level sign-flip test
    # valid. (An earlier global-selection version correlated the PUTs and
    # inflated type-I to ~0.17 -- recorded as a design finding.)
    treat_scores, comp_scores = {}, {}
    for p in range(n_put):
        dev_p_fams = [f for f in dev if f[0] == f"P{p}"]
        hold_p_fams = [f for f in hold if f[0] == f"P{p}"]
        dev_res_freq = Counter(dci for (_pp, _f, dci, _h) in dev_p_fams
                               if dci not in r0_classes)
        s1_classes = [c for c, _ in sorted(dev_res_freq.items(),
                                           key=lambda kv: (-kv[1], kv[0]))][:k]
        # pad if this PUT's dev residuals cover < k classes
        if len(s1_classes) < k:
            extra = [c for c in non_r0 if c not in s1_classes]
            s1_classes += list(rng.permutation(extra))[:k - len(s1_classes)]
        comp_classes = list(rng.choice(non_r0, size=min(k, len(non_r0)), replace=False))
        cover_t = set(r0_classes) | set(s1_classes)
        cover_c = set(r0_classes) | set(comp_classes)
        for (_pp, fid, _dci, hci) in hold_p_fams:
            treat_scores[(f"P{p}", fid)] = 1.0 if hci in cover_t else 0.0
            comp_scores[(f"P{p}", fid)] = 1.0 if hci in cover_c else 0.0

    by_put = ep.paired_family_diffs(treat_scores, comp_scores)
    d_put = ep.put_level_diffs(by_put)
    test = ep.signflip_test(d_put, shift=0.0, seed=int(rng.integers(1, 2**31)))
    return {"delta": float(d_put.mean()), "p": test["p_value"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-worlds", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20260710)
    args = ap.parse_args()
    # n_mech large + more families per PUT so that WHICH non-R0 classes are
    # covered matters (room for the transfer signal to act) while keeping the
    # per-PUT independence that the sign-flip test needs.
    base = dict(n_put=12, n_fam=16, n_mech=24, n_mr=40, k0=4, k=5)

    print("Definitive machinery validation: S1(real) vs potency-matched random")
    print("[equipotent single-class MRs; transfer purely controls signal informativeness]")
    for label, transfer in [("NULL (transfer=0)", 0.0),
                            ("WEAK (transfer=0.3)", 0.3),
                            ("SIGNAL (transfer=0.85)", 0.85)]:
        cfg = dict(base, transfer=transfer)
        rng = np.random.default_rng(args.seed + int(transfer * 1000))
        rej = 0; deltas = []
        for _ in range(args.n_worlds):
            r = run_one_world(rng, cfg)
            deltas.append(r["delta"]); rej += int(r["p"] <= 0.05)
        n = args.n_worlds
        kind = ("type-I, must be ~0.05" if transfer == 0
                else "power, should rise with transfer")
        print(f"\n=== {label} ===")
        print(f"  mean Delta(S1 - rand) = {np.mean(deltas):+.4f}")
        print(f"  reject rate @0.05      = {rej/n:.3f}   <- {kind}")


if __name__ == "__main__":
    main()
