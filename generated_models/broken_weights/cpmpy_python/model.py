# broken_weights: a CPMpy model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python broken_weights.py broken_weights.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]  # the total weight of the unbroken weight, in pounds
    n = instance["n"]  # the number of pieces it broke into

    # weights[j] is the weight of piece j, in pounds
    weights = cp.intvar(1, m, shape=n, name="weights")
    # x[i, j] says where piece j goes when weighing the load of i + 1 pounds: -1 on the
    # pan with the load, 1 on the other pan, 0 not used. Allowing both pans is what
    # lets a balance scale weigh more loads than a subset sum.
    x = cp.intvar(-1, 1, shape=(m, n), name="x")

    model = cp.Model()
    # The pieces are of different weights.
    model.add(cp.AllDifferent(weights))
    # The pieces add up to the whole weight.
    model.add(cp.sum(weights) == m)
    # Every load from 1 to m can be balanced by the pieces placed on the pans.
    model.add((x * weights).sum(axis=1) == np.arange(1, m + 1))

    return model, {"weights": weights}


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
