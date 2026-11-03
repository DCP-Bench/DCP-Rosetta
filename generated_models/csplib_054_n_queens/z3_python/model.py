# csplib_054_n_queens: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import z3


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board size and the number of queens

    # queens[i] is the column, from 1 to n, of the queen in row i
    queens = [z3.Int(f"queens_{row}") for row in range(n)]

    solver = z3.Solver()

    # Each queen stands on the board.
    solver.add([z3.And(queen >= 1, queen <= n) for queen in queens])
    # No two queens share a column.
    solver.add(z3.Distinct(queens))
    # No two queens share a diagonal going down to the right.
    solver.add(z3.Distinct([queens[row] - row for row in range(n)]))
    # No two queens share a diagonal going down to the left.
    solver.add(z3.Distinct([queens[row] + row for row in range(n)]))

    return solver, {"queens": queens}


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
