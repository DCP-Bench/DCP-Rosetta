# multi: a SCIP (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python multi.py multi.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A multi-commodity transportation problem: ship every product from the origins
    to the destinations at the least total cost, without an origin sending out more of
    a product than its supply, without a destination receiving other than its demand
    of each product, and without a lane carrying more, over all products, than its limit."""
    supply = np.array(instance["supply"])  # supply[i][p]: units of product p that origin i can send
    demand = np.array(instance["demand"])  # demand[j][p]: units of product p that destination j needs
    limit = np.array(instance["limit"])    # limit[i][j]: most units, all products together, on the lane from origin i to destination j
    cost = np.array(instance["cost"])      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins, n_destinations, n_products = cost.shape

    model = Model("multi")

    # ship[i, j, p] is the number of units of product p that origin i sends to destination j.
    # Its upper bound is the smallest of the three amounts that cap it on its own: supply[i][p],
    # demand[j][p] and limit[i][j]. Each of those is a constraint below with nonnegative
    # shipments, so the bound removes no feasible plan.
    ship_ub = np.minimum(np.minimum(supply[:, None, :], demand[None, :, :]), limit[:, :, None])
    ship = model.addMatrixVar((n_origins, n_destinations, n_products), vtype="I", lb=0, ub=ship_ub, name="ship")

    # total_cost is the total shipping cost of the plan, and the objective. It is a variable
    # of its own, equal to the cost sum, because the runner blocks the variables an output is
    # built from when it looks for another solution: blocking the shipments would rule out
    # every plan, while blocking total_cost rules out only that cost.
    # Its upper bound: every unit shipped costs at most the largest entry of cost, and the
    # demand constraints make exactly sum(demand) units shipped.
    total_cost = model.addVar(vtype="I", lb=0, ub=int(cost.max() * demand.sum()), name="total_cost")
    model.addCons(total_cost == (cost * ship).sum())

    # Each origin sends out no more of each product than its supply of that product.
    model.addMatrixCons(ship.sum(axis=1) <= supply)

    # Each destination receives exactly its demand of each product.
    model.addMatrixCons(ship.sum(axis=0) == demand)

    # The shipments on each lane, over all products, stay within the lane's limit.
    model.addMatrixCons(ship.sum(axis=2) <= limit)

    # Minimise the total shipping cost.
    model.setObjective(total_cost, "minimize")

    return model, {"total_cost": total_cost}


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
