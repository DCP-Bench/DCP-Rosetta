# facility_location: a Python-MIP (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python facility_location.py facility_location.json

import mip


def create_model(instance):
    """A company chooses which of four warehouses to open and how many units each
    open warehouse ships to each region, so that every region's demand is met at the
    least total of fixed and shipping costs. Three rules restrict which warehouses
    may be open."""
    warehouse_s = instance["warehouse_s"]        # warehouse_s[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the cost of keeping warehouse i open
    max_shipping = instance["max_shipping"]      # the most units an open warehouse can ship
    demands = instance["demands"]                # demands[j]: the number of units region j needs
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost of one unit from warehouse i to region j
    n_warehouses = len(fixed_costs)              # the number of warehouses
    n_regions = len(demands)                     # the number of regions

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [model.add_var(f"open_{i}", var_type=mip.BINARY) for i in range(n_warehouses)]
    # ships[i][j] is the number of units sent from warehouse i to region j. No region
    # needs more than its demand, and no warehouse ships more than max_shipping units.
    ships = [
        [
            model.add_var(
                f"ships_{i}_{j}",
                lb=0,
                ub=min(demands[j], max_shipping),
                var_type=mip.INTEGER,
            )
            for j in range(n_regions)
        ]
        for i in range(n_warehouses)
    ]
    # the most expensive shipping cost of one unit
    max_unit_cost = max(max(row) for row in shipping_costs)
    # total_cost is the total cost of the plan. No plan costs more than opening every
    # warehouse and shipping all demand at the most expensive rate.
    total_cost = model.add_var(
        "total_cost",
        lb=0,
        ub=sum(fixed_costs) + max_unit_cost * sum(demands),
        var_type=mip.INTEGER,
    )

    # Each region receives exactly its demand.
    for j in range(n_regions):
        model += mip.xsum(ships[i][j] for i in range(n_warehouses)) == demands[j]

    # An open warehouse ships at most max_shipping units in total, and a closed one ships nothing.
    for i in range(n_warehouses):
        model += mip.xsum(ships[i][j] for j in range(n_regions)) <= max_shipping * open_warehouse[i]

    # the warehouse indices of the cities named in the rules
    new_york = warehouse_s.index("New York")
    los_angeles = warehouse_s.index("Los Angeles")
    atlanta = warehouse_s.index("Atlanta")

    # If the New York warehouse is opened, the Los Angeles warehouse must be opened too.
    model += open_warehouse[new_york] <= open_warehouse[los_angeles]

    # No more than three warehouses can be open.
    model += mip.xsum(open_warehouse) <= 3

    # At least one of the Atlanta and Los Angeles warehouses must be opened.
    model += open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1

    # The total cost is the fixed costs of the open warehouses plus the shipping costs
    # of every unit sent.
    model += (
        total_cost
        == mip.xsum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
        + mip.xsum(
            shipping_costs[i][j] * ships[i][j]
            for i in range(n_warehouses)
            for j in range(n_regions)
        )
    )

    # Minimize the total cost.
    model.objective = total_cost

    return model, {
        "open_warehouse": open_warehouse,
        "ships": ships,
        "total_cost": total_cost,
    }


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
