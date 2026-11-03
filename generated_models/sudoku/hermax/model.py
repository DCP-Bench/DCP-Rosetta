# sudoku: a hermax (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install hermax`):
#   python sudoku.py sudoku.json

from hermax.model import Model


def create_model(instance):
    """Fill a 9 x 9 grid with the digits 1..9 so that every row, every column and every
    3 x 3 box contains each digit exactly once, keeping the digits already given.
    There is no objective: any completed grid is an answer."""
    given = instance["input_grid"]  # given[r][c]: the digit printed in cell (r, c), 0 when the cell is empty
    n = len(given)                  # side of the grid (9 in the puzzle)
    box = 3                         # side of a 3 x 3 box, a rule of Sudoku itself

    m = Model()

    # grid[r][c] is the digit written in row r, column c; it is one of 1..n
    grid = m.int_matrix("grid", n, n, 1, n)

    # The digits given in the puzzle stay where they are.
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                m &= (grid[r][c] == given[r][c])

    # Each row holds every digit once.
    for r in range(n):
        m &= grid.row(r).all_different()
    # Each column holds every digit once.
    for c in range(n):
        m &= grid.col(c).all_different()
    # Each 3 x 3 box holds every digit once.
    for top in range(0, n, box):
        for left in range(0, n, box):
            cells = [grid[r][c] for r in range(top, top + box) for c in range(left, left + box)]
            m &= m.vector(cells).all_different()

    return m, {"grid": grid}


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
