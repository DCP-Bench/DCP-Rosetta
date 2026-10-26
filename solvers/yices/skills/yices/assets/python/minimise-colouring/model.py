# Graph colouring with as few colours as possible (minimise the number of colours used).
from yices import Context, Model, Status, Terms, Types

edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]   # a 5-cycle plus a chord
n, max_colours = 5, 5
num = Terms.integer
colour = [Terms.new_uninterpreted_term(Types.int_type(), f"col{i}") for i in range(n)]

ctx = Context()
# colours are 0..max_colours-1
for c in colour:
    ctx.assert_formulas([Terms.arith_geq_atom(c, num(0)), Terms.arith_leq_atom(c, num(max_colours - 1))])
# neighbours get different colours
for a, b in edges:
    ctx.assert_formula(Terms.arith_neq_atom(colour[a], colour[b]))
# colour k is used if some vertex has it; count the used colours
used = [Terms.yor([Terms.arith_eq_atom(c, num(k)) for c in colour]) for k in range(max_colours)]
objective = Terms.sum([Terms.ite(u, num(1), num(0)) for u in used])

best, assignment = None, None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    best = model.get_value(objective)
    assignment = [model.get_value(c) for c in colour]
    model.dispose()
    ctx.assert_formula(Terms.arith_lt_atom(objective, num(best)))   # strictly fewer colours
print("Colours used:", best)
print("Assignment:", assignment)
