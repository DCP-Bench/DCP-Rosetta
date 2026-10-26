from yices import *
import yices_api
print({k:getattr(Status,k) for k in dir(Status) if k.isupper()})
I=Types.int_type()
def t(name, f):
    try: print(name, "->", repr(f()))
    except BaseException as e: print(name, "-> EXC", type(e).__name__, str(e).replace("\n"," | ")[:300])
def run(mode=None, logic=None):
    cfg=Config()
    if logic: cfg.default_config_for_logic(logic)
    if mode: cfg.set_config("mode",mode)
    c=Context(cfg); x=Terms.new_uninterpreted_term(I); y=Terms.new_uninterpreted_term(I)
    for v in (x,y): c.assert_formulas([Terms.arith_geq_atom(v,Terms.integer(0)),Terms.arith_leq_atom(v,Terms.integer(9))])
    c.assert_formula(Terms.arith_geq_atom(Terms.add(x,y),Terms.integer(5)))
    obj=Terms.add(x,y) if logic!="QF_NIA" else Terms.mul(x,y)
    res=[]
    while True:
        s=c.check_context()
        if s!=Status.SAT: res.append(s); break
        m=Model.from_context(c,1); b=m.get_value(obj); m.dispose(); res.append(b)
        c.assert_formula(Terms.arith_lt_atom(obj,Terms.integer(b)))
    return res
for mode in (None,"one-shot","multi-checks","push-pop","interactive"):
    t("mode %s"%mode, lambda: run(mode))
for logic in ("QF_LIA","QF_NIA","QF_IDL","QF_LRA","QF_BV","QF_UFLIA", "QF_AX", "NOPE"):
    t("logic %s"%logic, lambda: run(None, logic))
t("nia push-pop", lambda: run("push-pop","QF_NIA"))
def poptest():
    c=Context(); x=Terms.new_uninterpreted_term(I)
    c.push(); c.assert_formula(Terms.arith_gt_atom(x,Terms.integer(3))); c.assert_formula(Terms.arith_lt_atom(x,Terms.integer(2))); print(c.check_context())
    c.pop(); print(c.check_context()); return c.status()
t("pop after unsat", poptest)
t("pop without push", lambda: Context().pop())
