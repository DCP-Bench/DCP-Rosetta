# csplib_057_killer_sudoku: a CPMpy model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

import math

import cpmpy as cp


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n so that every row, column and box
    holds each number once, and every cage (a group of cells) holds distinct numbers
    adding up to the small number printed in its corner."""
    n = instance["n"]            # side of the grid
    cages = instance["problem"]  # each cage is [total, [[row, col], ...]], with 1-based cells
    box = math.isqrt(n)          # side of a box (3 for the usual 9x9 grid)

    # x[i][j] is the number written in the cell at row i, column j
    x = cp.intvar(1, n, shape=(n, n), name="x")

    model = cp.Model()

    # Every row holds each number once.
    for i in range(n):
        model.add(cp.AllDifferent(x[i, :]))

    # Every column holds each number once.
    for j in range(n):
        model.add(cp.AllDifferent(x[:, j]))

    # Every box holds each number once.
    for bi in range(n // box):
        for bj in range(n // box):
            model.add(cp.AllDifferent(x[bi * box:(bi + 1) * box, bj * box:(bj + 1) * box]))

    # Every cage adds up to its total, and no number appears twice inside a cage.
    for total, cells in cages:
        cage = cp.cpm_array([x[r - 1, c - 1] for r, c in cells])  # cells are 1-based in the data
        model.add(cp.sum(cage) == total)
        model.add(cp.AllDifferent(cage))

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
