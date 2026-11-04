# fixed_charge: a Z3 (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python fixed_charge.py fixed_charge.json

import z3


def create_model(instance):
    """A company makes shirts, shorts and pants. Each product needs labor and
    cloth from limited capacities, and can only be made on a machine the company
    rents at a fixed cost. Choose the machines to rent and how much of each
    product to make so that the profit, after the renting costs, is as large as
    possible."""
    n_products = instance["num_products"]        # the number of products
    n_machines = instance["num_machines"]        # the number of machines
    renting_cost = instance["renting_cost"]      # renting_cost[m]: the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r]: how much of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p][0]: profit per unit of product p; product[p][1]: its machine
    use = instance["use"]                        # use[p][r]: how much of resource r one unit of product p needs

    # rent[m] is true when the company rents machine m
    rent = [z3.Bool(f"rent_{m}") for m in range(n_machines)]
    # produce[p] is the number of units of product p made
    produce = [z3.Int(f"produce_{p}") for p in range(n_products)]
    # the total profit after the renting costs
    total_profit = z3.Int("total_profit")

    solver = z3.Optimize()

    # No negative production, and no more than max_production units of a product.
    solver.add([p >= 0 for p in produce] + [p <= max_production for p in produce])

    # The profit is in a loose range from 0 to 10000.
    solver.add(total_profit >= 0, total_profit <= 10000)

    # The total profit is the profit on the products minus the renting costs of the rented machines.
    solver.add(total_profit == z3.Sum([product[p][0] * produce[p] for p in range(n_products)])
               - z3.Sum([renting_cost[m] * z3.If(rent[m], 1, 0) for m in range(n_machines)]))

    # The products use no more of each resource than the company has.
    solver.add([z3.Sum([use[p][r] * produce[p] for p in range(n_products)]) <= capacity[r]
                for r in range(len(capacity))])

    # A product is only made on its machine, and only when that machine is rented.
    solver.add([produce[p] <= z3.If(rent[product[p][1]], max_production, 0)
                for p in range(n_products)])

    solver.maximize(total_profit)

    return solver, {"z": total_profit}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
