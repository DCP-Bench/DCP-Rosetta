# three_coins: a SCIP (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python three_coins.py three_coins.json

from pyscipopt import Model


def create_model(instance):
    """Coins lie on a table in the order given by the instance, each showing tails
    or heads. In exactly num_moves moves, make them all face the same way, all heads
    or all tails. A move chooses one coin and flips it over. The output steps holds
    the state of the coins before the first move and after each move, with True for
    tails and False for heads."""
    init = instance["init"]              # init[c]: 1 when coin c starts tails, 0 when heads, in table order
    num_moves = instance["num_moves"]    # the number of moves to make, exactly
    n = len(init)                        # the number of coins on the table

    model = Model("three_coins")

    # steps[t][c] is 1 when coin c shows tails after t moves, and 0 when it shows
    # heads.
    steps = model.addMatrixVar((num_moves + 1, n), vtype="B", name="steps")

    # Row 0 is the starting order, init.
    model.addMatrixCons(steps[0] == init)

    # flip[t][c] is 1 when move t flips coin c.
    flip = model.addMatrixVar((num_moves, n), vtype="B", name="flip")

    # Each move chooses one coin and flips it over: exactly one flip per move.
    model.addMatrixCons(flip.sum(axis=1) == 1)

    # flip[t][c] is the exclusive or of coin c before and after move t, so it is 1
    # exactly when the coin changed face. addConsXor takes one constraint per call and
    # no matrix form, so each coin and move gets its own call. The three binaries of a
    # call sum to an even number.
    for t in range(num_moves):
        for c in range(n):
            model.addConsXor([steps[t, c], steps[t + 1, c], flip[t, c]], False)

    # The final state (the last row) has every coin showing the same face: each coin
    # in it matches coin 0 in it.
    model.addMatrixCons(steps[num_moves] == steps[num_moves, 0])

    return model, {"steps": steps}


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
