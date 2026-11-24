# bowls_and_oranges: a PyCSP3 model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python bowls_and_oranges.py bowls_and_oranges.json

from pycsp3 import *


def create_model(instance):
    """Bowls are placed in a line at one metre intervals, numbered from 1. Put every
    orange in a bowl, at most one orange per bowl, so that no three oranges A, B and
    C have the distance between A and B equal to the distance between B and C.
    Print the bowls holding the oranges, in ascending order."""
    n_bowls = instance["n"]      # the bowls, numbered 1 to n_bowls
    n_oranges = instance["m"]    # the oranges to place, one per bowl

    # x[k] is the bowl holding the k-th orange, the bowls in ascending order
    x = VarArray(size=n_oranges, dom=range(1, n_bowls + 1))

    satisfy(
        # Each bowl holds at most one orange, and the list is in ascending order.
        Increasing(x, strict=True),
        # No three oranges, at bowls x[i] < x[j] < x[k], have the middle one exactly
        # halfway between the other two: the distance from i to j is not the distance from j to k.
        [x[i] + x[k] != 2 * x[j] for i in range(n_oranges) for j in range(i + 1, n_oranges) for k in range(j + 1, n_oranges)],
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
