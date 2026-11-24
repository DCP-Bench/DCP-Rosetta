# fixed_charge: a PyCSP3 model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python fixed_charge.py fixed_charge.json

from pycsp3 import *


def create_model(instance):
    """A company manufactures shirts, shorts and pants. Each product requires a number of
    hours of labor and an amount of cloth, and the company has a limited capacity of both.
    Each product can be manufactured only by renting its own machine type; the renting cost
    of a machine is paid once, however much is made on it. The profit on the products
    (excluding the cost of renting the machines) is known per unit, and each product is made
    in a whole number of units. Maximize the profit on the units made less the cost of the
    machines rented."""
    product = instance["product"]                # product[k] is [profit per unit of product k, the machine type product k needs]
    use = instance["use"]                        # use[k][r] is the amount of resource r (labor, cloth) one unit of product k needs
    capacity = instance["capacity"]              # capacity[r] is the amount of resource r the company has
    renting_cost = instance["renting_cost"]      # renting_cost[m] is the cost of renting machine m, paid once
    max_production = instance["max_production"]  # the largest number of units of any product, taken as the bound on units
    n_products = len(product)
    n_machines = len(renting_cost)
    n_resources = len(capacity)

    # units[k] is the number of units of product k made
    units = VarArray(size=n_products, dom=range(max_production + 1))
    # rented[m] is 1 when machine m is rented, else 0
    rented = VarArray(size=n_machines, dom={0, 1})

    # The profit lies between paying the rent of every machine (no product made) and selling
    # max_production units of every product; profits are taken as non-negative.
    most_rent = sum(renting_cost)
    most_sales = sum(product[k][0] for k in range(n_products)) * max_production
    # profit is the company's profit: the sales of the units made less the rent of the machines
    profit = Var(dom=range(-most_rent, most_sales + 1))

    satisfy(
        # The labor and the cloth used by the products made stay within the capacity of each.
        [Sum(use[k][r] * units[k] for k in range(n_products)) <= capacity[r] for r in range(n_resources)],
        # A product is made only on its own machine: units of product k are zero unless its machine is rented.
        [units[k] <= max_production * rented[product[k][1]] for k in range(n_products)],
        # The profit is the profit on the units made less the cost of the machines rented.
        profit == Sum(product[k][0] * units[k] for k in range(n_products))
        - Sum(renting_cost[m] * rented[m] for m in range(n_machines)),
    )

    # The objective is the company's profit, to be maximized.
    maximize(profit)

    return {"z": profit}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
