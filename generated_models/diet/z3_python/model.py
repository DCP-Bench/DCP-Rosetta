# diet: a Z3 (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python diet.py diet.json

import z3


def create_model(instance):
    """Given the price of each food and the least amount of each nutrient the diet
    must contain, find the cheapest diet."""
    n = instance["n"]            # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # the least calories, chocolate, sugar and fat the diet must contain

    # Calories in one portion of each food: chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
    calories = [400, 200, 150, 500]
    # Ounces of chocolate in one portion of each food.
    chocolate = [3, 2, 0, 0]
    # Ounces of sugar in one portion of each food.
    sugar = [2, 2, 4, 4]
    # Ounces of fat in one portion of each food.
    fat = [2, 4, 1, 5]

    # amount[i] is the number of portions of food i in the diet
    amount = [z3.Int(f"amount_{i}") for i in range(n)]
    # cost is the total price of the diet
    cost = z3.Int("cost")

    solver = z3.Optimize()

    # A diet has between 0 and 10000 portions of each food, and a cost between 0 and 1000.
    solver.add([a >= 0 for a in amount] + [a <= 10000 for a in amount])
    solver.add(cost >= 0, cost <= 1000)

    # The diet contains at least the required amount of each nutrient.
    for nutrient, least in zip((calories, chocolate, sugar, fat), limits):
        solver.add(z3.Sum([nutrient[i] * amount[i] for i in range(n)]) >= least)

    # The cost is the price of all the portions together.
    solver.add(cost == z3.Sum([price[i] * amount[i] for i in range(n)]))

    solver.minimize(cost)

    return solver, {"cost": cost}


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
