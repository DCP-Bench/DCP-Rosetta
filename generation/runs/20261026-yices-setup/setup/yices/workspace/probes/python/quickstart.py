from yices import Context, Model, Status, Terms, Types

INT = Types.int_type()
x = Terms.new_uninterpreted_term(INT, "x")          # a decision variable
y = Terms.new_uninterpreted_term(INT, "y")
n = Terms.integer

ctx = Context()
ctx.assert_formulas([Terms.arith_geq_atom(x, n(1)), Terms.arith_leq_atom(x, n(5)),
                     Terms.arith_eq_atom(Terms.add(x, y), n(7)), Terms.arith_gt_atom(y, x)])
if ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)             # 1 = keep substituted variables
    print(model.get_value(x), model.get_value(y))
    model.dispose()
ctx.dispose()
