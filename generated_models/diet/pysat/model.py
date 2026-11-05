# diet: a PySAT (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python diet.py diet.json

from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

# Nutrient content of one portion of each food: chocolate cake, chocolate ice cream,
# cola and pineapple cheesecake.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]  # ounces
SUGAR = [2, 2, 4, 4]      # ounces
FAT = [2, 4, 1, 5]        # ounces

# Diets costing more than this are not considered.
MAX_COST = 1000


def create_model(instance):
    """Given the prices and the nutritional requirements for each food, find the
    diet of lowest cost that meets every requirement."""
    n = instance["n"]            # the number of foods
    price = instance["price"]    # price[i]: the price of one portion of food i
    limits = instance["limits"]  # limits[k]: the least amount of nutrient k the diet must contain
    contents = [CALORIES, CHOCOLATE, SUGAR, FAT]

    pool = IDPool()  # names the variables of the model

    # amount[i] is the number of portions of food i in the diet. No optimal diet buys more
    # portions of a food than the largest number that meets one requirement on its own.
    amount = []
    for i in range(n):
        enough = [-(-limits[j] // contents[j][i]) for j in range(len(contents))
                  if contents[j][i] > 0]
        top = max(enough + [1])
        amount.append(Integer(f"x_{i}", 0, top, encoding="order", vpool=pool))

    # Every price is a multiple of unit, the largest common divisor of the prices (1 when
    # all prices are zero). The cost of a diet is then counted in units of unit.
    unit = 0
    for p in price:
        unit = gcd(unit, p)
    unit = unit or 1
    cost_units = Integer("cost_units", 0, max(MAX_COST // unit, 1), encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=amount + [cost_units], vpool=pool)  # constraints on the diet

    # The diet contains at least the required amount of each nutrient.
    for j, content in enumerate(contents):
        engine.add_linear(sum(content[i] * amount[i] for i in range(n)) >= limits[j])

    # The cost in units is the price of the portions bought, in units.
    engine.add_linear(sum((price[i] // unit) * amount[i] for i in range(n)) - cost_units == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # cost is the price of the diet, which is cost_units times unit.
    cost = Integer("cost", 0, MAX_COST, encoding="coupled", vpool=pool)
    formula.extend(cost.domain_clauses())
    # A diet costs at least v exactly when its cost in units is at least ceil(v / unit).
    for v in range(1, MAX_COST + 1):
        k = -(-v // unit)
        if k <= cost_units.ub:
            formula.append([-cost.ge(v), cost_units.ge(k)])
            formula.append([cost.ge(v), -cost_units.ge(k)])
        else:
            formula.append([-cost.ge(v)])
    if MAX_COST // unit + 1 <= cost_units.ub:
        formula.append([-cost_units.ge(MAX_COST // unit + 1)])

    # Minimise the price of the diet: each portion bought costs the price of its food.
    for i in range(n):
        if price[i] > 0:
            for v in range(1, amount[i].ub + 1):
                formula.append([-amount[i].ge(v)], weight=price[i])

    # The objective in the problem's terms: the price of the diet (as RC2's cost).
    return formula, {"cost": cost}, cost


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
