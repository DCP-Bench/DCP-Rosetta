# facility_location: a CPMpy model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python facility_location.py facility_location.json

import cpmpy as cp


def create_model(instance):
    """A company chooses which of four warehouses to open and how many units each
    ships to each region, meeting every region's demand at the least total of
    fixed and shipping costs, under three rules about which warehouses are opened."""
    names = instance["warehouse_s"]              # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship per week
    demands = instance["demands"]                # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    num_warehouses = len(names)
    num_regions = len(demands)

    # The rules are about named cities, so find their warehouse indices.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = cp.boolvar(shape=num_warehouses, name="open_warehouse")
    # ships[i][j] is the number of units sent from warehouse i to region j
    ships = cp.intvar(0, max_shipping, shape=(num_warehouses, num_regions), name="ships")
    # total_cost is the fixed cost of the open warehouses plus the cost of all shipping;
    # it cannot exceed all fixed costs plus the full capacity shipped at every route's price
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)
    total_cost = cp.intvar(0, cost_bound, name="total_cost")

    model = cp.Model()

    # A warehouse ships at most max_shipping units per week, and nothing when it is closed.
    model.add(ships.sum(axis=1) <= max_shipping * open_warehouse)

    # Every region receives at least its weekly demand.
    model.add(ships.sum(axis=0) >= demands)

    # The total cost is the fixed cost of every open warehouse plus the cost of every unit shipped.
    model.add(total_cost == cp.sum(open_warehouse * fixed_costs) + cp.sum(ships * shipping_costs))

    # Rule 1: if the New York warehouse is opened, the Los Angeles warehouse must be opened too.
    model.add(open_warehouse[new_york].implies(open_warehouse[los_angeles]))

    # Rule 2: at most three warehouses can be open.
    model.add(cp.sum(open_warehouse) <= 3)

    # Rule 3: the Atlanta or the Los Angeles warehouse (or both) must be open.
    model.add(open_warehouse[atlanta] | open_warehouse[los_angeles])

    # Minimize the total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
