# revenue_maximization: a Choco-solver (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python revenue_maximization.py revenue_maximization.json

from pychoco.model import Model


def create_model(instance):
    """Flight legs have a limited number of passenger seats, and each package of flight
    itineraries sells at a fixed price with an estimated demand. Choose how many units of
    each package to sell so that the total revenue is as large as possible, with the seats
    reserved for the packages sold staying within the seats on every leg."""
    available_seats = instance["available_seats"]  # available_seats[j]: the passenger seats on flight leg j
    demand = instance["demand"]                    # demand[i]: the estimated demand for package i
    revenue = instance["revenue"]                  # revenue[i]: the price of one unit of package i
    delta = instance["delta"]                      # delta[i][j]: 1 if package i includes flight leg j, else 0
    n_packages = len(demand)
    n_legs = len(available_seats)

    model = Model()

    # packages_to_sell[i]: the number of units of package i to sell, at most its demand
    packages_to_sell = [model.intvar(0, demand[i], name=f"packages_to_sell_{i}") for i in range(n_packages)]

    # The seats reserved on each leg by all packages that include it do not exceed the seats on that leg.
    for j in range(n_legs):
        model.scalar(packages_to_sell, [delta[i][j] for i in range(n_packages)], "<=", available_seats[j]).post()

    # max_revenue: the total revenue from the packages sold
    max_revenue = model.intvar(0, sum(revenue[i] * demand[i] for i in range(n_packages)), name="max_revenue")
    model.scalar(packages_to_sell, revenue, "=", max_revenue).post()

    # Make the revenue as large as possible.
    return model, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}, {"objective": max_revenue, "maximize": True}


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
