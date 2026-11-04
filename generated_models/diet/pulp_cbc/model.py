# diet: a PuLP (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python diet.py diet.json

import pulp


def create_model(instance):
    """Given the prices and the nutritional requirements (at least) for each
    nutrition type, find the diet of lowest cost."""
    n_foods = instance["n"]      # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain, in the order of nutrients

    # nutrients[k][i]: the amount of nutrient k in one portion of food i, for
    # chocolate cake, chocolate ice cream, cola and pineapple cheesecake
    nutrients = [
        [400, 200, 150, 500],  # calories
        [3, 2, 0, 0],          # chocolate (ounces)
        [2, 2, 4, 4],          # sugar (ounces)
        [2, 4, 1, 5],          # fat (ounces)
    ]

    problem = pulp.LpProblem("diet", pulp.LpMinimize)

    # amount[i] is the number of portions of food i in the diet
    amount = [pulp.LpVariable(f"amount_{i}", 0, 10000, cat="Integer") for i in range(n_foods)]
    # cost is the price of the diet
    cost = pulp.LpVariable("cost", 0, 1000, cat="Integer")

    # The diet has at least the required amount of each nutrient.
    for row, least in zip(nutrients, limits):
        problem += pulp.lpSum(row[i] * amount[i] for i in range(n_foods)) >= least
    # The cost is the price of each food times its portions, added up.
    problem += cost == pulp.lpSum(price[i] * amount[i] for i in range(n_foods))

    # The objective: the cheapest diet.
    problem += cost

    return problem, {"cost": cost}


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
