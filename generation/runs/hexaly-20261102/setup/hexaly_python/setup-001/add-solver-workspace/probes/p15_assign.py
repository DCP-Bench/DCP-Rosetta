import time
import hexaly.optimizer as hx
COST = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
N = 4
def run(name, build):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model; total = build(m); m.minimize(total); m.close()
        p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0); p.time_limit = 10
        opt.solve(); s = opt.solution
        print(f"{name}: {s.status.name} total={total.value} bound={s.get_objective_bound(0)} t={time.time()-t:.2f}", flush=True)
def bools(m):
    x = [[m.bool() for _ in range(N)] for _ in range(N)]
    for i in range(N): m.constraint(m.sum(x[i]) == 1)
    for j in range(N): m.constraint(m.sum(x[i][j] for i in range(N)) == 1)
    return m.sum(COST[i][j] * x[i][j] for i in range(N) for j in range(N))
def ints_distinct(m):
    job = [m.int(0, N - 1) for _ in range(N)]
    m.constraint(m.count(m.distinct(m.array(job))) == N)
    return m.sum(m.at(m.array(COST[w]), job[w]) for w in range(N))
def ints_pairwise(m):
    job = [m.int(0, N - 1) for _ in range(N)]
    for a in range(N):
        for b in range(a + 1, N): m.constraint(job[a] != job[b])
    return m.sum(m.at(m.array(COST[w]), job[w]) for w in range(N))
def list_lambda(m):
    job = m.list(N); m.constraint(m.count(job) == N)
    cost = m.array(COST)
    return m.sum(m.range(0, N), m.lambda_function(lambda w: m.at(cost, w, job[w])))
run("bool matrix", bools); run("ints+distinct", ints_distinct); run("ints pairwise !=", ints_pairwise); run("list + lambda sum", list_lambda)
