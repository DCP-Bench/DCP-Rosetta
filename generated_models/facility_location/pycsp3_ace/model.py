# facility_location: a PyCSP3 model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python facility_location.py facility_location.json

from pycsp3 import *


def create_model(instance):
    """A company considers opening warehouses in four cities to meet the weekly demand of
    each region at minimal cost. An open warehouse has a fixed weekly cost and ships at
    most max_shipping units a week; a closed one ships nothing. Shipping one unit from a
    warehouse to a region has a given cost, and each region must receive at least its
    weekly demand. If the New York warehouse is opened, the Los Angeles warehouse must also
    be opened. No more than three warehouses can be operational. Either the Atlanta or the
    Los Angeles warehouse must be opened. Minimise the fixed costs of the open warehouses
    plus the shipping costs."""
    warehouse_names = instance["warehouse_s"]  # the names of the candidate cities
    fixed_costs = instance["fixed_costs"]  # fixed_costs[i] is the weekly cost of opening warehouse i
    max_shipping = instance["max_shipping"]  # the most units an open warehouse ships a week
    demands = instance["demands"]  # demands[j] is the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j] is the cost of one unit from warehouse i to region j
    n_warehouses = len(fixed_costs)  # the number of candidate warehouses
    n_regions = len(demands)  # the number of regions
    city = {name: i for i, name in enumerate(warehouse_names)}  # warehouse index of each city

    max_operational = 3  # the most warehouses that can be operational in one week

    # open_warehouse[i] is 1 when warehouse i is opened
    open_warehouse = VarArray(size=n_warehouses, dom={0, 1})

    # ships[i][j] is the number of units shipped from warehouse i to region j. Shipping costs
    # are positive, so no warehouse ships more to a region than its demand in an optimal
    # plan (assumed: this only drops solutions that are not optimal); the domain uses that bound.
    ships = VarArray(
        size=[n_warehouses, n_regions],
        dom=lambda i, j: range(min(max_shipping, demands[j]) + 1),
    )

    # total_cost is the fixed costs plus the shipping costs. Its domain is bounded by all fixed costs
    # plus each region's demand at its highest unit cost: an optimal plan opens no more than all
    # warehouses and, shipping costs being positive, ships exactly the demand to each region.
    max_total_cost = sum(fixed_costs) + sum(
        demands[j] * max(shipping_costs[i][j] for i in range(n_warehouses)) for j in range(n_regions)
    )
    total_cost = Var(dom=range(max_total_cost + 1))

    # load[i] is the number of units warehouse i ships in a week (at most max_shipping, which bounds its domain)
    load = VarArray(size=n_warehouses, dom=range(max_shipping + 1))

    satisfy(
        # The load of a warehouse is what it ships to all regions.
        [load[i] == Sum(ships[i]) for i in range(n_warehouses)],
        # Implied, not in the description (it speeds up the proof of optimality): no optimal plan ships to a region
        # from a warehouse while a cheaper open warehouse for that region has spare capacity, because moving one
        # unit to the cheaper warehouse would lower the cost.
        [Or(ships[i][j] == 0, open_warehouse[k] == 0, load[k] == max_shipping)
         for i in range(n_warehouses) for k in range(n_warehouses) for j in range(n_regions)
         if shipping_costs[k][j] < shipping_costs[i][j]],
        # Each region receives at least its weekly demand. Shipping costs are positive, so an optimal
        # plan ships exactly the demand; the equality is used (it drops only non-optimal plans) as it propagates better.
        [Sum(ships[:, j]) == demands[j] for j in range(n_regions)],
        # An open warehouse ships at most max_shipping units; a closed one ships nothing.
        [load[i] <= max_shipping * open_warehouse[i] for i in range(n_warehouses)],
        # If the New York warehouse is opened, the Los Angeles warehouse must also be opened.
        open_warehouse[city["New York"]] <= open_warehouse[city["Los Angeles"]],
        # No more than three warehouses can be operational in any given week.
        Sum(open_warehouse) <= max_operational,
        # Either the Atlanta or the Los Angeles warehouse must be opened.
        open_warehouse[city["Atlanta"]] + open_warehouse[city["Los Angeles"]] >= 1,
        # total_cost is the fixed costs of the open warehouses plus the shipping costs.
        total_cost == Sum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
        + Sum(shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions)),
    )

    # The total cost is minimised.
    minimize(total_cost)

    return {"open_warehouse": open_warehouse, "ships": ships, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("open_warehouse", "=", values(outputs["open_warehouse"]))
        print("ships", "=", values(outputs["ships"]))
        print("total_cost", "=", value(outputs["total_cost"]))
    else:
        print("No solution:", status())
