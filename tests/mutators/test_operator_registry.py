from collections import Counter
from p2.mutators.operator_registry import (
    MutationOperator, OPERATORS, get_operators_for_put, key_operators,
)

VALID_CATEGORIES = {"OS", "CE", "SI", "HP", "CF", "TF"}
EXPECTED_PUTS = {"a1", "a2", "a3", "b1", "b2", "b3",
                 "c1", "c2", "c3", "d1", "d2", "d3"}


def test_each_put_has_at_least_three_operators():
    by_put = Counter(op.put for op in OPERATORS)
    for put in EXPECTED_PUTS:
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
    import re
    pat = re.compile(r"^([a-d][1-3])_(OS|CE|SI|HP|CF|TF)\d+$")
    for op in OPERATORS:
        m = pat.match(op.id)
        assert m, f"bad id format: {op.id}"
        assert m.group(1) == op.put and m.group(2) == op.category


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
