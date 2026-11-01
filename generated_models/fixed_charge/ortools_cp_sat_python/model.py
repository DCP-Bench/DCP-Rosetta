# fixed_charge: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install ortools`):
#   python fixed_charge.py fixed_charge.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A company manufactures shirts, shorts and pants. Each product needs labor
    and cloth from limited capacities, and can only be made on a machine the
    company rents at a cost. Choose the machines to rent and how much of each
    product to make to maximize the profit after the renting costs."""
    n_products = instance["num_products"]        # the number of products
    n_machines = instance["num_machines"]        # the number of machines
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: the available amount of resource r
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p]: the profit per unit of product p and the machine that makes it
    use = instance["use"]                        # use[p][r]: the amount of resource r that one unit of product p needs

    model = cp_model.CpModel()

    # rent[m] is true when machine m is rented
    rent = [model.new_bool_var(f"rent_{m}") for m in range(n_machines)]
    # produce[p] is the number of units of product p made
    produce = [model.new_int_var(0, max_production, f"produce_{p}") for p in range(n_products)]
    # z is the profit
    z = model.new_int_var(0, 10000, "z")

    # The profit on the products, minus the renting costs of the rented machines.
    model.add(z == sum(product[p][0] * produce[p] for p in range(n_products))
              - sum(renting_cost[m] * rent[m] for m in range(n_machines)))

    # The products use no more of each resource than the company has.
    for r in range(len(capacity)):
        model.add(sum(use[p][r] * produce[p] for p in range(n_products)) <= capacity[r])

    # A product can only be made on its rented machine.
    for p in range(n_products):
        model.add(produce[p] <= max_production * rent[product[p][1]])

    # Maximize the profit.
    model.maximize(z)

    return model, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
