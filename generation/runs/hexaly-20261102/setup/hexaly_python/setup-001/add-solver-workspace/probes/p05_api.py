import time, sys
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def section(t): print("\n##", t, flush=True)

section("gap_limit default and params")
with hx.HexalyOptimizer() as opt:
    p = opt.param
    print("gap_limit", p.get_gap_limit(), "nb_threads", p.nb_threads, "seed", p.seed, "verbosity", p.verbosity, "time_limit", p.time_limit, "iteration_limit", p.iteration_limit)

section("value types, 64-bit, list var, array output")
with hx.HexalyOptimizer() as opt:
    m = opt.model
    b = m.bool(); i = m.int(0, 10**12); f = m.float(0, 1)
    l = m.list(4); m.constraint(m.count(l) == 4)
    arr = m.array([m.int(0, 3) for _ in range(3)])
    m.constraint(i >= 5 * 10**9)
    m.constraint(b == 1)
    m.minimize(i + m.at(l, 0))
    m.close(); p = opt.param; p.verbosity = 0; p.nb_threads = 1; p.time_limit = 5
    opt.solve(); s = opt.solution
    print("status", s.status)
    for name, e in [("b", b), ("i", i), ("f", f), ("l", l), ("arr", arr)]:
        v = e.value
        print(name, type(e).__name__, "op", e.operator if hasattr(e, 'operator') else '-', "value", repr(v), type(v).__name__,
              "is_int", e.is_int(), "is_bool", e.is_bool(), "is_array", e.is_array(), "is_collection", e.is_collection(), flush=True)
    lv = l.value
    print("list as py", list(lv), [x for x in lv], "count", lv.count())
    av = arr.value
    print("array as py", [av.get(k) for k in range(av.count())])
    print("obj", s.get_objective_bound(0), "status", s.status, "objective value via model", m.get_objective(0).value, "nb_obj", m.nb_objectives, "dir", m.get_objective_direction(0))

section("errors")
def err(label, fn):
    try:
        with hx.HexalyOptimizer() as opt:
            fn(opt, opt.model)
        print(label, "no error")
    except Exception as e:
        print(label, "->", type(e).__module__, type(e).__name__, ":", e)
err("bad bounds", lambda o, m: m.int(5, 1))
err("bool + str", lambda o, m: m.bool() + "a")
def unclosed(o, m):
    x = m.int(0, 3); m.minimize(x); o.solve()
err("solve unclosed", unclosed)
def py_bool(o, m):
    x = m.int(0, 3)
    if x > 1: pass
err("python truthiness", py_bool)
def double_close(o, m):
    x = m.int(0, 3); m.minimize(x); m.close(); m.close()
err("double close", double_close)
def two_obj(o, m):
    x = m.int(0, 3); m.minimize(x); m.maximize(x); m.close(); print("nb_objectives", m.nb_objectives)
err("two objectives", two_obj)
def remove_obj(o, m):
    x = m.int(0, 3); m.minimize(x); m.close(); o.param.verbosity = 0; o.solve(); m.open(); m.remove_objective(0); m.constraint(x == 0); m.minimize(0); m.close(); o.solve(); print("after remove", o.solution.status, x.value, m.nb_objectives)
err("remove objective", remove_obj)
