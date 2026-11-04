# kakuro: a CPMpy model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python kakuro.py kakuro.json

import cpmpy as cp


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # blanks[k]: the [row, col] (1-based) of a black cell
    entries = instance["problem"]  # each entry is [clue, [row, col], [row, col], ...]: its clue, then its cells (1-based)

    # x[i, j] is the digit in the cell at row i, column j (0-based); black cells hold 0
    x = cp.intvar(0, 9, shape=(n, n), name="x")

    model = cp.Model()

    # Black cells hold 0.
    for row, col in blanks:
        model.add(x[row - 1, col - 1] == 0)

    for clue, *cells in entries:
        entry = cp.cpm_array([x[row - 1, col - 1] for row, col in cells])
        # The cells of an entry are white, so each holds a digit from 1 to 9.
        model.add(entry >= 1)
        # The digits of the entry add up to its clue.
        model.add(cp.sum(entry) == clue)
        # No digit is repeated within the entry.
        model.add(cp.AllDifferent(entry))

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
