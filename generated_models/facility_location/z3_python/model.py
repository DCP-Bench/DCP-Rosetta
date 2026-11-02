# facility_location: a Z3 (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python facility_location.py facility_location.json

import z3


def create_model(instance):
    """A company chooses which of four candidate warehouses to open and how many units each
    open warehouse ships to each region. Every region's demand must be met, and the total of
    fixed and shipping costs should be as low as possible. Three rules restrict which
    warehouses may be open together."""
    names = instance["warehouse_s"]              # names[i]: the city of candidate warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship per week
    demands = instance["demands"]                # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    n_warehouses = len(names)                    # the number of candidate warehouses
    n_regions = len(demands)                     # the number of regions

    # The rules name three cities, so find their warehouse numbers.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [z3.Bool(f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] is the number of units sent from warehouse i to region j
    ships = [[z3.Int(f"ships_{i}_{j}") for j in range(n_regions)] for i in range(n_warehouses)]
    # total_cost is the total cost of the plan
    total_cost = z3.Int("total_cost")
    # cost_bound is the most any plan can cost: all fixed costs, and the full capacity shipped on every route
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)

    solver = z3.Optimize()

    # Each shipment is between zero and the most one warehouse can send.
    solver.add([z3.And(0 <= shipment, shipment <= max_shipping) for row in ships for shipment in row])

    # A warehouse ships at most max_shipping units, and nothing when it is closed.
    solver.add([
        z3.Sum(ships[i]) <= z3.If(open_warehouse[i], max_shipping, 0) for i in range(n_warehouses)
    ])

    # Every region receives at least its weekly demand.
    solver.add([
        z3.Sum([ships[i][j] for i in range(n_warehouses)]) >= demands[j] for j in range(n_regions)
    ])

    # The total cost lies between zero and cost_bound.
    solver.add(z3.And(total_cost >= 0, total_cost <= cost_bound))

    # The plan's cost adds the fixed costs of the open warehouses to the cost of every shipment.
    solver.add(
        total_cost
        == z3.Sum([z3.If(open_warehouse[i], fixed_costs[i], 0) for i in range(n_warehouses)])
        + z3.Sum([shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions)])
    )

    # Rule 1: if the New York warehouse is open, the Los Angeles warehouse is open too.
    solver.add(z3.Implies(open_warehouse[new_york], open_warehouse[los_angeles]))

    # Rule 2: at most three warehouses are open.
    solver.add(z3.AtMost(*open_warehouse, 3))

    # Rule 3: the Atlanta or the Los Angeles warehouse, or both, is open.
    solver.add(z3.Or(open_warehouse[atlanta], open_warehouse[los_angeles]))

    outputs = {"open_warehouse": open_warehouse, "ships": ships, "total_cost": total_cost}
    solver.minimize(total_cost)

    return solver, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
