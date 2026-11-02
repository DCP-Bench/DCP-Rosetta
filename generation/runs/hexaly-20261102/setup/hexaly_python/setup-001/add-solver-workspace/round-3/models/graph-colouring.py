"""Graph colouring: colour the nodes of an undirected graph so that the endpoints of every
edge get different colours, using as few distinct colours as possible.

Boolean assignment x[v][c] with linear constraints, so that Hexaly's bound can prove the
minimum. The palette size K comes from a greedy colouring; node v may only use colours
0..v and colour c is used only if colour c - 1 is (symmetry breaking).
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
n = data["n_nodes"]
edges = sorted({(min(u, v), max(u, v)) for u, v in data["edges"] if u != v})

if n == 0:
    print(json.dumps({"colour": []}))
    sys.exit()

# Upper bound on the number of colours: a greedy colouring in node order
neighbours = [set() for _ in range(n)]
for u, v in edges:
    neighbours[u].add(v)
    neighbours[v].add(u)
greedy = []
for v in range(n):
    taken = {greedy[u] for u in neighbours[v] if u < v}
    greedy.append(next(c for c in range(n) if c not in taken))
K = max(greedy) + 1

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # OPTIMAL must mean proven exactly
    param.time_limit = 90
    model = optimizer.model
    # x[v][c]: node v gets colour c; node v only gets one of the colours 0..min(v, K-1)
    x = [[model.bool() for _ in range(min(v + 1, K))] for v in range(n)]
    used = [model.bool() for _ in range(K)]  # used[c]: some node has colour c

    # Every node gets exactly one colour
    for v in range(n):
        model.constraint(model.sum(x[v]) == 1)
    # A colour is used by any node that has it
    for v in range(n):
        for c in range(len(x[v])):
            model.constraint(x[v][c] <= used[c])
    # The two endpoints of every edge get different colours
    for u, v in edges:
        for c in range(min(len(x[u]), len(x[v]))):
            model.constraint(x[u][c] + x[v][c] <= used[c])
    # Colours are used in order 0, 1, 2, ...
    for c in range(1, K):
        model.constraint(used[c] <= used[c - 1])

    # As few distinct colours as possible
    colours = model.sum(used)
    model.minimize(colours)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    if status in (S.OPTIMAL, S.FEASIBLE):
        if status != S.OPTIMAL:
            print("warning: best found, optimality not proven", file=sys.stderr)
        colour = [next(c for c in range(len(x[v])) if x[v][c].value) for v in range(n)]
        print(json.dumps({"colour": colour}))
        print(f"status {status.name} colours {colours.value} bound {optimizer.solution.get_objective_bound(0)}",
              file=sys.stderr)
    else:
        print(f"no colouring found: {status.name}", file=sys.stderr)
