# kakuro: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install ortools`):
#   python kakuro.py kakuro.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of the grid so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the black cells
    entries = instance["problem"]  # each entry has its clue and the cells it covers

    model = cp_model.CpModel()

    # The cells of the entries are white, so they hold a digit from 1 to 9.
    white = {(row - 1, col - 1) for _, *cells in entries for row, col in cells}

    # x[r][c] is the digit in the cell at row r, column c.
    x = [
        [model.new_int_var(1 if (r, c) in white else 0, 9, f"x_{r}_{c}") for c in range(n)]
        for r in range(n)
    ]

    # Black cells hold 0.
    for row, col in blanks:
        model.add(x[row - 1][col - 1] == 0)

    for clue, *cells in entries:
        # The digits in the cells of the entry.
        entry = [x[row - 1][col - 1] for row, col in cells]
        # The digits of the entry add up to its clue.
        model.add(sum(entry) == clue)
        # No digit is repeated within the entry.
        model.add_all_different(entry)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
