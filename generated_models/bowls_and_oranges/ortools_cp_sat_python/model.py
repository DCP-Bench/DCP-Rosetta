# bowls_and_oranges: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install ortools`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from itertools import combinations

from ortools.sat.python import cp_model


def create_model(instance):
    """n bowls stand in a line at intervals of one metre, numbered 1 to n. Place all the
    oranges in the bowls, at most one orange per bowl, so that no three oranges A, B and C
    have the distance from A to B equal to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls
    n_oranges = instance["m"]  # the number of oranges

    model = cp_model.CpModel()

    # x[i] is the bowl that orange i is placed in
    x = [model.new_int_var(1, n_bowls, f"x_{i}") for i in range(n_oranges)]

    # At most one orange per bowl.
    model.add_all_different(x)
    # The bowls are listed in ascending order.
    for a, b in zip(x, x[1:]):
        model.add(a <= b)
    # No three oranges are evenly spaced: the gap from the first to the second is not the gap
    # from the second to the third.
    for a, b, c in combinations(x, 3):
        model.add(b - a != c - b)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
