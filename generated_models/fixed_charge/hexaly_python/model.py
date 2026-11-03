"""Fixed charge: produce shirts, shorts and pants on rented machines within labour and cloth capacity, maximising profit."""
import hexaly.optimizer as hx


def build(instance):
    product, use = instance["product"], instance["use"]  # product[p] = [profit, machine]; use[p] = per-resource use
    capacity, renting_cost = instance["capacity"], instance["renting_cost"]
    top = instance["max_production"]
    n_products, n_machines, n_resources = len(product), len(renting_cost), len(capacity)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # produce[p] is the amount of product p made; rent[m] = 1 if machine m is rented
    produce = [model.int(0, top) for _ in range(n_products)]
    rent = [model.bool() for _ in range(n_machines)]

    # Each resource (labour, cloth) is used within its capacity
    for r in range(n_resources):
        model.constraint(model.sum(use[p][r] * produce[p] for p in range(n_products)) <= capacity[r])
    # A product is made only when its machine is rented, and never more than max_production
    for p in range(n_products):
        model.constraint(produce[p] <= top * rent[product[p][1]])

    # Maximise the profit of the products minus the renting costs
    z = model.sum(product[p][0] * produce[p] for p in range(n_products)) - model.sum(
        renting_cost[m] * rent[m] for m in range(n_machines))
    model.maximize(z)
    return optimizer, {"z": z}
