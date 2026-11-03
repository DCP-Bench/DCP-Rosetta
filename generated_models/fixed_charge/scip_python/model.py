# fixed_charge: a SCIP (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python fixed_charge.py fixed_charge.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A company makes shirts, shorts and pants from labour hours and cloth.
    Each product can be made only on its own machine, and a machine can be
    used only if it is rented, at a fixed rent. Choose which machines to rent
    and how many units of each product to make, so that the profit from the
    products minus the rent of the machines is as large as possible."""
    products = instance["products"]              # the product indices: shirts, shorts, pants
    resources = instance["resources"]            # the resource indices: labour hours and cloth
    capacity = instance["capacity"]              # capacity[r]: how much of resource r the company has
    use = instance["use"]                        # use[p][r]: how much of resource r one unit of product p takes
    machines = instance["machines"]              # the machine indices that can be rented
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the rent for machine m
    max_production = instance["max_production"]  # the most units of one product the company can make

    # product[p] is [profit, machine]: profit[p] is the profit per unit of product p, and
    # needs_machine[p] the machine that product p is made on (matching shirtM, shortM and
    # pantM for shirts, shorts and pants in every instance)
    profit = [row[0] for row in instance["product"]]
    needs_machine = [row[1] for row in instance["product"]]

    model = Model("fixed_charge")

    # made[p] is how many units of product p the company makes; the most is the instance's
    # max_production, which is taken as the cap on one product (the statement names no other)
    made = [model.addVar(f"made_{p}", vtype="I", lb=0, ub=max_production) for p in products]

    # rent[m] is 1 when the company rents machine m, and 0 when it does not
    rent = [model.addVar(f"rent_{m}", vtype="B") for m in machines]

    # z is the company's profit after paying the rent of the machines. Its upper bound is the
    # profit of every product made at its maximum, with no rent. Its lower bound 0 is only a
    # bound on the optimum: making nothing and renting nothing is allowed and gives 0, so the
    # best z is at least 0. A plan that loses money has a smaller z, which lb=0 excludes; that
    # does not change the optimum.
    z = model.addVar("z", vtype="I", lb=0,
                     ub=sum(max(profit[p], 0) * max_production for p in products))

    # The products made use no more labour hours, or cloth, than the company has.
    for r in resources:
        model.addCons(quicksum(use[p][r] * made[p] for p in products) <= capacity[r])

    # A product is made only on a rented machine: when its machine is not rented
    # (rent = 0), no unit of that product is made.
    for p in products:
        model.addConsIndicator(made[p] <= 0, binvar=rent[needs_machine[p]], activeone=False)

    # z is computed as the profit from the products made minus the rent of the machines rented.
    model.addCons(z == quicksum(profit[p] * made[p] for p in products)
                  - quicksum(renting_cost[m] * rent[m] for m in machines))

    # The company wants the largest profit after rent, so maximise z.
    model.setObjective(z, "maximize")

    return model, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
