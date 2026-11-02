import time
import hexaly.optimizer as hx
S = hx.HxSolutionStatus
def trial(label, fn):
    try:
        with hx.HexalyOptimizer() as opt:
            m = opt.model
            out = fn(m)
            if m.nb_objectives == 0: m.minimize(0)
            m.close(); p = opt.param; p.verbosity = 0; p.nb_threads = 4; p.time_limit = 10; p.set_gap_limit(0)
            t = time.time(); opt.solve()
            print(label, "->", opt.solution.status, out() if callable(out) else out, f"t={time.time()-t:.2f}", flush=True)
    except Exception as e:
        print(label, "-> EXC", type(e).__name__, str(e)[:200], flush=True)

def ops(m):
    x = m.int(-7, -7); y = m.int(2, 2)
    exprs = {"x/y": x / y, "x%y": x % y, "x//y": None, "floor(x/y)": m.floor(x / y), "m.div": m.div(x, y), "m.mod": m.mod(x, y), "x**2": x ** 2, "abs": m.abs(x), "iif": m.iif(x < 0, 1, 2)}
    try: exprs["x//y"] = x // y
    except Exception as e: exprs["x//y"] = f"EXC {type(e).__name__}: {e}"
    return lambda: {k: (v.value if hasattr(v, "value") else v) for k, v in exprs.items()}
trial("ops", ops)
def logic(m):
    a = m.bool(); b = m.bool()
    m.constraint(a | b); m.constraint(~a if False else m.not_(a)); 
    return lambda: (a.value, b.value)
trial("logic | not_", logic)
def amp(m):
    a = m.bool(); b = m.bool(); m.constraint(a & b); return lambda: (a.value, b.value)
trial("logic &", amp)
def distinct_alldiff(m):
    n = 8
    q = [m.int(0, n - 1) for _ in range(n)]
    arr = m.array(q)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i]))) == n)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i] + i))) == n)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i] - i))) == n)
    return lambda: [v.value for v in q]
trial("queens8 via distinct", distinct_alldiff)
def distinct3(m):
    n = 3
    q = [m.int(0, n - 1) for _ in range(n)]
    arr = m.array(q)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i]))) == n)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i] + i))) == n)
    m.constraint(m.count(m.distinct(m.range(0, n), m.lambda_function(lambda i: arr[i] - i))) == n)
    return lambda: [v.value for v in q]
trial("queens3 via distinct (infeasible)", distinct3)
def distinct_array(m):
    q = [m.int(0, 2) for _ in range(3)]
    arr = m.array(q)
    m.constraint(m.count(m.distinct(arr)) == 3)
    return lambda: [v.value for v in q]
trial("distinct(array) one-arg", distinct_array)
def arrays(m):
    a = m.array([m.int(0, 5) for _ in range(3)])
    i = m.int(0, 2)
    m.constraint(a[i] == 4); m.constraint(m.at(a, i) == 4)
    c = m.array([[1, 2], [3, 4]])
    j = m.int(0, 1)
    m.constraint(m.at(c, j, j) == 4)
    return lambda: (i.value, j.value, list(a.value) if hasattr(a.value, "__iter__") else "not iterable", [a.value.get(k) for k in range(a.value.count())])
trial("arrays/at", arrays)
def const(m):
    x = m.int(0, 3); m.constraint(True); m.constraint(x >= 1); return lambda: x.value
trial("constraint(True)", const)
def pysum(m):
    xs = [m.int(0, 3) for _ in range(3)]
    m.constraint(sum(xs) == 9)
    return lambda: [v.value for v in xs]
trial("builtin sum", pysum)
def nested(m):
    xs = [m.int(0, 3) for _ in range(3)]
    m.constraint(m.sum(xs) == 9); m.constraint(m.sum(x for x in xs) == 9); m.constraint(m.sum(*xs) == 9)
    return lambda: [v.value for v in xs]
trial("m.sum list/gen/varargs", nested)
