# candies: an Exact (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python candies.py candies.json

from exact import Exact


def create_model(instance):
    """Children sit in a line, each with a rating. Give every child at least one candy, and
    give a child more candies than a neighbour with a lower rating. Use as few candies as
    possible in total."""
    ratings = instance["ratings"]  # ratings[i]: the rating of child i, in line order
    n_children = len(ratings)

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is the number of candies given to child i
    x = [f"x{i}" for i in range(n_children)]
    for name in x:
        solver.addVariable(name, 1, n_children)

    # Neighbours with different ratings: the child with the higher rating gets more candies.
    for i in range(1, n_children):
        if ratings[i - 1] > ratings[i]:
            # the child on the left has the higher rating
            solver.addConstraint([(1, x[i - 1]), (-1, x[i])], True, 1, False, 0)
        elif ratings[i - 1] < ratings[i]:
            # the child on the right has the higher rating
            solver.addConstraint([(1, x[i]), (-1, x[i - 1])], True, 1, False, 0)

    # z is the total number of candies given out
    solver.addVariable("z", n_children, n_children * n_children)
    solver.addConstraint([(1, name) for name in x] + [(-1, "z")], True, 0, True, 0)

    # Use as few candies as possible in total.
    solver.setObjective([(1, "z")], minimize=True)

    return solver, {"x": x, "z": "z"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
