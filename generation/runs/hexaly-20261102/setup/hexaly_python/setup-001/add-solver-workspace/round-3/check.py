"""Scratch checker: python check.py PROBLEM INSTANCE OUTPUT_FILE. Brute force where small."""
import itertools
import json
import sys

problem, inst_path, out_path = sys.argv[1:4]
inst = json.load(open(inst_path))
lines = [json.loads(l) for l in open(out_path, encoding="utf-8", errors="replace") if l.startswith("{")]


def fail(msg):
    print("FAIL", problem, inst_path.split("/")[-1], msg)
    sys.exit(1)


def ok(msg):
    print("OK  ", problem, inst_path.split("/")[-1], msg)


def queens_ok(q):
    n = len(q)
    return sorted(q) == list(range(n)) and len({r - c for r, c in enumerate(q)}) == n and len({r + c for r, c in enumerate(q)}) == n


def all_queens(n):
    return [list(p) for p in itertools.permutations(range(n)) if queens_ok(p)]


def knap_opt(w, v, cap):
    n = len(w)
    best, sols = -1, []
    for t in itertools.product((0, 1), repeat=n):
        if sum(a * b for a, b in zip(w, t)) <= cap:
            val = sum(a * b for a, b in zip(v, t))
            if val > best:
                best, sols = val, [list(t)]
            elif val == best:
                sols.append(list(t))
    return best, sols


if problem == "knapsack":
    if len(lines) != 1:
        fail(f"{len(lines)} lines")
    t = lines[0]["take"]
    w, v, cap = inst["weights"], inst["values"], inst["capacity"]
    if sum(a * b for a, b in zip(w, t)) > cap:
        fail("overweight")
    best, _ = knap_opt(w, v, cap)
    val = sum(a * b for a, b in zip(v, t))
    (ok if val == best else fail)(f"value {val} brute-force optimum {best}")

elif problem == "knapsack-all-optimal":
    best, sols = knap_opt(inst["weights"], inst["values"], inst["capacity"])
    got = [l["take"] for l in lines]
    if len(got) != len({tuple(g) for g in got}):
        fail("duplicates")
    if sorted(got) != sorted(sols):
        fail(f"got {len(got)} expected {len(sols)}")
    ok(f"{len(got)} optimal selections of value {best}, all and only")

elif problem == "n-queens":
    n = inst["n"]
    sols = all_queens(n)
    if len(lines) != 1:
        fail(f"{len(lines)} lines")
    if lines[0] == {"status": "unsatisfiable"}:
        (ok if not sols else fail)(f"unsatisfiable; brute force finds {len(sols)}")
    else:
        (ok if queens_ok(lines[0]["queens"]) else fail)(f"placement {lines[0]['queens']}")

elif problem == "n-queens-all":
    sols = all_queens(inst["n"])
    got = [l["queens"] for l in lines]
    if len(got) != len({tuple(g) for g in got}):
        fail("duplicates")
    (ok if sorted(got) == sorted(sols) else fail)(f"got {len(got)} brute force {len(sols)}")

elif problem == "cryptarithm":
    adds, tot = inst["addends"], inst["sum"]
    words = adds + [tot]
    letters = sorted(set("".join(words)))
    lead = {w[0] for w in words if len(w) > 1}

    def holds(d):
        if any(d[w[0]] == 0 for w in words if len(w) > 1):
            return False
        num = lambda w: int("".join(str(d[c]) for c in w))
        return len(set(d.values())) == len(d) and sum(num(w) for w in adds) == num(tot)

    count = 0
    for p in itertools.permutations(range(10), len(letters)):
        if holds(dict(zip(letters, p))):
            count += 1
    if len(lines) != 1:
        fail(f"{len(lines)} lines")
    if lines[0] == {"status": "unsatisfiable"}:
        (ok if count == 0 else fail)(f"unsatisfiable; brute force finds {count}")
    else:
        d = lines[0]["digits"]
        if sorted(d) != letters:
            fail(f"letters {sorted(d)}")
        (ok if holds(d) else fail)(f"assignment {d}; brute force has {count} solutions")

elif problem == "graph-colouring":
    n, edges = inst["n_nodes"], inst["edges"]
    if len(lines) != 1:
        fail(f"{len(lines)} lines")
    col = lines[0]["colour"]
    if len(col) != n or any(not isinstance(c, int) or c < 0 for c in col):
        fail("bad vector")
    if any(col[u] == col[v] for u, v in edges):
        fail("edge conflict")
    k = len(set(col))
    # smallest k with a proper colouring, by backtracking
    def colourable(k):
        cols = [-1] * n
        def bt(v):
            if v == n:
                return True
            for c in range(k):
                if all(cols[u] != c for a, b in edges for u in ((b,) if a == v else (a,) if b == v else ())):
                    cols[v] = c
                    if bt(v + 1):
                        return True
                    cols[v] = -1
            return False
        return bt(0)
    chi = next(k for k in range(1, n + 1) if colourable(k))
    (ok if k == chi else fail)(f"{k} colours; chromatic number {chi}")

elif problem == "jobshop":
    jobs = inst["jobs"]
    if len(lines) != 1:
        fail(f"{len(lines)} lines")
    st = lines[0]["start"]
    if [len(s) for s in st] != [len(j) for j in jobs]:
        fail("shape")
    for j, job in enumerate(jobs):
        for k in range(len(job)):
            if st[j][k] < 0 or (k and st[j][k] < st[j][k - 1] + job[k - 1][1]):
                fail(f"precedence job {j} task {k}")
    by_m = {}
    for j, job in enumerate(jobs):
        for k, (m, d) in enumerate(job):
            by_m.setdefault(m, []).append((st[j][k], st[j][k] + d))
    for m, iv in by_m.items():
        iv.sort()
        if any(a[1] > b[0] for a, b in zip(iv, iv[1:])):
            fail(f"overlap on machine {m}")
    mk = max(st[j][-1] + jobs[j][-1][1] for j in range(len(jobs)) if jobs[j])
    # brute force over machine orders when small
    tasks_m = {}
    for j, job in enumerate(jobs):
        for k, (m, d) in enumerate(job):
            tasks_m.setdefault(m, []).append((j, k))
    size = 1
    for v in tasks_m.values():
        for i in range(2, len(v) + 1):
            size *= i
    if size <= 200000:
        best = None
        ms = sorted(tasks_m)
        for orders in itertools.product(*[itertools.permutations(tasks_m[m]) for m in ms]):
            # longest path; iterate to fixpoint, detect cycles by bound
            s = {(j, k): 0 for j, job in enumerate(jobs) for k in range(len(job))}
            for _ in range(len(s) + 1):
                changed = False
                for j, job in enumerate(jobs):
                    for k in range(1, len(job)):
                        e = s[(j, k - 1)] + job[k - 1][1]
                        if s[(j, k)] < e:
                            s[(j, k)], changed = e, True
                for order in orders:
                    for a, b in zip(order, order[1:]):
                        e = s[a] + jobs[a[0]][a[1]][1]
                        if s[b] < e:
                            s[b], changed = e, True
                if not changed:
                    break
            else:
                continue  # cycle
            val = max(s[(j, len(job) - 1)] + job[-1][1] for j, job in enumerate(jobs) if job)
            best = val if best is None else min(best, val)
        (ok if mk == best else fail)(f"makespan {mk}; brute-force optimum {best}")
    else:
        ok(f"feasible schedule, makespan {mk} (optimality not brute-forced)")
