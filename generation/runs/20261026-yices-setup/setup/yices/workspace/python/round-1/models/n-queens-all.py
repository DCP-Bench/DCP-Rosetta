# All n-queens solutions: enumerate with a no-good over the column variables after each model.
# Usage: python n-queens-all.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def main():
    n = json.load(open(sys.argv[1]))["n"]
    INT = Types.int_type()
    col = [Terms.new_uninterpreted_term(INT, f"c{i}") for i in range(n)]

    ctx = Context()
    for c in col:
        ctx.assert_formula(Terms.arith_geq_atom(c, Terms.integer(0)))
        ctx.assert_formula(Terms.arith_leq_atom(c, Terms.integer(n - 1)))
    if n > 1:
        ctx.assert_formula(Terms.distinct(col))
    for i in range(n):
        for j in range(i + 1, n):
            d = j - i
            for diff in (d, -d):
                ctx.assert_formula(Terms.arith_neq_atom(Terms.sub(col[i], col[j]), Terms.integer(diff)))

    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        queens = [model.get_value(c) for c in col]
        model.dispose()
        print(json.dumps({"queens": queens}))
        ctx.assert_formula(Terms.yor([Terms.arith_neq_atom(c, Terms.integer(q))
                                      for c, q in zip(col, queens)]))
    ctx.dispose()


if __name__ == "__main__":
    main()
