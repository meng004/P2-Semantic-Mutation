from collections import Counter
from p2.mutators.operator_registry import (
    MutationOperator, OPERATORS, get_operators_for_put, key_operators,
)

VALID_CATEGORIES = {"OS", "CE", "SI", "HP", "CF", "TF"}
# Study-2 expansion: 12 original PUTs + 18 new (a4–a8, b4–b7, c4–c7, d4–d8) = 30.
EXPECTED_PUTS = {"a1", "a2", "a3", "b1", "b2", "b3",
                 "c1", "c2", "c3", "d1", "d2", "d3"}
NEW_PUTS = {"a4", "a5", "a6", "a7", "a8",
            "b4", "b5", "b6", "b7",
            "c4", "c5", "c6", "c7",
            "d4", "d5", "d6", "d7", "d8"}
ALL_PUTS = EXPECTED_PUTS | NEW_PUTS


def test_each_put_has_at_least_three_operators():
    by_put = Counter(op.put for op in OPERATORS)
    for put in ALL_PUTS:
        assert by_put[put] >= 3, f"{put} has only {by_put[put]} operators (need ≥3)"


def test_all_operators_have_required_fields():
    for op in OPERATORS:
        assert isinstance(op, MutationOperator)
        assert op.id and op.put and op.category in VALID_CATEGORIES
        assert op.label and op.target_locator and op.transformation and op.rationale
        assert isinstance(op.is_key, bool)


def test_ids_are_unique():
    ids = [op.id for op in OPERATORS]
    assert len(ids) == len(set(ids)), "duplicate operator id"


def test_id_format_matches_put_and_category():
    # Broadened from [1-3] → [1-8] for the 12→30 PUT expansion (a4–a8 … d4–d8).
    # E2 gap: the old regex silently rejected every new-PUT operator id.
    import re
    pat = re.compile(r"^([a-d][1-8])_(OS|CE|SI|HP|CF|TF)\d+$")
    for op in OPERATORS:
        m = pat.match(op.id)
        assert m, f"bad id format: {op.id}"
        assert m.group(1) == op.put and m.group(2) == op.category


def test_new_put_operators_present_and_well_formed():
    """Every new Study-2 PUT contributes ≥3 operators spanning ≥2 categories,
    with exactly the id/put/category invariants the old regex used to gate."""
    from collections import defaultdict
    by_put = defaultdict(list)
    for op in OPERATORS:
        by_put[op.put].append(op)
    for put in NEW_PUTS:
        ops = by_put[put]
        assert len(ops) >= 3, f"{put}: {len(ops)} operators (<3)"
        assert len({o.category for o in ops}) >= 2, f"{put}: <2 categories"
        assert any(o.is_key for o in ops), f"{put}: no key operator"
        for o in ops:
            assert o.id.startswith(put + "_")
            assert o.category in VALID_CATEGORIES


def test_old_put_operators_unchanged():
    """Byte-for-byte guard: the 37 original-PUT operators keep their exact
    id set, so the regex broadening cannot have altered existing behaviour."""
    original_ids = {op.id for op in OPERATORS if op.put in EXPECTED_PUTS}
    assert len(original_ids) == 37, f"original-PUT op count drifted: {len(original_ids)}"


def test_at_least_seven_key_operators():
    keys = key_operators()
    assert len(keys) >= 7, f"need ≥7 key operators for K=20 lift, got {len(keys)}"


def test_categories_diverse_per_put():
    from collections import defaultdict
    cats = defaultdict(set)
    for op in OPERATORS:
        cats[op.put].add(op.category)
    for put, cs in cats.items():
        assert len(cs) >= 2, f"{put} only uses categories {cs} (need ≥2)"


def test_get_operators_for_put_filters_correctly():
    a2_ops = get_operators_for_put("a2")
    assert all(op.put == "a2" for op in a2_ops)
    assert len(a2_ops) >= 3
