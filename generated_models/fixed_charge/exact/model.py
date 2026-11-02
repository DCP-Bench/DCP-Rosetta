# fixed_charge: an Exact (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python fixed_charge.py fixed_charge.json

from exact import Exact


def create_model(instance):
    """A company makes shirts, shorts and pants from limited labor and cloth. Each product
    can be made only on its own machine, which the company rents at a fixed cost. Choose
    which machines to rent and how much of each product to make, to maximize the profit:
    the profit on the products, minus the renting costs."""
    machines = instance["machines"]              # the machines the company can rent
    products = instance["products"]              # shirts, shorts and pants
    resources = instance["resources"]            # labor and cloth
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: the amount of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p]: the profit per unit of product p, and the machine it needs
    use = instance["use"]                        # use[p][r]: the amount of resource r that one unit of product p uses

    solver = Exact()

    # Exact identifies its variables by name.
    # rent[m] is 1 when machine m is rented
    rent = [f"rent_{m}" for m in machines]
    for name in rent:
        solver.addVariable(name, 0, 1)

    # produce[p] is the number of units of product p made
    produce = [f"produce_{p}" for p in products]
    for name in produce:
        solver.addVariable(name, 0, max_production)

    # z is the profit, at most 10000
    solver.addVariable("z", 0, 10000)

    # Profit from each product made.
    profit_terms = [(product[p][0], produce[p]) for p in products]
    # Renting cost of each machine, paid when the machine is rented.
    rent_terms = [(-renting_cost[m], rent[m]) for m in machines]
    # z is the products' profit minus the renting costs.
    solver.addConstraint(profit_terms + rent_terms + [(-1, "z")], True, 0, True, 0)

    # The labor and cloth used cannot exceed what the company has.
    for r in resources:
        solver.addConstraint([(use[p][r], produce[p]) for p in products], False, 0, True, capacity[r])

    # A product is made only on its rented machine.
    for p in products:
        solver.addConstraint([(1, produce[p]), (-max_production, rent[product[p][1]])], False, 0, True, 0)

    solver.setObjective([(1, "z")], minimize=False)

    return solver, {"z": "z"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
