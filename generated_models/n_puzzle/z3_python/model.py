# n_puzzle: a Z3 (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python n_puzzle.py n_puzzle.json

import z3


def create_model(instance):
    """N-puzzle: on a square board with numbered tiles and one empty square, find the
    N_STEPS boards from the start board to the end board, where each board follows from
    the one before by sliding a tile into the empty square. The board changes at every step."""
    n_steps = instance["N_STEPS"]     # number of boards, the start and end boards included
    start = instance["puzzle_start"]  # start[i][j]: the tile in row i, column j at the start
    end = instance["puzzle_end"]      # end[i][j]: the tile in row i, column j at the end
    n_rows = len(start)               # the board is n_rows x n_rows squares
    n_tiles = n_rows * n_rows - 1     # the numbered tiles, 1 to n_tiles

    # steps[t][i][j]: the tile in row i, column j of board t; the empty square holds 0
    steps = [[[z3.Int(f"steps_{t}_{i}_{j}") for j in range(n_rows)] for i in range(n_rows)]
             for t in range(n_steps)]

    # The square (i, j) and the squares beside it on the board, left, right, above and below.
    def near(i, j):
        return [(a, b) for a, b in [(i, j), (i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
                if 0 <= a < n_rows and 0 <= b < n_rows]

    solver = z3.Solver()

    # Every square of every board holds a tile number from 0 to n_tiles.
    solver.add([z3.And(tile >= 0, tile <= n_tiles)
                for board in steps for row in board for tile in row])

    # The first board is the start board and the last board is the end board.
    solver.add([steps[0][i][j] == start[i][j] for i in range(n_rows) for j in range(n_rows)])
    solver.add([steps[-1][i][j] == end[i][j] for i in range(n_rows) for j in range(n_rows)])

    for t in range(1, n_steps):
        before, after = steps[t - 1], steps[t]

        # Every board holds each tile, and the empty square, exactly once.
        solver.add(z3.Distinct([after[i][j] for i in range(n_rows) for j in range(n_rows)]))

        # The empty square moves only to a square beside where it was: if it is on a square
        # after the move, it was on that square or beside it before the move.
        solver.add([z3.Implies(after[i][j] == 0, z3.Or([before[a][b] == 0 for a, b in near(i, j)]))
                    for i in range(n_rows) for j in range(n_rows)])

        # Only the empty square moves: a square that is neither empty before nor after the
        # move keeps its tile.
        solver.add([z3.Or(before[i][j] == 0, after[i][j] == 0, before[i][j] == after[i][j])
                    for i in range(n_rows) for j in range(n_rows)])

        # Each board differs from the one before it.
        solver.add(z3.Or([before[i][j] != after[i][j] for i in range(n_rows) for j in range(n_rows)]))

    return solver, {"steps": steps}


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
