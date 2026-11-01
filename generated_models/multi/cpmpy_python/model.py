# multi: a CPMpy model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python multi.py multi.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Multi-commodity transportation: ship products from origins to destinations,
    respecting each origin's supply and each destination's demand, to minimise
    the total shipping cost."""
    supply = np.array(instance["supply"])  # supply[i][p]: units of product p available at origin i
    demand = np.array(instance["demand"])  # demand[j][p]: units of product p needed at destination j
    limit = np.array(instance["limit"])    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = np.array(instance["cost"])      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    origins, destinations, products = cost.shape

    # ship[i, j, p] is the number of units of product p shipped from origin i to destination j;
    # no origin has more than its largest supply of any product to send.
    ship = cp.intvar(0, supply.max(), shape=(origins, destinations, products), name="ship")

    # total_cost is the total cost of all shipments; it is at most the whole supply at the dearest price.
    total_cost = cp.intvar(0, supply.sum() * cost.max(), name="total_cost")

    model = cp.Model()
    # An origin ships no more of a product than its supply.
    model.add(ship.sum(axis=1) <= supply)
    # A destination receives at least its demand of each product.
    model.add(ship.sum(axis=0) >= demand)
    # The units, over all products, from an origin to a destination stay within the limit.
    model.add(ship.sum(axis=2) <= limit)
    # The total cost is the sum of units shipped times their unit cost.
    model.add(total_cost == cp.sum(ship * cost))
    # Ship at the lowest total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost}


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
