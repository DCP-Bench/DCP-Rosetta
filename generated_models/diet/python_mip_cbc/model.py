# diet: a Python-MIP (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python diet.py diet.json

import mip

# Nutrition table from the problem: NUTRIENTS[i][j] is the amount of nutrient j
# (calories, chocolate in ounces, sugar in ounces, fat in ounces) in one portion
# of food i (chocolate cake, chocolate ice cream, cola, pineapple cheesecake).
NUTRIENTS = [
    [400, 3, 2, 2],
    [200, 2, 2, 4],
    [150, 0, 4, 1],
    [500, 0, 4, 5],
]


def create_model(instance):
    """Given the prices and the minimum amounts of calories, chocolate, sugar and
    fat, find the diet of whole portions that meets the minimums at the lowest cost."""
    n_foods = instance["n"]      # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # limits[j]: the least amount of nutrient j the diet must contain
    n_nutrients = len(limits)    # the number of nutrients with a minimum

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # The most portions of food i that could be needed: enough to meet the minimum of
    # any one nutrient alone. More than that only adds cost.
    max_portions = []
    for i in range(n_foods):
        most = 0
        for j in range(n_nutrients):
            if NUTRIENTS[i][j] > 0:
                most = max(most, -(-limits[j] // NUTRIENTS[i][j]))
        max_portions.append(most)

    # portions[i] is the number of portions of food i in the diet
    portions = [
        model.add_var(f"portions_{i}", lb=0, ub=max_portions[i], var_type=mip.INTEGER)
        for i in range(n_foods)
    ]
    # cost is the total price of the diet
    cost = model.add_var(
        "cost", lb=0, ub=sum(price[i] * max_portions[i] for i in range(n_foods)), var_type=mip.INTEGER
    )

    # The diet contains at least the minimum amount of each nutrient.
    for j in range(n_nutrients):
        model.add_constr(
            mip.xsum(NUTRIENTS[i][j] * portions[i] for i in range(n_foods)) >= limits[j],
            name=f"requirement_{j}",
        )

    # The cost is the price of all portions together.
    model.add_constr(
        cost == mip.xsum(price[i] * portions[i] for i in range(n_foods)),
        name="total_cost",
    )

    # Choose the cheapest diet.
    model.objective = cost

    return model, {"cost": cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
