# facility_location: a hermax (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install hermax`):
#   python facility_location.py facility_location.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Choose which of four candidate warehouses to open, and how many units each open
    warehouse ships to each region, so that every region gets exactly its demand, no
    warehouse ships more than its weekly limit, and the fixed opening costs plus the
    shipping costs are as small as possible. Three rules from the problem statement
    also apply: New York needs Los Angeles, at most three warehouses may be open, and
    Atlanta or Los Angeles must be open."""
    names = instance["warehouse_s"]              # names[i]: the city of candidate warehouse i (the four cities of the statement)
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: cost of opening warehouse i
    max_shipping = instance["max_shipping"]      # max_shipping: most units one warehouse may ship per week
    demands = instance["demands"]                # demands[j]: units region j needs
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: cost of one unit from warehouse i to region j
    n_warehouses = len(names)  # number of candidate warehouses
    n_regions = len(demands)   # number of regions to supply

    # The rules name the cities, so their warehouses are found by name.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    m = Model()

    # open_warehouse[i] is true when warehouse i is opened
    open_warehouse = m.bool_vector("open_warehouse", n_warehouses)

    # ships[i][j] is the number of units sent from warehouse i to region j. Region j never
    # needs more than its demand, and no warehouse ships more than the weekly limit.
    ships = [[m.int(f"ships_{i}_{j}", 0, min(demands[j], max_shipping))
              for j in range(n_regions)] for i in range(n_warehouses)]

    # full[i] is true when warehouse i ships exactly its weekly limit, which the
    # dominance rule below uses. It is defined from the warehouse's total shipment.
    full = [m.bool() for _ in range(n_warehouses)]

    # Every region receives exactly its demand, summed over all warehouses. The statement
    # only asks to meet the demand, so exact delivery is an implied restriction. It is safe
    # because shipping costs are non-negative: extra units never lower the cost. The ship
    # domain above relies on it.
    for j in range(n_regions):
        m &= (sum_expr(ships[i][j] for i in range(n_warehouses)) == demands[j])

    # A warehouse that is not opened ships nothing, and an opened one ships at most
    # max_shipping units in total. full[i] records whether it ships exactly that many.
    for i in range(n_warehouses):
        m &= (sum_expr(ships[i]) <= max_shipping * open_warehouse[i])
        m &= (sum_expr(ships[i]) >= max_shipping).iff(full[i])

    # Rule 1: if the New York warehouse is opened, the Los Angeles one must be opened too.
    m &= (~open_warehouse[new_york] | open_warehouse[los_angeles])

    # Rule 2: no more than three warehouses are operational (the limit of the statement).
    m &= (sum_expr(open_warehouse[i] for i in range(n_warehouses)) <= 3)

    # Rule 3: the Atlanta or the Los Angeles warehouse (or both) must be opened.
    m &= (open_warehouse[atlanta] | open_warehouse[los_angeles])

    # Dominance (exchange argument): if warehouse k ships to region j while a strictly
    # cheaper warehouse i is open and not full, moving one unit of region
    # j's supply from k to i keeps every demand and every limit, keeps the open set, and
    # lowers the cost. So such a solution is never optimal, and ruling it out keeps every
    # optimal solution. This is a speed-up only.
    for j in range(n_regions):
        for i in range(n_warehouses):
            for k in range(n_warehouses):
                if shipping_costs[i][j] < shipping_costs[k][j]:
                    # a dearer warehouse k serves region j only when the cheaper open warehouse i is full
                    m &= ((ships[k][j] == 0) | ~open_warehouse[i] | full[i])

    # total_cost is the declared total: the fixed costs of the opened warehouses plus the
    # shipping costs of all units. It is the linear expression itself, not an extra variable.
    total_cost = (sum_expr(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
                  + sum_expr(shipping_costs[i][j] * ships[i][j]
                             for i in range(n_warehouses) for j in range(n_regions)))

    # Minimise the total cost.
    m.obj += total_cost

    return m, {"open_warehouse": open_warehouse, "ships": ships, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
