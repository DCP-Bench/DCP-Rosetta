"""Fixed charge: produce shirts, shorts and pants on rented machines within labour and cloth capacity, maximising profit.
Each product needs labour and cloth and can be made only on its own rented machine."""
import hexaly.optimizer as hx


def build(instance):
    # product[p] = [profit per unit of product p (before renting costs), index of the machine product p needs]
    # use[p][r] = amount of resource r (labour or cloth) that one unit of product p uses
    product, use = instance["product"], instance["use"]
    # capacity[r] = available amount of resource r; renting_cost[m] = cost of renting machine m
    capacity, renting_cost = instance["capacity"], instance["renting_cost"]
    top = instance["max_production"]  # upper limit on the units made of any one product
    n_products, n_machines, n_resources = len(product), len(renting_cost), len(capacity)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # produce[p] = number of units of product p made (0 up to max_production, an instance field)
    produce = [model.int(0, top) for _ in range(n_products)]
    # rent[m] = 1 if machine m is rented
    rent = [model.bool() for _ in range(n_machines)]

    # Each resource (labour, cloth) is used within its capacity
    for r in range(n_resources):
        model.constraint(model.sum(use[p][r] * produce[p] for p in range(n_products)) <= capacity[r])
    # A product is made only when its machine is rented, and never more than max_production
    # (max_production is the variable's own upper bound, so it also serves as the big-M of this link)
    for p in range(n_products):
        model.constraint(produce[p] <= top * rent[product[p][1]])

    # z = profit of the products made minus the renting costs of the machines rented, to be maximised
    z = model.sum(product[p][0] * produce[p] for p in range(n_products)) - model.sum(
        renting_cost[m] * rent[m] for m in range(n_machines))
    model.maximize(z)
    return optimizer, {"z": z}
