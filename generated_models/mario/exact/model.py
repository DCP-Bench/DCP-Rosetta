# mario: an Exact (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python mario.py mario.json

from exact import Exact


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's house
    and ends at Luigi's house, driving between houses on limited fuel."""
    n = instance["nHouses"]  # number of houses
    mario = instance["marioHouse"]  # the house Mario starts from
    luigi = instance["luigiHouse"]  # the house Mario ends at
    fuel_limit = instance["fuelLimit"]  # the most fuel Mario has for the whole route
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j]: fuel used to drive from house i to house j
    gold = instance["goldInHouse"]  # gold in each house

    solver = Exact()

    # Exact identifies its variables by name.
    # succ[i][j] is 1 when the route drives straight from house i to house j, and 0 when not.
    # succ[i][i] is 1 when house i is not on the route.
    succ = [[f"succ_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            # the last drive of the route, from Luigi's house, goes back to Mario's house
            lower = 1 if (i, j) == (luigi, mario) else 0
            solver.addVariable(succ[i][j], lower, 1)
    for i in range(n):
        # each house has exactly one successor
        solver.addConstraint([(1, succ[i][j]) for j in range(n)], True, 1, True, 1)
    for j in range(n):
        # each house is the successor of exactly one house
        solver.addConstraint([(1, succ[i][j]) for i in range(n)], True, 1, True, 1)

    # s[i] is the house that follows house i on the route, and i itself when house i is not on it
    s = [f"s_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(s[i], 0, n - 1)
        solver.addConstraint([(j, succ[i][j]) for j in range(1, n)] + [(-1, s[i])], True, 0, True, 0)

    # order[i] is the place of house i along the route, counting Mario's house as 1
    order = [f"order_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(order[i], 1, 1 if i == mario else n)

    for i in range(n):
        for j in range(n):
            # a drive from house i to house j moves one place further along the route,
            # except the drive into Mario's house, which closes the route
            if j != i and j != mario:
                solver.addConstraint([(1, order[j]), (-1, order[i]), (-n, succ[i][j])], True, 1 - n)
                solver.addConstraint([(1, order[j]), (-1, order[i]), (n, succ[i][j])], False, 0, True, 1 + n)
        # a house off the route comes after Luigi's house in the places
        solver.addConstraint([(1, order[i]), (-1, order[luigi]), (-n, succ[i][i])], True, 1 - n)

    # the drives Mario takes use no more fuel than the limit; a drive that uses no fuel is left out
    fuel = [(arc_fuel[i][j], succ[i][j]) for i in range(n) for j in range(n) if arc_fuel[i][j]]
    solver.addConstraint(fuel, False, 0, True, fuel_limit)

    # visited[i] is 1 when house i is on the route, and 0 when it is not
    visited = [f"visited_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(visited[i], 0, 1)
        # a house is on the route exactly when it is not its own successor
        solver.addConstraint([(1, visited[i]), (1, succ[i][i])], True, 1, True, 1)

    # collect as much gold as possible from the houses on the route
    solver.setObjective([(gold[i], visited[i]) for i in range(n) if gold[i]], minimize=False)

    return solver, {"s": s}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
