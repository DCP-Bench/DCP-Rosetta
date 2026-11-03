# csplib_034_warehouse_location: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

import mip


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse can supply at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimise the maintenance cost of the open warehouses plus the
    supply cost of all stores."""
    n_warehouses = instance["n_suppliers"]     # the number of candidate warehouses
    n_stores = instance["n_stores"]            # the number of stores
    building_cost = instance["building_cost"]  # the maintenance cost of an open warehouse
    capacity = instance["capacity"]            # capacity[w]: the most stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]      # cost_matrix[s][w]: the cost of supplying store s from warehouse w

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # open_warehouses[w] is 1 when warehouse w is open, and 0 when it stays closed
    open_warehouses = [model.add_var(f"open_{w}", var_type=mip.BINARY) for w in range(n_warehouses)]
    # serves[s][w] is 1 when warehouse w supplies store s
    serves = [
        [model.add_var(f"x_{s}_{w}", var_type=mip.BINARY) for w in range(n_warehouses)]
        for s in range(n_stores)
    ]

    # Each store is supplied by exactly one warehouse, and that warehouse is open.
    for s in range(n_stores):
        model += mip.xsum(serves[s][w] for w in range(n_warehouses)) == 1
        for w in range(n_warehouses):
            model += serves[s][w] <= open_warehouses[w]

    # A warehouse supplies at most its capacity of stores, and none when it is closed.
    for w in range(n_warehouses):
        model += mip.xsum(serves[s][w] for s in range(n_stores)) <= capacity[w] * open_warehouses[w]

    # supplier_assignment[s] is the number of the warehouse that supplies store s.
    supplier_assignment = []
    for s in range(n_stores):
        a = model.add_var(f"supplier_{s}", lb=0, ub=n_warehouses - 1, var_type=mip.INTEGER)
        model += a == mip.xsum(w * serves[s][w] for w in range(n_warehouses))
        supplier_assignment.append(a)

    # Bounds on the total cost: every store at its cheapest or dearest warehouse, and each
    # warehouse either charged its maintenance cost or not.
    cost_lower = min(0, building_cost) * n_warehouses + sum(min(row) for row in cost_matrix)
    cost_upper = max(0, building_cost) * n_warehouses + sum(max(row) for row in cost_matrix)

    # total_cost is the maintenance cost of the open warehouses plus the supply cost of all stores.
    total_cost = model.add_var("total_cost", lb=cost_lower, ub=cost_upper, var_type=mip.INTEGER)
    model += total_cost == building_cost * mip.xsum(open_warehouses) + mip.xsum(
        cost_matrix[s][w] * serves[s][w] for s in range(n_stores) for w in range(n_warehouses)
    )

    # Minimise the total cost.
    model.objective = total_cost

    return model, {
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }


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
