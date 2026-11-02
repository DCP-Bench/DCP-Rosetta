import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def solve(name, build, tl=10):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        build(m)
        if m.nb_objectives == 0: m.minimize(0)
        m.close()
        p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = 1; p.set_gap_limit(0)
        opt.solve(); s = opt.solution
        extra = f"obj={m.get_objective(0).value} bound={s.get_objective_bound(0)}" if s.status in (S.FEASIBLE, S.OPTIMAL) else ""
        print(f"{name}: {s.status} {extra} t={time.time()-t:.2f}", flush=True)

def qbool(n, soft=False):
    def b(m):
        x = [[m.bool() for _ in range(n)] for _ in range(n)]
        cons = []
        for i in range(n): cons.append(("eq", m.sum(x[i])))
        for j in range(n): cons.append(("eq", m.sum(x[i][j] for i in range(n))))
        for d in range(-n + 1, n):
            cons.append(("le", m.sum(x[i][i - d] for i in range(n) if 0 <= i - d < n)))
            cons.append(("le", m.sum(x[i][d - i + n - 1] for i in range(n) if 0 <= d - i + n - 1 < n)))
        if not soft:
            for k, e in cons: m.constraint(e == 1 if k == "eq" else e <= 1)
        else:
            for k, e in cons[:2*n]: m.constraint(e == 1)
            m.minimize(m.sum(m.max(0, e - 1) for k, e in cons[2*n:]))
    return b
def qint_soft(n):
    def b(m):
        q = [m.int(0, n - 1) for _ in range(n)]
        conf = []
        for i in range(n):
            for j in range(i + 1, n):
                conf += [q[i] == q[j], q[i] + i == q[j] + j, q[i] - i == q[j] - j]
        m.minimize(m.sum(conf))
    return b
solve("queens bool hard n3", qbool(3))
solve("queens bool soft n3", qbool(3, soft=True))
solve("queens int soft n3", qint_soft(3))
def crypt_ab(m):
    # AB + AB = AAA, A,B distinct digits, leading non-zero
    A = m.int(1, 9); B = m.int(0, 9); m.constraint(A != B)
    m.constraint(2 * (10 * A + B) == 111 * A)
crypt_ab_fn = crypt_ab
solve("crypt ab-ab-aaa", crypt_ab)
def php_lin(m):
    n, h = 6, 5
    x = [[m.bool() for _ in range(h)] for _ in range(n)]
    for i in range(n): m.constraint(m.sum(x[i]) == 1)
    for j in range(h): m.constraint(m.sum(x[i][j] for i in range(n)) <= 1)
solve("php lin 6/5", php_lin)
