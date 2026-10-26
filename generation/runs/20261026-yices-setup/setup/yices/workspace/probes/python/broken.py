# deliberately wrong programs; each caught separately
from yices import *
I=Types.int_type()
def t(name, f):
    try: print(name, "->", repr(f()))
    except BaseException as e: print(name, "-> EXC", type(e).__name__, str(e).replace("\n"," | ")[:300])
x=Terms.new_uninterpreted_term(I,"bx")
def a(): 
    c=Context(); c.assert_formula(x>3)   # z3 style
t("x>3", a)
def b():
    c=Context(); c.assert_formula(Terms.arith_gt_atom(x,3))  # python int, not term
t("atom with python int", b)
def c_():
    c=Context(); c.assert_formula(Terms.arith_gt_atom(x,Terms.integer(3))); s=c.check_context(); return s=="sat", s=="SAT"
t("status vs string", c_)
t("undefined type", lambda: Terms.new_uninterpreted_term(Types.int_type, "q"))
t("bool var from var", lambda: Terms.new_variable(Types.bool_type(),"q"))
t("Terms.yand not list", lambda: Terms.yand(Terms.true(), Terms.false()))
t("Terms.add 3 args", lambda: Terms.add(x,x,x))
t("Terms.sum of ints", lambda: Terms.sum([1,2]))
t("integer of float", lambda: Terms.integer(2.5))
t("Terms.integer of term", lambda: Terms.integer(x))
t("check_context before assert", lambda: Context().check_context())
t("get_value of term not in model (new term after check)", lambda: (lambda c: (c.check_context(), Model.from_context(c,1).get_value(Terms.new_uninterpreted_term(I,"late")))) (Context()))
t("assert_formula list", lambda: Context().assert_formula([Terms.true()]))
t("ite with int cond", lambda: Terms.ite(x, Terms.integer(1), Terms.integer(2)))
t("mul ite", lambda: Terms.mul(Terms.ite(Terms.true(),Terms.integer(1),Terms.integer(2)), x))
t("used after dispose", lambda: (lambda c: (c.dispose(), c.check_context()))(Context()))
t("model use after dispose", lambda: (lambda c: (c.check_context(), (lambda m: (m.dispose(), m.get_value(x)))(Model.from_context(c,1))))(Context()))
