import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus

def run(name, build, tl=5, reopen=None):
    t = time.time()
    try:
        with hx.HexalyOptimizer() as opt:
            m = opt.model
            vs = build(m)
            m.close()
            opt.param.time_limit = tl; opt.param.verbosity = 0; opt.param.nb_threads = 1
            opt.solve()
            s = opt.solution
            vals = [v.value for v in vs] if s.status in (S.FEASIBLE, S.OPTIMAL) else None
            print(f"{name}: status={s.status} vals={vals} t={time.time()-t:.2f}s state={opt.state}", flush=True)
            if reopen:
                reopen(opt, m, vs)
    except Exception as e:
        print(f"{name}: EXC {type(e).__name__}: {e} t={time.time()-t:.2f}s", flush=True)

def infeas(m):
    x = m.int(0, 10); y = m.int(0, 10); m.constraint(x + y == 7); m.constraint(x + y >= 9); m.minimize(0); return [x, y]
run("infeasible_small", infeas)
def php(n, h):
    def b(m):
        x = [m.int(0, h - 1) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n): m.constraint(x[i] != x[j])
        m.minimize(0); return x
    return b
run("php_6_5", php(6, 5), tl=10)
run("php_9_8", php(9, 8), tl=10)
def php_bool(n, h):
    def b(m):
        x = [[m.bool() for _ in range(h)] for _ in range(n)]
        for i in range(n): m.constraint(m.sum(x[i]) == 1)
        for j in range(h): m.constraint(m.sum(x[i][j] for i in range(n)) <= 1)
        m.minimize(0); return [v for r in x for v in r]
    return b
run("php_bool_9_8", php_bool(9, 8), tl=10)

# enumeration by reopening
def enum_reopen(opt, m, vs):
    sols = []
    S_ = hx.HxSolutionStatus
    for k in range(20):
        s = opt.solution
        if s.status not in (S_.FEASIBLE, S_.OPTIMAL):
            print("  stop status", s.status, "after", len(sols)); return
        cur = [v.value for v in vs]
        sols.append(cur)
        m.open()
        m.constraint(m.or_(*[v != c for v, c in zip(vs, cur)]))
        m.close()
        opt.solve()
    print("  sols", sols)
def b5(m):
    b = [m.bool() for _ in range(5)]; m.constraint(m.sum(b) == 2); m.minimize(0); return b
run("enum_bools", b5, reopen=enum_reopen)
