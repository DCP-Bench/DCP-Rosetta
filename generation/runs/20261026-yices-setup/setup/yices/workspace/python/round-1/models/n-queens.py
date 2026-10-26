# N-queens: one placement with queen i in row i at column c_i.
# Usage: python n-queens.py INSTANCE.json
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
    # different columns
    if n > 1:
        ctx.assert_formula(Terms.distinct(col))
    # no shared diagonal: c_i - c_j is neither +d nor -d for the row distance d
    for i in range(n):
        for j in range(i + 1, n):
            d = j - i
            for diff in (d, -d):
                ctx.assert_formula(Terms.arith_neq_atom(Terms.sub(col[i], col[j]), Terms.integer(diff)))

    if ctx.check_context() != Status.SAT:
        print(json.dumps({"status": "unsatisfiable"}))
        return
    model = Model.from_context(ctx, 1)
    queens = [model.get_value(c) for c in col]
    model.dispose()
    ctx.dispose()
    print(json.dumps({"queens": queens}))


if __name__ == "__main__":
    main()
