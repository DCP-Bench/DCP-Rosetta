# hidato: a hermax (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install hermax`):
#   python hidato.py hidato.json

from functools import reduce
from operator import or_

from hermax.model import Model


def create_model(instance):
    """Hidato: fill a grid with the numbers 1..rows*cols, each used once, keeping the
    given numbers, so that consecutive numbers sit in cells that touch horizontally,
    vertically or diagonally."""
    puzzle = instance["puzzle"]  # puzzle[i][j]: the given number in cell (i, j), 0 for an empty cell
    rows = len(puzzle)           # the number of rows of the grid
    cols = len(puzzle[0])        # the number of columns of the grid
    total = rows * cols          # the numbers run from 1 to total, each once

    # the given numbers as (row, col, value)
    givens = [(i, j, puzzle[i][j]) for i in range(rows) for j in range(cols) if puzzle[i][j] > 0]

    def neighbours(i, j):
        # the cells touching (i, j), diagonals included, inside the grid
        return [(i + di, j + dj)
                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                if (di, dj) != (0, 0) and 0 <= i + di < rows and 0 <= j + dj < cols]

    # Which numbers each cell can hold. A given number stays in its cell. Any other
    # cell at Chebyshev distance d from the cell of a given number v can only hold a
    # number k with |k - v| >= d, because consecutive numbers touch and each step moves
    # at most one cell. This is a consequence of the rules that keeps domains small.
    allowed = {}
    for i in range(rows):
        for j in range(cols):
            if puzzle[i][j] > 0:
                allowed[(i, j)] = [puzzle[i][j]]
            else:
                allowed[(i, j)] = [k for k in range(1, total + 1)
                                   if all(max(abs(i - gi), abs(j - gj)) <= abs(k - v) for gi, gj, v in givens)]

    m = Model()

    # x[i][j] is the number written in cell (i, j) (the declared output), with the
    # smallest range covering the numbers that cell can hold (the exact set is enforced below).
    # A given cell can hold only its given number, so its range already fixes it.
    x = [[m.int(f"x_{i}_{j}", min(allowed[(i, j)]), max(allowed[(i, j)])) for j in range(cols)]
         for i in range(rows)]

    # Rule out the holes: numbers inside the range of a cell but not allowed there.
    for i in range(rows):
        for j in range(cols):
            for k in range(min(allowed[(i, j)]), max(allowed[(i, j)]) + 1):
                if k not in allowed[(i, j)]:
                    m &= (x[i][j] != k)

    # Every cell holds a different number: the numbers 1..total fill the grid exactly once.
    m &= m.vector([x[i][j] for i in range(rows) for j in range(cols)]).all_different()

    # Consecutive numbers touch. If a cell holds k (k < total), then one of the cells
    # touching it holds k + 1 (only allowed numbers are listed, the holes are excluded
    # above). Since every number is used once, this chains 1, 2, ..., total through
    # touching cells.
    for (i, j), ks in allowed.items():
        for k in ks:
            if k < total:
                # the literals that say the cell is not k, or a touching cell is k + 1
                options = [x[i][j] != k] + [x[a][b] == k + 1 for a, b in neighbours(i, j)
                                            if k + 1 in allowed[(a, b)]]
                m &= reduce(or_, options)

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
