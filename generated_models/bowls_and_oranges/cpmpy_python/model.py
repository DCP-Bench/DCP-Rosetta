# bowls_and_oranges: a CPMpy model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from itertools import combinations

import cpmpy as cp


def create_model(instance):
    """Place all the oranges in bowls that stand in a line one metre apart, at most one
    orange per bowl, so that no three oranges A, B and C have the distance from A to B equal
    to the distance from B to C."""
    n = instance["n"]  # the number of bowls, numbered 1 to n along the line
    m = instance["m"]  # the number of oranges

    # x[i] is the bowl that orange i is placed in
    x = cp.intvar(1, n, shape=m, name="x")

    model = cp.Model()
    # No bowl holds more than one orange.
    model.add(cp.AllDifferent(x))
    # The bowls are reported in ascending order.
    model.add(x[:-1] <= x[1:])
    # No three oranges are evenly spaced: the gap from the first to the second differs from
    # the gap from the second to the third.
    for i, j, k in combinations(range(m), 3):
        model.add((x[j] - x[i]) != (x[k] - x[j]))

    return model, {"x": x}


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
