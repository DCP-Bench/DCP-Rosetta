# futoshiki: a PyCSP3 model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python futoshiki.py futoshiki.json

from pycsp3 import *


def create_model(instance):
    """A futoshiki puzzle on a square grid, such as 5 x 5: place the digits 1 to n (n the side
    of the grid) so that each row and each column holds every digit once. Some digits are given
    at the start, and inequalities are given between some pairs of squares, one square of each
    pair being higher than the other. These inequalities must be honoured."""
    given = instance["values"]  # given[r][c] is the digit at row r + 1, column c + 1, or 0 for an empty square
    lt = instance["lt"]  # each [r1, c1, r2, c2] (1-based) says the square (r1, c1) is lower than the square (r2, c2)
    n = len(given)  # the side of the grid

    # grid[r][c] is the digit in row r + 1, column c + 1 (0-based indices in the code)
    grid = VarArray(size=[n, n], dom=range(1, n + 1))

    satisfy(
        # Each row holds every digit from 1 to n once.
        [AllDifferent(grid[r]) for r in range(n)],
        # Each column holds every digit from 1 to n once.
        [AllDifferent(grid[:, c]) for c in range(n)],
        # Each digit given at the start stays in its square; 0 marks an empty square.
        [grid[r][c] == given[r][c] for r in range(n) for c in range(n) if given[r][c] != 0],
        # The square (r1, c1) holds a lower digit than the square (r2, c2), for each inequality.
        [grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1] for r1, c1, r2, c2 in lt],
    )

    return {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("grid", "=")
        for row in outputs["grid"]:
            print(values(row))
    else:
        print("No solution:", status())
