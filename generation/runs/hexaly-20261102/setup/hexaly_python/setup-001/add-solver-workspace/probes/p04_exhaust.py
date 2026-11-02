import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus

def enum(name, build, nogood, tl=5):
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        vs = build(m)
        m.close()
        opt.param.time_limit = tl; opt.param.verbosity = 0; opt.param.nb_threads = 1
        sols = []
        while True:
            t = time.time(); opt.solve(); dt = time.time() - t
            s = opt.solution
            if s.status not in (S.FEASIBLE, S.OPTIMAL):
                print(f"{name}: {len(sols)} sols, last status {s.status} in {dt:.2f}s", flush=True); return
            cur = [v.value for v in vs]; sols.append(cur)
            m.open(); nogood(m, vs, cur); m.close()

def or_ne(m, vs, cur): m.constraint(m.or_(*[v != c for v, c in zip(vs, cur)]))
def lin_bool(m, vs, cur): m.constraint(m.sum(*[(1 - v) if c else v for v, c in zip(vs, cur)]) >= 1)
def sum_ne(m, vs, cur): m.constraint(m.sum(*[v != c for v, c in zip(vs, cur)]) >= 1)
def b5(m):
    b = [m.bool() for _ in range(5)]; m.constraint(m.sum(b) == 2); m.minimize(0); return b
def i3(m):
    x = [m.int(1, 3) for _ in range(3)]
    for i in range(3):
        for j in range(i+1, 3): m.constraint(x[i] != x[j])
    m.minimize(0); return x
enum("bools_or", b5, or_ne)
enum("bools_lin", b5, lin_bool)
enum("bools_sumne", b5, sum_ne)
enum("perm3_or", i3, or_ne)
enum("perm3_sumne", i3, sum_ne)
