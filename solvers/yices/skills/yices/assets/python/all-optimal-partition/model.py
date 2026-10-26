# Split numbers into two groups with the smallest possible difference of sums,
# then list every optimal split.
from yices import Context, Model, Status, Terms, Types

weights = [3, 1, 4, 1, 5, 9, 2, 6]
num = Terms.integer
side = [Terms.new_uninterpreted_term(Types.bool_type(), f"s{i}") for i in range(len(weights))]

def signed(w, s):               # +w in group A, -w in group B
    return Terms.ite(s, num(w), num(-w))
diff = Terms.abs(Terms.sum([signed(w, s) for w, s in zip(weights, side)]))

def new_context():
    return Context()            # terms are global: any context can reuse `side` and `diff`

# step 1: find the optimum by tightening the bound until UNSAT
ctx = new_context()
best = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    best = model.get_value(diff)
    model.dispose()
    ctx.assert_formula(Terms.arith_lt_atom(diff, num(best)))   # strictly better next time
ctx.dispose()
print("Optimal difference:", best)       # UNSAT after a SAT proves it

# step 2: a fresh context with the objective pinned to the optimum; enumerate over the outputs
ctx = new_context()
ctx.assert_formula(Terms.arith_eq_atom(diff, num(best)))
count = 0
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    values = [model.get_bool_value(s) for s in side]
    model.dispose()
    count += 1
    ctx.assert_formula(Terms.yor([Terms.neq(s, Terms.true() if v else Terms.false()) for s, v in zip(side, values)]))
print("Optimal solutions:", count)
