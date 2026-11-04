# csplib_034_warehouse_location: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from hermax.model import Model


def create_model(instance):
    """Warehouse location: choose which candidate warehouses to open so that every store
    is supplied by exactly one open warehouse, no warehouse supplies more stores than its
    capacity, and the total cost (the maintenance costs of the open warehouses plus the
    supply cost of every store) is as small as possible."""
    n_stores = instance["n_stores"]          # number of stores to supply
    n_wh = instance["n_suppliers"]           # number of candidate warehouse locations
    capacity = instance["capacity"]          # capacity[j]: most stores warehouse j can supply
    cost = instance["cost_matrix"]           # cost[i][j]: cost of supplying store i from warehouse j
    building = instance["building_cost"]     # maintenance cost of one open warehouse

    m = Model()

    # open_wh[j] is true when warehouse j is open
    open_wh = m.bool_vector("open", n_wh)
    # x[i][j] is true when store i is supplied by warehouse j
    x = m.bool_matrix("x", n_stores, n_wh)
    # supplier[i] is the index (0-based) of the warehouse that supplies store i
    supplier = m.int_vector("supplier", n_stores, 0, n_wh - 1)

    # Each store is supplied by exactly one warehouse.
    for i in range(n_stores):
        m &= x.row(i).exactly_one()

    # A store can only be supplied by a warehouse that is open.
    for i in range(n_stores):
        for j in range(n_wh):
            m &= x[i][j].implies(open_wh[j])

    # The number of stores a warehouse supplies is at most its capacity.
    for j in range(n_wh):
        m &= (sum(x[i][j] for i in range(n_stores)) <= capacity[j])

    # The supplier output is the warehouse each store is assigned to.
    for i in range(n_stores):
        for j in range(n_wh):
            m &= x[i][j].implies(supplier[i] == j)

    # Total cost: the maintenance cost of the open warehouses plus the supply cost of each store.
    total_cost = sum(building * open_wh[j] for j in range(n_wh)) + \
        sum(cost[i][j] * x[i][j] for i in range(n_stores) for j in range(n_wh))

    # Minimise the total cost.
    m.obj += total_cost

    return m, {"open_warehouses": open_wh, "supplier_assignment": supplier, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
