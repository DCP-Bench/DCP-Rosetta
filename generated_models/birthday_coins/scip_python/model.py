# birthday_coins: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python birthday_coins.py

from pyscipopt import Model


def create_model(instance):
    """Tommy was given 15 coins for his birthday: half-crowns, shillings and
    sixpences, worth exactly £1 5s 6d in total. How many half-crowns was he given?

    Money is counted in pence (a pound is 240d, a shilling 12d). Each of the three
    kinds of coin is among the coins he was given, so each appears at least once.
    The instance is an empty list: every number here is fixed by the statement,
    so the model takes no data from it.
    """
    # The statement fixes these numbers.
    coins = 15                                # the number of coins he was given
    total_pence = 240 + 5 * 12 + 6            # £1 5s 6d = 240d + 60d + 6d = 306d
    half_crown_pence = 2 * 12 + 6             # a half-crown is 2s 6d = 30d
    shilling_pence = 12                       # a shilling is 12d
    sixpence_pence = 6                        # a sixpence is 6d

    model = Model("birthday_coins")

    # half_crowns: how many half-crowns he was given (the answer).
    # Upper bound: the shillings and sixpences need at least one coin each,
    # so at most coins - 2 half-crowns.
    half_crowns = model.addVar("half_crowns", vtype="I", lb=1, ub=coins - 2)

    # shillings: how many shillings he was given. Same bound reasoning.
    shillings = model.addVar("shillings", vtype="I", lb=1, ub=coins - 2)

    # sixpences: how many sixpences he was given. Same bound reasoning.
    sixpences = model.addVar("sixpences", vtype="I", lb=1, ub=coins - 2)

    # He was given 15 coins in all, of the three kinds.
    model.addCons(half_crowns + shillings + sixpences == coins)

    # Together the coins add up to £1 5s 6d (306 pence).
    model.addCons(
        half_crown_pence * half_crowns
        + shilling_pence * shillings
        + sixpence_pence * sixpences == total_pence
    )

    # The puzzle has no objective: any assignment that meets the constraints is an answer.
    return model, {"half_crowns": half_crowns}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
