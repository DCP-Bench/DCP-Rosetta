# Nonlinear integer arithmetic: integers a < b with a + b = 13 and a*b <= 50; maximise the product a*b.
from yices import Config, Context, Model, Status, Terms, Types, YicesException

num = Terms.integer
a = Terms.new_uninterpreted_term(Types.int_type(), "a")
b = Terms.new_uninterpreted_term(Types.int_type(), "b")
product = Terms.mul(a, b)
facts = [Terms.arith_gt_atom(a, num(1)), Terms.arith_gt_atom(b, a),
         Terms.arith_eq_atom(Terms.add(a, b), num(13)), Terms.arith_leq_atom(product, num(50))]

# the default context only does linear arithmetic: the error appears when the product is asserted
try:
    Context().assert_formulas(facts)
except YicesException as e:
    print("Default context error:", e)

# a logic with nonlinear integer arithmetic selects the MCSAT engine
cfg = Config()
cfg.default_config_for_logic("QF_NIA")
ctx = Context(cfg)
ctx.assert_formulas(facts)
best = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    best = (model.get_value(a), model.get_value(b), model.get_value(product))
    model.dispose()
    ctx.assert_formula(Terms.arith_gt_atom(product, num(best[2])))
print("Maximum product: a=%d b=%d a*b=%d" % best)
