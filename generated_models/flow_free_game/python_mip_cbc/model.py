# flow_free_game: a Python-MIP (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python flow_free_game.py flow_free_game.json

import mip


def create_model(instance):
    """Flow Free: connect the two numbered cells of each colour with a pipe. Each colour forms
    one pipe, the pipes do not cross or overlap, and together they cover the whole board.
    Report the colour of every cell."""
    board = instance["board"]  # board[i][j]: the colour of cell (i, j), or 0 when the cell is empty
    rows = len(board)          # the number of rows
    cols = len(board[0])       # the number of columns
    n_cells = rows * cols      # the number of cells on the board

    # Every cell of the board, as (row, column).
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    # The colours used on the board.
    colours = sorted({v for row in board for v in row if v != 0})
    # The two numbered cells of each colour. The pipe of a colour runs from the first to the second.
    ends = {k: [p for p in cells if board[p[0]][p[1]] == k] for k in colours}
    for k in colours:
        assert len(ends[k]) == 2, "each colour must have exactly two numbered cells"

    # The cells directly above, below, left and right of cell p, that lie on the board.
    def neighbours(p):
        r, c = p
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                yield (r + dr, c + dc)

    model = mip.Model(solver_name="CBC")

    # x[p, k] is 1 when cell p has colour k, and 0 when not. A numbered cell is fixed to its colour.
    x = {}
    for p in cells:
        for k in colours:
            lb = 1 if board[p[0]][p[1]] == k else 0
            x[p, k] = model.add_var(name=f"x_{p[0]}_{p[1]}_{k}", var_type=mip.BINARY, lb=lb)

    # Every cell has exactly one colour, so the whole board is covered.
    for p in cells:
        model.add_constr(mip.xsum(x[p, k] for k in colours) == 1)

    # order[p] is the step of cell p along its pipe, from 0 to n_cells - 1. Steps grow along a pipe,
    # so a pipe cannot close into a loop away from its start.
    order = {p: model.add_var(name=f"o_{p[0]}_{p[1]}", var_type=mip.INTEGER, lb=0, ub=n_cells - 1) for p in cells}

    # y[q, p, k] is 1 when the pipe of colour k runs from the neighbouring cell q into cell p, and 0 when not.
    y = {}
    for k in colours:
        start = ends[k][0]
        for p in cells:
            # The pipe starts at the first numbered cell of its colour, so no piece enters that cell.
            if p == start:
                continue
            for q in neighbours(p):
                y[q, p, k] = model.add_var(name=f"y_{q[0]}_{q[1]}_{p[0]}_{p[1]}_{k}", var_type=mip.BINARY)
                # A piece only joins two cells of its colour.
                model.add_constr(y[q, p, k] <= x[q, k])
                model.add_constr(y[q, p, k] <= x[p, k])
                # The pipe runs from an earlier cell to a later one, so it has no loops.
                model.add_constr(order[p] - order[q] - n_cells * y[q, p, k] >= 1 - n_cells)

    # The pipe of each colour is one path from its first numbered cell to its second.
    for k in colours:
        start, end = ends[k]
        for p in cells:
            # The pieces of colour k that enter and that leave cell p.
            inc = [y[q, p, k] for q in neighbours(p) if (q, p, k) in y]
            out = [y[p, q, k] for q in neighbours(p) if (p, q, k) in y]
            if p == start:
                # The pipe leaves its first numbered cell by one piece.
                model.add_constr(mip.xsum(out) == 1)
            elif p == end:
                # The pipe enters its second numbered cell by one piece, and no other piece touches it.
                model.add_constr(mip.xsum(inc) == 1)
                model.add_constr(mip.xsum(inc + out) == 1)
            else:
                # A cell in the middle of the pipe has one piece in and one out. A cell of another colour has no piece.
                model.add_constr(mip.xsum(inc) == x[p, k])
                model.add_constr(mip.xsum(inc + out) == 2 * x[p, k])

    # The lowest and the highest colour on the board.
    lo, hi = min(colours), max(colours)
    # B[r][c] is the colour of cell (r, c), a number from lo to hi. It is the colour that cell holds.
    B = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            B[r][c] = model.add_var(name=f"B_{r}_{c}", var_type=mip.INTEGER, lb=lo, ub=hi)
            model.add_constr(B[r][c] == mip.xsum(k * x[(r, c), k] for k in colours))

    return model, {"B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
