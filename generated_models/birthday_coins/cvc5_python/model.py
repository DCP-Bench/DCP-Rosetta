# birthday_coins: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install cvc5 numpy`) with:
#   python birthday_coins.py

import cvc5.pythonic as c5


def create_model(instance):
    """Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence) or a
    sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
    worth £1 5s 6d. How many half-crowns could he have been given?"""
    # The instance has no fields: every number below is from the problem statement.
    half_crowns = c5.Int("half_crowns")  # how many half-crowns he was given
    shillings = c5.Int("shillings")      # how many shillings
    sixpences = c5.Int("sixpences")      # how many sixpences

    solver = c5.Solver()

    # A kind may be absent, so each count is at least 0; none can exceed the 15 coins.
    solver.add([c5.And(0 <= k, k <= 15) for k in (half_crowns, shillings, sixpences)])

    # He was given 15 coins.
    solver.add(half_crowns + shillings + sixpences == 15)

    # They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    # shilling 12 and a sixpence 6.
    solver.add(30 * half_crowns + 12 * shillings + 6 * sixpences == 306)

    return solver, {"half_crowns": half_crowns}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
