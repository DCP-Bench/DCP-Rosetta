# aircraft_assignment: a Python-MIP (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

import mip


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i on route j
    n_types = len(availability)
    n_routes = len(demand)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # allocation[i][j] is the number of aircraft of type i assigned to route j.
    allocation = [
        [
            model.add_var(name=f"allocation_{i}_{j}", lb=0, ub=availability[i], var_type=mip.INTEGER)
            for j in range(n_routes)
        ]
        for i in range(n_types)
    ]

    # The aircraft of each type, over all routes, do not exceed the number available.
    for i in range(n_types):
        model += mip.xsum(allocation[i][j] for j in range(n_routes)) <= availability[i]

    # On each route, the aircraft carry at least the passengers demanded there.
    for j in range(n_routes):
        model += mip.xsum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= demand[j]

    # Minimise the total operating cost of the assigned aircraft.
    model.objective = mip.xsum(
        costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)
    )

    return model, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
