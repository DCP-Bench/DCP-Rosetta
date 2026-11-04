# bananas: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install ortools`) with:
#   python bananas.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Buy 100 fruits for exactly 100 dollars, at least one of each kind."""
    # Price of one fruit in units of 1/945 dollar:
    # banana 3/5 dollar = 567, orange 5/7 = 675, mango 7/9 = 735, apple 9/3 = 2835.
    prices = [567, 675, 735, 2835]

    model = cp_model.CpModel()

    # The number of bananas, oranges, mangoes and apples bought
    bananas = model.new_int_var(1, 100, "bananas")
    oranges = model.new_int_var(1, 100, "oranges")
    mangoes = model.new_int_var(1, 100, "mangoes")
    apples = model.new_int_var(1, 100, "apples")
    # the four counts, in the same order as prices
    fruits = [bananas, oranges, mangoes, apples]

    # 100 fruits in total.
    model.add(sum(fruits) == 100)
    # They cost exactly 100 dollars.
    model.add(sum(p * f for p, f in zip(prices, fruits)) == 100 * 945)

    # Buy as few bananas and apples as possible.
    model.minimize(bananas + apples)

    return model, {
        "bananas": bananas,
        "oranges": oranges,
        "mangoes": mangoes,
        "apples": apples,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
