# bowls_and_oranges: a Z3 (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from itertools import combinations

import z3


def create_model(instance):
    """Place all the oranges in bowls that stand in a line one metre apart, at most one
    orange per bowl, so that no three oranges A, B and C have the distance from A to B equal
    to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls, numbered 1 to n along the line
    n_oranges = instance["m"]  # the number of oranges

    # x[i]: the bowl that the i-th orange is placed in
    x = [z3.Int(f"x_{i}") for i in range(n_oranges)]

    solver = z3.Solver()

    # Each orange is in one of the bowls.
    solver.add([z3.And(1 <= xi, xi <= n_bowls) for xi in x])

    # No bowl holds more than one orange.
    solver.add(z3.Distinct(x))

    # The bowls are listed in ascending order.
    solver.add([a <= b for a, b in zip(x, x[1:])])

    # No three oranges are evenly spaced: the gap from the first to the second is not the
    # gap from the second to the third.
    solver.add([b - a != c - b for a, b, c in combinations(x, 3)])

    return solver, {"x": x}


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
