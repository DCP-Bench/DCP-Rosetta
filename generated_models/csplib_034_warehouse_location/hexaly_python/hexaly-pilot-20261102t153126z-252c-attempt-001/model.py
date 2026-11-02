"""Warehouse location: open warehouses and supply every store from one open warehouse at minimum total cost."""
import hexaly.optimizer as hx


def build(instance):
    n_sup, n_stores = instance["n_suppliers"], instance["n_stores"]
    building_cost, capacity, cost = instance["building_cost"], instance["capacity"], instance["cost_matrix"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # open_[w] = 1 if warehouse w is opened; supplies[s][w] = 1 if store s is supplied by warehouse w
    open_ = [model.bool() for _ in range(n_sup)]
    supplies = [[model.bool() for _ in range(n_sup)] for _ in range(n_stores)]

    # Each store is supplied by exactly one warehouse
    for s in range(n_stores):
        model.constraint(model.sum(supplies[s]) == 1)
    for w in range(n_sup):
        # Only an open warehouse supplies stores
        for s in range(n_stores):
            model.constraint(supplies[s][w] <= open_[w])
        # A warehouse supplies at most as many stores as its capacity
        model.constraint(model.sum(supplies[s][w] for s in range(n_stores)) <= capacity[w])
        # A warehouse that supplies no store stays closed (it would only add maintenance cost)
        model.constraint(open_[w] <= model.sum(supplies[s][w] for s in range(n_stores)))

    # Total cost: maintenance of the open warehouses plus the supply cost of every store
    total_cost = building_cost * model.sum(open_) + model.sum(
        cost[s][w] * supplies[s][w] for s in range(n_stores) for w in range(n_sup))
    model.minimize(total_cost)

    # The warehouse (0..n_suppliers-1) that supplies each store
    supplier_assignment = [model.sum(w * supplies[s][w] for w in range(n_sup)) for s in range(n_stores)]
    return optimizer, {"total_cost": total_cost, "open_warehouses": open_,
                       "supplier_assignment": supplier_assignment}
