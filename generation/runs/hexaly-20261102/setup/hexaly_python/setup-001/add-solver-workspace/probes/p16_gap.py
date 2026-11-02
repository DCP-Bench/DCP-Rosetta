import random, time
import hexaly.optimizer as hx
weights = [647339, 534286, 945876, 418162, 483384, 403694, 283173, 903321, 839395, 838428, 666425, 793510, 391794, 215513, 128245, 360993, 502832, 954784, 882652, 539947, 364643, 625968, 941350, 432854, 771638, 987439, 817681, 859454, 521098, 244222, 677958, 165213, 246676, 952082, 930078, 306113, 258246, 839842, 658741, 686040]
values = [650779, 539709, 954722, 420185, 484517, 408759, 289885, 904662, 847706, 846195, 676254, 795830, 398489, 223804, 133756, 361285, 509922, 960882, 892018, 540793, 370453, 626792, 949169, 438995, 781141, 987523, 824324, 863368, 523016, 253344, 681461, 169285, 255309, 957975, 931030, 310490, 259298, 844355, 661898, 695934]
capacity = 12010544
def run(gap):
    t = time.time()
    with hx.HexalyOptimizer() as opt:
        m = opt.model
        x = [m.bool() for _ in weights]
        m.constraint(m.sum(w * xi for w, xi in zip(weights, x)) <= capacity)
        obj = m.sum(v * xi for v, xi in zip(values, x)); m.maximize(obj); m.close()
        p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.time_limit = 60
        if gap is not None: p.set_gap_limit(gap)
        opt.solve(); s = opt.solution
        print(f"gap_limit={p.get_gap_limit()}: {s.status.name} obj={obj.value} bound={s.get_objective_bound(0)} t={time.time()-t:.1f}", flush=True)
run(None); run(0)
