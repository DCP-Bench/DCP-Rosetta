# broken_weights: a Z3 (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python broken_weights.py broken_weights.json

import z3


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]  # the total weight of the unbroken weight, in pounds
    n = instance["n"]  # the number of pieces it broke into

    # weights[j] is the weight of piece j, in pounds
    weights = [z3.Int(f"weights_{j}") for j in range(n)]
    # on_other_pan[i][j]: piece j is on the pan opposite the load when weighing i + 1 pounds
    on_other_pan = [[z3.Bool(f"other_{i}_{j}") for j in range(n)] for i in range(m)]
    # on_load_pan[i][j]: piece j is on the pan with the load when weighing i + 1 pounds
    on_load_pan = [[z3.Bool(f"load_{i}_{j}") for j in range(n)] for i in range(m)]

    solver = z3.Solver()

    # Each piece weighs between 1 and m pounds.
    for w in weights:
        solver.add(w >= 1, w <= m)

    # The pieces add up to the whole weight.
    solver.add(z3.Sum(weights) == m)

    # A piece is on at most one pan.
    solver.add([z3.Not(z3.And(a, b))
                for row_a, row_b in zip(on_other_pan, on_load_pan)
                for a, b in zip(row_a, row_b)])

    # Every load from 1 to m balances. Pieces on the other pan add their weight, pieces on
    # the load's pan take theirs away, and the result is the load.
    for i in range(m):
        solver.add(z3.Sum([z3.If(a, w, z3.If(b, -w, 0))
                           for w, a, b in zip(weights, on_other_pan[i], on_load_pan[i])])
                   == i + 1)

    return solver, {"weights": weights}


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
