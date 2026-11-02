# facility_location: a PuLP (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python facility_location.py facility_location.json

import pulp


def create_model(instance):
    """A company chooses which of four warehouses to open and how many units each
    ships to each region, meeting every region's demand at the least total cost
    under three rules about which warehouses are open."""
    names = instance["warehouse_s"]              # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly cost of keeping warehouse i open
    max_shipping = instance["max_shipping"]      # the most units an open warehouse ships each week
    demands = instance["demands"]                # demands[j]: the units region j needs each week
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost of one unit from warehouse i to region j
    n_warehouses = len(names)                    # the number of warehouses
    n_regions = len(demands)                     # the number of regions

    # The rules name three cities, so find their warehouse numbers.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    problem = pulp.LpProblem("facility_location", pulp.LpMinimize)

    # open_warehouse[i] is 1 when warehouse i is open, and 0 when it is closed
    open_warehouse = [pulp.LpVariable(f"open_{i}", cat="Binary") for i in range(n_warehouses)]
    # ships[i][j] is the number of units shipped from warehouse i to region j
    ships = [[pulp.LpVariable(f"ships_{i}_{j}", 0, max_shipping, cat="Integer")
              for j in range(n_regions)]
             for i in range(n_warehouses)]
    # cost_bound is the most the total cost can be: all fixed costs, and the full
    # capacity shipped on every route
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)
    # total_cost is the total cost of the plan
    total_cost = pulp.LpVariable("total_cost", 0, cost_bound, cat="Integer")

    # An open warehouse ships at most max_shipping units, and a closed one ships nothing.
    for i in range(n_warehouses):
        problem += pulp.lpSum(ships[i]) <= max_shipping * open_warehouse[i]

    # Every region receives at least its weekly demand.
    for j in range(n_regions):
        problem += pulp.lpSum(ships[i][j] for i in range(n_warehouses)) >= demands[j]

    # The total cost is the fixed costs of the open warehouses plus the cost of every unit shipped.
    problem += total_cost == pulp.lpSum(
        fixed_costs[i] * open_warehouse[i]
        + pulp.lpSum(shipping_costs[i][j] * ships[i][j] for j in range(n_regions))
        for i in range(n_warehouses))

    # Rule 1: if the New York warehouse is open, the Los Angeles warehouse is open too.
    problem += open_warehouse[new_york] <= open_warehouse[los_angeles]

    # Rule 2: at most three warehouses are open in any week.
    problem += pulp.lpSum(open_warehouse) <= 3

    # Rule 3: the Atlanta or the Los Angeles warehouse, or both, is open.
    problem += open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1

    # Minimize the total cost.
    problem += total_cost

    return problem, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
