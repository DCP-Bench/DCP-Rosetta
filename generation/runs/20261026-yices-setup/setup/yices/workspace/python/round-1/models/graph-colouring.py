# Graph colouring: colour nodes so adjacent nodes differ, using as few distinct colours as possible.
# The objective counts colours that are used by some node; it is minimised by tightening.
# Usage: python graph-colouring.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def main():
    inst = json.load(open(sys.argv[1]))
    n = inst["n_nodes"]
    edges = inst["edges"]

    INT = Types.int_type()
    zero, one = Terms.integer(0), Terms.integer(1)
    col = [Terms.new_uninterpreted_term(INT, f"c{i}") for i in range(n)]

    ctx = Context()
    # colours are 0 .. n-1, always enough
    for c in col:
        ctx.assert_formula(Terms.arith_geq_atom(c, zero))
        ctx.assert_formula(Terms.arith_leq_atom(c, Terms.integer(n - 1)))
    # the two ends of every edge get different colours
    for u, v in edges:
        ctx.assert_formula(Terms.arith_neq_atom(col[u], col[v]))
    # colour k counts as used when some node has it
    used = [Terms.yor([Terms.arith_eq_atom(col[i], Terms.integer(k)) for i in range(n)])
            for k in range(n)]
    objective = Terms.sum([Terms.ite(u, one, zero) for u in used])

    best_colours = None
    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        colours = [model.get_value(c) for c in col]
        model.dispose()
        best_colours = colours
        ctx.assert_formula(Terms.arith_lt_atom(objective, Terms.integer(len(set(colours)))))
    ctx.dispose()
    print(json.dumps({"colour": best_colours}))


if __name__ == "__main__":
    main()
