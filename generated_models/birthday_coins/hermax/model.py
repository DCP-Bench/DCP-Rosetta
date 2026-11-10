# birthday_coins: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install hermax`) with:
#   python birthday_coins.py

from hermax.model import Model


def create_model(instance):
    """Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence) or a
    sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
    worth £1 5s 6d. How many half-crowns could he have been given?"""
    # The instance has no fields: every number below is from the problem statement.
    m = Model()

    # How many coins of each kind he was given: a kind may be absent (0), and no kind can
    # number more than the 15 coins.
    half_crowns = m.int("half_crowns", 0, 15)
    shillings = m.int("shillings", 0, 15)
    sixpences = m.int("sixpences", 0, 15)

    # He was given 15 coins.
    m &= (half_crowns + shillings + sixpences == 15)

    # They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    # shilling 12 and a sixpence 6.
    m &= (30 * half_crowns + 12 * shillings + 6 * sixpences == 306)

    return m, {"half_crowns": half_crowns}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
