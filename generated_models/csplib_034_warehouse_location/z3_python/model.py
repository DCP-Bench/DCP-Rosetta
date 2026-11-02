# csplib_034_warehouse_location: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

import z3


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

    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [z3.Int(f"supplier_{s}") for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [z3.Bool(f"open_{w}") for w in range(n_suppliers)]
    # the cost to minimise
    total_cost = z3.Int("total_cost")

    # the rules the warehouses and stores must follow
    solver = z3.Optimize()

    # Each store is supplied by one of the candidate warehouses.
    for s in range(n_stores):
        solver.add(z3.And(supplier_assignment[s] >= 0, supplier_assignment[s] < n_suppliers))

    for w in range(n_suppliers):
        # supplied[s] is true when warehouse w supplies store s
        supplied = [supplier_assignment[s] == w for s in range(n_stores)]
        # A warehouse supplies no more stores than its capacity.
        solver.add(z3.AtMost(*supplied, capacity[w]))
        # A warehouse is open exactly when it supplies at least one store, so no store is supplied
        # from a closed warehouse.
        solver.add(open_warehouses[w] == z3.Or(supplied))

    # The supply cost of all stores, each from the warehouse that supplies it.
    supply = z3.Sum([z3.If(supplier_assignment[s] == w, cost_matrix[s][w], 0)
                     for s in range(n_stores) for w in range(n_suppliers)])
    # The total cost is the supply cost plus the maintenance cost of the open warehouses.
    solver.add(total_cost == supply + building_cost * z3.Sum([z3.If(o, 1, 0) for o in open_warehouses]))

    # Minimise the total cost.
    solver.minimize(total_cost)

    return solver, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                    "supplier_assignment": supplier_assignment}


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
