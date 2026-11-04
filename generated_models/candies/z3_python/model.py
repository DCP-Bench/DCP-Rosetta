# candies: a Z3 (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python candies.py candies.json

import z3


def create_model(instance):
    """Alice gives candies to children sitting in a line, each with a rating. Every child gets
    at least one candy, and of two neighbours the one with the higher rating gets more candies.
    Minimise the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)               # the number of children

    # x[i] is the number of candies the child at position i gets
    x = [z3.Int(f"x_{i}") for i in range(n)]
    # z is the total number of candies
    z = z3.Int("z")

    # The rules on the candies.
    solver = z3.Optimize()

    # Each child gets at least one candy and at most n. No child needs more than n in an optimal plan.
    solver.add([z3.And(c >= 1, c <= n) for c in x])

    # The total is the sum of the candies given to the children.
    solver.add(z == z3.Sum(x))

    # The total is at least n, one candy per child, and at most n * n.
    solver.add(z >= n, z <= n * n)

    # Of two neighbours, the child with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            solver.add(x[i - 1] > x[i])
        elif ratings[i - 1] < ratings[i]:
            solver.add(x[i - 1] < x[i])

    # Minimise the total number of candies.
    solver.minimize(z)

    return solver, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
