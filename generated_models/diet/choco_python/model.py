# diet: a Choco-solver (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python diet.py diet.json

from pychoco.model import Model


def create_model(instance):
    """Choose how many units of each food to buy so that the diet contains at
    least the required amount of every nutrient, at the lowest total cost."""
    n = instance["n"]            # the number of foods
    price = instance["price"]    # price[i]: the price in cents of one unit of food i
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain

    # Nutrient content of one unit of each food, in the order chocolate cake,
    # chocolate ice cream, cola and pineapple cheesecake.
    calories = [400, 200, 150, 500]
    chocolate = [3, 2, 0, 0]  # ounces
    sugar = [2, 2, 4, 4]      # ounces
    fat = [2, 4, 1, 5]        # ounces

    model = Model()

    # x[i] is the number of units of food i bought, at most 10000
    x = [model.intvar(0, 10000, name=f"x_{i}") for i in range(n)]

    # The diet contains at least the required amount of each nutrient.
    for amounts, least in zip((calories, chocolate, sugar, fat), limits):
        model.scalar(x, amounts[:n], ">=", least).post()

    # cost is the total price of the diet in cents, at most 1000
    cost = model.intvar(0, 1000, name="cost")
    # The cost is the price of all units bought.
    model.scalar(x, price, "=", cost).post()

    # Buy the cheapest diet.
    return model, {"cost": cost}, {"objective": cost, "maximize": False}


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
