# frog_circle: a SCIP (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python frog_circle.py frog_circle.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Cards numbered 1 to n sit on a circle of n places, numbered 0 to n-1 clockwise.
    A frog sits on card 1 and jumps 1 place clockwise; from card k it then jumps
    k places clockwise, and it keeps jumping. Find an arrangement of the cards
    such that the frog lands on every card, starting from card 1.

    The arrangement is x, where x[i] is the number of the card in place i.
    Rotating the circle does not change the jumps, so card 1 is fixed in place 0;
    this keeps exactly one arrangement from each rotation.
    """
    n = instance["n"]  # the number of cards, and of places on the circle

    model = Model("frog_circle")

    # card[i, c] is 1 when card c + 1 is in place i, and 0 when not
    card = model.addMatrixVar((n, n), vtype="B", name="card")
    model.addMatrixCons(card.sum(axis=1) == 1)  # each place holds exactly one card
    model.addMatrixCons(card.sum(axis=0) == 1)  # each card is in exactly one place
    model.addCons(card[0, 0] == 1)  # card 1 is in place 0, the rotation fixed above

    x = card @ np.arange(1, n + 1)  # x[i] is the number of the card in place i

    # frog[t, i] is 1 when the frog stands in place i after t jumps (t = 0 to n-1), and 0 when not
    frog = model.addMatrixVar((n, n), vtype="B", name="frog")
    model.addMatrixCons(frog.sum(axis=1) == 1)  # after t jumps the frog is in one place
    model.addMatrixCons(frog.sum(axis=0) == 1)  # the n times cover all n places, each once
    model.addCons(frog[0, 0] == 1)  # the frog starts in place 0, where card 1 is

    # card_under[t] is the number of the card the frog stands on after t jumps; cards are 1 to n
    card_under = model.addMatrixVar(n, vtype="I", lb=1, ub=n, name="card_under")
    for t in range(n):
        for i in range(n):
            # when the frog stands in place i, the card under it is x[i]; addConsIndicator takes
            # only <= or >=, so this equality is two indicators on the same binary frog[t, i]
            model.addConsIndicator(card_under[t] - x[i] <= 0, binvar=frog[t, i])
            model.addConsIndicator(card_under[t] - x[i] >= 0, binvar=frog[t, i])

    # place[t] is the place the frog stands in after t jumps
    place = frog @ np.arange(n)
    # wrap[t] is 1 when the jump from time t to time t + 1 passes place n - 1 and wraps to place 0
    wrap = model.addMatrixVar(n - 1, vtype="B", name="wrap")
    # each jump: the next place is the current place plus the card's number, taken modulo n.
    # From place p the frog jumps k places to (p + k) mod n; p + k is at most 2n - 1 (p <= n - 1,
    # k <= n), so the modulo subtracts n once or not at all, which is what wrap records.
    model.addMatrixCons(place[1:] == place[:-1] + card_under[:-1] - n * wrap)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
