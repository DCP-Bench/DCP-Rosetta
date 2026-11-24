# revenue_maximization: a CPLEX (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python revenue_maximization.py revenue_maximization.json

from docplex.mp.model import Model


def create_model(instance):
    """Choose how many units of each flight-itinerary package to sell, up to its estimated demand,
    reserving seats on the flight legs within their capacity, so that the total revenue is maximal."""
    seats = instance["available_seats"]  # seats[j]: the passenger capacity of flight leg j
    demand = instance["demand"]          # demand[i]: the estimated demand for package i
    revenue = instance["revenue"]        # revenue[i]: the price of one unit of package i
    uses = instance["delta"]             # uses[i][j] is 1 if package i flies on leg j
    packages = range(len(demand))
    legs = range(len(seats))

    model = Model("revenue_maximization")

    # packages_to_sell[i] is how many units of package i are sold; selling no more
    # than the estimated demand is the variable's upper bound.
    packages_to_sell = [model.integer_var(0, demand[i], name=f"packages_to_sell_{i}") for i in packages]

    # The packages sold fit into the seats available on every flight leg.
    model.add_constraints(model.sum(uses[i][j] * packages_to_sell[i] for i in packages) <= seats[j]
                          for j in legs)

    # Maximise the revenue of the packages sold.
    max_revenue = model.dot(packages_to_sell, revenue)
    model.maximize(max_revenue)

    return model, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}


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
