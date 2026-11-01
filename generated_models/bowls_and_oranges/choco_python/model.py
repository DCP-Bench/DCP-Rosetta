# bowls_and_oranges: a Choco-solver (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from itertools import combinations

from pychoco.model import Model


def create_model(instance):
    """n bowls stand in a line at intervals of one metre, numbered 1 to n. Place all the
    oranges in the bowls, at most one orange per bowl, so that no three oranges A, B and C
    have the distance from A to B equal to the distance from B to C."""
    n_bowls = instance["n"]      # the number of bowls
    n_oranges = instance["m"]    # the number of oranges

    model = Model()

    # x[i] is the bowl that orange i is placed in
    x = [model.intvar(1, n_bowls, name=f"x{i}") for i in range(n_oranges)]

    # At most one orange per bowl.
    model.all_different(x).post()

    # The oranges are listed by bowl number, lowest first.
    for a, b in zip(x, x[1:]):
        model.arithm(a, "<=", b).post()

    # No three oranges are evenly spaced: the middle one is not halfway between the other two.
    for i, j, k in combinations(range(n_oranges), 3):
        model.scalar([x[j], x[i], x[k]], [2, -1, -1], "!=", 0).post()

    return model, {"x": x}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
