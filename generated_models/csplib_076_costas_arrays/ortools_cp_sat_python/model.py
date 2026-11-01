# csplib_076_costas_arrays: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n_marks = instance["n"]  # the size of the grid and the number of marks

    model = cp_model.CpModel()

    # costas[i] is the column (1 to n) of the mark in row i
    costas = [model.new_int_var(1, n_marks, f"costas_{i}") for i in range(n_marks)]

    # One mark per column: the columns form a permutation.
    model.add_all_different(costas)

    # For each row distance d, the differences costas[j] - costas[j - d] are all different.
    for d in range(1, n_marks - 1):
        model.add_all_different([costas[j] - costas[j - d] for j in range(d, n_marks)])

    return model, {"costas": costas}


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
