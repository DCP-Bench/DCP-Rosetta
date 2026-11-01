# facility_location: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install ortools`):
#   python facility_location.py facility_location.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A company chooses which of four warehouses to open and how many units each
    ships to each region, meeting every region's demand at the least total of
    fixed and shipping costs, under three rules about which warehouses are opened."""
    names = instance["warehouse_s"]              # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship per week
    demands = instance["demands"]                # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    n_warehouses = len(names)                    # the number of warehouses
    n_regions = len(demands)                     # the number of regions

    # The rules name three cities, so find their warehouse indices.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    model = cp_model.CpModel()

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [model.new_bool_var(f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] is the number of units sent from warehouse i to region j
    ships = [[model.new_int_var(0, max_shipping, f"ships_{i}_{j}") for j in range(n_regions)]
             for i in range(n_warehouses)]
    # cost_bound is the most the total cost can be: all fixed costs, and the full
    # capacity shipped on every route
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)
    # total_cost is the total cost of the plan
    total_cost = model.new_int_var(0, cost_bound, "total_cost")

    # A warehouse ships at most max_shipping units, and nothing when it is closed.
    for i in range(n_warehouses):
        model.add(sum(ships[i]) <= max_shipping * open_warehouse[i])

    # Every region receives at least its weekly demand.
    for j in range(n_regions):
        model.add(sum(ships[i][j] for i in range(n_warehouses)) >= demands[j])

    # The total cost is the fixed costs of the open warehouses plus the cost of every unit shipped.
    model.add(
        total_cost
        == sum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
        + sum(shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions))
    )

    # Rule 1: if the New York warehouse is open, the Los Angeles warehouse is open too.
    model.add_implication(open_warehouse[new_york], open_warehouse[los_angeles])
    # Rule 2: at most three warehouses are open.
    model.add(sum(open_warehouse) <= 3)
    # Rule 3: the Atlanta or the Los Angeles warehouse, or both, is open.
    model.add_bool_or([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # Minimize the total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}


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
