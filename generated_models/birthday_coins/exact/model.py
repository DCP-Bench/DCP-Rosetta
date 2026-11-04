# birthday_coins: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install exact numpy`) with:
#   python birthday_coins.py

from exact import Exact


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to one pound,
    five shillings and six pence. How many half-crowns was he given?"""
    shilling = 12                         # pence in a shilling
    pound = 20 * shilling                 # pence in a pound, which is 20 shillings
    sixpence = 6                          # pence in a sixpence
    half_crown = 2 * shilling + sixpence  # pence in a half-crown, which is 2 shillings and sixpence
    values = [half_crown, shilling, sixpence]     # pence in one coin of each kind
    total_value = pound + 5 * shilling + sixpence  # 1 pound, 5 shillings and 6 pence, in pence
    n_coins = 15                          # the number of coins Tommy was given

    solver = Exact()

    # Exact identifies its variables by name.
    # coins[c] is how many coins of kind c Tommy was given, kinds in the order of values
    coins = [f"coins_{c}" for c in range(len(values))]
    for name in coins:
        solver.addVariable(name, 0, n_coins)

    # The coins add up to the total value.
    solver.addConstraint([(values[c], coins[c]) for c in range(len(values))],
                         True, total_value, True, total_value)

    # The coin counts add up to the number of coins.
    solver.addConstraint([(1, name) for name in coins], True, n_coins, True, n_coins)

    return solver, {"half_crowns": coins[0]}  # the half-crowns are the first kind of coin


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
