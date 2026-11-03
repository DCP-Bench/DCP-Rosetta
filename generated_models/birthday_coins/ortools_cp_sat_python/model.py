# birthday_coins: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install ortools`) with:
#   python birthday_coins.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Tommy was given 15 old British coins (half-crowns, shillings and sixpences). Together
    they make one pound, five shillings and six pence. How many half-crowns was he given?"""
    # Money is counted in pence.
    shilling = 12          # pence in a shilling
    pound = 20 * shilling  # pence in a pound
    sixpence = 6           # pence in a sixpence
    # pence of a half-crown, a shilling and a sixpence
    values = [2 * shilling + sixpence, shilling, sixpence]
    total_value = pound + 5 * shilling + sixpence  # the total worth of the coins, in pence
    n_coins = 15                                   # the number of coins Tommy was given

    model = cp_model.CpModel()

    # coins[c] is the number of coins of kind c that Tommy was given
    coins = [model.new_int_var(0, n_coins, f"coins_{c}") for c in range(len(values))]
    # The half-crowns are the first kind of coin.
    half_crowns = coins[0]

    # The coins add up to the total worth.
    model.add(sum(v * n for v, n in zip(values, coins)) == total_value)
    # The coin counts add up to the number of coins.
    model.add(sum(coins) == n_coins)

    return model, {"half_crowns": half_crowns}


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
