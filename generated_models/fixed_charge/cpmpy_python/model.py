# fixed_charge: a CPMpy model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python fixed_charge.py fixed_charge.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A company makes products, each needing some of each limited resource
    (labor and cloth). A product can only be made on a rented machine, which
    has a fixed renting cost. Choose the machines to rent and the amount to
    produce of each product to maximize the profit, which is the products'
    profit minus the renting costs."""
    num_products = instance["num_products"]  # the number of products
    num_machines = instance["num_machines"]  # the number of machines
    renting_cost = instance["renting_cost"]  # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]          # capacity[r]: the available amount of resource r
    max_production = instance["max_production"]  # the most of any one product that can be made
    product = np.array(instance["product"])
    # product[p][0]: the profit per unit of product p, excluding the renting cost
    profit = product[:, 0]
    # product[p][1]: the machine that product p needs
    machine = product[:, 1]
    # use[p][r]: the amount of resource r that one unit of product p needs
    use = np.array(instance["use"])
    num_resources = use.shape[1]

    # rent[m] is true when machine m is rented
    rent = cp.boolvar(shape=num_machines, name="rent")
    # produce[p] is the number of units made of product p
    produce = cp.intvar(0, max_production, shape=num_products, name="produce")
    # z is the total profit: the sale profit minus the renting costs
    z = cp.intvar(0, 10000, name="z")

    model = cp.Model()
    model.add(z == cp.sum(produce * profit) - cp.sum(rent * renting_cost))

    # The production does not use more of each resource than is available.
    for r in range(num_resources):
        model.add(cp.sum(produce * use[:, r]) <= capacity[r])
    # A product can only be made if its machine is rented; max_production bounds the amount made on a rented machine.
    model.add(produce <= max_production * rent[machine])

    # Make as much profit as possible.
    model.maximize(z)

    return model, {"z": z}


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
