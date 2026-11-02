# aircraft_assignment: an Exact (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

from exact import Exact


def create_model(instance):
    """Assign aircraft of several types to routes at the lowest total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and a cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i on route j
    n_types = len(availability)  # the number of aircraft types
    n_routes = len(demand)       # the number of routes

    solver = Exact()

    # Exact identifies its variables by name.
    # allocation[i][j] is the number of aircraft of type i assigned to route j. No type
    # needs more aircraft on one route than its whole fleet, so the largest fleet bounds it.
    allocation = [[f"allocation_{i}_{j}" for j in range(n_routes)] for i in range(n_types)]
    for row in allocation:
        for name in row:
            solver.addVariable(name, 0, max(availability))

    # The aircraft of each type assigned to all routes add up to no more than the fleet.
    for i in range(n_types):
        solver.addConstraint([(1, name) for name in allocation[i]], False, 0, True, availability[i])

    # The aircraft on each route together carry at least the route's passenger demand.
    for j in range(n_routes):
        solver.addConstraint([(capabilities[i][j], allocation[i][j]) for i in range(n_types)], True, demand[j])

    # The total operating cost of all assigned aircraft.
    objective = [(costs[i][j], allocation[i][j]) for i in range(n_types) for j in range(n_routes)]
    solver.setObjective(objective, minimize=True)

    return solver, {"allocation": allocation}


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
