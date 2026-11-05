# tsp: a Paramita (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python tsp.py tsp.json

import math

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, Or, add_to_weighted_container, to_cnf


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city. The distance between two cities is their Euclidean distance rounded
    to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n_cities = len(locations)          # the number of cities

    # dist[i][j]: the distance between city i and city j
    dist = [[round(math.dist(a, b)) for b in locations] for a in locations]

    # Subtract the cheapest departure from each city, then the cheapest arrival at each
    # city. Every route departs from each city once and arrives at each city once, so
    # every route is shorter by the same total, which is added back at the end.
    cost = [row[:] for row in dist]
    shift = 0
    for i in range(n_cities):
        cheapest = min(cost[i][j] for j in range(n_cities) if j != i)
        shift += cheapest
        for j in range(n_cities):
            if j != i:
                cost[i][j] -= cheapest
    for j in range(n_cities):
        cheapest = min(cost[i][j] for i in range(n_cities) if i != j)
        shift += cheapest
        for i in range(n_cities):
            if i != j:
                cost[i][j] -= cheapest

    # succ[(i, j)] is true when the route goes directly from city i to city j
    succ = {(i, j): Bool(f"succ_{i}_{j}") for i in range(n_cities) for j in range(n_cities) if i != j}
    # at_least[i][k] is true when city i is at position k or later on the route, counting
    # the origin city as position 0; k runs from 1 to n_cities - 1
    at_least = [{k: Bool(f"ge_{i}_{k}") for k in range(1, n_cities)} for i in range(n_cities)]

    constraints = []

    # The origin city is the first city of the route.
    constraints += [~at_least[0][k] for k in range(1, n_cities)]

    # A city at position k + 1 or later is also at position k or later.
    for i in range(n_cities):
        constraints += [Or([~at_least[i][k + 1], at_least[i][k]]) for k in range(1, n_cities - 1)]

    # Each city has exactly one city after it on the route.
    constraints += [sum(succ[i, j] for j in range(n_cities) if j != i) == 1 for i in range(n_cities)]
    # Each city has exactly one city before it on the route.
    constraints += [sum(succ[i, j] for i in range(n_cities) if i != j) == 1 for j in range(n_cities)]
    # Two cities never follow each other directly.
    constraints += [Or([~succ[i, j], ~succ[j, i]]) for i in range(n_cities) for j in range(i + 1, n_cities)]

    # The route is one closed loop through all the cities. If city j follows city i and j
    # is not the origin, j is one position later than i. The city in the last position is
    # followed only by the origin.
    for i in range(n_cities):
        for j in range(1, n_cities):
            if i == j:
                continue
            constraints.append(Or([~succ[i, j], at_least[j][1]]))
            for k in range(1, n_cities - 1):
                constraints.append(Or([~succ[i, j], ~at_least[i][k], at_least[j][k + 1]]))
            constraints.append(Or([~succ[i, j], ~at_least[i][n_cities - 1]]))

    # travel_distance: the length of the route. The shift is added back to the shifted
    # distances of the arcs taken.
    travel_distance = shift + sum(cost[i][j] * succ[i, j] for i in range(n_cities)
                                  for j in range(n_cities) if i != j and cost[i][j] > 0)

    # Minimise the length of the route.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-travel_distance, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the travel distance, minimised (its negation
    # is what the soft clauses maximise).
    return (formula, pool), {"travel_distance": travel_distance}, travel_distance


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
