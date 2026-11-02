# hidato: a cvc5 (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python hidato.py hidato.json

import cvc5.pythonic as c5


# At least one of the expressions holds.
def any_of(items):
    if len(items) == 1:
        return items[0]
    return c5.Or(items)


# The cells that touch cell (i, j) horizontally, vertically or diagonally.
def touching(i, j, n_rows, n_cols):
    return [
        (a, b)
        for a in range(i - 1, i + 2)
        for b in range(j - 1, j + 2)
        if (a, b) != (i, j) and 0 <= a < n_rows and 0 <= b < n_cols
    ]


def create_model(instance):
    """Fill the empty cells of a grid with the numbers 1 to r*c, each used once, so that
    the given numbers keep their cells and consecutive numbers touch horizontally,
    vertically or diagonally."""
    puzzle = instance["puzzle"]  # puzzle[i][j] is the number given in cell (i, j), or 0 if the cell is empty
    n_rows = len(puzzle)         # number of rows in the grid
    n_cols = len(puzzle[0])      # number of columns in the grid
    n_cells = n_rows * n_cols    # how many numbers the grid holds

    # x[i][j] is the number written in cell (i, j)
    x = [[c5.Int(f"x_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]
    # All cells in one flat list, row by row.
    cells = [x[i][j] for i in range(n_rows) for j in range(n_cols)]

    solver = c5.Solver()

    # Each number is used in one cell only.
    solver.add(c5.Distinct(cells))

    # Every cell holds a number from 1 to n_cells.
    solver.add([c >= 1 for c in cells])
    solver.add([c <= n_cells for c in cells])

    # The given numbers keep their cells.
    solver.add([
        x[i][j] == puzzle[i][j]
        for i in range(n_rows)
        for j in range(n_cols)
        if puzzle[i][j] != 0
    ])

    # If a cell holds k, a touching cell holds k + 1.
    for i in range(n_rows):
        for j in range(n_cols):
            for k in range(1, n_cells):
                solver.add(
                    c5.Implies(
                        x[i][j] == k,
                        any_of([x[a][b] == k + 1 for a, b in touching(i, j, n_rows, n_cols)]),
                    )
                )

    return solver, {"x": x}


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
