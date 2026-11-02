# n_puzzle: a cvc5 (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python n_puzzle.py n_puzzle.json

import cvc5.pythonic as c5


def create_model(instance):
    """Slide the tiles of an n x n board, one tile into the empty square per step, to turn
    the start board into the end board in N_STEPS boards. The board changes at every step."""
    n_steps = instance["N_STEPS"]      # number of boards, the start and the end board included
    start = instance["puzzle_start"]   # start[i][j]: the tile in row i, column j at the start (0 = empty)
    end = instance["puzzle_end"]       # end[i][j]: the tile in row i, column j at the end (0 = empty)
    n = len(start)                     # the board is n x n squares
    top = n * n - 1                    # the largest tile number
    cells = [(r, c) for r in range(n) for c in range(n)]

    # board[t][r][c]: the tile in row r, column c on board t (0 = empty square)
    board = [[[c5.Int(f"board_{t}_{r}_{c}") for c in range(n)] for r in range(n)]
             for t in range(n_steps)]

    solver = c5.Solver()

    # Every board holds the tiles 0 to n*n - 1, each one once.
    for t in range(n_steps):
        for r, c in cells:
            solver.add(board[t][r][c] >= 0)
            solver.add(board[t][r][c] <= top)
        solver.add(c5.Distinct([board[t][r][c] for r, c in cells]))

    # The first board is the start board and the last board is the end board.
    for r, c in cells:
        solver.add(board[0][r][c] == start[r][c])
        solver.add(board[n_steps - 1][r][c] == end[r][c])

    # Pairs (p, q) of neighbouring squares, in both directions.
    adjacent = []
    for r, c in cells:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n:
                adjacent.append(((r, c), (rr, cc)))

    # Each step slides one tile into the empty square from a neighbouring square.
    # Every other square keeps its tile.
    for t in range(n_steps - 1):
        before = board[t]
        after = board[t + 1]
        moves = []
        for p, q in adjacent:
            parts = [
                before[p[0]][p[1]] == 0,
                after[p[0]][p[1]] == before[q[0]][q[1]],
                after[q[0]][q[1]] == 0,
            ]
            parts += [after[r][c] == before[r][c] for r, c in cells if (r, c) != p and (r, c) != q]
            moves.append(c5.And(*parts))
        solver.add(c5.Or(*moves))

    outputs = {
        "steps": [[[board[t][r][c] for c in range(n)] for r in range(n)] for t in range(n_steps)],
    }
    return solver, outputs


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
