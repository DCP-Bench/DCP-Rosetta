# bananas: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python bananas.py

from pyscipopt import Model


def create_model(instance):
    """Buy exactly 100 fruits for exactly 100 dollars, buying at least one of
    each kind, and as few bananas and apples as possible (they are disliked).
    The problem has no instance data: every number is stated in the description,
    so `instance` is not read."""
    # Prices from the statement, in dollars:
    #   5 bananas cost 3 dollars, 7 oranges cost 5, 9 mangoes cost 7, 3 apples cost 9.
    # Price per fruit in dollars: bananas 3/5, oranges 5/7, mangoes 7/9, apples 9/3 = 3.
    # To keep every coefficient an integer, all money is counted in units of 1/315
    # dollar (315 = lcm of 5, 7, 9 and 3). The budget of 100 dollars is then 31500.
    unit_per_dollar = 315
    budget_units = 100 * unit_per_dollar   # 31500
    banana_price = 3 * unit_per_dollar // 5   # 189: 3/5 dollar each
    orange_price = 5 * unit_per_dollar // 7   # 225: 5/7 dollar each
    mango_price = 7 * unit_per_dollar // 9    # 245: 7/9 dollar each
    apple_price = 9 * unit_per_dollar // 3    # 945: 3 dollars each

    # Fruits to buy in total, from the statement.
    total_fruits = 100

    model = Model("bananas")

    # Each variable is the number of that fruit bought.
    # Bounds: at least 1 because all types must be bought (from the statement);
    # at most 100 because the 100 fruits are all there is to buy.
    bananas = model.addVar(name="bananas", vtype="I", lb=1, ub=total_fruits)  # number of bananas
    oranges = model.addVar(name="oranges", vtype="I", lb=1, ub=total_fruits)  # number of oranges
    mangoes = model.addVar(name="mangoes", vtype="I", lb=1, ub=total_fruits)  # number of mangoes
    apples = model.addVar(name="apples", vtype="I", lb=1, ub=total_fruits)    # number of apples

    # Exactly 100 fruits are purchased.
    model.addCons(bananas + oranges + mangoes + apples == total_fruits)

    # The purchase costs exactly 100 dollars (the budget is spent in full, which is
    # the reading that makes the puzzle's numbers meet; a cap would leave slack).
    model.addCons(
        banana_price * bananas + orange_price * oranges
        + mango_price * mangoes + apple_price * apples == budget_units
    )

    # Minimise the bananas and apples bought, since they are not liked.
    model.setObjective(bananas + apples, "minimize")

    outputs = {
        "apples": apples,
        "bananas": bananas,
        "mangoes": mangoes,
        "oranges": oranges,
    }
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
