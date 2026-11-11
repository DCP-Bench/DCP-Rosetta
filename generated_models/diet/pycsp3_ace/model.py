# diet: a PyCSP3 model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python diet.py diet.json

from pycsp3 import *


def create_model(instance):
    """Given the prices and the nutritional requirements (at least) for each nutrition
    type, what is the optimal diet? The optimal diet is to minimize the cost of the
    products. Each food is bought in a whole number of units."""
    n_foods = instance["n"]          # the number of foods in the table
    price = instance["price"]        # price[j]: the price of one unit of food j
    limits = instance["limits"]      # limits[i]: the least amount of nutrition type i the diet must give

    # The nutrients in one unit of each food, as the statement's table gives them, in the
    # order calories, chocolate (ounces), sugar (ounces), fat (ounces).
    nutrients = [
        [400, 3, 2, 2],   # Chocolate Cake (1 slice)
        [200, 2, 2, 4],   # Chocolate ice cream (1 scoop)
        [150, 0, 4, 1],   # Cola (1 bottle)
        [500, 0, 4, 5],   # Pineapple cheesecake (1 piece)
    ]

    # max_units: the most units of one food the diet can need. Taken as max(limits): a food
    # with more units than that is cut to max(limits) units without breaking a requirement,
    # since any nutrient it contains in amount at least 1 then already reaches its limit,
    # and the cost does not rise, so no optimal diet is lost.
    max_units = max(limits)

    # units[j] is the number of units of food j that are bought
    units = VarArray(size=n_foods, dom=range(max_units + 1))

    # cost is the price of the bought foods; at most every food bought in max_units units.
    max_cost = sum(price) * max_units
    cost = Var(dom=range(max_cost + 1))

    # The diet gives at least the required amount of each nutrition type.
    satisfy(
        Sum(nutrients[j][i] * units[j] for j in range(n_foods)) >= limits[i]
        for i in range(len(limits))
    )

    # The cost is the price of the units bought.
    satisfy(cost == Sum(price[j] * units[j] for j in range(n_foods)))

    # Minimize the cost of the diet.
    minimize(cost)

    return {"cost": cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
