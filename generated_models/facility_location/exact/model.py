# facility_location: an Exact (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python facility_location.py facility_location.json

from exact import Exact


def create_model(instance):
    """A company opens some of four candidate warehouses and ships units from them to
    the regions, meeting every region's demand at the least total of fixed and shipping
    costs, under three rules about which warehouses may be open together."""
    names = instance["warehouse_s"]              # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship per week
    demands = instance["demands"]                # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    n_warehouses = len(names)                    # the number of candidate warehouses
    n_regions = len(demands)                     # the number of regions

    # The rules name three cities, so find their warehouse indices.
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    # cost_bound is the most the total cost can be: every fixed cost, and the full shipping
    # capacity on every route.
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)

    solver = Exact()

    # Exact identifies its variables by name.
    # open_warehouse[i] is 1 when warehouse i is open, and 0 when it is closed
    open_warehouse = [f"open_{i}" for i in range(n_warehouses)]
    for name in open_warehouse:
        solver.addVariable(name, 0, 1)

    # ships[i][j] is the number of units sent from warehouse i to region j
    ships = [[f"ships_{i}_{j}" for j in range(n_regions)] for i in range(n_warehouses)]
    for row in ships:
        for name in row:
            solver.addVariable(name, 0, max_shipping)

    # A warehouse ships at most max_shipping units, and nothing when it is closed.
    for i in range(n_warehouses):
        solver.addConstraint([(1, name) for name in ships[i]] + [(-max_shipping, open_warehouse[i])],
                             False, 0, True, 0)

    # Every region receives at least its weekly demand.
    for j in range(n_regions):
        solver.addConstraint([(1, ships[i][j]) for i in range(n_warehouses)], True, demands[j])

    # Rule 1: if the New York warehouse is open, the Los Angeles warehouse is open too.
    solver.addConstraint([(1, open_warehouse[los_angeles]), (-1, open_warehouse[new_york])], True, 0)

    # Rule 2: at most three warehouses are open.
    solver.addConstraint([(1, name) for name in open_warehouse], False, 0, True, 3)

    # Rule 3: the Atlanta or the Los Angeles warehouse, or both, is open.
    solver.addConstraint([(1, open_warehouse[atlanta]), (1, open_warehouse[los_angeles])], True, 1)

    # The cost of the plan: the fixed costs of the open warehouses, plus the shipping cost of
    # every unit sent.
    cost_terms = [(fixed_costs[i], open_warehouse[i]) for i in range(n_warehouses)]
    cost_terms += [(shipping_costs[i][j], ships[i][j]) for i in range(n_warehouses) for j in range(n_regions)]

    # total_cost is that cost.
    solver.addVariable("total_cost", 0, cost_bound)
    solver.addConstraint(cost_terms + [(-1, "total_cost")], True, 0, True, 0)

    # Minimise the total cost.
    solver.setObjective(cost_terms, minimize=True)

    return solver, {"total_cost": "total_cost", "open_warehouse": open_warehouse, "ships": ships}


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
