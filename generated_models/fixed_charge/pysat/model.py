# fixed_charge: a PySAT (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python fixed_charge.py fixed_charge.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A company makes products, each needing some of each limited resource.
    A product can only be made on a machine the company rents, which has a
    fixed renting cost. Choose the machines to rent and how much of each
    product to make, to maximize the profit from the products minus the
    renting costs."""
    machines = instance["machines"]              # the machines the company can rent
    products = instance["products"]              # the products the company makes
    resources = instance["resources"]            # the resources the products need, such as labor and cloth
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: the amount of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p]: the profit per unit of product p, and the machine it needs
    use = instance["use"]                        # use[p][r]: the amount of resource r that one unit of product p needs

    pool = IDPool()

    # produce[p] is the number of units of product p made. The upper bound is
    # max_production, or less when the scarcest resource runs out sooner.
    produce = {}
    for p in products:
        top = max_production
        for r in resources:
            if use[p][r] > 0:
                top = min(top, capacity[r] // use[p][r])
        produce[p] = Integer(f"produce_{p}", 0, max(top, 1), encoding="order", vpool=pool)

    # rent[m] is 1 when machine m is rented, 0 otherwise
    rent = {m: Integer(f"rent_{m}", 0, 1, vpool=pool) for m in machines}

    # z is the profit: the products' profit minus the renting costs. Making nothing
    # gives 0, so it is never below 0. It is capped at 10000, and at the profit of
    # making every product at its upper bound.
    most = sum(product[p][0] * produce[p].ub for p in products if product[p][0] > 0)
    z = Integer("z", 0, max(min(10000, most), 1), encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=list(produce.values()) + list(rent.values()) + [z], vpool=pool)

    # The profit is the products' profit minus the renting costs of the rented machines.
    engine.add_linear(sum(product[p][0] * produce[p] for p in products)
                      - sum(renting_cost[m] * rent[m] for m in machines)
                      - z == 0)

    # The products made use no more of each resource than the company has.
    for r in resources:
        engine.add_linear(sum(use[p][r] * produce[p] for p in products) <= capacity[r])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A product can only be made when its machine is rented.
    for p in products:
        m = product[p][1]
        formula.append([-produce[p].ge(1), rent[m].equals(1)])

    # Maximize the profit. Each unit of product p that is not made costs its profit,
    # and a product that loses money costs its loss for each unit made.
    for p in products:
        for v in range(1, produce[p].ub + 1):
            if product[p][0] > 0:
                formula.append([produce[p].ge(v)], weight=product[p][0])
            elif product[p][0] < 0:
                formula.append([-produce[p].ge(v)], weight=-product[p][0])

    # Each rented machine costs its renting cost.
    for m in machines:
        if renting_cost[m] > 0:
            formula.append([-rent[m].equals(1)], weight=renting_cost[m])

    return formula, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
