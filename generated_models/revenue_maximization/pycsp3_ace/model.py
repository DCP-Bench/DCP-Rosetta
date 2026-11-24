# revenue_maximization: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python revenue_maximization.py revenue_maximization.json

from pycsp3 import *


def create_model(instance):
    """A set of flight legs has a limited passenger capacity. Itineraries are sold as packages,
    each at a given price, with an estimated demand. Choose how many units of each package to
    sell, at most its demand, so that the seats on every leg are not exceeded.
    Maximise the total revenue."""
    available_seats = instance["available_seats"]  # available_seats[l] is the seat capacity of flight leg l
    demand = instance["demand"]                    # demand[p] is the estimated demand for package p
    revenue = instance["revenue"]                  # revenue[p] is the price of one unit of package p
    uses_leg = instance["delta"]                   # uses_leg[p][l] is 1 when package p includes flight leg l
    n_packages = len(demand)
    n_legs = len(available_seats)

    # packages_to_sell[p] is the number of units of package p to sell, from 0 up to its demand.
    packages_to_sell = VarArray(size=n_packages, dom=lambda p: range(demand[p] + 1))

    # The revenue is at most the sum of revenue[p] * demand[p] over the packages, taking the
    # prices and demands as non-negative.
    max_revenue_bound = sum(revenue[p] * demand[p] for p in range(n_packages))
    # max_revenue is the total revenue from the units sold.
    max_revenue = Var(dom=range(max_revenue_bound + 1))

    satisfy(
        # Each leg carries no more passengers than it has seats: the units sold of every package
        # that includes the leg add up to at most its seats.
        [Sum(packages_to_sell[p] for p in range(n_packages) if uses_leg[p][l] == 1) <= available_seats[l]
         for l in range(n_legs)],
        # The total revenue is the price times the units sold, summed over the packages.
        max_revenue == Sum(revenue[p] * packages_to_sell[p] for p in range(n_packages)),
    )

    # The total revenue is maximised.
    maximize(max_revenue)

    return {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("packages_to_sell", "=", values(outputs["packages_to_sell"]))
        print("max_revenue", "=", value(outputs["max_revenue"]))
    else:
        print("No solution:", status())
