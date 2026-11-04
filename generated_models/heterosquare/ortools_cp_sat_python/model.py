# heterosquare: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install ortools`):
#   python heterosquare.py heterosquare.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square

    model = cp_model.CpModel()

    # x[i][j] is the number in row i, column j
    x = [[model.new_int_var(1, n * n, f"x_{i}_{j}") for j in range(n)]
         for i in range(n)]

    # The sums of the rows, the columns and the two diagonals. Each sum adds n
    # numbers of at most n^2, so it is at most n^3.
    row_sums = [model.new_int_var(1, n ** 3, f"row_sum_{i}") for i in range(n)]
    col_sums = [model.new_int_var(1, n ** 3, f"col_sum_{j}") for j in range(n)]
    # diag_sum runs from top left to bottom right, anti_diag_sum from top right to
    # bottom left
    diag_sum = model.new_int_var(1, n ** 3, "diag_sum")
    anti_diag_sum = model.new_int_var(1, n ** 3, "anti_diag_sum")

    # The numbers in the square are distinct.
    model.add_all_different([cell for row in x for cell in row])

    # Each sum is the total of its cells.
    for i in range(n):
        model.add(row_sums[i] == sum(x[i]))
    for j in range(n):
        model.add(col_sums[j] == sum(x[i][j] for i in range(n)))
    model.add(diag_sum == sum(x[i][i] for i in range(n)))
    model.add(anti_diag_sum == sum(x[i][n - 1 - i] for i in range(n)))

    # The row, column and diagonal sums are all different.
    model.add_all_different(row_sums + col_sums + [diag_sum, anti_diag_sum])

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
