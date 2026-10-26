from yices import *
I=Types.int_type()
def t(name, f):
    try: print(name, "->", repr(f()))
    except BaseException as e: print(name, "-> EXC", type(e).__name__, str(e).replace("\n"," | ")[:300])
def mk(term):
    c=Context(); z=Terms.new_uninterpreted_term(I)
    c.assert_formula(Terms.arith_eq_atom(z,term)); s=c.check_context(); m=Model.from_context(c,1); return s,m.get_value(z)
t("integer(10**30)", lambda: mk(Terms.integer(10**30)))
t("integer(2**63)", lambda: mk(Terms.integer(2**63)))
t("parse_rational", lambda: mk(Terms.parse_rational("1000000000000000000000000000000")))
t("mul big", lambda: mk(Terms.mul(Terms.integer(2**40),Terms.integer(2**40))))
t("add big", lambda: mk(Terms.add(Terms.integer(2**62),Terms.integer(2**62))))
t("get_value of product", lambda: mk(Terms.mul(Terms.integer(2**40),Terms.integer(2**40))))
t("get_integer_value big", lambda: (lambda: (lambda c,z: (c.assert_formula(Terms.arith_eq_atom(z,Terms.parse_rational("1000000000000000000000000000000"))), c.check_context(), Model.from_context(c,1).get_integer_value(z)))(Context(), Terms.new_uninterpreted_term(I)))())
t("from_context after unsat then get_value", lambda: (lambda c,z: (c.assert_formula(Terms.false()), c.check_context(), Model.from_context(c,1).get_value(z)))(Context(), Terms.new_uninterpreted_term(I)))
import yices_api
t("init on import: error_code", lambda: yices_api.yices_error_code())
t("Yices.exit exists", lambda: hasattr(Yices,"exit"))
