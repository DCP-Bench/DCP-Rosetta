# aircraft_assignment: a PuLP (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

import pulp


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of flying one aircraft of type i on route j
    n_types = len(availability)
    n_routes = len(demand)

    problem = pulp.LpProblem("aircraft_assignment", pulp.LpMinimize)

    # allocation[i][j]: number of aircraft of type i sent to route j.
    # No type needs more aircraft on one route than its whole fleet, so the
    # fleet size bounds every entry.
    allocation = [[pulp.LpVariable(f"allocation_{i}_{j}", 0, availability[i], cat="Integer")
                   for j in range(n_routes)] for i in range(n_types)]

    # Total operating cost of all flights.
    problem += pulp.lpSum(costs[i][j] * allocation[i][j]
                          for i in range(n_types) for j in range(n_routes))

    # Each type sends no more aircraft than it has.
    for i in range(n_types):
        problem += pulp.lpSum(allocation[i]) <= availability[i]

    # The passengers carried on each route cover its demand.
    for j in range(n_routes):
        problem += pulp.lpSum(capabilities[i][j] * allocation[i][j]
                              for i in range(n_types)) >= demand[j]

    return problem, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
