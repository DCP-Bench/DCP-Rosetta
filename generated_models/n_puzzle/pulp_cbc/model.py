# n_puzzle: a PuLP (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python n_puzzle.py n_puzzle.json

import pulp


def create_model(instance):
    """N-puzzle: on a square board with tiles 1..n and one empty square (0), a move slides
    a tile next to the empty square into it. Find N_STEPS boards from the start board to the
    end board, where the board changes at every step."""
    n_steps = instance["N_STEPS"]     # number of boards, counting the start and end boards
    start = instance["puzzle_start"]  # start[i][j]: the tile in row i, column j at the start
    end = instance["puzzle_end"]      # end[i][j]: the tile in row i, column j at the end
    dim = len(start)                  # the board is dim x dim squares
    cells = [(i, j) for i in range(dim) for j in range(dim)]  # the squares of the board
    values = range(dim * dim)         # the tiles 1..dim*dim-1, and 0 for the empty square

    # the squares that share a side with square cell
    def next_to(cell):
        i, j = cell
        return [(i + di, j + dj) for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= i + di < dim and 0 <= j + dj < dim]

    # no objective: any sequence of boards that follows the rules is a solution
    problem = pulp.LpProblem("n_puzzle", pulp.LpMinimize)

    # board[t][(cell, v)] is 1 when square cell holds value v on board t, and 0 when not
    board = [{(cell, v): pulp.LpVariable(f"board_{t}_{cell[0]}_{cell[1]}_{v}", cat="Binary")
              for cell in cells for v in values} for t in range(n_steps)]

    # Each board holds one value on each square, and each value on one square.
    for t in range(n_steps):
        for cell in cells:
            problem += pulp.lpSum(board[t][(cell, v)] for v in values) == 1
        for v in values:
            problem += pulp.lpSum(board[t][(cell, v)] for cell in cells) == 1

    # The first board is the start board and the last board is the end board.
    for cell in cells:
        problem += board[0][(cell, start[cell[0]][cell[1]])] == 1
        problem += board[n_steps - 1][(cell, end[cell[0]][cell[1]])] == 1

    for t in range(n_steps - 1):
        # slide[(a, b)] is 1 when the tile on square a slides into the empty square b
        # between board t and board t + 1
        slide = {(a, b): pulp.LpVariable(f"slide_{t}_{a[0]}_{a[1]}_{b[0]}_{b[1]}", 0, 1)
                 for b in cells for a in next_to(b)}

        # Exactly one tile slides between two boards, so the board changes at every step.
        # The tile slides into the empty square of board t, and the square it leaves is the
        # empty square of board t + 1.
        for b in cells:
            problem += pulp.lpSum(slide[(a, b)] for a in next_to(b)) == board[t][(b, 0)]
        for a in cells:
            problem += pulp.lpSum(slide[(a, b)] for b in next_to(a)) == board[t + 1][(a, 0)]

        for v in values:
            if v == 0:
                continue
            # A tile that slides from a to b is on b on the next board.
            for (a, b), moved in slide.items():
                problem += board[t + 1][(b, v)] >= board[t][(a, v)] + moved - 1
            # A tile that does not slide stays on its square.
            for a in cells:
                problem += board[t + 1][(a, v)] >= board[t][(a, v)] - pulp.lpSum(
                    slide[(a, b)] for b in next_to(a))

    # steps[t][i][j] is the tile in row i, column j on board t
    steps = [[[pulp.lpSum(v * board[t][((i, j), v)] for v in values) for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]

    return problem, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
