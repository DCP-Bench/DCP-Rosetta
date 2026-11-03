# bananas: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install z3-solver numpy`) with:
#   python bananas.py

import z3


def create_model(instance):
    """Buy exactly 100 fruits for exactly 100 dollars, at least one of each kind.
    Bananas cost 3 dollars for 5, oranges 5 dollars for 7, mangoes 7 dollars for 9
    and apples 9 dollars for 3. Bananas and apples are disliked, so buy as few of
    them as possible."""
    # Prices in units of 1/945 dollar, which makes them whole numbers: banana 3/5 dollar
    # is 567, orange 5/7 is 675, mango 7/9 is 735, apple 9/3 is 2835.
    prices = [567, 675, 735, 2835]

    # The number of bananas, oranges, mangoes and apples bought, in the order of prices.
    bananas, oranges, mangoes, apples = z3.Ints("bananas oranges mangoes apples")
    fruits = [bananas, oranges, mangoes, apples]

    solver = z3.Optimize()

    # At least one of each kind, and at most 100 of each.
    solver.add([z3.And(1 <= f, f <= 100) for f in fruits])

    # 100 fruits in total.
    solver.add(z3.Sum(fruits) == 100)
    # They cost exactly 100 dollars, which is 100 * 945 units.
    solver.add(z3.Sum([p * f for p, f in zip(prices, fruits)]) == 100 * 945)

    # Bananas and apples are disliked, so the objective counts them.
    disliked = bananas + apples

    solver.minimize(disliked)

    return solver, {"bananas": bananas, "oranges": oranges,
                    "mangoes": mangoes, "apples": apples}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
