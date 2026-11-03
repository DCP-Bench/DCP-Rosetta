# n_puzzle: a SCIP (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python n_puzzle.py n_puzzle.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """The N-Puzzle: a square board holds numbered tiles and one empty square (tile 0).
    A move slides a tile into the empty square. Find N_STEPS boards, counting the start
    and the end, that run from the start board to the end board, each board one slide
    away from the board before it, so that no step leaves the board unchanged."""
    N_STEPS = instance["N_STEPS"]                # the number of boards in the plan, start and end included
    start = np.array(instance["puzzle_start"])   # start[r, c]: the tile in row r, column c of the start board
    end = np.array(instance["puzzle_end"])       # end[r, c]: the tile in row r, column c of the end board
    n = len(start)                               # the board is n x n, with n read from the start board
    cells = n * n                                # cells are numbered p = r * n + c, row by row
    tiles = np.arange(cells)                     # tile numbers are 0 to n * n - 1, with 0 the empty square

    model = Model("n_puzzle")

    # at[s, p, v] is 1 when, on board s, cell p holds tile v. SCIP has no all-different
    # constraint, so each board, a permutation of the tiles over the cells, is written with
    # one-hot binaries: the sums below say each cell holds one tile and each tile sits on one cell.
    at = model.addMatrixVar((N_STEPS, cells, cells), vtype="B", name="at")

    # Each cell holds exactly one tile.
    model.addMatrixCons(at.sum(axis=2) == 1)
    # Each tile sits on exactly one cell.
    model.addMatrixCons(at.sum(axis=1) == 1)

    # The first board is the start board and the last board is the end board. Row p of
    # np.eye(cells) is the one-hot form of tile p, so the rows fix the tile on each cell.
    model.addMatrixCons(at[0] == np.eye(cells, dtype=int)[start.reshape(-1)])
    model.addMatrixCons(at[-1] == np.eye(cells, dtype=int)[end.reshape(-1)])

    # adj[p, q] is 1 when cells p and q share an edge, that is when they are one row or one
    # column apart and not both. A slide moves a tile between two cells that share an edge.
    row = np.arange(cells) // n
    col = np.arange(cells) % n
    adj = ((np.abs(row[:, None] - row[None, :]) + np.abs(col[:, None] - col[None, :])) == 1).astype(int)

    # The empty square moves to a neighbouring cell at every step: if it is on cell p on board s,
    # then on board s + 1 it is on a cell that shares an edge with p. A cell shares no edge with
    # itself, so the empty square cannot stay where it is and every step is a slide.
    blank = at[:, :, 0]
    model.addMatrixCons(blank[:-1] <= blank[1:] @ adj)

    # A slide changes only the two cells involved: the cell the empty square leaves on board s
    # and the cell it enters on board s + 1. Let touched[s, p] be 1 for those two cells and 0
    # elsewhere. Every other cell keeps its tile, so for each cell and tile the change from board
    # s to board s + 1 is 0 wherever touched is 0. It is written as two inequalities
    # (change <= touched and -change <= touched) instead of abs(change) <= touched, because SCIP
    # handles abs slowly. touched does not depend on the tile, so it is repeated over the tile axis.
    touched = blank[:-1] + blank[1:]
    change = at[1:] - at[:-1]
    model.addMatrixCons(change <= touched[:, :, None])
    model.addMatrixCons(-change <= touched[:, :, None])

    # There is no objective: any plan that meets the constraints is an answer.

    # Each board is read back as its n x n grid of tile numbers. On board s, cell p holds tile
    # sum over v of v * at[s, p, v], since exactly one at[s, p, v] is 1; the reshape cuts each
    # board of n * n cells into n rows of n.
    steps = (at * tiles).sum(axis=2).reshape(N_STEPS, n, n)
    return model, {"steps": steps}


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
