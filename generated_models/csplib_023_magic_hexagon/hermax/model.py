# csplib_023_magic_hexagon: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from hermax.model import Model

# The hexagon's cells are numbered 0..18, row by row (rows of 3, 4, 5, 4 and 3 cells):
#       0  1  2
#     3  4  5  6
#   7  8  9 10 11
#    12 13 14 15
#      16 17 18
# The geometry is fixed by the problem, so the 15 lines are fixed too.
# Lines running across: the 5 rows.
ROWS = [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18]]
# Lines running from top left to bottom right: 5 lines.
DIAGONALS_DOWN = [[0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18]]
# Lines running from top right to bottom left: 5 lines.
DIAGONALS_UP = [[2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16]]


def create_model(instance):
    """Magic hexagon: place the numbers 1 to NUM_CELLS in the cells of a hexagon so that
    the numbers along each of the 15 lines (5 rows and 10 diagonals) add up to the same
    magic sum MAGIC_SUM. Satisfaction problem: any arrangement meeting every line sum."""
    n_cells = instance["NUM_CELLS"]    # NUM_CELLS: how many cells there are, and the largest number used (19)
    magic_sum = instance["MAGIC_SUM"]  # MAGIC_SUM: the total every line must reach (38)

    m = Model()

    # cell[c] is the number written in hexagon cell c, one of 1..NUM_CELLS
    cell = m.int_vector("cell", n_cells, 1, n_cells)

    # Every number from 1 to NUM_CELLS is used exactly once.
    m &= cell.all_different()

    # Each of the 5 rows adds up to the magic sum.
    for line in ROWS:
        m &= (sum(cell[c] for c in line) == magic_sum)

    # Each of the 5 diagonals running top left to bottom right adds up to the magic sum.
    for line in DIAGONALS_DOWN:
        m &= (sum(cell[c] for c in line) == magic_sum)

    # Each of the 5 diagonals running top right to bottom left adds up to the magic sum.
    for line in DIAGONALS_UP:
        m &= (sum(cell[c] for c in line) == magic_sum)

    # LD: the numbers in the cells A..S, in order (A is cell 0 ... S is cell 18)
    return m, {"LD": cell}


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
