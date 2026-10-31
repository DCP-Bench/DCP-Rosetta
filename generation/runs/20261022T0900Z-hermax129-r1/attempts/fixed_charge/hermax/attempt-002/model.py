from hermax.model import Model


def build(instance):
    # product[p] = [profit per unit, machine needed to make it]
    product = instance["product"]
    # use[p][r] = amount of resource r used per unit of product p
    use = instance["use"]
    capacity = instance["capacity"]
    renting_cost = instance["renting_cost"]
    max_production = instance["max_production"]

    num_products = len(product)
    num_machines = len(renting_cost)
    num_resources = len(capacity)

    # Units of each product as binary digits, so every weighted sum is linear
    # over Booleans. A quantity cannot exceed max_production.
    bits = max_production.bit_length()

    m = Model()
    rent = m.bool_vector("rent", num_machines)
    qty_bits = [m.bool_vector(f"make{p}", bits) for p in range(num_products)]

    def qty_terms(p):
        return [(2 ** k, qty_bits[p][k]) for k in range(bits)]

    # Production of each product stays within the maximum.
    for p in range(num_products):
        m &= (sum(c * b for c, b in qty_terms(p)) <= max_production)

    # Fixed charge: a product can be made only on its rented machine.
    for p in range(num_products):
        machine = product[p][1]
        for _, b in qty_terms(p):
            m &= (~b | rent[machine])

    # Labour and cloth capacity for the total use of each resource.
    for r in range(num_resources):
        m &= (sum(use[p][r] * c * b for p in range(num_products) for c, b in qty_terms(p))
              <= capacity[r])

    # Profit on products minus the cost of renting the machines.
    profit = sum(product[p][0] * c * b for p in range(num_products) for c, b in qty_terms(p))
    rental = sum(renting_cost[k] * rent[k] for k in range(num_machines))

    # Maximise profit: minimise the negated profit.
    m.obj += 0 - (profit - rental)

    return m, {"z": profit - rental}
