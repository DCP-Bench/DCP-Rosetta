import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus

def enum(name, build, tl=20):
    t0 = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        vs = build(m)
        m.minimize(0)
        m.close()
        p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = 1; p.set_gap_limit(0)
        opt.solve()
        sols = []
        matches = []
        while True:
            s = opt.solution
            if s.status == S.INCONSISTENT:
                print(f"{name}: inconsistent after {len(sols)}"); return
            if s.status not in (S.FEASIBLE, S.OPTIMAL):
                print(f"{name}: {s.status} after {len(sols)} t={time.time()-t0:.2f}"); return
            obj = m.get_objective(0).value
            if obj >= 1:
                if s.status == S.OPTIMAL:
                    print(f"{name}: EXHAUSTED (proven) after {len(sols)} sols t={time.time()-t0:.2f}"); return
                print(f"{name}: unproven min>=1 after {len(sols)} t={time.time()-t0:.2f}"); return
            cur = [v.value for v in vs]; sols.append(cur)
            m.open()
            m.remove_objective(0)
            matches.append(m.and_(*[v == c for v, c in zip(vs, cur)]))
            m.minimize(m.sum(matches))
            m.close()
            t = time.time(); opt.solve()

def xy(n):
    def b(m):
        x = m.int(0, n); y = m.int(0, n); m.constraint(x + y == n); return [x, y]
    return b
def b5(m):
    b = [m.bool() for _ in range(5)]; m.constraint(m.sum(b) == 2); return b
def i3(m):
    x = [m.int(1, 3) for _ in range(3)]
    for i in range(3):
        for j in range(i+1, 3): m.constraint(x[i] != x[j])
    return x
def queens(n):
    def b(m):
        q = [m.int(0, n - 1) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                m.constraint(q[i] != q[j]); m.constraint(q[i] + i != q[j] + j); m.constraint(q[i] - i != q[j] - j)
        return q
    return b
enum("xy2", xy(2)); enum("xy3", xy(3)); enum("b5", b5); enum("perm3", i3); enum("queens6", queens(6)); enum("queens8", queens(8), tl=60)
