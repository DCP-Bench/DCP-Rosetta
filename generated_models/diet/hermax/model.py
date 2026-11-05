# diet: a hermax (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install hermax`):
#   python diet.py diet.json

from hermax.model import Model

# Nutrition content of one unit of each food, from the problem statement's table.
# NUTRITION[j][i] is the amount of nutrient j in one unit of food i.
# Nutrients (rows): calories, chocolate (ounces), sugar (ounces), fat (ounces).
# Foods (columns): chocolate cake (1 slice), chocolate ice cream (1 scoop),
# cola (1 bottle), pineapple cheesecake (1 piece).
NUTRITION = [
    [400, 200, 150, 500],
    [3, 2, 0, 0],
    [2, 2, 4, 4],
    [2, 4, 1, 5],
]


def create_model(instance):
    """Choose whole units of each food so that the diet reaches the minimum amount of every
    nutrient, at the lowest total price."""
    n = instance["n"]            # n: number of foods (4, matching the table above)
    price = instance["price"]    # price[i]: cost of one unit of food i
    limits = instance["limits"]  # limits[j]: minimum amount of nutrient j the diet must provide

    # Upper bound on the units of each food. An optimal diet never needs more than u[i] units of
    # food i: u[i] units of food i alone cover every nutrient j it contains (NUTRITION[j][i] > 0),
    # so any further unit can be removed. Removing a unit never raises the cost because prices
    # are non-negative.
    u = []
    for i in range(n):
        bounds = [-(-limits[j] // NUTRITION[j][i]) for j in range(len(limits)) if NUTRITION[j][i] > 0]
        u.append(max(bounds))

    m = Model()

    # count[i] is the number of units of food i in the diet
    count = [m.int(f"count_{i}", 0, u[i]) for i in range(n)]

    # Each nutrient must reach at least its minimum requirement.
    for j in range(len(limits)):
        m &= (sum(NUTRITION[j][i] * count[i] for i in range(n)) >= limits[j])

    # The total price of the diet: the cost of every food times the units bought.
    total_cost = sum(price[i] * count[i] for i in range(n))

    # Minimise the total cost of the diet.
    m.obj += total_cost

    # The objective in the problem's terms: the total cost of the diet, the cost minimised above.
    return m, {"cost": total_cost}, total_cost


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
