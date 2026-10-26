from yices import *
I=Types.int_type()
xs=[Terms.new_uninterpreted_term(I,f"x{i}") for i in range(3)]
def mk():
    c=Context()
    for x in xs: c.assert_formulas([Terms.arith_geq_atom(x,Terms.integer(1)),Terms.arith_leq_atom(x,Terms.integer(3))])
    c.assert_formula(Terms.distinct(xs)); return c
c=mk(); n=0; seen=[]
while c.check_context()==Status.SAT and n<30:
    m=Model.from_context(c,1); seen.append(tuple(m.get_value(x) for x in xs)); m.dispose(); n+=1
    c.assert_blocking_clause()
print("blocking clause: iterations",n,"distinct",len(set(seen)),"final",c.status())
print("true", Terms.true(), "distinct1", Terms.distinct([xs[0]]), "yand[]", Terms.yand([]), "zero", Terms.ZERO, "sum[]", Terms.sum([]), Terms.to_string(Terms.sum([])))
# reset after interrupt
n=13
ys=[Terms.new_uninterpreted_term(I) for _ in range(n)]
c=Context()
for y in ys: c.assert_formulas([Terms.arith_geq_atom(y,Terms.integer(1)),Terms.arith_leq_atom(y,Terms.integer(n-1))])
c.assert_formula(Terms.distinct(ys)); print(c.check_context(timeout=1))
c.reset_context(); print("after reset", c.check_context(), "(no assertions => SAT)")
