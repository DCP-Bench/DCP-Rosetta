# fixed_charge: a Python-MIP (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python fixed_charge.py fixed_charge.json

import mip


def create_model(instance):
    """A company manufactures shirts, shorts and pants. Each product needs labor
    and cloth from limited capacities, and can only be made on a machine the
    company rents at a fixed cost. Choose the machines to rent and how much of
    each product to make to maximize the profit after the renting costs."""
    n_products = instance["num_products"]        # the number of products
    n_machines = instance["num_machines"]        # the number of machines
    n_resources = len(instance["resources"])     # the number of limited resources: labor and cloth
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: the amount of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    use = instance["use"]                        # use[p][r]: the amount of resource r one unit of product p needs
    products = instance["products"]              # products[p]: the type of product p, shirt, shorts or pants

    # profit[p]: the profit on one unit of product p, before the renting costs
    profit = [instance["product"][p][0] for p in range(n_products)]

    # The machine that makes each product type: shirts on shirtM, shorts on shortM, pants on pantM.
    machine_of_type = {
        instance["shirt"]: instance["shirtM"],
        instance["shorts"]: instance["shortM"],
        instance["pants"]: instance["pantM"],
    }
    # machine_of[p]: the machine that product p is made on
    machine_of = [machine_of_type[t] for t in products]

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[p] is how many units of product p are made.
    x = [
        model.add_var(f"x_{p}", lb=0, ub=max_production, var_type=mip.INTEGER)
        for p in range(n_products)
    ]

    # rent[m] is 1 when machine m is rented, and 0 when not.
    rent = [model.add_var(f"rent_{m}", var_type=mip.BINARY) for m in range(n_machines)]

    # A product is made only on a rented machine.
    for p in range(n_products):
        model += x[p] <= max_production * rent[machine_of[p]]

    # The products use no more of each resource than the company has.
    for r in range(n_resources):
        model += mip.xsum(use[p][r] * x[p] for p in range(n_products)) <= capacity[r]

    # z is the profit: the products' profit minus the renting costs of the rented machines.
    # It lies between the loss from renting every machine and the profit from making the most of every product.
    z_lb = -sum(renting_cost)
    z_ub = sum(profit[p] * max_production for p in range(n_products))
    z = model.add_var("z", lb=z_lb, ub=z_ub, var_type=mip.INTEGER)
    model += z == (
        mip.xsum(profit[p] * x[p] for p in range(n_products))
        - mip.xsum(renting_cost[m] * rent[m] for m in range(n_machines))
    )

    model.objective = z

    return model, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
