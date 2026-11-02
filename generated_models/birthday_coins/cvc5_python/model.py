# birthday_coins: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install cvc5 numpy`) with:
#   python birthday_coins.py

import cvc5.pythonic as c5


def create_model(instance):
    """Tommy was given 15 coins for his birthday: half-crowns, shillings and sixpences. They
    add up to one pound, five shillings and six pence. How many half-crowns was he given?"""
    # Money in pence.
    pence_in_shilling = 12
    pence_in_sixpence = 6
    pence_in_half_crown = 2 * pence_in_shilling + pence_in_sixpence  # two shillings and sixpence
    pence_in_pound = 20 * pence_in_shilling
    total_pence = pence_in_pound + 5 * pence_in_shilling + pence_in_sixpence  # one pound, five shillings and six pence
    n_coins = 15  # the number of coins Tommy was given

    # How many half-crowns, shillings and sixpences Tommy was given.
    half_crowns, shillings, sixpences = c5.Ints("half_crowns shillings sixpences")

    solver = c5.Solver()

    # The coins number 15 in all.
    solver.add(half_crowns + shillings + sixpences == n_coins)

    # He was given coins of each kind.
    solver.add(half_crowns >= 1, shillings >= 1, sixpences >= 1)

    # The coins add up to the total.
    solver.add(
        pence_in_half_crown * half_crowns + pence_in_shilling * shillings
        + pence_in_sixpence * sixpences == total_pence
    )

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
