# bowls_and_oranges: an Exact (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from exact import Exact


def create_model(instance):
    """Place all the oranges in bowls that stand in a line one metre apart, at most one orange
    per bowl, so that no three oranges A, B and C have the distance from A to B equal to the
    distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls, numbered 1 to n along the line
    n_oranges = instance["m"]  # the number of oranges

    solver = Exact()

    # Exact identifies its variables by name.
    # in_bowl[i][p] is 1 when orange i is in bowl p + 1, and 0 when not
    in_bowl = [[f"orange_{i}_in_{p + 1}" for p in range(n_bowls)] for i in range(n_oranges)]
    for i in range(n_oranges):
        for name in in_bowl[i]:
            solver.addVariable(name, 0, 1)
        # Each orange is in exactly one bowl.
        solver.addConstraint([(1, name) for name in in_bowl[i]], True, 1, True, 1)

    # x[i] is the number of the bowl that orange i is in, numbered from 1
    x = [f"x_{i}" for i in range(n_oranges)]
    for i in range(n_oranges):
        solver.addVariable(x[i], 1, n_bowls)
        # The bowl number of orange i is the bowl it is in.
        solver.addConstraint([(p + 1, in_bowl[i][p]) for p in range(n_bowls)] + [(-1, x[i])],
                             True, 0, True, 0)
    # Each orange lies in a bowl further along the line than the one before it, so no two
    # oranges share a bowl.
    for i in range(n_oranges - 1):
        solver.addConstraint([(1, x[i + 1]), (-1, x[i])], True, 1)

    # Any three bowls at equal spacing, first, first + gap and first + 2 * gap, hold at most
    # two oranges between them.
    for first in range(1, n_bowls + 1):
        for gap in range(1, (n_bowls - first) // 2 + 1):
            # the oranges in the three bowls
            terms = [(1, in_bowl[i][q - 1]) for i in range(n_oranges)
                     for q in (first, first + gap, first + 2 * gap)]
            solver.addConstraint(terms, False, 0, True, 2)

    return solver, {"x": x}


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
