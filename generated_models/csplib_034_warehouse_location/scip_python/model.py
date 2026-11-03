# csplib_034_warehouse_location: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Warehouse location: a company chooses which candidate warehouses to open
    so that every store is supplied by exactly one open warehouse, no warehouse
    supplies more stores than its capacity, and the total cost is as small as
    possible. The total cost is the maintenance cost of the open warehouses plus
    the supply cost of every store from the warehouse that supplies it.

    Returns the model and the outputs open_warehouses, supplier_assignment and
    total_cost."""
    n_stores = instance["n_stores"]            # the number of stores to supply
    n_warehouses = instance["n_suppliers"]     # the number of candidate warehouse sites (named suppliers in the data)
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse, the same for every warehouse
    capacity = np.array(instance["capacity"])  # capacity[j]: the most stores warehouse j can supply
    cost = np.array(instance["cost_matrix"])   # cost[i][j]: cost of supplying store i from warehouse j

    model = Model("csplib_034_warehouse_location")

    # x[i, j] is 1 when warehouse j supplies store i, and 0 when not. The stores
    # by warehouses form a grid, so x is one matrix of binaries.
    x = model.addMatrixVar((n_stores, n_warehouses), vtype="B", name="x")
    # open_warehouses[j] is 1 when warehouse j is opened, and 0 when it stays closed
    open_warehouses = model.addMatrixVar((n_warehouses,), vtype="B", name="open")

    # Each store is supplied by exactly one warehouse: each row of x sums to 1.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # A store can be supplied only by a warehouse that is open. x[i, j] <= open[j]
    # is linear in two binaries, so it needs no indicator constraint.
    model.addMatrixCons(x <= open_warehouses)
    # Warehouse j supplies at most capacity[j] stores: each column of x sums to
    # at most the capacity from the instance.
    model.addMatrixCons(x.sum(axis=0) <= capacity)

    # The objective: the maintenance cost of the open warehouses plus the supply
    # cost of every store. It is linear, so it is set directly as an expression.
    total_cost = building_cost * open_warehouses.sum() + (cost * x).sum()
    model.setObjective(total_cost, "minimize")

    # supplier_assignment[i] is the 0-based index j of the warehouse with x[i, j] = 1.
    # Since x[i, :] has exactly one 1, the weighted sum sum_j j * x[i, j] is that
    # index, so the sum is the output itself and no extra integer variable is needed.
    supplier_assignment = (x * np.arange(n_warehouses)).sum(axis=1)

    outputs = {
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
