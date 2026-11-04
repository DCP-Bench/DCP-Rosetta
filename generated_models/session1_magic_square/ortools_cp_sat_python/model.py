# session1_magic_square: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install ortools`):
#   python session1_magic_square.py session1_magic_square.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n^2 so that every row, column and
    diagonal adds up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The common sum is n * (n^2 + 1) / 2: the numbers 1..n^2 total
    # n^2 * (n^2 + 1) / 2, shared equally between n rows.
    magic_sum = n * (n * n + 1) // 2

    model = cp_model.CpModel()

    # square[i][j] is the number in row i, column j
    square = [[model.new_int_var(1, n * n, f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # All numbers in the square are different.
    model.add_all_different([square[i][j] for i in range(n) for j in range(n)])

    # Every row adds up to the magic sum.
    for i in range(n):
        model.add(sum(square[i]) == magic_sum)

    # Every column adds up to the magic sum.
    for j in range(n):
        model.add(sum(square[i][j] for i in range(n)) == magic_sum)

    # The main diagonal adds up to the magic sum.
    model.add(sum(square[i][i] for i in range(n)) == magic_sum)

    # The other diagonal adds up to the magic sum.
    model.add(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return model, {"square": square}


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
