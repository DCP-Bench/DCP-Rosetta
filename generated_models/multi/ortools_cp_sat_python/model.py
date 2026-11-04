# multi: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install ortools`):
#   python multi.py multi.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Multi-commodity transportation: ship products from origins to destinations,
    respecting each origin's supply and each destination's demand, to minimise
    the total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    origins, destinations, products = len(cost), len(cost[0]), len(cost[0][0])  # number of origins, destinations and products

    model = cp_model.CpModel()

    # The largest supply of any origin caps every shipment.
    largest_supply = max(max(row) for row in supply)
    # ship[i][j][p]: units of product p shipped from origin i to destination j
    ship = [[[model.new_int_var(0, largest_supply, f"ship_{i}_{j}_{p}")
              for p in range(products)]
             for j in range(destinations)]
            for i in range(origins)]

    # total_supply: all units available at the origins; dearest: the highest unit shipping cost
    total_supply = sum(sum(row) for row in supply)
    dearest = max(max(row) for matrix in cost for row in matrix)
    # total_cost: the cost of all shipments, at most every unit shipped at the dearest unit cost
    total_cost = model.new_int_var(0, total_supply * dearest, "total_cost")

    # An origin ships no more of each product than its supply.
    for i in range(origins):
        for p in range(products):
            model.add(sum(ship[i][j][p] for j in range(destinations)) <= supply[i][p])

    # A destination receives at least its demand of each product.
    for j in range(destinations):
        for p in range(products):
            model.add(sum(ship[i][j][p] for i in range(origins)) >= demand[j][p])

    # Units of all products sent from an origin to a destination stay within the limit.
    for i in range(origins):
        for j in range(destinations):
            model.add(sum(ship[i][j]) <= limit[i][j])

    # The total cost is the units shipped times their unit cost, summed over all routes.
    model.add(total_cost == sum(cost[i][j][p] * ship[i][j][p]
                                for i in range(origins)
                                for j in range(destinations)
                                for p in range(products)))

    # Ship at the lowest total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
