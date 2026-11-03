# multi: a Z3 (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python multi.py multi.json

import z3


def create_model(instance):
    """Multi-commodity transportation: ship products from origins to destinations,
    respecting each origin's supply and each destination's demand, to minimise
    the total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins, n_destinations, n_products = len(supply), len(demand), len(supply[0])  # number of origins, destinations and products

    # No shipment is larger than the biggest supply of any origin.
    largest_supply = max(max(row) for row in supply)
    # Every unit shipped costs at most the dearest unit cost.
    dearest = max(max(row) for matrix in cost for row in matrix)
    # All units available at the origins.
    total_supply = sum(sum(row) for row in supply)

    # ship[i][j][p]: units of product p shipped from origin i to destination j
    ship = [[[z3.Int(f"ship_{i}_{j}_{p}") for p in range(n_products)]
             for j in range(n_destinations)]
            for i in range(n_origins)]
    # total_cost: the total cost of all shipments
    total_cost = z3.Int("total_cost")

    solver = z3.Optimize()

    # Shipments are whole numbers from 0 up to the largest supply.
    solver.add([v >= 0 for row in ship for lane in row for v in lane])
    solver.add([v <= largest_supply for row in ship for lane in row for v in lane])
    # The total cost is between 0 and all supply shipped at the dearest unit cost.
    solver.add(total_cost >= 0, total_cost <= total_supply * dearest)

    # An origin ships no more of each product than its supply.
    solver.add([z3.Sum([ship[i][j][p] for j in range(n_destinations)]) <= supply[i][p]
                for i in range(n_origins) for p in range(n_products)])

    # A destination receives at least its demand of each product.
    solver.add([z3.Sum([ship[i][j][p] for i in range(n_origins)]) >= demand[j][p]
                for j in range(n_destinations) for p in range(n_products)])

    # Units of all products sent from an origin to a destination stay within the limit.
    solver.add([z3.Sum(ship[i][j]) <= limit[i][j]
                for i in range(n_origins) for j in range(n_destinations)])

    # The total cost is the units shipped times their unit cost, summed over all routes.
    solver.add(total_cost == z3.Sum([cost[i][j][p] * ship[i][j][p]
                                     for i in range(n_origins)
                                     for j in range(n_destinations)
                                     for p in range(n_products)]))

    # Ship at the lowest total cost.
    solver.minimize(total_cost)

    return solver, {"total_cost": total_cost}


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
