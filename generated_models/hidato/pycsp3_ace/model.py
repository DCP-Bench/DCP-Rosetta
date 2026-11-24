# hidato: a PyCSP3 model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python hidato.py hidato.json

from pycsp3 import *


def create_model(instance):
    """A Hidato puzzle starts with some numbered tiles in a square grid. Fill in the empty
    cells, marked 0 in the given puzzle, so that the grid holds each number from 1 to the
    number of cells exactly once. Consecutive numbers must touch horizontally, vertically
    or diagonally, and the numbers must be in increasing order along the path. Find the
    solved puzzle."""
    # The given grid: puzzle[r][c] is the number in row r and column c, or 0 for an empty cell.
    puzzle = instance["puzzle"]
    # The grid is n by n.
    n = len(puzzle)
    # The numbers are 1 to n_cells, one per cell.
    n_cells = n * n

    # Cell i is in row i // n and column i % n (0-based). cell_value[i] is the number in cell i.
    cell_value = VarArray(size=n_cells, dom=range(1, n_cells + 1))
    # position[k] is the cell that holds the number k + 1 (k is 0-based, the number is 1-based).
    position = VarArray(size=n_cells, dom=range(n_cells))

    satisfy(
        # Each number is in one cell, and no two numbers share a cell.
        AllDifferent(position),
        # The position of each number is the cell that holds it.
        [cell_value[position[k]] == k + 1 for k in range(n_cells)],
        # The numbers given in the puzzle stay where they are; empty cells (0) are left free.
        [cell_value[r * n + c] == puzzle[r][c] for r in range(n) for c in range(n) if puzzle[r][c] != 0],
        # Consecutive numbers k + 1 and k + 2 touch: their cells are at most one row apart...
        [abs(position[k] // n - position[k + 1] // n) <= 1 for k in range(n_cells - 1)],
        # ...and at most one column apart. Together with the distinct cells, they touch diagonally too.
        [abs(position[k] % n - position[k + 1] % n) <= 1 for k in range(n_cells - 1)],
    )

    # The solved grid: x[r][c] is the number in row r and column c.
    x = [[cell_value[r * n + c] for c in range(n)] for r in range(n)]

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
