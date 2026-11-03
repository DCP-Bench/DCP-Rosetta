"""Facility location: open warehouses and ship to the regions to meet demand at minimum fixed plus shipping cost."""
import hexaly.optimizer as hx


def build(instance):
    names, fixed = instance["warehouse_s"], instance["fixed_costs"]
    demands, shipping, cap = instance["demands"], instance["shipping_costs"], instance["max_shipping"]
    w_count, regions = len(names), len(demands)
    ny, la, atlanta = names.index("New York"), names.index("Los Angeles"), names.index("Atlanta")
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    open_warehouse = [model.bool() for _ in range(w_count)]
    # ships[i][j] is the number of units shipped from warehouse i to region j
    ships = [[model.int(0, cap) for _ in range(regions)] for _ in range(w_count)]

    # A warehouse ships at most max_shipping units, and nothing unless it is open
    for i in range(w_count):
        model.constraint(model.sum(ships[i]) <= cap * open_warehouse[i])
    # Each region receives exactly its demand
    for j in range(regions):
        model.constraint(model.sum(ships[i][j] for i in range(w_count)) == demands[j])

    # If New York is opened, Los Angeles is opened too
    model.constraint(open_warehouse[ny] <= open_warehouse[la])
    # No more than three warehouses are open
    model.constraint(model.sum(open_warehouse) <= 3)
    # Atlanta or Los Angeles is open
    model.constraint(open_warehouse[atlanta] + open_warehouse[la] >= 1)

    # Minimise the fixed costs of the open warehouses plus the shipping costs
    total_cost = model.sum(fixed[i] * open_warehouse[i] for i in range(w_count)) + model.sum(
        shipping[i][j] * ships[i][j] for i in range(w_count) for j in range(regions))
    model.minimize(total_cost)
    return optimizer, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
