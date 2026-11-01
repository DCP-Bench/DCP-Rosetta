# csplib_054_n_queens: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board size and the number of queens

    model = cp_model.CpModel()

    # queens[i] is the column, from 1 to n, of the queen in row i
    queens = [model.new_int_var(1, n, f"queens_{i}") for i in range(n)]

    # No two queens share a column.
    model.add_all_different(queens)
    # No two queens are on the same diagonal running down to the right.
    model.add_all_different([q - i for i, q in enumerate(queens)])
    # No two queens are on the same diagonal running down to the left.
    model.add_all_different([q + i for i, q in enumerate(queens)])

    return model, {"queens": queens}


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
