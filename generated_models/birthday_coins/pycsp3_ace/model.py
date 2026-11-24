# birthday_coins: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python birthday_coins.py

from pycsp3 import *


def create_model(instance):
    """Tommy was given 15 coins for his birthday. Each coin is a half-crown, a shilling or a
    sixpence, but he was not necessarily given coins of all three kinds. He found that the
    coins added up to one pound 5 shillings 6 pence. How many half-crowns could he have been
    given?"""
    n_coins = 15  # the number of coins Tommy was given

    # Old British money, counted in pence.
    pence_per_sixpence = 6
    pence_per_shilling = 12
    shillings_per_pound = 20
    pence_per_pound = shillings_per_pound * pence_per_shilling  # a pound is 240 pence
    shillings_per_half_crown = 2
    # a half-crown is 2 shillings and sixpence
    pence_per_half_crown = shillings_per_half_crown * pence_per_shilling + pence_per_sixpence

    # The total Tommy found: 1 pound, 5 shillings and 6 pence, in pence.
    pounds_in_total = 1
    shillings_in_total = 5
    pence_in_total = 6
    total_pence = (
        pounds_in_total * pence_per_pound + shillings_in_total * pence_per_shilling + pence_in_total
    )

    # The number of half-crowns, shilling coins and sixpences he was given. He had n_coins
    # coins in all, so no kind can be more than n_coins.
    half_crowns = Var(dom=range(n_coins + 1))
    shilling_coins = Var(dom=range(n_coins + 1))
    sixpence_coins = Var(dom=range(n_coins + 1))

    satisfy(
        # He was given n_coins coins in all.
        half_crowns + shilling_coins + sixpence_coins == n_coins,
        # The coins added up to the total he found, in pence.
        pence_per_half_crown * half_crowns
        + pence_per_shilling * shilling_coins
        + pence_per_sixpence * sixpence_coins
        == total_pence,
    )

    return {"half_crowns": half_crowns}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
