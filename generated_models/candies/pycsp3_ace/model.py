# candies: a PyCSP3 model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python candies.py candies.json

from pycsp3 import *


def create_model(instance):
    """Alice gives each child at least one candy. The children sit in a line; when two
    neighbours have different ratings, the one with the higher rating gets more candies.
    Minimise the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of child i, in line order
    n_children = len(ratings)
    min_candies = 1  # every child gets at least one candy

    # A child never needs more than n_children candies in an optimal allocation: if a child
    # has k > 1 candies, a neighbour with a lower rating must have k - 1 (otherwise one candy
    # could be taken from the child, saving a candy), so a chain of children holds 1, 2, ..., k
    # candies and k <= n_children. The bound loses no optimal allocation.
    max_candies = n_children

    # x[i]: the number of candies child i gets
    x = VarArray(size=n_children, dom=range(min_candies, max_candies + 1))

    # z: the total number of candies given out, at least one per child and at most
    # max_candies per child
    z = Var(dom=range(n_children * min_candies, n_children * max_candies + 1))

    satisfy(
        # Neighbours with different ratings: the child with the higher rating gets more candies.
        # Neighbours with equal ratings have no constraint between them.
        [x[i] > x[i + 1] for i in range(n_children - 1) if ratings[i] > ratings[i + 1]],
        [x[i] < x[i + 1] for i in range(n_children - 1) if ratings[i] < ratings[i + 1]],
        # The total is the sum of the candies given to all children.
        z == Sum(x),
    )

    # Minimise the total number of candies.
    minimize(z)

    return {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("x =", values(outputs["x"]))
        print("z =", value(outputs["z"]))
    else:
        print("No solution:", status())
