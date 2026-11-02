# kakuro: an Exact (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python kakuro.py kakuro.json

from exact import Exact


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]  # side of the grid
    entries = instance["problem"]  # entries[k]: the clue of entry k and the cells it runs over
    blanks = instance["blanks"]  # the cells that are blank, as (row, column) counted from 1

    solver = Exact()

    blank = {(r - 1, c - 1) for r, c in blanks}

    # Exact identifies its variables by name.
    # x[r][c] is the digit in the cell at row r, column c; a blank cell holds 0
    x = [[f"x_{r}_{c}" for c in range(n)] for r in range(n)]
    # is_digit[r][c][d] is 1 when cell (r, c) holds digit d, and 0 when not
    is_digit = [[{} for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            solver.addVariable(x[r][c], 0, 0 if (r, c) in blank else 9)
            for d in range(1, 10):
                is_digit[r][c][d] = f"is_digit_{r}_{c}_{d}"
                solver.addVariable(is_digit[r][c][d], 0, 1)
            # a cell holds at most one digit
            solver.addConstraint([(1, is_digit[r][c][d]) for d in range(1, 10)], False, 0, True, 1)
            # the digit of a cell is the digit it holds
            solver.addConstraint([(d, is_digit[r][c][d]) for d in range(1, 10)] + [(-1, x[r][c])],
                                 True, 0, True, 0)

    for clue, *cells in entries:
        run = [(r - 1, c - 1) for r, c in cells]
        # each cell of the entry holds a digit from 1 to 9
        for r, c in run:
            solver.addConstraint([(1, is_digit[r][c][d]) for d in range(1, 10)], True, 1, True, 1)
        # the digits of the entry add up to its clue
        solver.addConstraint([(1, x[r][c]) for r, c in run], True, clue, True, clue)
        # no digit appears twice in the entry
        for d in range(1, 10):
            solver.addConstraint([(1, is_digit[r][c][d]) for r, c in run], False, 0, True, 1)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
