# bowls_and_oranges: a cvc5 (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from itertools import combinations

import cvc5.pythonic as c5


def create_model(instance):
    """n bowls stand in a line one metre apart, numbered 1 to n. Place all the oranges in the
    bowls, at most one orange per bowl, so that no three oranges A, B and C have the distance
    from A to B equal to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls
    n_oranges = instance["m"]  # the number of oranges

    # x[i]: the bowl that orange i is placed in
    x = [c5.Int(f"x_{i}") for i in range(n_oranges)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each orange sits in one of the bowls.
    for xi in x:
        solver.add(xi >= 1, xi <= n_bowls)

    # The bowls are in increasing order, so no bowl holds two oranges.
    solver.add([a < b for a, b in zip(x, x[1:])])

    # No three oranges are evenly spaced: the gap from the first to the second is not the gap
    # from the second to the third.
    for a, b, c in combinations(x, 3):
        solver.add(b - a != c - b)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
