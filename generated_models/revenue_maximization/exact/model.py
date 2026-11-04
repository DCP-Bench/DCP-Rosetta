# revenue_maximization: an Exact (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python revenue_maximization.py revenue_maximization.json

from exact import Exact


def create_model(instance):
    """Choose how many units of each package to sell, so that the total revenue is as large
    as possible and no flight leg is booked beyond its passenger seats."""
    seats = instance["available_seats"]  # seats[l]: passenger seats on flight leg l
    demand = instance["demand"]          # demand[p]: estimated demand for package p, the most units that can be sold
    revenue = instance["revenue"]        # revenue[p]: price of one unit of package p
    delta = instance["delta"]            # delta[p][l]: seats on leg l that one unit of package p uses
    packages, legs = len(demand), len(seats)

    solver = Exact()

    # Exact identifies its variables by name.
    # sell[p] is the number of units of package p to sell
    sell = [f"sell{p}" for p in range(packages)]
    for p, name in enumerate(sell):
        solver.addVariable(name, 0, demand[p])

    # the seats reserved for the packages sold on each leg do not exceed the seats on that leg
    for j in range(legs):
        solver.addConstraint([(delta[p][j], sell[p]) for p in range(packages) if delta[p][j]],
                             False, 0, True, seats[j])

    # max_revenue is the total price of the packages sold, at most the price of all the demand
    ceiling = sum(revenue[p] * demand[p] for p in range(packages))
    solver.addVariable("max_revenue", 0, ceiling)
    solver.addConstraint(list(zip(revenue, sell)) + [(-1, "max_revenue")], True, 0, True, 0)

    # Earn as much revenue as possible.
    solver.setObjective([(1, "max_revenue")], minimize=False)

    return solver, {"packages_to_sell": sell, "max_revenue": "max_revenue"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
