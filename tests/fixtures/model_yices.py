from yices import Terms, Types


def build(instance):
    n = instance["n"]
    x = Terms.new_uninterpreted_term(Types.int_type(), "x")
    y = Terms.new_uninterpreted_term(Types.int_type(), "y")
    total = Terms.add(x, y)
    # Yices integers are unbounded, so the bounds the reference declares must be added.
    bounds = [Terms.arith_geq_atom(v, Terms.integer(0)) for v in (x, y)]
    bounds += [Terms.arith_leq_atom(v, Terms.integer(n)) for v in (x, y)]
    if instance["optimize"]:
        return bounds + [Terms.arith_geq_atom(total, Terms.integer(n))], {"x": x, "y": y}, ("minimize", total)
    return bounds + [Terms.arith_eq_atom(total, Terms.integer(n))], {"x": x, "y": y}
