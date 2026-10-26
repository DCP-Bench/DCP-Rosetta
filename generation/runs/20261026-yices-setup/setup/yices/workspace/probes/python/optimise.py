# knapsack maximise, tightening w/o push-pop (assert after SAT) ; minimise too
from yices import *
I = Types.int_type(); B = Types.bool_type()
w=[3,4,5,2]; v=[30,40,45,20]; cap=9
xs=[Terms.new_uninterpreted_term(B,f"t{i}") for i in range(4)]
def val(x): return Terms.ite(x, Terms.integer(1), Terms.integer(0))
def lin(c): return Terms.sum([Terms.mul(Terms.integer(ci), val(x)) for ci,x in zip(c,xs)])
ctx = Context()
ctx.assert_formula(Terms.arith_leq_atom(lin(w), Terms.integer(cap)))
obj = lin(v); best=None
while True:
    s = ctx.check_context()
    print("status", s)
    if s != Status.SAT: break
    m = Model.from_context(ctx,1); best = m.get_value(obj); m.dispose()
    print("obj", best)
    ctx.assert_formula(Terms.arith_gt_atom(obj, Terms.integer(best)))   # assert after SAT in push-pop mode
print("best", best)
# after UNSAT, further assert?
try:
    ctx.assert_formula(Terms.true()); print("assert after unsat ok", ctx.status)
except Exception as e: print("assert after unsat:", type(e).__name__, e)
try:
    Model.from_context(ctx,1)
except Exception as e: print("model after unsat:", type(e).__name__, e)
# push/pop tightening
ctx2 = Context(); ctx2.assert_formula(Terms.arith_leq_atom(lin(w), Terms.integer(cap)))
ctx2.check_context(); 
ctx2.push(); ctx2.assert_formula(Terms.arith_gt_atom(obj, Terms.integer(70))); print(ctx2.check_context())
ctx2.pop(); print(ctx2.check_context(), ctx2.status)
# minimise: min of sum x subject to total >= 5
ys=[Terms.new_uninterpreted_term(I,f"y{i}") for i in range(3)]
c3=Context()
for y in ys: c3.assert_formulas([Terms.arith_geq_atom(y,Terms.integer(0)),Terms.arith_leq_atom(y,Terms.integer(4))])
c3.assert_formula(Terms.arith_geq_atom(Terms.sum(ys),Terms.integer(5)))
o=Terms.sum(ys)
while c3.check_context()==Status.SAT:
    m=Model.from_context(c3,1); b=m.get_value(o); m.dispose(); c3.assert_formula(Terms.arith_lt_atom(o,Terms.integer(b)))
print("min", b, c3.status)
