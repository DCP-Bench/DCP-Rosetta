import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
n = 8
def run(width):
    t0 = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        x = [[m.bool() for _ in range(n)] for _ in range(n)]
        for i in range(n): m.constraint(m.sum(x[i]) == 1)
        for j in range(n): m.constraint(m.sum(x[i][j] for i in range(n)) == 1)
        for d in range(-n + 1, n):
            for cells in ([x[r][r - d] for r in range(n) if 0 <= r - d < n], [x[r][d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n]):
                if len(cells) > 1: m.constraint(m.sum(cells) <= 1)
        m.minimize(0); m.close()
        p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0); p.time_limit = 100
        reps, times = [], []
        while True:
            t = time.time(); opt.solve(); times.append(time.time() - t); st = opt.solution.status
            if st not in (S.FEASIBLE, S.OPTIMAL) or m.get_objective(0).value >= 1: break
            cols = [next(j for j in range(n) if x[i][j].value) for i in range(n)]
            m.open(); m.remove_objective(0)
            if width == "queens": terms = [x[i][cols[i]] for i in range(n)]
            else: terms = [x[i][j] == int(cols[i] == j) for i in range(n) for j in range(n)]
            reps.append(m.and_(*terms)); m.minimize(m.sum(reps)); m.close()
        print(f"no-good over {width}: {len(times)-1} sols proven={st == S.OPTIMAL} total={time.time()-t0:.1f}s max solve before last={max(times[:-1]):.2f}s last (proof)={times[-1]:.1f}s", flush=True)
for w in ("queens", "all64", "queens", "all64"): run(w)
with hx.HexalyOptimizer() as opt:
    m = opt.model; r = m.int(0, 5); b = m.int(1, 5)
    try: m.constraint(0 <= r < b); print("chained: no error")
    except Exception as e: print("chained:", type(e).__name__, str(e)[:90])
    try: d = m.distinct([m.int(0, 2) for _ in range(3)]); print("distinct(python list): ok", d.operator)
    except Exception as e: print("distinct(python list):", type(e).__name__, str(e)[:120])
    s = m.sum([]); a = m.and_(m.range(0, 0), m.lambda_function(lambda i: r == i))
    m.minimize(0); m.close(); opt.param.verbosity = 0; opt.solve()
    print("sum([]) =", s.value, "; and_ over empty range =", a.value)
