import time
from yices import *
I=Types.int_type()
cfg=Config(); cfg.default_config_for_logic("QF_NIA"); c=Context(cfg)
x,y,z=[Terms.new_uninterpreted_term(I) for _ in range(3)]
for v in (x,y,z): c.assert_formula(Terms.arith_gt_atom(v,Terms.integer(1)))
def p3(v): return Terms.mul(v,Terms.mul(v,v))
c.assert_formula(Terms.arith_eq_atom(Terms.add(p3(x),p3(y)),p3(z)))
t=time.time(); s=c.check_context(timeout=3); print(s,"%.1f"%(time.time()-t))
