# csplib_076_costas_arrays: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import cvc5.pythonic as c5


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]  # size of the grid and number of marks

    # costas[i] is the column (1 to n) of the mark in row i
    costas = [c5.Int(f"costas_{i}") for i in range(n)]

    solver = c5.Solver()

    # Columns run from 1 to n.
    for x in costas:
        solver.add(x >= 1, x <= n)

    # One mark per column: the columns form a permutation.
    solver.add(c5.Distinct(costas))

    # Difference triangle. Line l holds the differences between the columns of marks
    # l rows apart. Each difference lies between -(n-1) and n-1 and is not zero.
    # Line n-1 has a single difference, so it needs no constraint.
    for l in range(1, n - 1):
        line = [c5.Int(f"d_{l}_{i}") for i in range(n - l)]
        for i, d in enumerate(line):
            solver.add(d == costas[i] - costas[i + l], d >= -(n - 1), d <= n - 1, d != 0)

        # No difference repeats within a line.
        solver.add(c5.Distinct(line))

    return solver, {"costas": costas}


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
