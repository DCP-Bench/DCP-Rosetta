# fancy_dress: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python fancy_dress.py

from pyscipopt import Model


def create_model(instance):
    """Mr Greenguest wants to join a dress party where the male guests must wear
    green. He picks which green items to wear (tie, hat, shirt, socks) so that the
    outfit keeps three dress rules, and pays an entrance fee if it breaks one of
    them. He pays for the tie, hat and socks, and owns a green shirt, so the shirt
    costs him nothing. The goal is the cheapest way for him to take part.

    The instance file is empty ([]): the prices and the fee come from the problem
    statement, so the instance argument is not read.
    """
    model = Model("fancy_dress")

    # The items he can wear. Each is 1 when worn in green, 0 when not.
    t = model.addVar("tie", vtype="B")    # green tie, bought for $10
    h = model.addVar("hat", vtype="B")    # green hat, bought used for $2
    r = model.addVar("shirt", vtype="B")  # green shirt, already owned, so no cost
    s = model.addVar("socks", vtype="B")  # green socks, bought for $12
    # 1 when he pays the $11 entrance fee (exact: see the fee constraint below)
    n = model.addVar("fee", vtype="B")

    # Negations, 1 when the item is not worn in green. addConsAnd and addConsOr
    # take variables only, not negated expressions, so each negation is a binary
    # tied to its item by an equality.
    no_tie = model.addVar("no_tie", vtype="B")
    no_hat = model.addVar("no_hat", vtype="B")
    no_shirt = model.addVar("no_shirt", vtype="B")
    no_socks = model.addVar("no_socks", vtype="B")
    model.addCons(no_tie == 1 - t)
    model.addCons(no_hat == 1 - h)
    model.addCons(no_shirt == 1 - r)
    model.addCons(no_socks == 1 - s)

    # Rule 1: a guest wearing a green tie has to wear a green shirt.
    # Broken when he wears the tie and not the shirt.
    broken_1 = model.addVar("broken_1", vtype="B")  # 1 when rule 1 is broken
    model.addConsAnd([t, no_shirt], broken_1)

    # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie
    # or a green hat. Broken when he wears socks or the shirt, and neither tie nor hat.
    socks_or_shirt = model.addVar("socks_or_shirt", vtype="B")  # 1 when rule 2 applies
    model.addConsOr([s, r], socks_or_shirt)
    broken_2 = model.addVar("broken_2", vtype="B")  # 1 when rule 2 is broken
    model.addConsAnd([socks_or_shirt, no_tie, no_hat], broken_2)

    # Rule 3: a guest who wears a green shirt, or a green hat, or who does not wear
    # green socks, must wear a green tie. Broken when one of those holds and he has
    # no green tie.
    shirt_hat_or_no_socks = model.addVar("shirt_hat_or_no_socks", vtype="B")  # 1 when rule 3 applies
    model.addConsOr([r, h, no_socks], shirt_hat_or_no_socks)
    broken_3 = model.addVar("broken_3", vtype="B")  # 1 when rule 3 is broken
    model.addConsAnd([shirt_hat_or_no_socks, no_tie], broken_3)

    # Entrance fee: he pays exactly when some rule is broken. addConsOr works in
    # both directions, so the fee is 0 when all three rules hold.
    model.addConsOr([broken_1, broken_2, broken_3], n)

    # Cost: tie $10, hat $2, socks $12 and the $11 fee. The owned shirt adds nothing.
    model.setObjective(10 * t + 2 * h + 12 * s + 11 * n, "minimize")

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}


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
