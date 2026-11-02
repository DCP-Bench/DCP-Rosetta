"""Graph colouring: colour the nodes so that adjacent nodes differ, with as few colours as possible.

Boolean assignment x[v][c] with linear constraints, so that Hexaly can prove the minimum.
Colours are numbered by first use over the nodes, which removes colour permutations: node v
takes a colour no higher than v, and colour c is used only if colour c - 1 is.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    data = json.load(f)
n, edges = data["n_nodes"], data["edges"]
degree = [0] * n
for u, v in edges:
    degree[u] += 1
    degree[v] += 1
k = min(n, max(degree, default=0) + 1)  # greedy colouring never needs more than max degree + 1

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 60
    model = optimizer.model
    x = [[model.bool() for _ in range(k)] for _ in range(n)]  # x[v][c]: node v has colour c
    used = [model.bool() for _ in range(k)]

    # Every node gets exactly one colour, and only a used one
    for v in range(n):
        model.constraint(model.sum(x[v]) == 1)
        for c in range(k):
            model.constraint(x[v][c] <= used[c])
    # The two endpoints of every edge get different colours
    for u, v in edges:
        for c in range(k):
            model.constraint(x[u][c] + x[v][c] <= 1)
    # Colours are numbered by first use: node v takes a colour <= v, colours are used in order
    for v in range(n):
        for c in range(v + 1, k):
            model.constraint(x[v][c] == 0)
    for c in range(1, k):
        model.constraint(used[c] <= used[c - 1])

    # As few colours as possible
    n_colours = model.sum(used)
    model.minimize(n_colours)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    found = status in (S.OPTIMAL, S.FEASIBLE)
    print("status:", status.name, "colours:", n_colours.value if found else None,
          "bound:", optimizer.solution.get_objective_bound(0), file=sys.stderr)
    if found:
        colour = [next(c for c in range(k) if x[v][c].value) for v in range(n)]
        print(json.dumps({"colour": colour}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
