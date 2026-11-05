"""Travelling salesman: the shortest tour through 6 places, proven optimal.

Boolean arcs with one arc in and one out of every place, and an order variable against sub-tours, give Hexaly
bounds that a list (permutation) decision does not.
"""
from math import hypot

import hexaly.optimizer as hx

PLACES = [(0, 0), (4, 0), (4, 3), (0, 3), (2, 6), (7, 2)]
N = len(PLACES)
# Distances between places, rounded to whole numbers
DIST = [[round(hypot(a[0] - b[0], a[1] - b[1])) for b in PLACES] for a in PLACES]

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 20
    model = optimizer.model

    # arc[i][j] = 1 if the tour goes straight from place i to place j
    arc = [[model.bool() if i != j else 0 for j in range(N)] for i in range(N)]
    for i in range(N):
        # Every place is left once and entered once
        model.constraint(model.sum(arc[i][j] for j in range(N) if j != i) == 1)
        model.constraint(model.sum(arc[j][i] for j in range(N) if j != i) == 1)
    # No separate loops: place 0 comes first, and the order grows along every arc that does not return to it
    order = [model.int(0, N - 1) for _ in range(N)]
    model.constraint(order[0] == 0)
    for i in range(N):
        for j in range(1, N):
            if i != j:
                model.constraint(order[j] >= order[i] + 1 - N * (1 - arc[i][j]))

    length = model.sum(DIST[i][j] * arc[i][j] for i in range(N) for j in range(N) if i != j)
    model.minimize(length)
    model.close()
    optimizer.solve()

    solution = optimizer.solution
    print("Status:", solution.status.name)
    if solution.status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        # Follow the arcs from place 0
        tour, here = [0], 0
        for _ in range(N - 1):
            here = next(j for j in range(N) if j != here and arc[here][j].value)
            tour.append(here)
        print("Tour length:", length.value)
        print("Tour:", tour)
