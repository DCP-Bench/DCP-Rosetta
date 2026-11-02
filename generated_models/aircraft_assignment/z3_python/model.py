# aircraft_assignment: a Z3 (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

import z3


def create_model(instance):
    """Assign aircraft of several types to routes at the lowest total operating cost.
    Each type has a limited fleet, and each route has a passenger demand that must be met."""
    availability = instance["availability"]  # availability[i]: aircraft of type i in the fleet
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i flying route j
    n_types = len(availability)
    n_routes = len(demand)

    # allocation[i][j] is the number of aircraft of type i assigned to route j.
    allocation = [[z3.Int(f"allocation_{i}_{j}") for j in range(n_routes)] for i in range(n_types)]

    solver = z3.Optimize()

    # Each count is between 0 and the largest fleet, since no type needs more aircraft
    # on one route than its whole fleet.
    solver.add([
        z3.And(0 <= allocation[i][j], allocation[i][j] <= max(availability))
        for i in range(n_types)
        for j in range(n_routes)
    ])

    # Each type is assigned no more aircraft, over all routes, than its fleet holds.
    solver.add([z3.Sum(allocation[i]) <= availability[i] for i in range(n_types)])

    # The aircraft flying each route carry at least the passengers that route needs.
    solver.add([
        z3.Sum([capabilities[i][j] * allocation[i][j] for i in range(n_types)]) >= demand[j]
        for j in range(n_routes)
    ])

    # Total operating cost of all assigned aircraft.
    total_cost = z3.Sum([costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)])

    solver.minimize(total_cost)

    return solver, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
