import time, sys
import hexaly.optimizer as hx

def run(name, build, tl=5, **params):
    t = time.time()
    try:
        with hx.HexalyOptimizer() as opt:
            m = opt.model
            vs = build(m)
            m.close()
            opt.param.time_limit = tl
            opt.param.verbosity = 0
            opt.param.nb_threads = 1
            for k, v in params.items(): setattr(opt.param, k, v)
            opt.solve()
            s = opt.solution
            vals = [v.value for v in vs] if s.status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL) else None
            print(f"{name}: status={s.status} vals={vals} t={time.time()-t:.2f}s", flush=True)
    except Exception as e:
        print(f"{name}: EXC {type(e).__name__}: {e} t={time.time()-t:.2f}s", flush=True)

# 1 satisfaction, no objective
def sat(m):
    x = m.int(0, 10); y = m.int(0, 10); m.constraint(x + y == 7); m.constraint(x - y >= 1); return [x, y]
run("sat_noobj", sat)
# 2 satisfaction with constant objective
def sat_const(m):
    vs = sat(m); m.minimize(0); return vs
run("sat_constobj", sat_const)
# 3 infeasible small
def infeas(m):
    x = m.int(0, 10); y = m.int(0, 10); m.constraint(x + y == 7); m.constraint(x + y >= 9); return [x, y]
run("infeasible_small", infeas)
def infeas_obj(m):
    vs = infeas(m); m.minimize(vs[0]); return vs
run("infeasible_small_obj", infeas_obj)
# 4 harder infeasible: pigeonhole 9 pigeons 8 holes
def php(m):
    n = 9; h = 8
    x = [m.int(0, h - 1) for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m.constraint(x[i] != x[j])
    return x
run("pigeonhole_9_8", php, tl=10)
# 5 bools sat
def bools(m):
    b = [m.bool() for _ in range(5)]; m.constraint(m.sum(b) == 2); return b
run("bools_noobj", bools)
