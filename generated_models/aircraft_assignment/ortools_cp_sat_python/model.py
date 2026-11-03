# aircraft_assignment: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install ortools`):
#   python aircraft_assignment.py aircraft_assignment.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i on route j
    # The number of aircraft types.
    n_types = len(availability)
    # The number of routes.
    n_routes = len(demand)

    model = cp_model.CpModel()

    # allocation[i][j] is the number of aircraft of type i assigned to route j.
    # No type needs more aircraft on one route than its whole fleet, so the
    # largest fleet bounds every entry.
    allocation = [
        [model.new_int_var(0, max(availability), f"allocation_{i}_{j}") for j in range(n_routes)]
        for i in range(n_types)
    ]

    # A type is not assigned more aircraft than are available.
    for row, available in zip(allocation, availability):
        model.add(sum(row) <= available)

    # The aircraft on each route together carry at least the route's demand.
    for j, passengers in enumerate(demand):
        model.add(sum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= passengers)

    # Minimise the total operating cost.
    model.minimize(sum(costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)))

    return model, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
