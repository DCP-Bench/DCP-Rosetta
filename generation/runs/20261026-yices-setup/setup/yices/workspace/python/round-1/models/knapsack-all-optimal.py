# All optimal 0/1 knapsack selections.
# Step 1 finds the optimum by tightening; step 2 uses a fresh context with value == optimum
# and lists every solution with a no-good over the item variables.
# Usage: python knapsack-all-optimal.py INSTANCE.json
import json
import sys

from yices import Context, Model, Status, Terms, Types


def assert_base(ctx, x, weights, capacity):
    for xi in x:
        ctx.assert_formula(Terms.arith_geq_atom(xi, Terms.integer(0)))
        ctx.assert_formula(Terms.arith_leq_atom(xi, Terms.integer(1)))
    weight = Terms.sum([Terms.mul(Terms.integer(weights[i]), x[i]) for i in range(len(x))])
    ctx.assert_formula(Terms.arith_leq_atom(weight, Terms.integer(capacity)))


def main():
    inst = json.load(open(sys.argv[1]))
    weights, values, capacity = inst["weights"], inst["values"], inst["capacity"]
    n = len(weights)
    INT = Types.int_type()
    x = [Terms.new_uninterpreted_term(INT, f"take{i}") for i in range(n)]
    value = Terms.sum([Terms.mul(Terms.integer(values[i]), x[i]) for i in range(n)])

    # step 1: optimum
    ctx = Context()
    assert_base(ctx, x, weights, capacity)
    best = None
    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        take = [model.get_value(xi) for xi in x]
        model.dispose()
        best = sum(values[i] * take[i] for i in range(n))
        ctx.assert_formula(Terms.arith_gt_atom(value, Terms.integer(best)))
    ctx.dispose()

    # step 2: every selection reaching the optimum
    ctx = Context()
    assert_base(ctx, x, weights, capacity)
    ctx.assert_formula(Terms.arith_eq_atom(value, Terms.integer(best)))
    while ctx.check_context() == Status.SAT:
        model = Model.from_context(ctx, 1)
        take = [model.get_value(xi) for xi in x]
        model.dispose()
        print(json.dumps({"take": take}))
        ctx.assert_formula(Terms.yor([Terms.arith_neq_atom(xi, Terms.integer(t))
                                      for xi, t in zip(x, take)]))
    ctx.dispose()


if __name__ == "__main__":
    main()
