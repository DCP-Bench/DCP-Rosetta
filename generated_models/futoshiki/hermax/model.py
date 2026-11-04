# futoshiki: a hermax (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install hermax`):
#   python futoshiki.py futoshiki.json

from hermax.model import Model


def create_model(instance):
    """Futoshiki: fill an n x n grid with the numbers 1 to n so that every row and every
    column holds each number exactly once, the given digits stay where they are, and
    every "less than" sign between two neighbouring cells holds."""
    values = instance["values"]  # values[r][c]: the given digit of cell (r, c), 0 when the cell is empty
    lt = instance["lt"]          # lt[k] = [i1, j1, i2, j2]: cell (i1, j1) is smaller than cell (i2, j2), 1-based
    n = len(values)              # the board is n x n, taken from the instance

    m = Model()

    # grid[r][c] is the number written in row r, column c (0-based), between 1 and n
    grid = m.int_matrix("grid", n, n, 1, n)

    # The given digits are fixed.
    for r in range(n):
        for c in range(n):
            if values[r][c] > 0:
                m &= (grid[r][c] == values[r][c])

    # Every row and every column holds different numbers, so each number appears once.
    for i in range(n):
        m &= grid.row(i).all_different()
        m &= grid.col(i).all_different()

    # Each "less than" sign: the first cell holds a smaller number than the second.
    # The coordinates in the data start at 1, so they are shifted to 0-based indices.
    for i1, j1, i2, j2 in lt:
        m &= (grid[i1 - 1][j1 - 1] < grid[i2 - 1][j2 - 1])

    # The puzzle is a satisfaction problem: there is no objective.
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
