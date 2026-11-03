# kakuro: a cvc5 (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python kakuro.py kakuro.json

import cvc5.pythonic as c5


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the black cells, as [row, col]
    entries = instance["problem"]  # each entry is [clue, [row, col], ...]: its clue, then the cells it covers

    # x[i][j] is the digit in the cell at row i + 1, column j + 1; black cells hold 0
    x = [[c5.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    black = {(row - 1, col - 1) for row, col in blanks}

    solver = c5.Solver()

    for i in range(n):
        for j in range(n):
            if (i, j) in black:
                solver.add(x[i][j] == 0)
            else:
                # Each white cell holds a digit from 1 to 9.
                solver.add(x[i][j] >= 1, x[i][j] <= 9)

    for clue, *cells in entries:
        entry = [x[row - 1][col - 1] for row, col in cells]
        # The digits of the entry add up to its clue.
        solver.add(c5.Sum(entry) == clue)
        # No digit repeats within the entry.
        if len(entry) >= 2:
            solver.add(c5.Distinct(entry))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
