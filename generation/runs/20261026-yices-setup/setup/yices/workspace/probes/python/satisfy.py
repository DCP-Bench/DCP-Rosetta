from yices import *
x = Terms.new_uninterpreted_term(Types.int_type(), "x")
y = Terms.new_uninterpreted_term(Types.int_type(), "y")
cfg = Config(); ctx = Context(cfg); cfg.dispose()
ctx.assert_formulas([Terms.arith_geq_atom(x, Terms.integer(1)), Terms.arith_leq_atom(x, Terms.integer(5)),
  Terms.arith_eq_atom(Terms.add(x, y), Terms.integer(7)), Terms.arith_gt_atom(y, x)])
s = ctx.check_context()
print(s, s == Status.SAT, type(s))
m = Model.from_context(ctx, 1)
print(m.get_value(x), m.get_value(y), type(m.get_value(x)), m.get_integer_value(x))
b = Terms.new_uninterpreted_term(Types.bool_type(), "b")
ctx.assert_formula(b)
print(ctx.check_context()); m = Model.from_context(ctx,1); print(m.get_value(b), m.get_bool_value(b))
m.dispose(); ctx.dispose()
