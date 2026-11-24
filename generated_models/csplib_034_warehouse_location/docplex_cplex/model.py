# csplib_034_warehouse_location: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from docplex.mp.model import Model


def create_model(instance):
    """Warehouse location: assign every store to one warehouse within the warehouses' capacities,
    paying the supply cost of each assignment plus a building cost for every warehouse that
    supplies at least one store, at the least total cost."""
    n_suppliers = instance["n_suppliers"]      # number of warehouses
    n_stores = instance["n_stores"]            # number of stores
    building_cost = instance["building_cost"]  # cost of each open warehouse
    capacity = instance["capacity"]            # capacity[w]: stores warehouse w can supply
    cost = instance["cost_matrix"]             # cost[s][w]: cost of warehouse w supplying store s

    warehouses = range(n_suppliers)
    stores = range(n_stores)

    model = Model("warehouse_location")

    # supplies[s, w] is 1 when warehouse w supplies store s; each store has exactly one.
    supplies = model.binary_var_matrix(stores, warehouses, name="supplies")
    model.add_constraints(model.sum(supplies[s, w] for w in warehouses) == 1 for s in stores)

    # supplier_assignment[s] is the number w of the warehouse that supplies store s (from 0).
    supplier_assignment = [model.sum(w * supplies[s, w] for w in warehouses) for s in stores]

    # open_warehouses[w] is 1 if warehouse w is open.
    open_warehouses = model.binary_var_list(n_suppliers, name="open")

    for w in warehouses:
        served = model.sum(supplies[s, w] for s in stores)
        # The number of stores assigned to a warehouse cannot exceed its capacity.
        model.add_constraint(served <= capacity[w])
        # A warehouse is open if and only if it supplies at least one store: open when any
        # store is assigned to it, closed when none is.
        model.add_constraints(open_warehouses[w] >= supplies[s, w] for s in stores)
        model.add_constraint(open_warehouses[w] <= served)

    # Total cost: supply costs plus the building cost of every open warehouse.
    total_cost = (model.sum(cost[s][w] * supplies[s, w] for s in stores for w in warehouses)
                  + building_cost * model.sum(open_warehouses))

    # Minimise the total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                   "supplier_assignment": supplier_assignment}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
