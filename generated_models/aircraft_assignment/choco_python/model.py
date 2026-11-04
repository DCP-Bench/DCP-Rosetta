# aircraft_assignment: a Choco-solver (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

from pychoco.model import Model


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i on route j
    n_types = len(availability)  # number of aircraft types
    n_routes = len(demand)       # number of routes

    model = Model()

    # allocation[i][j] is the number of aircraft of type i assigned to route j. No type
    # needs more aircraft on one route than its whole fleet, so the largest fleet bounds
    # every entry.
    allocation = [
        [model.intvar(0, max(availability), name=f"allocation_{i}_{j}") for j in range(n_routes)]
        for i in range(n_types)
    ]

    # A type is not assigned more aircraft than are available.
    for i in range(n_types):
        model.sum(allocation[i], "<=", availability[i]).post()

    # The aircraft on each route together carry at least the route's demand.
    for j in range(n_routes):
        model.scalar([allocation[i][j] for i in range(n_types)],
                     [capabilities[i][j] for i in range(n_types)], ">=", demand[j]).post()

    # Every allocation entry, one per type and route.
    cells = [allocation[i][j] for i in range(n_types) for j in range(n_routes)]
    # Cost of one aircraft for each entry in cells, in the same order.
    cell_costs = [costs[i][j] for i in range(n_types) for j in range(n_routes)]

    # Total operating cost of the assignment, the sum of aircraft count times cost over all types and routes.
    total_cost = model.intvar(0, max(availability) * sum(cell_costs), name="total_cost")
    model.scalar(cells, cell_costs, "=", total_cost).post()

    return model, {"allocation": allocation}, {"objective": total_cost, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
