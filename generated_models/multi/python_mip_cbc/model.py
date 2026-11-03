# multi: a Python-MIP (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python multi.py multi.json

import mip


def create_model(instance):
    """Multi-commodity transportation: ship each product from the origins to the
    destinations so that every destination gets its demand, no origin ships more of a
    product than it has, and the total shipping cost is as low as possible."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins = len(supply)      # the number of origins
    n_products = len(supply[0])  # the number of products
    n_destinations = len(demand)  # the number of destinations

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][j][p] is the number of units of product p shipped from origin i to destination j.
    # It is at most the smallest of the supply, the demand and the route limit it can use.
    x = [
        [
            [
                model.add_var(
                    name=f"x_{i}_{j}_{p}",
                    lb=0,
                    ub=min(supply[i][p], demand[j][p], limit[i][j]),
                    var_type=mip.INTEGER,
                )
                for p in range(n_products)
            ]
            for j in range(n_destinations)
        ]
        for i in range(n_origins)
    ]

    # An origin ships no more of a product than it has.
    for i in range(n_origins):
        for p in range(n_products):
            model.add_constr(mip.xsum(x[i][j][p] for j in range(n_destinations)) <= supply[i][p])

    # Each destination receives exactly its demand of each product.
    for j in range(n_destinations):
        for p in range(n_products):
            model.add_constr(mip.xsum(x[i][j][p] for i in range(n_origins)) == demand[j][p])

    # The units of all products on a route stay within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            model.add_constr(mip.xsum(x[i][j][p] for p in range(n_products)) <= limit[i][j])

    # total_cost is the shipping cost of all shipments together.
    total_cost = mip.xsum(
        cost[i][j][p] * x[i][j][p]
        for i in range(n_origins)
        for j in range(n_destinations)
        for p in range(n_products)
    )

    # Ship at the lowest total cost.
    model.objective = total_cost

    return model, {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
