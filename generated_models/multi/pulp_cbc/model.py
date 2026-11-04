# multi: a PuLP (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python multi.py multi.json

import pulp


def create_model(instance):
    """Multi-commodity transportation: ship several products from origins to destinations,
    within each origin's supply and each destination's demand, at the lowest total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    origins = len(supply)        # the number of origins
    destinations = len(demand)   # the number of destinations
    products = len(supply[0])    # the number of products

    # no origin ships more of a product than its largest supply
    largest_supply = max(max(row) for row in supply)
    # all units available at the origins
    total_supply = sum(sum(row) for row in supply)
    # the highest cost of shipping one unit
    dearest = max(max(row) for matrix in cost for row in matrix)

    problem = pulp.LpProblem("multi", pulp.LpMinimize)

    # ship[i][j][p] is the number of units of product p shipped from origin i to destination j
    ship = [[[pulp.LpVariable(f"ship_{i}_{j}_{p}", 0, largest_supply, cat="Integer")
              for p in range(products)]
             for j in range(destinations)]
            for i in range(origins)]

    # total_cost is the cost of all shipments, at most every unit shipped at the highest unit cost
    total_cost = pulp.LpVariable("total_cost", 0, total_supply * dearest, cat="Integer")

    # An origin ships no more of each product than its supply.
    for i in range(origins):
        for p in range(products):
            problem += pulp.lpSum(ship[i][j][p] for j in range(destinations)) <= supply[i][p]

    # Each destination receives at least its demand of each product.
    for j in range(destinations):
        for p in range(products):
            problem += pulp.lpSum(ship[i][j][p] for i in range(origins)) >= demand[j][p]

    # The units of all products sent from an origin to a destination stay within the limit.
    for i in range(origins):
        for j in range(destinations):
            problem += pulp.lpSum(ship[i][j][p] for p in range(products)) <= limit[i][j]

    # The total cost is the units shipped times their unit cost, summed over all routes.
    problem += total_cost == pulp.lpSum(
        cost[i][j][p] * ship[i][j][p]
        for i in range(origins) for j in range(destinations) for p in range(products))

    # Ship at the lowest total cost.
    problem += total_cost

    return problem, {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
