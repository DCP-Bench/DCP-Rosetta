# aircraft_assignment: a CPLEX (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python aircraft_assignment.py aircraft_assignment.json

from docplex.mp.model import Model


def create_model(instance):
    """Aircraft assignment: assign aircraft of several types to routes at the lowest total cost.
    Each type has a limited number of aircraft, each route has a passenger demand that must be
    met, and each (type, route) pair has a seat capacity and a cost per aircraft."""
    availability = instance["availability"]  # availability[a]: aircraft available of type a
    demand = instance["demand"]              # demand[r]: passengers on route r
    capabilities = instance["capabilities"]  # capabilities[a][r]: seats of one type a aircraft on route r
    costs = instance["costs"]                # costs[a][r]: cost of one type a aircraft on route r

    types = range(len(availability))
    routes = range(len(demand))

    model = Model("aircraft_assignment")

    # allocation[a][r] is the number of aircraft of type a assigned to route r; at most
    # max(availability) of them, as no type has more aircraft than that.
    allocation = [[model.integer_var(0, max(availability), name=f"allocation_{a}_{r}")
                   for r in routes] for a in types]

    # Objective: minimize the total cost of the assignment.
    model.minimize(model.sum(costs[a][r] * allocation[a][r] for a in types for r in routes))

    # The aircraft of a type assigned to all routes do not exceed its availability.
    model.add_constraints(model.sum(allocation[a][r] for r in routes) <= availability[a] for a in types)

    # The seats on each route cover its demand.
    model.add_constraints(model.sum(capabilities[a][r] * allocation[a][r] for a in types) >= demand[r]
                          for r in routes)

    return model, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
