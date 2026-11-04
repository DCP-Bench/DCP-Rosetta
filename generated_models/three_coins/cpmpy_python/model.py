# three_coins: a CPMpy model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python three_coins.py three_coins.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Three coins lie on a table. In exactly the given number of moves, each flipping
    one coin, make them all face heads or all face tails."""
    init = np.array(instance["init"], dtype=bool)  # init[j]: true when coin j starts as tails
    num_moves = instance["num_moves"]              # the number of moves, each flipping one coin
    n = len(init)                                  # the number of coins

    # steps[m, j] is true when coin j is tails after m moves (row 0 is the start)
    steps = cp.boolvar(shape=(num_moves + 1, n), name="steps")

    model = cp.Model()

    # The coins start as given.
    model.add(steps[0] == init)

    # Each move flips exactly one coin.
    for m in range(1, num_moves + 1):
        model.add(cp.sum(steps[m] != steps[m - 1]) == 1)

    # After the last move the coins are all heads or all tails.
    tails = cp.sum(steps[num_moves])
    model.add((tails == 0) | (tails == n))

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
