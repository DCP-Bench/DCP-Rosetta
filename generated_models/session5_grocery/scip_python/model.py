# session5_grocery: a SCIP (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session5_grocery.py session5_grocery.json

import math

from pyscipopt import Model, quicksum


def create_model(instance):
    """A kid buys some items. The cashier multiplies the item prices instead of
    adding them, and the total comes to the same either way. Find the prices of
    the items, in whole cents, whose sum and whose product both equal total_price."""
    num_items = instance["num_items"]      # the number of items the kid bought
    total_price = instance["total_price"]  # the total in cents, by adding and by multiplying

    model = Model("session5_grocery")

    # prices[i] is the price of item i in cents. Bounds: prices are not negative
    # (an assumption about prices), so no price is above the sum total_price, and
    # no price is 0, since the product is total_price * 100**(n-1) > 0.
    prices = [model.addVar(f"price_{i}", vtype="I", lb=1, ub=total_price)
              for i in range(num_items)]

    # Adding the prices gives the total.
    model.addCons(quicksum(prices) == total_price)

    # Multiplying the prices gives the same total. The product is read in cents:
    # each price in dollars is price / 100, so the product of n prices is
    # product / 100**n dollars, which is product / 100**(n-1) cents. Hence
    # product == total_price * 100**(n-1). Example: 200 and 200 cents multiply
    # to 2.00 * 2.00 = 4.00 dollars = 400 cents.
    model.addCons(math.prod(prices) == total_price * 100 ** (num_items - 1))

    # No objective: the question asks for prices that fit, not for the best ones.
    return model, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
