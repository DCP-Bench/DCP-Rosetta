# csplib_076_costas_arrays: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import z3


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]  # size of the grid and number of marks

    # costas[i] is the column (1 to n) of the mark in row i
    costas = [z3.Int(f"costas_{i}") for i in range(n)]

    solver = z3.Solver()

    # Each mark lies in a column from 1 to n.
    solver.add([z3.And(1 <= mark, mark <= n) for mark in costas])

    # One mark per column: the columns form a permutation.
    solver.add(z3.Distinct(costas))

    # For each gap between rows, the differences between the columns of marks that
    # far apart are all different, so no two vectors between marks are equal.
    for gap in range(1, n - 1):
        solver.add(z3.Distinct([costas[j] - costas[j - gap] for j in range(gap, n)]))

    return solver, {"costas": costas}


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
