# birthday_coins: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install cpmpy`) with:
#   python birthday_coins.py

import cpmpy as cp


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to
    one pound, five shillings and six pence. How many half-crowns was he given?"""
    # The problem statement fixes all the data, in pence: a pound is 240 pence and a
    # shilling is 12 pence.
    values = [30, 12, 6]                 # values[c]: the worth of one coin of type c (half-crown, shilling, sixpence)
    total_value = 240 + 5 * 12 + 6       # 1 pound, 5 shillings and 6 pence
    total_coins = 15                     # the number of coins Tommy was given

    # coins[c] is how many coins of type c Tommy has; there are at most 15 coins in total
    coins = cp.intvar(0, total_coins, shape=len(values), name="coins")
    half_crowns = coins[0]

    model = cp.Model()
    # The coins are worth 1 pound, 5 shillings and 6 pence together.
    model.add(cp.sum(coins * values) == total_value)
    # Tommy was given 15 coins.
    model.add(cp.sum(coins) == total_coins)

    return model, {"half_crowns": half_crowns}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
