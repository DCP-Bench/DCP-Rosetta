import json, time, sys
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
T = "/toy"
def load(p): return json.load(open(f"{T}/{p}"))

def solve(name, build, tl=20):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        show = build(m)
        if m.nb_objectives == 0: m.minimize(0)
        m.close()
        p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = 1; p.set_gap_limit(0)
        opt.solve(); s = opt.solution
        extra = ""
        if m.nb_objectives and s.status in (S.FEASIBLE, S.OPTIMAL):
            extra = f"obj={m.get_objective(0).value} bound={s.get_objective_bound(0)}"
        print(f"{name}: {s.status} {extra} {show() if show and s.status in (S.FEASIBLE, S.OPTIMAL) else ''} t={time.time()-t:.2f}", flush=True)

def queens_int(n):
    def b(m):
        q = [m.int(0, n - 1) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                m.constraint(q[i] != q[j]); m.constraint(q[i] + i != q[j] + j); m.constraint(q[i] - i != q[j] - j)
        return lambda: [x.value for x in q]
    return b
def queens_list(n):
    def b(m):
        q = m.list(n); m.constraint(m.count(q) == n)
        for i in range(n):
            for j in range(i + 1, n):
                m.constraint(m.abs(q[i] - q[j]) != j - i)
        return lambda: list(q.value)
    return b
solve("queens_int n3", queens_int(3), tl=10)
solve("queens_list n3", queens_list(3), tl=10)
solve("queens_int n8", queens_int(8), tl=10)

def knap(path):
    d = load(path)
    def b(m):
        keys = list(d.keys())
        return d, keys
    return d
d = load("knapsack/instances/p01.json"); print("knap keys", list(d.keys()))
