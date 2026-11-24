# csplib_057_killer_sudoku: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from pycsp3 import *


def create_model(instance):
    """Killer sudoku: fill the grid with numbers from 1 to 9 so that each row, column and nonet contains
    each number exactly once, the sum of all numbers in each cage matches the small number printed in its
    corner, and no number appears more than once in a cage."""
    # n: the side of the grid, 9 in the statement.
    n = instance["n"]

    # box: the side of a nonet, a block of box by box cells: the square root of n
    box = int(n ** 0.5)

    # cages[k] is [total, cells] for cage k: total is the sum printed in its corner, and cells lists
    # the [row, column] of each cell in the cage, both numbered from 1.
    cages = instance["problem"]

    # x[i][j] is the number in the cell of row i + 1 and column j + 1, from 1 to n.
    x = VarArray(size=[n, n], dom=range(1, n + 1))

    satisfy(
        # Each row contains each number exactly once.
        [AllDifferent(x[i]) for i in range(n)],
        # Each column contains each number exactly once.
        [AllDifferent(x[:, j]) for j in range(n)],
        # Each nonet contains each number exactly once.
        [AllDifferent(x[r:r + box, c:c + box]) for r in range(0, n, box) for c in range(0, n, box)],
        # No number appears twice in a cage (the cells are numbered from 1, so row - 1 and column - 1 index x).
        [AllDifferent(x[row - 1][col - 1] for row, col in cells) for total, cells in cages],
        # The numbers in each cage sum to the total printed in its corner.
        [Sum(x[row - 1][col - 1] for row, col in cells) == total for total, cells in cages],
    )

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
