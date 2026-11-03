# candies: a CPMpy model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python candies.py candies.json

import cpmpy as cp


def create_model(instance):
    """Alice, a kindergarten teacher, gives candies to the children sitting in a line, each with a
    rating. Every child gets at least 1 candy, and of two neighbours the one with the higher
    rating gets more candies. Minimise the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)

    # x[i] is the number of candies the child at position i gets; n is an upper bound since an
    # optimal solution never needs a child to get more candies than there are children.
    x = cp.intvar(1, n, shape=n, name="x")
    # z is the total number of candies
    z = cp.intvar(1, n * n, name="z")

    model = cp.Model()
    # The total is the sum of the candies given to the children.
    model.add(z == cp.sum(x))
    # Implied: every child gets at least one candy, so the total is at least n.
    model.add(z >= n)

    # Of two neighbours, the child with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.add(x[i - 1] > x[i])
        elif ratings[i - 1] < ratings[i]:
            model.add(x[i - 1] < x[i])

    # Minimise the total number of candies.
    model.minimize(z)

    return model, {"z": z, "x": x}


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
