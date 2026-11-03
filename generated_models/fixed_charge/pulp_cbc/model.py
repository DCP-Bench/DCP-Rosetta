# fixed_charge: a PuLP (Python) model from DCP Rosetta.
# Download the `fixed_charge.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fixed_charge.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python fixed_charge.py fixed_charge.json

import pulp


def create_model(instance):
    """A company makes products, each needing some of each limited resource (labor
    and cloth). A product can only be made on its machine, and the company must rent
    a machine at a fixed cost to use it. Choose the machines to rent and how much of
    each product to make, to maximize the profit on the products minus the renting
    costs."""
    num_machines = instance["num_machines"]      # the number of machines
    num_products = instance["num_products"]      # the number of products
    renting_cost = instance["renting_cost"]      # renting_cost[m] is the cost of renting machine m
    capacity = instance["capacity"]              # capacity[r] is the amount of resource r the company has
    max_production = instance["max_production"]  # the most units of one product that can be made
    product = instance["product"]                # product[p][0] is the profit per unit of product p, and product[p][1] its machine
    use = instance["use"]                        # use[p][r] is the amount of resource r that one unit of product p needs

    problem = pulp.LpProblem("fixed_charge", pulp.LpMaximize)

    # rent[m] is 1 when machine m is rented, and 0 when not
    rent = [pulp.LpVariable(f"rent_{m}", cat="Binary") for m in range(num_machines)]
    # produce[p] is the number of units of product p made
    produce = [pulp.LpVariable(f"produce_{p}", 0, max_production, cat="Integer") for p in range(num_products)]
    # profit is the profit on the products minus the renting costs. It stays between the
    # worst case, where every product loses its maximum amount, and the best case, where
    # every product makes its maximum profit.
    profit_low = sum(min(0, product[p][0]) for p in range(num_products)) * max_production - sum(renting_cost)
    profit_high = sum(max(0, product[p][0]) for p in range(num_products)) * max_production
    z = pulp.LpVariable("z", profit_low, profit_high, cat="Integer")

    # The profit is the profit on the products minus the renting costs of the rented machines.
    problem += z == pulp.lpSum(product[p][0] * produce[p] for p in range(num_products)) \
        - pulp.lpSum(renting_cost[m] * rent[m] for m in range(num_machines))

    # The products together use no more of each resource than the company has.
    for r in range(len(capacity)):
        problem += pulp.lpSum(use[p][r] * produce[p] for p in range(num_products)) <= capacity[r]

    # A product is made only when its machine is rented.
    for p in range(num_products):
        problem += produce[p] <= max_production * rent[product[p][1]]

    # Maximize the profit.
    problem += z

    return problem, {"z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
