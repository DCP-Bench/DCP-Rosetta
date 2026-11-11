# sudoku: a PyCSP3 model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python sudoku.py sudoku.json

from pycsp3 import *


def create_model(instance):
    """Fill a 9x9 grid with numbers so that each row, column and 3x3 section contain
    all the digits between 1 and 9, keeping the numbers already given in the input grid."""
    clues = instance["input_grid"]  # clues[i][j] is the number given in row i, column j, 0 when empty
    n = 9  # the grid is 9 by 9 and holds the digits 1 to 9 (fixed by the statement)
    box = 3  # each section is 3 by 3 (fixed by the statement)

    # grid[i][j] is the number in row i, column j
    grid = VarArray(size=[n, n], dom=range(1, n + 1))

    satisfy(
        # The given numbers stay where they are.
        [grid[i][j] == clue for i, row in enumerate(clues) for j, clue in enumerate(row) if clue != 0],
        # Each row contains all the digits once.
        [AllDifferent(grid[i]) for i in range(n)],
        # Each column contains all the digits once.
        [AllDifferent(grid[:, j]) for j in range(n)],
        # Each 3x3 section contains all the digits once.
        [AllDifferent(grid[r + a][c + b] for a in range(box) for b in range(box))
         for r in range(0, n, box) for c in range(0, n, box)],
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
