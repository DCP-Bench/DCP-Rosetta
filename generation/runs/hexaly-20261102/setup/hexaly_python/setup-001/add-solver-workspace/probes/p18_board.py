import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
n = 8
t0 = time.time()
with hx.HexalyOptimizer() as opt:
    m = opt.model
    x = [[m.bool() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        m.constraint(m.sum(x[i]) == 1)
        m.constraint(m.sum(x[r][i] for r in range(n)) == 1)
    for d in range(-n + 1, n):
        m.constraint(m.sum(x[r][r - d] for r in range(n) if 0 <= r - d < n) <= 1)
        m.constraint(m.sum(x[r][d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n) <= 1)
    m.minimize(0); m.close()
    p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0)
    reps, sols, limits = [], 0, set()
    while True:
        p.time_limit = 30 if sols % 2 else 31   # changed before every solve
        limits.add(p.time_limit)
        opt.solve(); st = opt.solution.status
        if st not in (S.FEASIBLE, S.OPTIMAL): print("stop", st.name, sols); break
        if m.get_objective(0).value >= 1:
            print(f"bool board soft and_: {sols} sols, proven={st == S.OPTIMAL}, {time.time()-t0:.1f}s, time_limit values used {sorted(limits)}"); break
        sols += 1
        cols = [next(j for j in range(n) if x[i][j].value) for i in range(n)]
        m.open(); m.remove_objective(0); reps.append(m.and_(*[x[i][cols[i]] for i in range(n)])); m.minimize(m.sum(reps)); m.close()
