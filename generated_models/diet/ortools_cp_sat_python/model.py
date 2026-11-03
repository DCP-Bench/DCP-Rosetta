# diet: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install ortools`):
#   python diet.py diet.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given the prices and the nutritional requirements (at least) for each
    nutrition type, find the diet of lowest cost."""
    n_foods = instance["n"]      # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain

    # nutrients[k][i]: the amount of nutrient k in one portion of food i. The foods are
    # chocolate cake, chocolate ice cream, cola and pineapple cheesecake.
    nutrients = [
        [400, 200, 150, 500],  # calories
        [3, 2, 0, 0],          # chocolate (ounces)
        [2, 2, 4, 4],          # sugar (ounces)
        [2, 4, 1, 5],          # fat (ounces)
    ]

    model = cp_model.CpModel()

    # amount[i] is the number of portions of food i in the diet
    amount = [model.new_int_var(0, 10000, f"x_{i}") for i in range(n_foods)]
    # cost is the total price of the diet
    cost = model.new_int_var(0, 1000, "cost")

    # The diet contains at least the required amount of each nutrient.
    for row, least in zip(nutrients, limits):
        model.add(sum(row[i] * amount[i] for i in range(n_foods)) >= least)
    # The cost is the price of all portions together.
    model.add(cost == sum(price[i] * amount[i] for i in range(n_foods)))

    # Choose the cheapest diet.
    model.minimize(cost)

    return model, {"cost": cost}


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
