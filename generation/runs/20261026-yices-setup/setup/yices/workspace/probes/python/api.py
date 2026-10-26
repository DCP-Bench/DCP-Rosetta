import yices, inspect
print([n for n in dir(yices) if not n.startswith('_')])
from yices import *
print([n for n in dir(Parameters) if not n.startswith('_')])
p=Parameters(); p.set_param("random-seed","7"); print("param ok")
try: p.set_param("nope","1")
except Exception as e: print(type(e).__name__,e)
I=Types.int_type(); x=Terms.new_uninterpreted_term(I,"x")
c=Context(); c.assert_formula(Terms.arith_gt_atom(x,Terms.integer(3)))
print(c.check_context(p)); m=Model.from_context(c,1); print(m.to_string(80,23,0), "|", Terms.to_string(Terms.arith_gt_atom(x,Terms.integer(3))))
for n in ["add","mul","sub","neg","eq","neq","ite","implies","iff","xor","distinct","idiv","imod","abs","sum","product","power","yand","yor","ynot","arith_leq_atom","arith_eq_atom","new_uninterpreted_term","integer","parse_rational"]:
    print(n, inspect.signature(getattr(Terms,n)))
print(inspect.signature(Config.set_config), inspect.signature(Config.default_config_for_logic), inspect.signature(Context.__init__))
print(inspect.signature(Types.int_type), inspect.signature(Types.bool_type))
print(Terms.mul(x,Terms.integer(3)), Terms.is_int(x))
