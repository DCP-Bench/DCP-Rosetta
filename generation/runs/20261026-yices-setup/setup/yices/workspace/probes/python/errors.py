import traceback
from yices import *
I=Types.int_type(); B=Types.bool_type()
def t(name, f):
    try: print(name, "->", repr(f()))
    except BaseException as e: print(name, "-> EXC", type(e).__name__, str(e).replace("\n"," | ")[:300])
x=Terms.new_uninterpreted_term(I,"xx"); y=Terms.new_uninterpreted_term(I,"yy")
ctx=Context()
ctx.assert_formula(Terms.arith_gt_atom(x,Terms.integer(3))); ctx.assert_formula(Terms.arith_lt_atom(x,Terms.integer(2)))
print(ctx.check_context())
t("model after unsat", lambda: Model.from_context(ctx,1))
t("assert after unsat", lambda: ctx.assert_formula(Terms.true()))
t("status after", lambda: ctx.status())
t("check again", lambda: ctx.check_context())
# new_variable misuse
v=Terms.new_variable(I,"v")
c2=Context()
t("assert new_variable bool-typed?", lambda: c2.assert_formula(Terms.arith_gt_atom(v,Terms.integer(0))))
# type mismatch
t("add bool+int", lambda: Terms.add(x, Terms.true()))
t("assert int term", lambda: Context().assert_formula(x))
t("and_ attr", lambda: Terms.and_)
t("yand empty", lambda: Terms.yand([]))
t("yor empty", lambda: Terms.yor([]))
t("distinct 1", lambda: Terms.distinct([x]))
t("distinct 0", lambda: Terms.distinct([]))
t("sum empty", lambda: Terms.sum([]))
t("x+1", lambda: x+1)
t("x==y", lambda: x==y)
t("int literal as formula", lambda: Context().assert_formula(1))
t("dup name", lambda: Terms.new_uninterpreted_term(I,"xx"))
t("get_value unconstrained", lambda: (lambda c,z: (c.check_context(), Model.from_context(c,1).get_value(z)))(Context(), Terms.new_uninterpreted_term(I,"free1")))
t("from_context keep_subst=0 free", lambda: (lambda c,z: (c.assert_formula(Terms.arith_eq_atom(z,z)), c.check_context(), Model.from_context(c,0).get_value(z)))(Context(), Terms.new_uninterpreted_term(I,"free2")))
def dm():
    c=Context(); z=Terms.new_uninterpreted_term(I,"free3"); w=Terms.new_uninterpreted_term(I,"w3")
    c.assert_formula(Terms.arith_gt_atom(w,Terms.integer(2)))
    c.check_context(); m=Model.from_context(c,1); return m.get_value(z), m.get_value(w)
t("unconstrained term value, keep_subst=1", dm)
def big():
    c=Context(); z=Terms.new_uninterpreted_term(I,"big")
    c.assert_formula(Terms.arith_eq_atom(z,Terms.integer(10**30))); c.check_context(); m=Model.from_context(c,1); return m.get_value(z), m.get_integer_value(z)
t("big", big)
def big2():
    c=Context(); z=Terms.new_uninterpreted_term(I,"big2")
    c.assert_formula(Terms.arith_eq_atom(z,Terms.integer(2**40))); c.check_context(); m=Model.from_context(c,1); return m.get_value(z), m.get_integer_value(z)
t("2**40", big2)
def real():
    c=Context(); z=Terms.new_uninterpreted_term(Types.real_type(),"r")
    c.assert_formula(Terms.arith_eq_atom(Terms.mul(Terms.integer(2),z),Terms.integer(1))); c.check_context(); m=Model.from_context(c,1); return m.get_value(z)
t("real", real)
def idm():
    c=Context(); z=Terms.new_uninterpreted_term(I,"d1")
    c.assert_formula(Terms.arith_eq_atom(z,Terms.idiv(Terms.integer(-7),Terms.integer(2)))); c.check_context(); m=Model.from_context(c,1); z2=Terms.new_uninterpreted_term(I,"d2")
    return m.get_value(z)
t("idiv -7 2", idm)
def imd():
    c=Context(); z=Terms.new_uninterpreted_term(I,"m1")
    c.assert_formula(Terms.arith_eq_atom(z,Terms.imod(Terms.integer(-7),Terms.integer(3)))); c.check_context(); m=Model.from_context(c,1); return m.get_value(z)
t("imod -7 3", imd)
def nl():
    c=Context(); a=Terms.new_uninterpreted_term(I,"na"); b=Terms.new_uninterpreted_term(I,"nb")
    c.assert_formula(Terms.arith_eq_atom(Terms.mul(a,b),Terms.integer(12)))
    r=c.check_context(); return r
t("nonlinear default", nl)
def nl2():
    cfg=Config(); cfg.default_config_for_logic("QF_NIA"); c=Context(cfg); a=Terms.new_uninterpreted_term(I,"na2"); b=Terms.new_uninterpreted_term(I,"nb2")
    c.assert_formulas([Terms.arith_eq_atom(Terms.mul(a,b),Terms.integer(12)),Terms.arith_gt_atom(a,Terms.integer(1)),Terms.arith_gt_atom(b,Terms.integer(1)), Terms.arith_lt_atom(a,b)])
    r=c.check_context(); m=Model.from_context(c,1); return r, m.get_value(a), m.get_value(b)
t("nonlinear QF_NIA", nl2)
def nl3():
    c=Context(); a=Terms.new_uninterpreted_term(I,"na3"); b=Terms.new_uninterpreted_term(I,"nb3")
    return Terms.mul(a,b)
t("mul term built", nl3)
print("version", Yices.version, "mcsat", __import__("yices_api").yices_has_mcsat())
