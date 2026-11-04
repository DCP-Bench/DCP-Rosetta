# birthday_coins: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install hermax`) with:
#   python birthday_coins.py

from hermax.model import Model


def create_model(instance):
    """Tommy was given 15 coins for his birthday: half-crowns, shillings and sixpences,
    worth 1 pound 5 shillings 6 pence in all. Find how many half-crowns he was given."""
    # The puzzle is fixed by its statement, so the instance carries no data to read.

    # Values in pence: a half-crown is 2 shillings and sixpence (30 pence), a shilling is
    # 12 pence, a sixpence is 6 pence. The money he had is 1 pound (240 pence),
    # 5 shillings (60 pence) and 6 pence.
    half_crown_pence = 30
    shilling_pence = 12
    sixpence_pence = 6
    total_pence = 240 + 5 * 12 + 6
    total_coins = 15

    m = Model()

    # half_crowns, shillings, sixpences: how many coins of each kind Tommy was given.
    # Each kind is given at least once (the puzzle lists all three kinds of coin).
    half_crowns = m.int("half_crowns", 1, total_coins)
    shillings = m.int("shillings", 1, total_coins)
    sixpences = m.int("sixpences", 1, total_coins)

    # He was given 15 coins in all.
    m &= (half_crowns + shillings + sixpences == total_coins)
    # Together the coins are worth 1 pound 5 shillings 6 pence.
    m &= (half_crown_pence * half_crowns + shilling_pence * shillings + sixpence_pence * sixpences == total_pence)

    return m, {"half_crowns": half_crowns}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
