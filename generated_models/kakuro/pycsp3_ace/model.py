# kakuro: a PyCSP3 model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python kakuro.py kakuro.json

from pycsp3 import *


def create_model(instance):
    """Fill the white cells of a Kakuro grid with the digits 1 to 9 so that the digits
    of each entry sum to its clue and no digit is used twice in an entry."""
    n = instance["n"]                 # the grid has n rows and n columns
    blanks = instance["blanks"]       # [row, column] of each clue or black cell, 1-based: these hold no digit
    max_digit = 9                     # the digits are 1 to 9

    # each entry is its clue and its white cells, [row, column] 1-based; shifted to 0-based
    entries = [(entry[0], [(r - 1, c - 1) for r, c in entry[1:]]) for entry in instance["problem"]]
    # the clue and black cells, 0-based
    blank_cells = [(r - 1, c - 1) for r, c in blanks]
    # the white cells, 0-based: every cell that is not a blank
    white_cells = [(r, c) for r in range(n) for c in range(n) if (r, c) not in blank_cells]

    # x[r][c] is the digit in row r and column c (0-based), 0 for a blank cell
    x = VarArray(size=[n, n], dom=range(max_digit + 1), id="x")

    satisfy(
        # the clue and black cells hold no digit
        [x[r][c] == 0 for r, c in blank_cells],
        # every white cell holds a digit from 1 to 9
        [x[r][c] >= 1 for r, c in white_cells],
        # no digit is duplicated within an entry
        [AllDifferent([x[r][c] for r, c in cells]) for clue, cells in entries],
        # the digits of each entry sum to its clue
        [Sum(x[r][c] for r, c in cells) == clue for clue, cells in entries],
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
