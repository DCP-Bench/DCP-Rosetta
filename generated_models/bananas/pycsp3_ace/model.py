# bananas: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python bananas.py

from pycsp3 import *


def create_model(instance):
    """Buy exactly 100 fruits for exactly 100 dollars, buying every kind of fruit at least once,
    and minimise the number of bananas and apples bought together."""
    n_fruits = 100                   # the fruits to buy
    n_dollars = 100                  # the money to spend
    # Money is counted in units of 1/315 dollar: 315 is the least common multiple of 5, 7, 9 and 3,
    # so every price below is a whole number of units.
    unit = 315
    budget = n_dollars * unit

    # Price of one fruit in units of 1/315 dollar: 5 bananas cost 3 dollars, 7 oranges 5 dollars,
    # 9 mangoes 7 dollars, 3 apples 9 dollars.
    banana_price = 3 * unit // 5
    orange_price = 5 * unit // 7
    mango_price = 7 * unit // 9
    apple_price = 9 * unit // 3

    # The number of each fruit bought: every kind at least once, and at most all the fruits.
    bananas = Var(dom=range(1, n_fruits + 1))
    oranges = Var(dom=range(1, n_fruits + 1))
    mangoes = Var(dom=range(1, n_fruits + 1))
    apples = Var(dom=range(1, n_fruits + 1))

    satisfy(
        # 100 fruits in total.
        bananas + oranges + mangoes + apples == n_fruits,
        # 100 dollars in total.
        banana_price * bananas + orange_price * oranges + mango_price * mangoes + apple_price * apples == budget,
    )

    # The number of bananas and apples together should be as small as possible.
    minimize(bananas + apples)

    return {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
