# flow_free_game: a SCIP (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python flow_free_game.py flow_free_game.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Flow Free: the two cells of each colour are joined by a pipe of that colour,
    every cell carries exactly one pipe, and pipes move only between orthogonally
    neighbouring cells. The output B is the completed board: the colour of each cell."""
    board = instance["board"]  # board[r][c]: the colour of cell (r, c), or 0 when the cell is empty
    rows = len(board)          # the number of rows of the board
    cols = len(board[0])       # the number of columns of the board
    # The colours are 1 to K. The description pairs every colour and the board gives both
    # of its cells, so K is the largest colour on the board.
    K = max(max(row) for row in board)

    cells = [(r, c) for r in range(rows) for c in range(cols)]
    # ends[j]: the two cells the board gives colour j + 1, in reading order. The pipe runs
    # from the first to the second. A pipe can be walked from either end, so this choice
    # of direction loses no solution.
    ends = [[(r, c) for (r, c) in cells if board[r][c] == j + 1] for j in range(K)]
    # nbrs[v]: the cells orthogonally next to cell v, the only cells a pipe can step to
    nbrs = {(r, c): [(r + dr, c + dc) for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                     if 0 <= r + dr < rows and 0 <= c + dc < cols]
            for (r, c) in cells}

    model = Model("flow_free_game")

    # x[r, c, j] is 1 when cell (r, c) carries colour j + 1. A cell the board colours is
    # fixed to that colour; an empty cell may take any colour.
    lb = [[[int(board[r][c] == j + 1) for j in range(K)] for c in range(cols)] for r in range(rows)]
    ub = [[[int(board[r][c] in (0, j + 1)) for j in range(K)] for c in range(cols)] for r in range(rows)]
    x = model.addMatrixVar((rows, cols, K), vtype="B", lb=lb, ub=ub)
    # Every cell carries exactly one colour, so no two pipes share a cell.
    model.addMatrixCons(x.sum(axis=2) == 1)

    # arc[v, w, j] is 1 when the pipe of colour j steps from cell v to the neighbouring cell w.
    arc = {(v, w, j): model.addVar(vtype="B") for v in cells for w in nbrs[v] for j in range(K)}
    # level[r, c, j] is the position of cell (r, c) along the pipe of colour j. A pipe visits
    # each cell at most once, so it has at most rows * cols cells, and positions run from 0
    # to rows * cols - 1.
    level = model.addMatrixVar((rows, cols, K), vtype="I", lb=0, ub=rows * cols - 1)

    # Each pipe is a single path from its first cell to its last. Every cell of the pipe
    # has one step out, except its last cell, and one step in, except its first cell.
    # A cell without the colour has no steps at all.
    for j in range(K):
        first, last = ends[j]
        for v in cells:
            model.addCons(quicksum(arc[v, w, j] for w in nbrs[v]) == x[v + (j,)] - int(v == last))
            model.addCons(quicksum(arc[w, v, j] for w in nbrs[v]) == x[v + (j,)] - int(v == first))

    # SCIP has no connectivity constraint for a path, so a pipe could close into a loop of
    # cells apart from its own path. A step from v to w puts w at least one position further
    # along the pipe than v. Going round a loop would raise the position forever, so no loop
    # can form, and with the degree rules above each colour's cells are exactly one path.
    for (v, w, j), step in arc.items():
        model.addConsIndicator(level[v + (j,)] - level[w + (j,)] <= -1, binvar=step)

    # No objective: the problem is satisfaction, and any completed board is a solution.

    # B[r][c] is the colour of cell (r, c): the colour j + 1 of the one entry x[r, c, j] that is 1.
    B = (x * list(range(1, K + 1))).sum(axis=2)
    return model, {"B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
