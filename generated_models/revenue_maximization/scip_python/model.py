# revenue_maximization: a SCIP (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python revenue_maximization.py revenue_maximization.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """An airline chooses how many units of each package of flight itineraries to
    sell, so that total revenue is as large as possible, without the sold packages
    needing more passenger seats on a flight leg than that leg has."""
    seats = np.array(instance["available_seats"])  # seats[l]: the passenger seats on flight leg l
    uses = np.array(instance["delta"])  # uses[p][l] is 1 when package p includes flight leg l, else 0
    demand = np.array(instance["demand"])  # demand[p]: the estimated demand for package p, in units
    revenue = np.array(instance["revenue"])  # revenue[p]: the revenue of one unit of package p

    num_packages = len(demand)

    model = Model("revenue_maximization")

    # sell[p] is the number of units of package p to sell: a whole number from 0 up to
    # the estimated demand for p. The lower bound 0 is because units cannot be negative.
    # The upper bound is the estimated demand: the statement gives it as what customers
    # will buy, so it caps the units sold (an assumption read from the statement).
    sell = model.addMatrixVar((num_packages,), vtype="I", lb=0, ub=demand, name="sell")

    # Each unit of a package reserves one passenger seat on every leg the package uses,
    # so the units sold that use a leg add up to no more than the seats on that leg.
    model.addMatrixCons(sell @ uses <= seats)

    # Total revenue of the packages sold: units sold times the revenue of one unit,
    # summed over the packages. Maximise it.
    total_revenue = (revenue * sell).sum()
    model.setObjective(total_revenue, "maximize")

    return model, {"max_revenue": total_revenue, "packages_to_sell": sell}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
