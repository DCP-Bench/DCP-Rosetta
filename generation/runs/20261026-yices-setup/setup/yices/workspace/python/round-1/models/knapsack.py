# 0/1 knapsack: maximise total value under the capacity, by tightening the value bound.
# Usage: python knapsack.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def main():
    inst = json.load(open(sys.argv[1]))
    weights, values, capacity = inst["weights"], inst["values"], inst["capacity"]
    n = len(weights)
    INT = Types.int_type()
    x = [Terms.new_uninterpreted_term(INT, f"take{i}") for i in range(n)]

    ctx = Context()
    # item i is taken (1) or not (0)
    for xi in x:
        ctx.assert_formula(Terms.arith_geq_atom(xi, Terms.integer(0)))
        ctx.assert_formula(Terms.arith_leq_atom(xi, Terms.integer(1)))
    weight = Terms.sum([Terms.mul(Terms.integer(weights[i]), x[i]) for i in range(n)])
    value = Terms.sum([Terms.mul(Terms.integer(values[i]), x[i]) for i in range(n)])
    ctx.assert_formula(Terms.arith_leq_atom(weight, Terms.integer(capacity)))

    best_take = None
    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        best_take = [model.get_value(xi) for xi in x]
        model.dispose()
        best = sum(values[i] * best_take[i] for i in range(n))
        ctx.assert_formula(Terms.arith_gt_atom(value, Terms.integer(best)))
    ctx.dispose()
    print(json.dumps({"take": best_take}))


if __name__ == "__main__":
    main()
