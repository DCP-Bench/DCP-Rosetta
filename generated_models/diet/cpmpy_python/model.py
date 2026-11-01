# diet: a CPMpy model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python diet.py diet.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Given the prices and the nutritional requirements (at least) for each
    nutrition type, find the diet of lowest cost."""
    n = instance["n"]            # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain

    # Nutrition table from the problem statement: nutrients[k][i] is the amount of
    # nutrient k (calories, chocolate, sugar, fat) in one portion of food i
    # (chocolate cake, chocolate ice cream, cola, pineapple cheesecake).
    nutrients = np.array([
        [400, 200, 150, 500],  # calories
        [3, 2, 0, 0],          # chocolate (ounces)
        [2, 2, 4, 4],          # sugar (ounces)
        [2, 4, 1, 5],          # fat (ounces)
    ])

    # amount[i] is the number of portions of food i in the diet
    amount = cp.intvar(0, 10000, shape=n, name="amount")
    # cost is the total price of the diet
    cost = cp.intvar(0, 1000, name="cost")

    model = cp.Model()
    # The diet contains at least the required amount of each nutrient.
    for k in range(len(limits)):
        model.add(cp.sum(amount * nutrients[k]) >= limits[k])
    # The cost is the sum of the prices of all portions.
    model.add(cost == cp.sum(amount * price))
    # Choose the cheapest diet.
    model.minimize(cost)

    return model, {"cost": cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
