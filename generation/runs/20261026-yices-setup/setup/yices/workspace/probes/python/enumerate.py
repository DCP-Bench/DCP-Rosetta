from yices import *
I = Types.int_type()
xs = [Terms.new_uninterpreted_term(I, f"x{i}") for i in range(3)]
ctx = Context()
for x in xs:
    ctx.assert_formulas([Terms.arith_geq_atom(x, Terms.integer(1)), Terms.arith_leq_atom(x, Terms.integer(3))])
ctx.assert_formula(Terms.distinct(xs))
n = 0
while ctx.check_context() == Status.SAT:
    m = Model.from_context(ctx, 1)
    vals = [m.get_value(x) for x in xs]; m.dispose()
    n += 1
    ctx.assert_formula(Terms.yor([Terms.arith_neq_atom(x, Terms.integer(v)) for x, v in zip(xs, vals)]))
print(n, ctx.status)
