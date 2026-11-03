# n_puzzle: a Python-MIP (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python n_puzzle.py n_puzzle.json

import mip


def create_model(instance):
    """N-puzzle: on a square board with tiles 1..n and one blank square (0), find
    n_steps board states from the start board to the end board. Each state follows
    from the one before by sliding a tile into the blank square, so the board
    changes at every step."""
    n_steps = instance["N_STEPS"]     # the number of board states, the start and the end included
    start = instance["puzzle_start"]  # start[i][j]: the tile on row i, column j at the start
    end = instance["puzzle_end"]      # end[i][j]: the tile on row i, column j at the end
    n_rows = len(start)               # the number of rows
    n_cols = len(start[0])            # the number of columns
    n_squares = n_rows * n_cols       # the number of squares, which is also the number of tile values, the blank included

    cells = [(r, c) for r in range(n_rows) for c in range(n_cols)]  # every square of the board

    # the squares directly above, below, left and right of cell
    def neighbours(cell):
        r, c = cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < n_rows and 0 <= cc < n_cols:
                yield (rr, cc)

    # position(board)[v] is the square that holds tile v on the board
    def position(board):
        pos = {}
        for r in range(n_rows):
            for c in range(n_cols):
                pos[board[r][c]] = (r, c)
        return pos

    # the number of slides from square a to square b, moving one square at a time
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    start_pos = position(start)  # the square of each tile at the start
    end_pos = position(end)      # the square of each tile at the end

    # the colour, 0 or 1, of the blank's start square
    blank_colour = sum(start_pos[0]) % 2

    # A tile moves one square per step, so after t steps it is within t squares of its start
    # and within n_steps - 1 - t squares of its end. The blank also changes colour with each step.
    def allowed(t, cell, v):
        if dist(cell, start_pos[v]) > t or dist(cell, end_pos[v]) > n_steps - 1 - t:
            return False
        if v == 0 and (cell[0] + cell[1] - blank_colour - t) % 2 != 0:
            return False
        return True

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # tile[t, cell, v] is 1 when tile v (0 is the blank) is on cell at step t, and 0 when not.
    tile = {}
    for t in range(n_steps):
        for cell in cells:
            for v in range(n_squares):
                if allowed(t, cell, v):
                    tile[t, cell, v] = model.add_var(name=f"tile_{t}_{cell[0]}_{cell[1]}_{v}", var_type=mip.BINARY)

    # at(t, cell, v) is the variable tile[t, cell, v], or None when tile v cannot be on cell at step t
    def at(t, cell, v):
        return tile.get((t, cell, v))

    # every pair of neighbouring squares (p, q), in both directions
    arcs = [(p, q) for p in cells for q in neighbours(p)]

    # slide[t, p, q] is 1 when the blank moves from square p to the neighbouring square q between step t and step t + 1
    slide = {}
    for t in range(n_steps - 1):
        for p, q in arcs:
            if at(t, p, 0) is not None and at(t + 1, q, 0) is not None:
                slide[t, p, q] = model.add_var(name=f"slide_{t}_{p[0]}_{p[1]}_{q[0]}_{q[1]}", var_type=mip.BINARY)

    # Each step is exactly one slide of the blank.
    for t in range(n_steps - 1):
        model.add_constr(mip.xsum(slide[t, p, q] for p, q in arcs if (t, p, q) in slide) == 1)
        for p, q in arcs:
            if (t, p, q) in slide:
                # the blank is on p at step t and on q at step t + 1
                model.add_constr(slide[t, p, q] <= at(t, p, 0))
                model.add_constr(slide[t, p, q] <= at(t + 1, q, 0))

    # When the blank slides from p to q, the tile on q moves to p.
    for t in range(n_steps - 1):
        for p, q in arcs:
            if (t, p, q) not in slide:
                continue
            s = slide[t, p, q]
            for v in range(n_squares):
                before = at(t, q, v)
                after = at(t + 1, p, v)
                if before is None and after is None:
                    continue
                if before is None:
                    model.add_constr(after + s <= 1)
                elif after is None:
                    model.add_constr(before + s <= 1)
                else:
                    model.add_constr(after - before + s <= 1)
                    model.add_constr(before - after + s <= 1)

    # A tile stays on its square unless the blank enters or leaves that square in this step.
    for t in range(n_steps - 1):
        for cell in cells:
            # moved is 1 when the blank enters or leaves cell in this step
            moved = mip.xsum(slide[t, p, q] for p, q in arcs if (t, p, q) in slide and cell in (p, q))
            for v in range(n_squares):
                before = at(t, cell, v)
                after = at(t + 1, cell, v)
                if before is None and after is None:
                    continue
                change = mip.xsum([after] if after is not None else []) - mip.xsum([before] if before is not None else [])
                model.add_constr(change - moved <= 0)
                model.add_constr(-change - moved <= 0)

    # Each board holds exactly one tile on each square, and each tile sits on exactly one square.
    for t in range(n_steps):
        for cell in cells:
            model.add_constr(mip.xsum(tile[t, cell, v] for v in range(n_squares) if (t, cell, v) in tile) == 1)
        for v in range(n_squares):
            model.add_constr(mip.xsum(tile[t, cell, v] for cell in cells if (t, cell, v) in tile) == 1)

    # steps[t][i][j] is the tile on row i, column j at step t.
    steps = []
    for t in range(n_steps):
        board = []
        for r in range(n_rows):
            row = []
            for c in range(n_cols):
                row.append(mip.xsum(v * tile[t, (r, c), v] for v in range(1, n_squares) if (t, (r, c), v) in tile))
            board.append(row)
        steps.append(board)

    return model, {"steps": steps}


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
