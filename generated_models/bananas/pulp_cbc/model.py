# bananas: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install pulp numpy`) with:
#   python bananas.py

import pulp


def create_model(instance):
    """Buy exactly 100 fruits for exactly 100 dollars, at least one of each kind, taking
    as few bananas and apples as possible. Bananas cost 3 dollars for 5, oranges 5 dollars
    for 7, mangoes 7 dollars for 9 and apples 9 dollars for 3."""
    # Money is counted in units of 1/945 dollar, so that every price is a whole number.
    unit = 3 * 5 * 7 * 9

    # Price of one fruit of each kind, in those units: banana, orange, mango, apple.
    prices = [3 * unit // 5, 5 * unit // 7, 7 * unit // 9, 9 * unit // 3]

    problem = pulp.LpProblem("bananas", pulp.LpMinimize)

    # The number bought of each kind, from 1 to 100.
    bananas = pulp.LpVariable("bananas", 1, 100, cat="Integer")
    oranges = pulp.LpVariable("oranges", 1, 100, cat="Integer")
    mangoes = pulp.LpVariable("mangoes", 1, 100, cat="Integer")
    apples = pulp.LpVariable("apples", 1, 100, cat="Integer")

    # the four counts, in the same order as prices
    fruits = [bananas, oranges, mangoes, apples]

    # 100 fruits in all.
    problem += pulp.lpSum(fruits) == 100

    # Together they cost exactly 100 dollars.
    problem += pulp.lpSum(p * f for p, f in zip(prices, fruits)) == 100 * unit

    # Bananas and apples are disliked, so buy as few of them as possible.
    problem += bananas + apples

    return problem, {
        "bananas": bananas, "oranges": oranges,
        "mangoes": mangoes, "apples": apples,
    }


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
