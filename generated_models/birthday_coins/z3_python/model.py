# birthday_coins: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install z3-solver numpy`) with:
#   python birthday_coins.py

import z3


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to one
    pound, five shillings and six pence. How many half-crowns was he given?"""
    pence_per_shilling = 12
    pence_per_pound = 20 * pence_per_shilling
    sixpence = 6

    # Worth in pence of a half-crown, a shilling and a sixpence
    values = [2 * pence_per_shilling + sixpence, pence_per_shilling, sixpence]
    total_value = pence_per_pound + 5 * pence_per_shilling + sixpence
    total_coins = 15

    # coins[c]: how many coins of each kind Tommy was given
    coins = [z3.Int(f"coins_{c}") for c in range(len(values))]

    solver = z3.Solver()

    # Each kind has between 0 and 15 coins.
    solver.add([z3.And(0 <= n, n <= total_coins) for n in coins])

    # The coins are worth one pound, five shillings and six pence together.
    solver.add(z3.Sum([v * n for v, n in zip(values, coins)]) == total_value)

    # He was given 15 coins in all.
    solver.add(z3.Sum(coins) == total_coins)

    half_crowns = coins[0]
    return solver, {"half_crowns": half_crowns}


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
