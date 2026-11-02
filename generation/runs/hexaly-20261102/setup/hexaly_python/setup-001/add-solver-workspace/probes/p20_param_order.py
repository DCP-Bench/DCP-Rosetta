import sys, time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
n = 8
def run(skip_single, tl, before=False):
    t0 = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        if before:
            q = opt.param; q.verbosity = 0; q.nb_threads = 4; q.set_gap_limit(0)
        x = [[m.bool() for _ in range(n)] for _ in range(n)]
        for i in range(n):
            m.constraint(m.sum(x[i]) == 1)
            m.constraint(m.sum(x[r][i] for r in range(n)) == 1)
        for d in range(-n + 1, n):
            for cells in ([x[r][r - d] for r in range(n) if 0 <= r - d < n], [x[r][d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n]):
                if len(cells) > 1 or not skip_single:
                    m.constraint(m.sum(cells) <= 1)
        m.minimize(0); m.close()
        p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0)
        reps, sols = [], 0
        while True:
            p.time_limit = tl
            opt.solve(); st = opt.solution.status
            if st not in (S.FEASIBLE, S.OPTIMAL) or m.get_objective(0).value >= 1:
                print(f"params_before_close={before} skip_single={skip_single} time_limit={tl}: {sols} sols, {st.name}, {time.time()-t0:.1f}s", flush=True); return
            sols += 1
            cols = [next(j for j in range(n) if x[i][j].value) for i in range(n)]
            m.open(); m.remove_objective(0); reps.append(m.and_(*[x[i][cols[i]] for i in range(n)])); m.minimize(m.sum(reps)); m.close()
run(False, 30, before=True); run(False, 30, before=False); run(False, 30, before=True)
