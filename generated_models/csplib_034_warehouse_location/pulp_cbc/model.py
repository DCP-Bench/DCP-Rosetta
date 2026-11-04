# csplib_034_warehouse_location: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

import pulp


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse supplies at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimize the building cost of the open warehouses plus the supply
    cost of all stores."""
    n_warehouses = instance["n_suppliers"]     # number of candidate warehouses
    n_stores = instance["n_stores"]            # number of stores
    building_cost = instance["building_cost"]  # cost of opening one warehouse
    capacity = instance["capacity"]            # capacity[w]: most stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]      # cost_matrix[s][w]: cost of supplying store s from warehouse w

    problem = pulp.LpProblem("warehouse_location", pulp.LpMinimize)

    # supplies[s][w] is 1 when warehouse w supplies store s
    supplies = [[pulp.LpVariable(f"supplies_{s}_{w}", cat="Binary") for w in range(n_warehouses)]
                for s in range(n_stores)]
    # open_warehouses[w] is 1 when warehouse w is open
    open_warehouses = [pulp.LpVariable(f"open_{w}", cat="Binary") for w in range(n_warehouses)]

    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [pulp.LpVariable(f"supplier_{s}", 0, n_warehouses - 1, cat="Integer")
                           for s in range(n_stores)]

    # Each store is supplied by exactly one warehouse, and supplier_assignment names that warehouse.
    for s in range(n_stores):
        problem += pulp.lpSum(supplies[s]) == 1
        problem += supplier_assignment[s] == pulp.lpSum(
            w * supplies[s][w] for w in range(n_warehouses))

    for w in range(n_warehouses):
        used = pulp.lpSum(supplies[s][w] for s in range(n_stores))

        # A warehouse supplies no more stores than its capacity.
        problem += used <= capacity[w]

        # A store is supplied only by an open warehouse, and an open warehouse supplies at least one store.
        for s in range(n_stores):
            problem += supplies[s][w] <= open_warehouses[w]
        problem += open_warehouses[w] <= used

    # The most the total cost can be: every warehouse open, and every store at its dearest warehouse.
    max_cost = building_cost * n_warehouses + sum(max(row) for row in cost_matrix)

    # total_cost is the building cost of the open warehouses plus the supply cost of every store.
    total_cost = pulp.LpVariable("total_cost", 0, max_cost, cat="Integer")
    problem += total_cost == (
        building_cost * pulp.lpSum(open_warehouses)
        + pulp.lpSum(cost_matrix[s][w] * supplies[s][w]
                     for s in range(n_stores) for w in range(n_warehouses)))

    # Minimize the total cost.
    problem += total_cost

    return problem, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                     "supplier_assignment": supplier_assignment}


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
