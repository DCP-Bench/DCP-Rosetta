from yices import *
x=Terms.new_uninterpreted_term(Types.int_type(),"x")
ctx=Context(); ctx.assert_formulas([Terms.arith_gt_atom(x,Terms.integer(3)),Terms.arith_lt_atom(x,Terms.integer(2))])
s=ctx.check_context(); print(s, s==Status.UNSAT)
try: Model.from_context(ctx,1)
except Exception as e: print(type(e).__name__, e)
