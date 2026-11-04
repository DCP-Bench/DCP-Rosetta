# diet: an Exact (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python diet.py diet.json

from exact import Exact


def create_model(instance):
    """Find the cheapest diet that contains at least the least amount of each
    nutrient, from chocolate cake, chocolate ice cream, cola and pineapple
    cheesecake."""
    n_foods = instance["n"]      # the number of foods
    price = instance["price"]    # price[j]: the price of one serving of food j
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain

    # macros[k][j]: the amount of nutrient k in one serving of food j, from the table of the problem,
    # with the foods in the order chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
    macros = [
        [400, 200, 150, 500],  # calories
        [3, 2, 0, 0],          # chocolate (ounces)
        [2, 2, 4, 4],          # sugar (ounces)
        [2, 4, 1, 5],          # fat (ounces)
    ]

    solver = Exact()

    # Exact identifies its variables by name.
    # x[j] is the number of servings of food j in the diet
    x = [f"x{j}" for j in range(n_foods)]
    for name in x:
        solver.addVariable(name, 0, 10000)

    # cost is the total price of the diet
    solver.addVariable("cost", 0, 1000)

    # The diet contains at least the least amount of each nutrient.
    for row, least in zip(macros, limits):
        solver.addConstraint([(row[j], x[j]) for j in range(n_foods) if row[j]], True, least)

    # The cost is the price of all servings together.
    solver.addConstraint(list(zip(price, x)) + [(-1, "cost")], True, 0, True, 0)

    # Choose the cheapest diet.
    solver.setObjective([(1, "cost")], minimize=True)

    return solver, {"cost": "cost"}


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
