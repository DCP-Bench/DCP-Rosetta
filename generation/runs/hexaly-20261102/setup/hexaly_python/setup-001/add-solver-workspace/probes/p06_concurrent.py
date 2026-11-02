import time, sys
import hexaly.optimizer as hx
t = time.time()
try:
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        x = [m.int(0, 50) for _ in range(30)]
        for i in range(29): m.constraint(x[i] != x[i+1])
        m.maximize(m.sum(x[i] * x[(i * 7) % 30] for i in range(30)) - m.sum(m.abs(x[i] - x[i+1]) for i in range(29)) * 3 + m.max(x) * m.min(x))
        m.close(); opt.param.verbosity = 0; opt.param.time_limit = 8; opt.param.nb_threads = 1
        opt.solve()
        print(sys.argv[1], "status", opt.solution.status, "t", round(time.time() - t, 2), flush=True)
except Exception as e:
    print(sys.argv[1], "EXC", type(e).__name__, e, "t", round(time.time() - t, 2), flush=True)
