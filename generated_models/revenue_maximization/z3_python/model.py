# revenue_maximization: a Z3 (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python revenue_maximization.py revenue_maximization.json

import z3


def create_model(instance):
    """Flight legs have limited passenger seats, and packages of itineraries are sold at a
    fixed price with an estimated demand. Choose how many units of each package to sell so
    that the total revenue is as large as possible, with the seats reserved for the sold
    units fitting on every leg."""
    seats = instance["available_seats"]  # seats[l]: passenger seats on flight leg l
    demand = instance["demand"]          # demand[p]: estimated number of units of package p that customers want
    revenue = instance["revenue"]        # revenue[p]: price of one unit of package p
    delta = instance["delta"]            # delta[p][l]: seats on leg l used by one unit of package p
    n_packages = len(demand)
    n_legs = len(seats)

    # sell[p] is the number of units of package p to sell
    sell = [z3.Int(f"s_{p}") for p in range(n_packages)]

    solver = z3.Optimize()

    solver.add(
        # No more units of a package are sold than its demand, and none are sold negatively.
        *[z3.And(sell[p] >= 0, sell[p] <= demand[p]) for p in range(n_packages)],
        # On each leg, the seats reserved for the packages sold do not exceed the seats available.
        *[z3.Sum([delta[p][l] * sell[p] for p in range(n_packages)]) <= seats[l] for l in range(n_legs)],
    )

    # total revenue of the packages sold
    earned = z3.Sum([revenue[p] * sell[p] for p in range(n_packages)])
    solver.maximize(earned)

    return solver, {"packages_to_sell": sell, "max_revenue": earned}


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
