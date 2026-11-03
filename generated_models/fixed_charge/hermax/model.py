# fixed_charge: a hermax (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install hermax`):
#   python fixed_charge.py fixed_charge.json

from hermax.model import Model


def create_model(instance):
    """A company makes shirts, shorts and pants. Each product needs labour and cloth,
    and can be made only on a machine the company has rented at a fixed cost. Choose
    how much of each product to make and which machines to rent so that the profit
    on the products, minus the rental costs, is as large as possible."""
    # product[p] = [profit per unit of product p, the machine product p needs]
    product = instance["product"]
    # use[p][r]: amount of resource r (labour, cloth) used by one unit of product p
    use = instance["use"]
    # capacity[r]: total amount of resource r the company has
    capacity = instance["capacity"]
    # renting_cost[k]: the price of renting machine k
    renting_cost = instance["renting_cost"]
    # max_production: the most units of any one product that may be made
    max_production = instance["max_production"]

    num_products = len(product)
    num_machines = len(renting_cost)
    num_resources = len(capacity)

    m = Model()

    # rent[k] is true when machine k is rented
    rent = m.bool_vector("rent", num_machines)

    # make[p] is the number of units of product p to make.
    # Its upper bound is the smallest of max_production and what each resource allows alone.
    top = []
    for p in range(num_products):
        limits = [max_production] + [capacity[r] // use[p][r]
                                     for r in range(num_resources) if use[p][r] > 0]
        top.append(min(limits))
    make = [m.int(f"make_{p}", 0, top[p]) for p in range(num_products)]

    # Fixed charge: a product can be made only when its machine is rented.
    for p in range(num_products):
        machine = product[p][1]
        m &= (make[p] <= top[p] * rent[machine])

    # Labour and cloth: the units made use no more than the capacity of each resource.
    for r in range(num_resources):
        m &= (sum(use[p][r] * make[p] for p in range(num_products)) <= capacity[r])

    # Profit on the products made, and the rental paid for the machines.
    profit = sum(product[p][0] * make[p] for p in range(num_products))
    rental = sum(renting_cost[k] * rent[k] for k in range(num_machines))

    # z is the total profit: the profit on the products minus the rental costs.
    z = m.int("z", -sum(renting_cost), sum(product[p][0] * top[p] for p in range(num_products)))
    m &= (z == profit - rental)

    # Maximise the profit: the solver minimises the negated profit.
    m.obj += rental - profit

    return m, {"z": z}


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
