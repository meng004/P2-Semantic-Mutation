from p2.lrca.decision_tree import classify_root_cause, RootCause, KillContext


def test_c2_when_l1_fragile():
    ctx = KillContext(l1_robust=False, l2_ood=False, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C2


def test_c3_when_ood_induced():
    ctx = KillContext(l1_robust=True, l2_ood=True, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C3


def test_c4_when_assumption_violated():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=True, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C4


def test_c5_when_artifact():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=False, artifact=True)
    assert classify_root_cause(ctx) == RootCause.C5


def test_c1_when_all_clear():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C1
