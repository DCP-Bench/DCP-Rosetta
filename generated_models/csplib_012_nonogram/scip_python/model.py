# csplib_012_nonogram: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from pyscipopt import Model, quicksum


def place_runs(model, shaded, runs):
    """Constrain the squares `shaded` of one line (a row or a column) to show the
    runs of consecutive shaded squares given by `runs`, in order, with at least
    one unshaded square between two runs."""
    n = len(shaded)  # the number of squares in the line, from the grid size

    # Run b can only start inside a window of squares, which the clue fixes.
    # It cannot start before the earlier runs and their gaps need room, which is
    # earliest[b]; it cannot start so late that the later runs and their gaps
    # would leave the line, which is latest[b]. Both come from the clue and n alone.
    earliest = [sum(length + 1 for length in runs[:b]) for b in range(len(runs))]
    latest = [n - runs[b] - sum(length + 1 for length in runs[b + 1:]) for b in range(len(runs))]

    # start[b][p] is 1 when run b begins at square p, for each p in its window.
    # SCIP has no constraint for a run of consecutive ones, so the position of
    # each run is a one-hot choice among the squares of its window.
    start = [{p: model.addVar(vtype="B") for p in range(earliest[b], latest[b] + 1)}
             for b in range(len(runs))]

    # Each run begins at exactly one square.
    for b in range(len(runs)):
        model.addCons(quicksum(start[b].values()) == 1)

    # Runs keep their order, and the next run begins after the last square of
    # the previous one plus one unshaded square.
    for b in range(len(runs) - 1):
        begin_b = quicksum(p * s for p, s in start[b].items())
        begin_next = quicksum(p * s for p, s in start[b + 1].items())
        model.addCons(begin_next >= begin_b + runs[b] + 1)

    # A square is shaded exactly when a run covers it. Run b covers square c when
    # it begins at one of the squares from c - runs[b] + 1 to c. Runs do not
    # overlap, so at most one run covers each square.
    for c in range(n):
        covering = [start[b][p]
                    for b in range(len(runs))
                    for p in range(max(earliest[b], c - runs[b] + 1), min(latest[b], c) + 1)]
        model.addCons(shaded[c] == quicksum(covering))


def create_model(instance):
    """Nonogram: shade squares of a grid so that the runs of consecutive shaded
    squares in each row and in each column match that row's or column's clue.
    A clue lists the run lengths in order (left to right for a row, top to
    bottom for a column), and two runs are separated by at least one unshaded
    square. The model returns the board, 1 for a shaded square and 0 for an
    unshaded one."""
    rows = instance["rows"]            # the number of rows of the grid
    cols = instance["cols"]            # the number of columns of the grid
    row_rules = instance["row_rules"]  # row_rules[i]: the clue of row i, padded with 0s on the left
    col_rules = instance["col_rules"]  # col_rules[j]: the clue of column j, padded with 0s on the left

    model = Model("csplib_012_nonogram")

    # board[i, j] is 1 when the square in row i and column j is shaded, and 0 when it is not
    board = model.addMatrixVar((rows, cols), vtype="B", name="board")

    # The 0s in a clue only pad it to the grid's clue width, so the runs are its nonzero entries.
    # Each row and each column is a line whose shaded squares must show its runs.
    for i in range(rows):
        place_runs(model, board[i, :], [n for n in row_rules[i] if n > 0])
    for j in range(cols):
        place_runs(model, board[:, j], [n for n in col_rules[j] if n > 0])

    # The board is a satisfaction problem, so no objective is set.
    return model, {"board": board}


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
