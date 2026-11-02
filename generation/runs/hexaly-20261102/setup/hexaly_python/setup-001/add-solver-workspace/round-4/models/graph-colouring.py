"""Graph colouring: colour the nodes of an undirected graph so that the two ends of every edge
get different colours, using as few distinct colours as possible.

Boolean assignment model with linear constraints (so Hexaly's bounds can prove the optimum):
colour[v][c] says node v takes colour c, used[c] says colour c is in use. The candidate colours
are those of a greedy colouring, an upper bound on the number needed.
Prints one optimal colouring as {"colour": [...]}.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
n, edges = data["n_nodes"], [tuple(e) for e in data["edges"]]

# Greedy colouring: its number of colours bounds the optimum from above
neighbours = [set() for _ in range(n)]
for u, v in edges:
    neighbours[u].add(v)
    neighbours[v].add(u)
greedy = [0] * n
for v in range(n):
    taken = {greedy[u] for u in neighbours[v] if u < v}
    greedy[v] = next(c for c in range(n) if c not in taken)
K = max(greedy, default=-1) + 1

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    optimizer.param.time_limit = 90
    model = optimizer.model
    colour = [[model.bool() for _ in range(K)] for _ in range(n)]
    used = [model.bool() for _ in range(K)]

    # Every node gets exactly one colour
    for v in range(n):
        model.constraint(model.sum(colour[v]) == 1)
    # A node only takes a colour in use
    for v in range(n):
        for c in range(K):
            model.constraint(colour[v][c] <= used[c])
    # The two endpoints of every edge get different colours
    for u, v in edges:
        for c in range(K):
            model.constraint(colour[u][c] + colour[v][c] <= used[c])
    # Colours are used in order (removes symmetric solutions, not optimal ones)
    for c in range(K - 1):
        model.constraint(used[c] >= used[c + 1])

    # As few distinct colours as possible
    n_colours = model.sum(used)
    model.minimize(n_colours)
    model.close()
    started = time.monotonic()
    optimizer.solve()

    status = optimizer.solution.status
    value = n_colours.value if status in (S.OPTIMAL, S.FEASIBLE) else None
    print(f"status {status.name} colours {value} bound {optimizer.solution.get_objective_bound(0)} "
          f"greedy {K} solve {time.monotonic() - started:.2f} s", file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: optimality not proven", file=sys.stderr)
        print(json.dumps({"colour": [next(c for c in range(K) if colour[v][c].value) for v in range(n)]}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no colouring found within the time limit", file=sys.stderr)
        sys.exit(1)
