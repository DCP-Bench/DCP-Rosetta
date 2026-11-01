# csplib_034_warehouse_location: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from pychoco.model import Model


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

    model = Model()

    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [model.intvar(0, n_suppliers - 1, name=f"supplier_{s}")
                           for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [model.boolvar(name=f"open_{w}") for w in range(n_suppliers)]

    for w in range(n_suppliers):
        # n_supplied is the number of stores warehouse w supplies
        n_supplied = model.intvar(0, min(capacity[w], n_stores), name=f"n_supplied_{w}")
        model.count(w, supplier_assignment, n_supplied).post()
        # A warehouse is open exactly when it supplies at least one store. So no store is
        # supplied from a closed warehouse.
        model.arithm(n_supplied, ">", 0).reify_with(open_warehouses[w])

    # supply_costs[s] is the cost of supplying store s from its chosen warehouse, read from the
    # row of the cost matrix for store s
    supply_costs = []
    for s in range(n_stores):
        supply_cost = model.intvar(min(cost_matrix[s]), max(cost_matrix[s]), name=f"supply_cost_{s}")
        model.element(supply_cost, cost_matrix[s], supplier_assignment[s]).post()
        supply_costs.append(supply_cost)

    # total_cost is the supply cost of all stores plus the maintenance cost of the open warehouses
    total_cost = model.intvar(0, sum(max(row) for row in cost_matrix) + n_suppliers * building_cost,
                              name="total_cost")
    model.scalar(supply_costs + open_warehouses,
                 [1] * n_stores + [building_cost] * n_suppliers, "=", total_cost).post()

    # Minimise the total cost.
    return (
        model,
        {"total_cost": total_cost, "open_warehouses": open_warehouses,
         "supplier_assignment": supplier_assignment},
        {"objective": total_cost, "maximize": False},
    )


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
