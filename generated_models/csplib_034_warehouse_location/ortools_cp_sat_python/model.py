# csplib_034_warehouse_location: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse can supply at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimise the maintenance cost of the open warehouses plus the
    supply cost of all stores."""
    n_suppliers = instance["n_suppliers"]      # the number of candidate warehouses
    n_stores = instance["n_stores"]            # the number of stores
    building_cost = instance["building_cost"]  # the maintenance cost of one open warehouse
    capacity = instance["capacity"]            # capacity[w]: the most stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]      # cost_matrix[s][w]: the cost of supplying store s from warehouse w

    model = cp_model.CpModel()

    # serves[s][w] is true when warehouse w supplies store s
    serves = [[model.new_bool_var(f"serves_{s}_{w}") for w in range(n_suppliers)] for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [model.new_bool_var(f"open_{w}") for w in range(n_suppliers)]
    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [model.new_int_var(0, n_suppliers - 1, f"supplier_{s}") for s in range(n_stores)]

    # Each store is supplied by exactly one warehouse, and supplier_assignment names that warehouse.
    for s in range(n_stores):
        model.add_exactly_one(serves[s])
        model.add(supplier_assignment[s] == sum(w * serves[s][w] for w in range(n_suppliers)))

    # A warehouse supplies no more stores than its capacity.
    # A warehouse is open exactly when it supplies at least one store, so no store is supplied
    # from a closed warehouse.
    for w in range(n_suppliers):
        model.add(sum(serves[s][w] for s in range(n_stores)) <= capacity[w])
        for s in range(n_stores):
            model.add_implication(serves[s][w], open_warehouses[w])
        model.add(sum(serves[s][w] for s in range(n_stores)) >= 1).only_enforce_if(open_warehouses[w])

    # max_supply is the cost of supplying every store from its dearest warehouse.
    max_supply = sum(max(row) for row in cost_matrix)
    # total_cost is the maintenance cost of the open warehouses plus the supply cost of all stores.
    # Its upper bound is every warehouse open and every store at its dearest warehouse.
    total_cost = model.new_int_var(0, n_suppliers * building_cost + max_supply, "total_cost")
    model.add(
        total_cost
        == building_cost * sum(open_warehouses)
        + sum(cost_matrix[s][w] * serves[s][w] for s in range(n_stores) for w in range(n_suppliers))
    )

    # Minimise the total cost.
    model.minimize(total_cost)

    return model, {
        "total_cost": total_cost,
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
    }


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
