import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def crypt(words, total, soft, tl=10):
    letters = sorted(set("".join(words + [total])))
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        d = {c: m.int(1 if c in {w[0] for w in words + [total]} else 0, 9) for c in letters}
        for i, a in enumerate(letters):
            for b in letters[i + 1:]: m.constraint(d[a] != d[b])
        val = lambda w: m.sum(10 ** (len(w) - 1 - k) * d[c] for k, c in enumerate(w))
        diff = m.sum(val(w) for w in words) - val(total)
        if soft: m.minimize(m.abs(diff))
        else: m.constraint(diff == 0); m.minimize(0)
        m.close(); p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.set_gap_limit(0); p.time_limit = tl
        opt.solve(); s = opt.solution
        miss = m.get_objective(0).value if s.status in (S.OPTIMAL, S.FEASIBLE) else None
        print(f"{'+'.join(words)}={total} {'soft' if soft else 'hard'}: {s.status.name} objective={miss} t={time.time()-t:.2f}s", flush=True)
crypt(["SEND", "MORE"], "MONEY", soft=True)
crypt(["CCEE", "GGCB"], "DHACI", soft=False)
crypt(["CCEE", "GGCB"], "DHACI", soft=True)
with hx.HexalyOptimizer() as opt:
    m = opt.model
    a, b, c = m.set(4), m.set(4), m.set(4)
    m.constraint(m.partition(a, b, c)); m.constraint(m.disjoint(a, b)); m.constraint(m.cover(a, b, c))
    m.constraint(m.count(a) == 2)
    e = m.sum(x for x in [])
    m.minimize(0); m.close(); opt.param.verbosity = 0; opt.solve()
    print("partition/disjoint/cover:", opt.solution.status.name, sorted(a.value), sorted(b.value), sorted(c.value), "| sum(empty generator) =", e.value)
