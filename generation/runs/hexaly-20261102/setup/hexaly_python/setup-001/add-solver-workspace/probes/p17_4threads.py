import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def solve(name, build, tl=10):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model; build(m)
        if m.nb_objectives == 0: m.minimize(0)
        m.close(); p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0)
        opt.solve(); print(f"{name}: {opt.solution.status.name} t={time.time()-t:.2f}", flush=True)
def queens(n):
    def b(m):
        q = [m.int(0, n - 1) for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                m.constraint(q[i] != q[j]); m.constraint(q[i] + i != q[j] + j); m.constraint(q[i] - i != q[j] - j)
    return b
def php(m):
    x = [m.int(0, 4) for _ in range(6)]
    for i in range(6):
        for j in range(i + 1, 6): m.constraint(x[i] != x[j])
solve("queens3 hard 4thr", queens(3)); solve("php 6/5 hard 4thr", php)
# hard nogood enumeration at 4 threads
with hx.HexalyOptimizer() as opt:
    m = opt.model; b = [m.bool() for _ in range(5)]; m.constraint(m.sum(b) == 2); m.minimize(0); m.close()
    p = opt.param; p.time_limit = 5; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0)
    n = 0
    while True:
        t = time.time(); opt.solve(); st = opt.solution.status
        if st not in (S.FEASIBLE, S.OPTIMAL): print(f"hard nogood 4thr: {n} sols, last {st.name} in {time.time()-t:.2f}s"); break
        n += 1; cur = [x.value for x in b]; m.open(); m.constraint(m.or_(*[x != c for x, c in zip(b, cur)])); m.close()
# soft nogood 8-queens at 4 threads
t0 = time.time()
with hx.HexalyOptimizer() as opt:
    m = opt.model; n = 8
    q = [m.int(0, n - 1) for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m.constraint(q[i] != q[j]); m.constraint(q[i] + i != q[j] + j); m.constraint(q[i] - i != q[j] - j)
    m.minimize(0); m.close(); p = opt.param; p.time_limit = 60; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0)
    reps = []; cnt = 0
    while True:
        opt.solve(); st = opt.solution.status
        if st not in (S.FEASIBLE, S.OPTIMAL): print("queens8 soft 4thr stop", st.name, cnt); break
        if m.get_objective(0).value >= 1: print(f"queens8 soft 4thr: {cnt} sols, proven={st == S.OPTIMAL} t={time.time()-t0:.1f}"); break
        cnt += 1; cur = [x.value for x in q]; m.open(); m.remove_objective(0); reps.append(m.and_(*[x == c for x, c in zip(q, cur)])); m.minimize(m.sum(reps)); m.close()
