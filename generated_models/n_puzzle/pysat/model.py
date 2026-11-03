# n_puzzle: a PySAT (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python n_puzzle.py n_puzzle.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Slide the tiles of an n-puzzle from the start board to the end board in exactly N_STEPS
    boards, the start and the end included. At each step the empty square swaps places with a
    tile next to it, so the board changes at every step."""
    n_steps = instance["N_STEPS"]     # the number of boards in the plan, the start and the end included
    start = instance["puzzle_start"]  # start[i][j]: the tile in row i, column j at the start (0 is the empty square)
    end = instance["puzzle_end"]      # end[i][j]: the tile in row i, column j at the end (0 is the empty square)
    side = len(start)                 # the board is side by side squares
    n_tiles = side * side - 1         # the numbered tiles, 1 to n_tiles

    pool = IDPool()

    # board[t][i][j] is the tile in row i, column j at step t (0 is the empty square)
    board = [[[Integer(f"b_{t}_{i}_{j}", 0, n_tiles, vpool=pool) for j in range(side)]
              for i in range(side)]
             for t in range(n_steps)]
    engine = IntegerEngine(vars=[cell for step in board for row in step for cell in row], vpool=pool)

    # The squares next to (i, j), with (i, j) itself: the square and its neighbours left, right,
    # above and below, inside the board.
    def around(i, j):
        return [(i + di, j + dj) for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + di < side and 0 <= j + dj < side]

    # Every board holds each tile and the empty square exactly once.
    for step in board:
        engine.add_alldifferent([cell for row in step for cell in row])
    cnf = engine.clausify()

    # The first board is the start board and the last board is the end board.
    for i in range(side):
        for j in range(side):
            cnf.append([board[0][i][j].equals(start[i][j])])
            cnf.append([board[-1][i][j].equals(end[i][j])])

    for t in range(1, n_steps):
        before, after = board[t - 1], board[t]  # the boards before and after this move
        changed = []  # the flags of the squares whose tile changes in this move

        for i in range(side):
            for j in range(side):
                # The empty square moves to a neighbouring square or stays put: if it is on (i, j)
                # after the move, it was on (i, j) or next to it before.
                cnf.append([-after[i][j].equals(0)] + [before[r][c].equals(0) for r, c in around(i, j)])

                # A tile on a square stays there, unless the empty square takes its place.
                for v in range(1, n_tiles + 1):
                    cnf.append([-before[i][j].equals(v), after[i][j].equals(v), after[i][j].equals(0)])

                # flag is true only when the tile on (i, j) differs before and after the move.
                flag = pool.id(("changed", t, i, j))
                for v in range(n_tiles + 1):
                    cnf.append([-flag, -before[i][j].equals(v), -after[i][j].equals(v)])
                changed.append(flag)

        # Each move changes the board: at least one square gets a different tile.
        cnf.append(changed)

    return cnf, {"steps": board}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
