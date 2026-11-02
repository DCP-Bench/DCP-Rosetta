import os, sys, time, io
import hexaly.optimizer as hx
o = hx.HexalyOptimizer()
p = o.param
for v in (2.5, 0, 1):
    try:
        p.time_limit = v; print("time_limit", v, "->", p.time_limit, file=sys.stderr)
    except Exception as e:
        print("time_limit", v, "EXC", type(e).__name__, e, file=sys.stderr)
print("log_writer default is sys.stdout:", p.log_writer is sys.stdout, type(p.log_writer), file=sys.stderr)
m = o.model
x = m.int(0, 5); m.minimize(x); m.close()
p.time_limit = 2
# default verbosity: where does the log go?
buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
o.solve()
sys.stdout = old
print("captured via sys.stdout swap:", len(buf.getvalue()), "chars", file=sys.stderr)
print("state", o.state, "status", o.solution.status, file=sys.stderr)
o.delete()
print("deleted ok", file=sys.stderr)
