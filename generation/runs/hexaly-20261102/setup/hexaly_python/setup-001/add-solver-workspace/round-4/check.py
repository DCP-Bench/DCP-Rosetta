"""Scratch checker: python check.py PROBLEM INSTANCE OUTPUT. Verifies feasibility and, where a
brute force is cheap, optimality or completeness, independently of Hexaly."""
import itertools
import json
import sys

problem, inst_path, out_path = sys.argv[1:4]
inst = json.load(open(inst_path))
sols = [json.loads(l) for l in open(out_path) if l.startswith("{")]


def report(ok, msg):
    print(("OK   " if ok else "FAIL ") + msg)


def queens_ok(q, n):
    return (len(q) == n and sorted(q) == list(range(n))
            and len({r - c for r, c in enumerate(q)}) == n and len({r + c for r, c in enumerate(q)}) == n)


def all_queens(n):
    out = []
    def rec(row, cols):
        if row == n:
            out.append(tuple(cols)); return
        for c in range(n):
            if all(c != cc and abs(c - cc) != row - r for r, cc in enumerate(cols)):
                rec(row + 1, cols + [c])
    rec(0, [])
    return out


if problem in ("knapsack", "knapsack-all-optimal"):
    w, v, cap = inst["weights"], inst["values"], inst["capacity"]
    n = len(w)
    best, best_sets = -1, set()
    for t in itertools.product((0, 1), repeat=n):
        if sum(a * b for a, b in zip(w, t)) <= cap:
            val = sum(a * b for a, b in zip(v, t))
            if val > best:
                best, best_sets = val, {t}
            elif val == best:
                best_sets.add(t)
    got = [tuple(s["take"]) for s in sols]
    for t in got:
        report(sum(a * b for a, b in zip(w, t)) <= cap and sum(a * b for a, b in zip(v, t)) == best,
               f"{list(t)} weight {sum(a * b for a, b in zip(w, t))} value {sum(a * b for a, b in zip(v, t))} (optimum {best})")
    if problem == "knapsack":
        report(len(got) == 1, f"{len(got)} solution line(s)")
    else:
        report(len(got) == len(set(got)) and set(got) == best_sets,
               f"{len(got)} printed, {len(set(got))} distinct, {len(best_sets)} optimal exist")
elif problem == "n-queens":
    n = inst["n"]
    exist = len(all_queens(n)) > 0
    if not exist:
        report(sols == [{"status": "unsatisfiable"}], f"n={n} has no solution; printed {sols}")
    else:
        report(len(sols) == 1 and "queens" in sols[0] and queens_ok(sols[0]["queens"], n), f"n={n} printed {sols}")
elif problem == "n-queens-all":
    n = inst["n"]
    truth = set(all_queens(n))
    got = [tuple(s["queens"]) for s in sols]
    report(all(queens_ok(list(q), n) for q in got) and len(got) == len(set(got)) and set(got) == truth,
           f"n={n}: {len(got)} printed, {len(set(got))} distinct, {len(truth)} exist")
elif problem == "graph-colouring":
    n, edges = inst["n_nodes"], inst["edges"]
    col = sols[0]["colour"] if len(sols) == 1 else None
    proper = col is not None and len(col) == n and all(c >= 0 for c in col) and all(col[a] != col[b] for a, b in edges)
    k = len(set(col)) if col else None
    # smallest k with a proper k-colouring, by backtracking
    def colourable(k):
        cs = [-1] * n
        def rec(v):
            if v == n:
                return True
            for c in range(k):
                if all(cs[u] != c for a, b in edges for u in ((b,) if a == v else (a,) if b == v else ()) ):
                    cs[v] = c
                    if rec(v + 1):
                        return True
                    cs[v] = -1
            return False
        return rec(0)
    chi = next(k2 for k2 in range(1, n + 1) if colourable(k2))
    report(proper and k == chi, f"proper {proper}, {k} colours, chromatic number {chi}")
elif problem == "cryptarithm":
    words = inst["addends"] + [inst["sum"]]
    letters = list(dict.fromkeys("".join(words)))
    def num(wd, d):
        return int("".join(str(d[c]) for c in wd))
    def valid(d):
        return (len(set(d.values())) == len(d) and all(d[wd[0]] != 0 for wd in words if len(wd) > 1)
                and sum(num(wd, d) for wd in inst["addends"]) == num(inst["sum"], d))
    count = 0
    if len(letters) <= 10:
        for p in itertools.permutations(range(10), len(letters)):
            if valid(dict(zip(letters, p))):
                count += 1
                break
    if count == 0:
        report(sols == [{"status": "unsatisfiable"}], f"no solution exists; printed {sols}")
    else:
        d = sols[0].get("digits") if len(sols) == 1 else None
        report(d is not None and sorted(d) == sorted(letters) and valid(d), f"printed {sols}")
elif problem == "jobshop":
    jobs = inst["jobs"]
    st = sols[0]["start"] if len(sols) == 1 else None
    ok = st is not None and len(st) == len(jobs)
    tasks = []
    for j, job in enumerate(jobs):
        ok = ok and len(st[j]) == len(job)
        for k, (m, d) in enumerate(job):
            s = st[j][k]
            ok = ok and isinstance(s, int) and s >= 0
            if k > 0:
                ok = ok and st[j][k - 1] + job[k - 1][1] <= s
            tasks.append((m, s, s + d))
    for a, b in itertools.combinations(tasks, 2):
        if a[0] == b[0] and a[1] < b[2] and b[1] < a[2]:
            ok = False
    ms = max(e for _, _, e in tasks)
    report(ok, f"feasible {ok}, makespan {ms}")
