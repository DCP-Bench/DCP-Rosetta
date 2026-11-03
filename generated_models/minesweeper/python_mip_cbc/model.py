# minesweeper: a Python-MIP (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python minesweeper.py minesweeper.json

import mip


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened cells hold a mine. An opened cell shows how many of its neighbouring
    cells are mines."""
    unopened = instance["X"]      # the value that marks a cell that is not opened yet
    game = instance["game_data"]  # game[r][c]: the number on cell (r, c), or the unopened marker
    rows = len(game)              # the number of rows
    cols = len(game[0])           # the number of columns

    model = mip.Model(solver_name="CBC")

    # mine[r][c] is 1 when cell (r, c) holds a mine, and 0 when not. Opened cells hold no mine.
    mine = [
        [
            model.add_var(f"mine_{r}_{c}", var_type=mip.INTEGER, lb=0, ub=1 if game[r][c] == unopened else 0)
            for c in range(cols)
        ]
        for r in range(rows)
    ]

    # The number on an opened cell is the count of mines among its neighbouring cells.
    for r in range(rows):
        for c in range(cols):
            clue = game[r][c]  # the number shown on cell (r, c)
            if clue == unopened:
                continue
            # the cells next to (r, c), fewer at the edge of the board
            neighbours = [
                mine[nr][nc]
                for nr in range(max(r - 1, 0), min(r + 2, rows))
                for nc in range(max(c - 1, 0), min(c + 2, cols))
                if (nr, nc) != (r, c)
            ]
            model.add_constr(mip.xsum(neighbours) == clue)

    # mines[r][c] is 1 where cell (r, c) holds a mine.
    return model, {"mines": mine}


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
