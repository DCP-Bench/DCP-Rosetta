# multi: an Exact (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python multi.py multi.json

from exact import Exact


def create_model(instance):
    """Ship several products from origins to destinations, within each origin's supply of
    each product and each destination's demand for each product, and within the limit on
    the units sent along each origin-destination route, at the lowest total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units of all products sent from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins = len(cost)
    n_destinations = len(cost[0])
    n_products = len(cost[0][0])

    # No shipment is larger than the biggest supply of any origin.
    largest_supply = max(max(row) for row in supply)
    # No total cost is larger than shipping every unit available at the dearest unit cost.
    total_supply = sum(sum(row) for row in supply)
    dearest = max(max(row) for matrix in cost for row in matrix)
    max_total_cost = total_supply * dearest

    solver = Exact()

    # Exact identifies its variables by name.
    # shipped[i][j][p] is the number of units of product p sent from origin i to destination j
    shipped = [[[f"shipped_{i}_{j}_{p}" for p in range(n_products)]
                for j in range(n_destinations)]
               for i in range(n_origins)]
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                solver.addVariable(shipped[i][j][p], 0, largest_supply)

    # An origin sends no more of a product than it has.
    for i in range(n_origins):
        for p in range(n_products):
            solver.addConstraint([(1, shipped[i][j][p]) for j in range(n_destinations)],
                                 False, 0, True, supply[i][p])

    # A destination receives at least its demand of each product.
    for j in range(n_destinations):
        for p in range(n_products):
            solver.addConstraint([(1, shipped[i][j][p]) for i in range(n_origins)],
                                 True, demand[j][p])

    # The units of all products sent along a route stay within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            solver.addConstraint([(1, shipped[i][j][p]) for p in range(n_products)],
                                 False, 0, True, limit[i][j])

    # total_cost is the cost of all shipments.
    solver.addVariable("total_cost", 0, max_total_cost)
    shipping = [(cost[i][j][p], shipped[i][j][p])
                for i in range(n_origins)
                for j in range(n_destinations)
                for p in range(n_products)
                if cost[i][j][p]]
    solver.addConstraint(shipping + [(-1, "total_cost")], True, 0, True, 0)

    # Ship at the lowest total cost.
    solver.setObjective([(1, "total_cost")], minimize=True)

    return solver, {"total_cost": "total_cost"}


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
