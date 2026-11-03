# birthday_coins: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install pulp numpy`) with:
#   python birthday_coins.py

import pulp


def create_model(instance):
    """Tommy was given 15 old British coins (half-crowns, shillings and sixpences) that add up to
    one pound, five shillings and six pence. How many half-crowns was he given?"""
    # Money in pence: a pound is 240 pence, a shilling 12 and a sixpence 6.
    values = [2 * 12 + 6, 12, 6]          # pence of a half-crown, a shilling and a sixpence
    total_value = 240 + 5 * 12 + 6        # one pound, five shillings and six pence
    n_coins = 15                          # the number of coins Tommy was given

    problem = pulp.LpProblem("birthday_coins", pulp.LpMinimize)

    # coins[c] is how many coins of kind c Tommy was given, at most n_coins in all
    coins = [pulp.LpVariable(f"coins_{c}", 0, n_coins, cat="Integer")
             for c in range(len(values))]

    # The coins add up to the total value.
    problem += pulp.lpSum(values[c] * coins[c] for c in range(len(values))) == total_value
    # The coins number n_coins in all.
    problem += pulp.lpSum(coins) == n_coins

    return problem, {"half_crowns": coins[0]}


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
