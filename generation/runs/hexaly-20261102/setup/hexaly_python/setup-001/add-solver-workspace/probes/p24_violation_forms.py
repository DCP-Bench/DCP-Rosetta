import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def run(name, build):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model; obj = build(m); m.minimize(obj); m.close()
        p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0); p.time_limit = 10
        opt.solve(); s = opt.solution
        print(f"{name}: {s.status.name} min={obj.value} bound={s.get_objective_bound(0)} t={time.time()-t:.2f}s", flush=True)
def ab(m):  # AB + AB = AAA as abs(lhs - rhs)
    A = m.int(1, 9); B = m.int(0, 9); m.constraint(A != B)
    return m.abs(2 * (10 * A + B) - 111 * A)
def queens3(m):  # rows and columns hard, diagonals as max(0, sum - 1)
    n = 3; x = [[m.bool() for _ in range(n)] for _ in range(n)]
    for i in range(n): m.constraint(m.sum(x[i]) == 1); m.constraint(m.sum(x[r][i] for r in range(n)) == 1)
    diags = [[x[r][r - d] for r in range(n) if 0 <= r - d < n] for d in range(-n + 1, n)] + \
            [[x[r][d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n] for d in range(-n + 1, n)]
    return m.sum(m.max(0, m.sum(c) - 1) for c in diags)
run("AB+AB=AAA as abs", ab); run("3-queens diagonals as max(0, sum - 1)", queens3)
