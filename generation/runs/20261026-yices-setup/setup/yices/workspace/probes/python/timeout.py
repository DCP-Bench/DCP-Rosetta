import time
from yices import *
I=Types.int_type()
# hard-ish pigeonhole 11 pigeons 10 holes via ints + distinct
n=13
xs=[Terms.new_uninterpreted_term(I) for _ in range(n)]
def mkctx():
    c=Context()
    for x in xs: c.assert_formulas([Terms.arith_geq_atom(x,Terms.integer(1)),Terms.arith_leq_atom(x,Terms.integer(n-1))])
    c.assert_formula(Terms.distinct(xs)); return c
c=mkctx(); t=time.time(); s=c.check_context(timeout=2); print("status",s,"elapsed %.1f"%(time.time()-t), "Status.INTERRUPTED",Status.INTERRUPTED, "UNKNOWN",Status.UNKNOWN)
print("status()", c.status())
try: m=Model.from_context(c,1); print("model after interrupt: object", m.get_value(xs[0]))
except Exception as e: print("model after interrupt:", type(e).__name__, e)
try: c.assert_formula(Terms.true()); print("assert after interrupt ok")
except Exception as e: print("assert after interrupt:", type(e).__name__, e)
t=time.time(); s=c.check_context(timeout=1); print("recheck", s, "%.1f"%(time.time()-t))
try: c.reset_context(); print("reset ok", c.status())
except Exception as e: print(e)
# stop_search on idle
c2=Context(); print("stop idle", c2.stop_search())
# timeout fast problem
c3=Context(); c3.assert_formula(Terms.true()); print(c3.check_context(timeout=5))
# thread leftover?
import threading; time.sleep(0.2); print("threads", threading.active_count())
