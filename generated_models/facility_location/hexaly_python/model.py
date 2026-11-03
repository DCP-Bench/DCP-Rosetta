"""Facility location: open warehouses and ship to the regions to meet demand at minimum fixed plus shipping cost."""
import hexaly.optimizer as hx


def build(instance):
    # warehouse_s[i] = city name of candidate warehouse i; fixed_costs[i] = cost of opening warehouse i
    names, fixed = instance["warehouse_s"], instance["fixed_costs"]
    # demands[j] = units region j needs; shipping_costs[i][j] = cost per unit shipped from warehouse i
    # to region j; max_shipping = most units one warehouse can ship in total
    demands, shipping, cap = instance["demands"], instance["shipping_costs"], instance["max_shipping"]
    w_count, regions = len(names), len(demands)  # number of candidate warehouses, number of regions
    # indices of the three cities named in the statement's conditions
    ny, la, atlanta = names.index("New York"), names.index("Los Angeles"), names.index("Atlanta")
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # open_warehouse[i] = 1 if warehouse i is opened
    open_warehouse = [model.bool() for _ in range(w_count)]
    # ships[i][j] = number of units shipped from warehouse i to region j; each is at most
    # max_shipping, as no warehouse ships more than that in total
    ships = [[model.int(0, cap) for _ in range(regions)] for _ in range(w_count)]

    # A warehouse ships at most max_shipping units, and nothing unless it is open
    for i in range(w_count):
        model.constraint(model.sum(ships[i]) <= cap * open_warehouse[i])
    # Each region receives exactly its demand, summed over all warehouses
    for j in range(regions):
        model.constraint(model.sum(ships[i][j] for i in range(w_count)) == demands[j])

    # 1. If New York is opened, Los Angeles must also be opened (an implication on 0/1 values)
    model.constraint(open_warehouse[ny] <= open_warehouse[la])
    # 2. No more than three warehouses are operational (the limit 3 is the statement's)
    model.constraint(model.sum(open_warehouse) <= 3)
    # 3. Either Atlanta or Los Angeles must be opened (at least one of the two)
    model.constraint(open_warehouse[atlanta] + open_warehouse[la] >= 1)

    # Minimise total cost: the fixed costs of the open warehouses plus the shipping costs of all units shipped
    total_cost = model.sum(fixed[i] * open_warehouse[i] for i in range(w_count)) + model.sum(
        shipping[i][j] * ships[i][j] for i in range(w_count) for j in range(regions))
    model.minimize(total_cost)
    return optimizer, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
