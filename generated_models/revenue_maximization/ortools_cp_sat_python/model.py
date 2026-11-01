# revenue_maximization: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install ortools`):
#   python revenue_maximization.py revenue_maximization.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Flight packages are sold at a fixed price, each with an estimated demand. Choose how
    many units of each package to sell so that the total revenue is as large as possible,
    while the seats reserved on each leg stay within the seats available."""
    seats = instance["available_seats"]  # seats[l]: the passenger seats on leg l
    demand = instance["demand"]          # demand[p]: the estimated demand for package p
    revenue = instance["revenue"]        # revenue[p]: the price of one unit of package p
    delta = instance["delta"]            # delta[p][l]: seats on leg l used by one unit of package p

    model = cp_model.CpModel()

    # sell[p] is the number of units of package p to sell
    sell = [model.new_int_var(0, demand[p], f"s_{p}") for p in range(len(demand))]

    # On each leg, the seats reserved for the packages sold do not exceed the seats available.
    for leg, available in enumerate(seats):
        model.add(sum(row[leg] * s for row, s in zip(delta, sell)) <= available)

    # max_revenue is the total price of the packages sold
    max_revenue = sum(r * s for r, s in zip(revenue, sell))
    # Make the revenue as large as possible.
    model.maximize(max_revenue)

    return model, {"packages_to_sell": sell, "max_revenue": max_revenue}


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
