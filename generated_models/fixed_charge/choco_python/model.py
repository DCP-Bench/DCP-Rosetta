# fixed_charge: a Choco-solver (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python fixed_charge.py fixed_charge.json

from pychoco.model import Model


def create_model(instance):
    """A company manufactures shirts, shorts and pants. Each product needs some
    labor and cloth from limited capacities, and can only be made on a machine
    the company rents at a fixed cost. Choose the machines to rent and how much
    of each product to make, to maximize the profit after the renting costs."""
    n_products = instance["num_products"]        # the number of products
    n_machines = instance["num_machines"]        # the number of machines
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: the amount of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p]: [profit per unit of product p, the machine it needs]
    use = instance["use"]                        # use[p][r]: the amount of resource r that one unit of product p needs

    model = Model()

    # rent[m] is true when machine m is rented
    rent = [model.boolvar(name=f"rent_{m}") for m in range(n_machines)]
    # produce[p] is the number of units of product p made
    produce = [model.intvar(0, max_production, name=f"produce_{p}") for p in range(n_products)]

    # The units made use no more of each resource than the company has.
    for r in range(len(capacity)):
        model.scalar(produce, [use[p][r] for p in range(n_products)], "<=", capacity[r]).post()

    # A product can only be made on its machine, and only if that machine is rented.
    for p in range(n_products):
        model.scalar([produce[p], rent[product[p][1]]], [1, -max_production], "<=", 0).post()

    # The profit: the units made, each at its profit, minus the renting cost of each rented machine.
    # z is the profit, between 0 and 10000.
    z = model.intvar(0, 10000, name="z")
    model.scalar(
        produce + rent,
        [product[p][0] for p in range(n_products)] + [-cost for cost in renting_cost],
        "=",
        z,
    ).post()

    return model, {"z": z}, {"objective": z, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
