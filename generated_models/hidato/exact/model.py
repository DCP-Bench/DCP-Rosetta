# hidato: an Exact (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python hidato.py hidato.json

from exact import Exact


def create_model(instance):
    """Hidato puzzles start semi-filled with numbered tiles. Fill the grid with the
    numbers 1 to r*c, each used once, keeping the given numbers, so that every number
    k and the next number k+1 sit in cells that touch horizontally, vertically or
    diagonally."""
    puzzle = instance["puzzle"]         # puzzle[i][j] is the number given in cell (i, j), or 0 for an empty cell
    r, c = len(puzzle), len(puzzle[0])  # the grid has r rows and c columns
    cells = r * c                       # the number of cells, which is also the largest number
    rows, cols = range(r), range(c)

    solver = Exact()

    # Exact identifies its variables by name.
    # holds[i][j][k - 1] is 1 when cell (i, j) holds the number k, and 0 when not
    holds = [[[f"cell_{i}_{j}_holds_{k}" for k in range(1, cells + 1)] for j in cols] for i in rows]
    for i in rows:
        for j in cols:
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # Each cell holds exactly one number.
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
    # Each number is in exactly one cell.
    for k in range(cells):
        solver.addConstraint([(1, holds[i][j][k]) for i in rows for j in cols], True, 1, True, 1)

    # x[i][j] is the number in cell (i, j). A number already given in the grid fixes it.
    x = [[f"x_{i}_{j}" for j in cols] for i in rows]
    for i in rows:
        for j in cols:
            if puzzle[i][j] > 0:
                solver.addVariable(x[i][j], puzzle[i][j], puzzle[i][j])
            else:
                solver.addVariable(x[i][j], 1, cells)
            solver.addConstraint([(k, holds[i][j][k - 1]) for k in range(1, cells + 1)] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    # If cell (i, j) holds k, then one of the cells next to it holds k + 1.
    for i in rows:
        for j in cols:
            # The cells that touch (i, j) horizontally, vertically or diagonally.
            neighbours = [(i + a, j + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                          if (a or b) and 0 <= i + a < r and 0 <= j + b < c]
            for k in range(1, cells):
                solver.addConstraint([(1, holds[ni][nj][k]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k - 1])], True, 0)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
