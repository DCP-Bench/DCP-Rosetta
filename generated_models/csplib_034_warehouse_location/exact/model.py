# csplib_034_warehouse_location: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from exact import Exact


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

    solver = Exact()

    # Exact identifies its variables by name.
    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [f"supplier_{s}" for s in range(n_stores)]
    # serves[s][w] is 1 when warehouse w supplies store s
    serves = [[f"serves_{s}_{w}" for w in range(n_suppliers)] for s in range(n_stores)]
    # open_warehouses[w] is 1 when warehouse w is open
    open_warehouses = [f"open_{w}" for w in range(n_suppliers)]
    for w in range(n_suppliers):
        solver.addVariable(open_warehouses[w], 0, 1)
    for s in range(n_stores):
        solver.addVariable(supplier_assignment[s], 0, n_suppliers - 1)
        for name in serves[s]:
            solver.addVariable(name, 0, 1)
        # each store is supplied by exactly one warehouse, and supplier_assignment names that warehouse
        solver.addConstraint([(1, name) for name in serves[s]], True, 1, True, 1)
        solver.addConstraint([(w, serves[s][w]) for w in range(1, n_suppliers)] + [(-1, supplier_assignment[s])],
                             True, 0, True, 0)

    for w in range(n_suppliers):
        # the stores that warehouse w supplies
        column = [(1, serves[s][w]) for s in range(n_stores)]
        # warehouse w supplies at most capacity[w] stores
        solver.addConstraint(column, False, 0, True, capacity[w])
        # warehouse w is open exactly when it supplies at least one store, so no store is supplied
        # from a closed warehouse
        solver.addConstraint(column + [(-n_stores, open_warehouses[w])], False, 0, True, 0)
        solver.addConstraint(column + [(-1, open_warehouses[w])], True, 0)

    # total_cost is the maintenance cost of the open warehouses plus the supply cost of all stores.
    # Its upper bound is every warehouse open and every store at its most expensive warehouse.
    total_cost = "total_cost"
    solver.addVariable(total_cost, 0, sum(max(row) for row in cost_matrix) + n_suppliers * building_cost)
    # the supply costs of the stores and the maintenance costs of the open warehouses that add up to total_cost
    terms = [(cost_matrix[s][w], serves[s][w]) for s in range(n_stores) for w in range(n_suppliers)]
    terms += [(building_cost, name) for name in open_warehouses]
    solver.addConstraint(terms + [(-1, total_cost)], True, 0, True, 0)

    solver.setObjective(terms, minimize=True)

    return solver, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                     "supplier_assignment": supplier_assignment}


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
