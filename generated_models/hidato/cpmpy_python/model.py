# hidato: a CPMpy model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python hidato.py hidato.json

import cpmpy as cp


def create_model(instance):
    """Fill a grid with the numbers 1 to r*c, each once, so that consecutive numbers sit
    in cells that touch horizontally, vertically or diagonally. Some numbers are
    given."""
    puzzle = instance["puzzle"]  # puzzle[i][j] is the given number in cell (i, j), or 0 for an empty cell
    r, c = len(puzzle), len(puzzle[0])
    n = r * c

    # x[i, j] is the number written in cell (i, j)
    x = cp.intvar(1, n, shape=(r, c), name="x")

    # Helper variables. Cells are numbered row by row, from 0 to n-1.
    # at_cell[q] is the number in cell q, counted from 0
    at_cell = cp.intvar(0, n - 1, shape=n, name="at_cell")
    # where_is[k] is the cell holding number k+1
    where_is = cp.intvar(0, n - 1, shape=n, name="where_is")

    model = cp.Model()
    # The grid and at_cell hold the same numbers.
    model.add(x.flatten() == at_cell + 1)
    # Every number appears in exactly one cell: where_is and at_cell are inverse
    # permutations of each other, which also makes all numbers differ.
    model.add(cp.Inverse(where_is, at_cell))
    # The numbers given at the start are fixed.
    for i in range(r):
        for j in range(c):
            if puzzle[i][j] > 0:
                model.add(x[i, j] == puzzle[i][j])
    # Consecutive numbers k+1 and k+2 sit in different cells that touch, diagonals
    # included. A table of the allowed (cell of k+1, cell of k+2) pairs states this.
    touching = [[i * c + j, (i + di) * c + (j + dj)]
                for i in range(r) for j in range(c)
                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (di != 0 or dj != 0) and 0 <= i + di < r and 0 <= j + dj < c]
    for k in range(n - 1):
        model.add(cp.Table([where_is[k], where_is[k + 1]], touching))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
