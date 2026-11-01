# csplib_034_warehouse_location: a CPMpy model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse can supply at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimise the maintenance cost of the open warehouses plus the
    supply cost of all stores."""
    n_warehouses = instance["n_suppliers"]     # the number of candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # the maintenance cost of each open warehouse
    capacity = instance["capacity"]            # capacity[w]: the most stores warehouse w can supply
    cost_matrix = np.array(instance["cost_matrix"])  # cost_matrix[s][w]: cost of supplying store s from warehouse w

    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = cp.intvar(0, n_warehouses - 1, shape=n_stores, name="supplier_assignment")
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = cp.boolvar(shape=n_warehouses, name="open_warehouses")
    # total_cost is the maintenance cost plus the supply cost; at most every store at its most
    # expensive warehouse plus every warehouse open
    max_cost = int(cost_matrix.max(axis=1).sum()) + n_warehouses * building_cost
    total_cost = cp.intvar(0, max_cost, name="total_cost")

    model = cp.Model()

    # A warehouse supplies no more stores than its capacity.
    for w in range(n_warehouses):
        model.add(cp.Count(supplier_assignment, w) <= capacity[w])

    # A warehouse is open exactly when it supplies at least one store. This also means that
    # no store is supplied from a closed warehouse.
    for w in range(n_warehouses):
        model.add(open_warehouses[w] == (cp.Count(supplier_assignment, w) > 0))

    # The total cost is the supply cost of every store from its warehouse plus the maintenance
    # cost of every open warehouse. The matrix is wrapped so a variable can index it.
    supply_costs = cp.cpm_array(cost_matrix)
    supply_cost = cp.sum([supply_costs[s, supplier_assignment[s]] for s in range(n_stores)])
    model.add(total_cost == supply_cost + cp.sum(open_warehouses) * building_cost)

    # Minimise the total cost.
    model.minimize(total_cost)

    return model, {"open_warehouses": open_warehouses,
                   "supplier_assignment": supplier_assignment,
                   "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
