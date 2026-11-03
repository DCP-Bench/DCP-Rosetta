# kakuro: a Z3 (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python kakuro.py kakuro.json

import z3


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the [row, col] of each black cell, counted from 1
    entries = instance["problem"]  # each entry is [clue, [row, col], ...]: its clue, then the cells it covers, counted from 1

    # x[r][c] is the digit in the cell at row r, column c; black cells hold 0
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    solver = z3.Solver()

    # Every cell holds a digit from 0 to 9.
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 0, x[r][c] <= 9)

    # Black cells hold 0.
    for row, col in blanks:
        solver.add(x[row - 1][col - 1] == 0)

    for clue, *cells in entries:
        entry = [x[row - 1][col - 1] for row, col in cells]
        # The cells of an entry are white, so each holds a digit from 1 to 9.
        solver.add([cell >= 1 for cell in entry])
        # The digits of the entry add up to its clue.
        solver.add(z3.Sum(entry) == clue)
        # No digit is repeated within the entry.
        solver.add(z3.Distinct(entry))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
