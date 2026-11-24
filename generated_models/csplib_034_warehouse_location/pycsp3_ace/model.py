# csplib_034_warehouse_location: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from pycsp3 import *


def create_model(instance):
    """A company decides which warehouses to open, from a set of candidate locations, to supply a
    set of stores. Each warehouse has a fixed maintenance cost and a capacity limiting the number of
    stores it can supply. Each store must be supplied by exactly one open warehouse, at a supply cost
    that depends on the store and the warehouse. Minimise the total cost: the maintenance costs of the
    opened warehouses plus the supply costs of all stores."""
    n_suppliers = instance["n_suppliers"]        # the number of candidate warehouses
    n_stores = instance["n_stores"]              # the number of stores to supply
    building_cost = instance["building_cost"]    # the fixed maintenance cost of each opened warehouse
    capacity = instance["capacity"]              # capacity[w] is the most stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]        # cost_matrix[s][w] is the cost of supplying store s from warehouse w

    # The costs are taken as non-negative, so every supply cost lies from 0 to the dearest cost in cost_matrix.
    max_cost = max(max(row) for row in cost_matrix)

    # open_warehouses[w] is 1 when warehouse w is opened
    open_warehouses = VarArray(size=n_suppliers, dom={0, 1})
    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = VarArray(size=n_stores, dom=range(n_suppliers))
    # supply_cost[s] is the cost of supplying store s from its assigned warehouse
    supply_cost = VarArray(size=n_stores, dom=range(max_cost + 1))
    # total_cost is the total cost of the opened warehouses and the supply of the stores. The upper bound
    # is taken as every warehouse opened and every store supplied at the dearest cost (costs non-negative).
    max_total_cost = building_cost * n_suppliers + n_stores * max_cost
    total_cost = Var(dom=range(max_total_cost + 1))

    satisfy(
        # Each store is supplied by a warehouse that is open.
        [open_warehouses[supplier_assignment[s]] == 1 for s in range(n_stores)],
        # Each warehouse supplies at most its capacity of stores.
        [Count(supplier_assignment, value=w) <= capacity[w] for w in range(n_suppliers)],
        # The supply cost of each store is its entry in cost_matrix for the warehouse that supplies it
        # (a Table, since a Python list cannot be indexed by a variable).
        [
            Table(
                scope=[supplier_assignment[s], supply_cost[s]],
                supports=[(w, cost_matrix[s][w]) for w in range(n_suppliers)],
            )
            for s in range(n_stores)
        ],
        # The total cost is the maintenance of the opened warehouses plus the supply cost of every store.
        total_cost == building_cost * Sum(open_warehouses) + Sum(supply_cost),
    )

    # Minimise the total cost.
    minimize(total_cost)

    return {
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("open_warehouses", "=", values(outputs["open_warehouses"]))
        print("supplier_assignment", "=", values(outputs["supplier_assignment"]))
        print("total_cost", "=", value(outputs["total_cost"]))
    else:
        print("No solution:", status())
