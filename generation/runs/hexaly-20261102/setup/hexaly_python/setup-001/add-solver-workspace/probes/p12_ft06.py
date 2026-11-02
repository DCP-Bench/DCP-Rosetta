import json, time, sys
sys.path.insert(0, "/p")
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
d = json.load(open("/toy/jobshop/instances/ft06.json"))
jobs = d["jobs"]; nm = 1 + max(mc for job in jobs for mc, _ in job); H = sum(du for job in jobs for _, du in job)
def run(name, build, tl=60, threads=1):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model; build(m); m.close()
        p = opt.param; p.time_limit = tl; p.verbosity = 0; p.nb_threads = threads; p.set_gap_limit(0)
        opt.solve(); s = opt.solution
        print(f"{name}: {s.status} obj={m.get_objective(0).value} bound={s.get_objective_bound(0)} t={time.time()-t:.1f}", flush=True)
def ints_disj(m):
    s = [[m.int(0, H) for _ in job] for job in jobs]
    for j, job in enumerate(jobs):
        for k in range(1, len(job)): m.constraint(s[j][k - 1] + job[k - 1][1] <= s[j][k])
    ops = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
    for a in range(len(ops)):
        for b in range(a + 1, len(ops)):
            (j1, k1), (j2, k2) = ops[a], ops[b]
            if jobs[j1][k1][0] == jobs[j2][k2][0] and j1 != j2:
                m.constraint(m.or_(s[j1][k1] + jobs[j1][k1][1] <= s[j2][k2], s[j2][k2] + jobs[j2][k2][1] <= s[j1][k1]))
    m.minimize(m.max(s[j][-1] + jobs[j][-1][1] for j in range(len(jobs))))
def intervals_lists(m):
    T = [[m.interval(0, H) for _ in job] for job in jobs]
    for j, job in enumerate(jobs):
        for k, (mc, du) in enumerate(job):
            m.constraint(m.length(T[j][k]) == du)
            if k: m.constraint(T[j][k - 1] < T[j][k])
    for mc in range(nm):
        ops = [T[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == mc]
        arr = m.array(ops); seq = m.list(len(ops)); m.constraint(m.count(seq) == len(ops))
        m.constraint(m.and_(m.range(0, len(ops) - 1), m.lambda_function(lambda i: arr[seq[i]] < arr[seq[i + 1]])))
    m.minimize(m.max(m.end(job[-1]) for job in T))
run("ft06 ints+disjunctions 1thr", ints_disj)
run("ft06 intervals+lists 4thr", intervals_lists, threads=4)
