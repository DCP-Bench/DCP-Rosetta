# revenue_maximization: a CPMpy model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python revenue_maximization.py revenue_maximization.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Flight legs have limited passenger seats, and packages of itineraries are sold
    at a given price with an estimated demand. Choose how many units of each package
    to sell so that the revenue is as large as possible, reserving seats for what is sold."""
    seats = instance["available_seats"]         # seats[l]: the passenger capacity of flight leg l
    demand = np.array(instance["demand"])       # demand[p]: the estimated demand for package p
    revenue = np.array(instance["revenue"])     # revenue[p]: the price of one unit of package p
    delta = np.array(instance["delta"])         # delta[p][l]: seats that one unit of package p uses on leg l

    # sell[p] is the number of units of package p that we sell
    sell = cp.intvar(0, max(demand), shape=len(demand), name="packages_to_sell")
    # max_revenue is the total revenue of the packages sold
    earned = cp.sum(sell * revenue)
    max_revenue = cp.intvar(*earned.get_bounds(), name="max_revenue")

    model = cp.Model()
    # On each leg, the seats reserved for the packages sold do not exceed the seats available.
    model.add(sell @ delta <= seats)
    # We sell no more of a package than its demand.
    model.add(sell <= demand)
    # max_revenue holds the revenue of the packages sold.
    model.add(max_revenue == earned)
    # Make the revenue as large as possible.
    model.maximize(max_revenue)

    return model, {"packages_to_sell": sell, "max_revenue": max_revenue}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
