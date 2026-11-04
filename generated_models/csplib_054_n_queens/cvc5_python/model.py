# csplib_054_n_queens: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import cvc5.pythonic as c5


def create_model(instance):
    """Place n queens on an n by n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board size and the number of queens

    # board[i][j] is true when a queen stands on row i, column j of the board
    board = [[c5.Bool(f"board_{i}_{j}") for j in range(n)] for i in range(n)]
    # queens[i] is the column, from 1 to n, of the queen in row i
    queens = [c5.Int(f"queens_{i}") for i in range(n)]

    solver = c5.Solver()

    # Each row holds a queen.
    solver.add([c5.Or(row) for row in board])

    # Every square of the board.
    cells = [(i, j) for i in range(n) for j in range(n)]
    # Two squares on the same row, column or diagonal cannot both hold a queen.
    for a, (i1, j1) in enumerate(cells):
        for i2, j2 in cells[a + 1:]:
            if i1 == i2 or j1 == j2 or i1 - j1 == i2 - j2 or i1 + j1 == i2 + j2:
                solver.add(c5.Or(c5.Not(board[i1][j1]), c5.Not(board[i2][j2])))

    # The column of the queen in each row is the column of the square that holds it.
    for i in range(n):
        solver.add(c5.And(queens[i] >= 1, queens[i] <= n))
        solver.add(queens[i] == c5.Sum([c5.If(board[i][j], j + 1, 0) for j in range(n)]))

    return solver, {"queens": queens}


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
