# kakuro: a hermax (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install hermax`):
#   python kakuro.py kakuro.json

from hermax.model import Model


def create_model(instance):
    """Kakuro: put a digit from 1 to 9 in each white cell so that every entry (a run of
    white cells across or down) adds up to its clue, and no digit repeats inside an
    entry. Black cells hold 0 in the answer."""
    n = instance["n"]  # side of the square grid
    blanks = instance["blanks"]  # blanks[k] = [row, col] of a black cell, rows and columns counted from 1
    entries = instance["problem"]  # entries[k] = [clue, [row, col], ...]: the clue and the white cells of an entry, counted from 1

    m = Model()

    # x[r][c] is the digit in row r, column c (0-based here), or 0 for a black cell
    x = m.int_matrix("x", n, n, 0, 9)

    # Black cells hold 0.
    for r, c in blanks:
        m &= (x[r - 1][c - 1] == 0)

    for clue, *cells in entries:
        run = [x[r - 1][c - 1] for r, c in cells]  # the white cells of this entry

        # Each white cell holds a real digit, 1 to 9 (0 is reserved for black cells).
        for cell in run:
            m &= cell.in_range(1, 9)

        # The digits of the entry add up to its clue.
        m &= (sum(run) == clue)

        # No digit is repeated within the entry.
        m &= m.vector(run).all_different()

    # Satisfaction problem: no objective.
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
