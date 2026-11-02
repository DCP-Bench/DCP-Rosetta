"""Graph colouring: colour the nodes so that the two endpoints of every edge differ, using as
few distinct colours as possible.

A Boolean per node and colour, a Boolean per colour for "this colour is used", linear
constraints, so Hexaly's bound can prove the minimum (gap limit 0). The number of colours
offered is the count of a greedy colouring, an upper bound on the optimum.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
n = data["n_nodes"]
edges = sorted({(min(a, b), max(a, b)) for a, b in data["edges"]})

if n == 0:
    print(json.dumps({"colour": []}))
    sys.exit(0)

# Greedy colouring in node order: an upper bound on the number of colours needed
neighbours = [set() for _ in range(n)]
for a, b in edges:
    neighbours[a].add(b)
    neighbours[b].add(a)
greedy = []
for v in range(n):
    taken = {greedy[u] for u in neighbours[v] if u < v}
    greedy.append(next(c for c in range(n) if c not in taken))
K = max(greedy) + 1

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 90
    model = optimizer.model
    x = [[model.bool() for _ in range(K)] for _ in range(n)]  # x[v][c]: node v gets colour c
    used = [model.bool() for _ in range(K)]  # used[c]: some node gets colour c

    # Every node gets exactly one colour
    for v in range(n):
        model.constraint(model.sum(x[v]) == 1)

    # The two endpoints of an edge get different colours, and a colour given is a colour used
    for a, b in edges:
        for c in range(K):
            model.constraint(x[a][c] + x[b][c] <= used[c])
    for v in range(n):
        for c in range(K):
            model.constraint(x[v][c] <= used[c])

    # Symmetry: colours are numbered in order of first use, so node v takes a colour <= v
    # and the used colours are 0 .. k-1
    for v in range(n):
        for c in range(v + 1, K):
            model.constraint(x[v][c] == 0)
    for c in range(K - 1):
        model.constraint(used[c + 1] <= used[c])

    # As few colours as possible
    n_colours = model.sum(used)
    model.minimize(n_colours)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("status:", status.name, file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        colour = [next(c for c in range(K) if x[v][c].value) for v in range(n)]
        out = {"colour": colour}
        if status == S.FEASIBLE:
            out["status"] = "feasible"  # best found, not proven optimal
        print(json.dumps(out))
        print("colours:", n_colours.value, "bound:", optimizer.solution.get_objective_bound(0),
              file=sys.stderr)
