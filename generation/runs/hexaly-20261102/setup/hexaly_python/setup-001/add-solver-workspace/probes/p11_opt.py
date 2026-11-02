import json, time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def load(p): return json.load(open("/toy/" + p))
def solve(name, build, tl=30):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        show = build(m); m.close()
        p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = 1; p.set_gap_limit(0)
        opt.solve(); s = opt.solution
        ok = s.status in (S.FEASIBLE, S.OPTIMAL)
        print(f"{name}: {s.status} obj={m.get_objective(0).value if ok else '-'} bound={s.get_objective_bound(0) if ok else '-'} {show() if ok and show else ''} t={time.time()-t:.2f}", flush=True)

def knap(path):
    d = load(path)
    def b(m):
        n = len(d["weights"]); x = [m.bool() for _ in range(n)]
        m.constraint(m.sum(w * xi for w, xi in zip(d["weights"], x)) <= d["capacity"])
        m.maximize(m.sum(v * xi for v, xi in zip(d["values"], x)))
        return lambda: [xi.value for xi in x]
    return b
def knap_set(path):
    d = load(path)
    def b(m):
        n = len(d["weights"]); s = m.set(n)
        W = m.array(d["weights"]); V = m.array(d["values"])
        m.constraint(m.sum(s, m.lambda_function(lambda i: W[i])) <= d["capacity"])
        m.maximize(m.sum(s, m.lambda_function(lambda i: V[i])))
        return lambda: sorted(s.value)
    return b
solve("knap p01 bool", knap("knapsack/instances/p01.json"))
solve("knap p01 set", knap_set("knapsack/instances/p01.json"))
def colour(path):
    d = load(path)
    def b(m):
        n = d["n_nodes"]; c = [m.int(0, n - 1) for _ in range(n)]
        for u, v in d["edges"]: m.constraint(c[u] != c[v])
        k = m.max(c) + 1
        m.minimize(k)
        return lambda: [x.value for x in c]
    return b
for g in ("petersen", "cycle6", "k4-tail"):
    solve(f"colour {g}", colour(f"graph-colouring/instances/{g}.json"))
def jobshop(path):
    d = load(path)
    def b(m):
        jobs = d["jobs"]; nj = len(jobs); nm = 1 + max(mc for job in jobs for mc, _ in job)
        H = sum(du for job in jobs for _, du in job)
        T = [[m.interval(0, H) for _ in job] for job in jobs]
        for j, job in enumerate(jobs):
            for k, (mc, du) in enumerate(job):
                m.constraint(m.length(T[j][k]) == du)
                if k: m.constraint(T[j][k - 1] < T[j][k])
        for mc in range(nm):
            ops = [T[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == mc]
            arr = m.array(ops); seq = m.list(len(ops))
            m.constraint(m.count(seq) == len(ops))
            m.constraint(m.and_(m.range(0, len(ops) - 1), m.lambda_function(lambda i: arr[seq[i]] < arr[seq[i + 1]])))
        m.minimize(m.max(m.end(job[-1]) for job in T))
        return lambda: [[iv.value.start() for iv in job] for job in T]
    return b
solve("jobshop small", jobshop("jobshop/instances/small.json"))
solve("jobshop ft06", jobshop("jobshop/instances/ft06.json"), tl=60)
